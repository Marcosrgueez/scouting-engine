"""Fase 5 - Player Role Score (score de encaje por rol, escala 0-100).

Puebla `player_role_scores` + `player_role_score_breakdown` de forma
idempotente (DELETE scoped + INSERT), a partir de `player_percentiles`
(Fase 3) y del catalogo `roles` / `role_buckets` / `role_weights`
(db/seed_catalogs.py).

Formula, por (jugador, temporada, rol) cuyo bucket de posicion aplique al
rol:

    score = SUM(percentil_metrica * peso) / SUM(peso)      -> ya en [0,100]

sobre las metricas del rol PARA LAS QUE EL JUGADOR TIENE PERCENTIL.

--- Metricas faltantes -----------------------------------------------------

Se EXCLUYEN del numerador y del denominador (el peso total se renormaliza
sobre lo disponible). NO se imputan a percentil 50.

Motivo: los percentiles de Fase 3 ya imputan los ceros que Sportmonks
omite ANTES de rankear, asi que un percentil BAJO ya significa "este
jugador hace poco de esto". Una fila de percentil AUSENTE significa otra
cosa: falta de dato (una liga/temporada futura donde esa metrica no se
recoge), no falta de la accion. Imputar 50 afirmaria "este jugador es
mediano en X" sin ninguna evidencia y sesgaria el score compuesto hacia
el centro justo en las metricas donde no sabemos nada. Renormalizar el
peso sobre lo disponible es como debe degradar una media ponderada.

Guarda: si el peso disponible < MIN_WEIGHT_COVERAGE * (peso total del rol),
NO se emite fila para ese jugador-rol (un score renormalizado sobre <60%
de la senal del rol no es comparable con el resto). Queda contado en el
resumen.

Sobre LaLiga 2024/25 la cobertura es del 100 % para las 18 metricas de
los 4 roles en todos los buckets (la imputacion de ceros de Fase 3
garantiza una fila por jugador y metrica), asi que 0 jugadores se ven
afectados por esta politica hoy; solo importa cuando entren mas ligas.

Uso:
    python -m analysis.role_scores                  # umbral 900 (como Fase 3)
    python -m analysis.role_scores --min-minutes 750
    python -m analysis.role_scores --season-id 1 --competition-id 1
    python -m analysis.role_scores --dry-run
"""

from __future__ import annotations

import argparse
import time

from sqlalchemy import text

from db.database import get_session

DEFAULT_MIN_MINUTES = 900
# fraccion minima del peso total de un rol que un jugador debe tener
# cubierta (con percentil disponible) para recibir score en ese rol.
MIN_WEIGHT_COVERAGE = 0.60


# contribucion de cada metrica de cada rol para cada jugador cuyo bucket
# de posicion aplique al rol. Es el nivel de detalle que se guarda en
# player_role_score_breakdown.
_CONTRIB_SQL = """
contrib AS (
    SELECT
        pp.player_id, pp.season_id, pp.position_bucket,
        rw.role_id, rw.stat_type_id, rw.tier, rw.weight,
        pp.percentile,
        ROUND(pp.percentile * rw.weight, 2) AS contribution
    FROM player_percentiles pp
    JOIN role_weights rw ON rw.stat_type_id = pp.stat_type_id
    JOIN role_buckets rb ON rb.role_id = rw.role_id AND rb.bucket = pp.position_bucket
    WHERE pp.min_minutes = :min_minutes
      AND (:season_id IS NULL OR pp.season_id = :season_id)
      AND (:competition_id IS NULL OR pp.competition_id = :competition_id)
),
role_full_weight AS (
    SELECT role_id, SUM(weight) AS full_weight
    FROM role_weights GROUP BY role_id
),
scored AS (
    SELECT
        c.player_id, c.season_id, c.position_bucket, c.role_id,
        SUM(c.contribution) / NULLIF(SUM(c.weight), 0) AS score,
        SUM(c.weight) AS total_weight,
        COUNT(*)      AS metrics_used
    FROM contrib c
    JOIN role_full_weight rfw ON rfw.role_id = c.role_id
    GROUP BY c.player_id, c.season_id, c.position_bucket, c.role_id, rfw.full_weight
    HAVING SUM(c.weight) >= :min_coverage * rfw.full_weight
)
"""

# INSERT en las 2 tablas en una sola sentencia: CTE data-modifying con
# RETURNING para enganchar el desglose al score recien creado.
_INSERT_SQL = f"""
WITH {_CONTRIB_SQL},
ins AS (
    INSERT INTO player_role_scores
        (player_id, season_id, role_id, position_bucket, score,
         total_weight, metrics_used, min_minutes)
    SELECT
        s.player_id, s.season_id, s.role_id, s.position_bucket,
        ROUND(s.score::numeric, 2), s.total_weight, s.metrics_used, :min_minutes
    FROM scored s
    RETURNING id, player_id, season_id, role_id
)
INSERT INTO player_role_score_breakdown
    (player_role_score_id, stat_type_id, tier, percentile, weight, contribution)
SELECT ins.id, c.stat_type_id, c.tier, c.percentile, c.weight, c.contribution
FROM contrib c
JOIN ins ON ins.player_id = c.player_id
        AND ins.season_id = c.season_id
        AND ins.role_id   = c.role_id
"""

_DELETE_SQL = """
DELETE FROM player_role_scores
WHERE (:season_id IS NULL OR season_id = :season_id)
"""

_SUMMARY_SQL = """
SELECT
    r.code, r.label,
    COUNT(*)                                                  AS jugadores,
    ROUND(AVG(prs.score), 1)                                  AS media,
    MIN(prs.score)                                            AS minimo,
    MAX(prs.score)                                            AS maximo,
    COUNT(*) FILTER (WHERE prs.total_weight < rfw.full_weight) AS con_huecos
FROM player_role_scores prs
JOIN roles r ON r.id = prs.role_id
JOIN (SELECT role_id, SUM(weight) AS full_weight FROM role_weights GROUP BY role_id) rfw
     ON rfw.role_id = prs.role_id
WHERE (:season_id IS NULL OR prs.season_id = :season_id)
GROUP BY r.id, r.code, r.label
ORDER BY r.id
"""

# (jugador, rol) con bucket aplicable pero descartados por la guarda de
# cobertura minima.
_SKIPPED_SQL = """
WITH rfw AS (
    SELECT role_id, SUM(weight) AS full_weight FROM role_weights GROUP BY role_id
),
cov AS (
    SELECT pp.player_id, rw.role_id, SUM(rw.weight) AS avail
    FROM player_percentiles pp
    JOIN role_weights rw ON rw.stat_type_id = pp.stat_type_id
    JOIN role_buckets rb ON rb.role_id = rw.role_id AND rb.bucket = pp.position_bucket
    WHERE pp.min_minutes = :min_minutes
      AND (:season_id IS NULL OR pp.season_id = :season_id)
      AND (:competition_id IS NULL OR pp.competition_id = :competition_id)
    GROUP BY pp.player_id, rw.role_id
)
SELECT COUNT(*)
FROM cov JOIN rfw ON rfw.role_id = cov.role_id
WHERE cov.avail < :min_coverage * rfw.full_weight
"""

_TOTALS_SQL = """
SELECT COUNT(*) AS filas, COUNT(DISTINCT player_id) AS jugadores
FROM player_role_scores
WHERE (:season_id IS NULL OR season_id = :season_id)
"""


def recompute(session, min_minutes=DEFAULT_MIN_MINUTES, season_id=None,
              competition_id=None, dry_run=False):
    started = time.monotonic()
    p = {
        "min_minutes": min_minutes,
        "season_id": season_id,
        "competition_id": competition_id,
        "min_coverage": MIN_WEIGHT_COVERAGE,
    }

    session.execute(text(_DELETE_SQL), p)
    session.execute(text(_INSERT_SQL), p)

    rows = session.execute(text(_SUMMARY_SQL), p).all()
    skipped = session.execute(text(_SKIPPED_SQL), p).scalar_one()
    filas, jugadores = session.execute(text(_TOTALS_SQL), p).one()

    if dry_run:
        session.rollback()
    else:
        session.commit()

    elapsed = time.monotonic() - started
    _print_summary(rows, skipped, filas, jugadores, min_minutes, elapsed, dry_run)
    return rows


def _print_summary(rows, skipped, filas, jugadores, min_minutes, elapsed, dry_run):
    print("\n" + "=" * 72)
    print(f"  player_role_scores - {'DRY-RUN' if dry_run else 'ESCRITO'}  "
          f"(percentiles con umbral {min_minutes} min)")
    print("=" * 72)
    print(f"  {'rol':<22} {'jug':>5} {'media':>7} {'min':>7} {'max':>7} {'c/huecos':>9}")
    print("  " + "-" * 62)
    for code, label, jug, media, minimo, maximo, con_huecos in rows:
        print(f"  {label:<22} {jug:>5} {media!s:>7} {minimo!s:>7} {maximo!s:>7} {con_huecos:>9}")
    print("  " + "-" * 62)
    print(f"  TOTAL: {filas} filas de score, {jugadores} jugadores distintos")
    print(f"  descartados por cobertura < {MIN_WEIGHT_COVERAGE:.0%} del peso del rol: {skipped}")
    print(f"  tiempo: {elapsed:.2f} s")
    print("=" * 72)


def main():
    ap = argparse.ArgumentParser(description="Fase 5: Player Role Score con pesos")
    ap.add_argument("--min-minutes", type=int, default=DEFAULT_MIN_MINUTES,
                    help="umbral con el que se calcularon los percentiles de entrada")
    ap.add_argument("--season-id", type=int, default=None)
    ap.add_argument("--competition-id", type=int, default=None)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    session = get_session()
    try:
        recompute(session, min_minutes=args.min_minutes, season_id=args.season_id,
                  competition_id=args.competition_id, dry_run=args.dry_run)
    finally:
        session.close()


if __name__ == "__main__":
    main()
