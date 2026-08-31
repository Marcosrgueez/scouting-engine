"""Fase 8 (parte de equipo) - ejes de estilo por equipo/formacion.

Puebla `team_style_axes` de forma idempotente (DELETE scoped + INSERT), a
partir de `team_fixtures` + `team_fixture_statistics` (Fase 7). Es la parte
CARA y reutilizable del Tactical Fit Score: los percentiles de estilo
entre los 20 equipos de LaLiga, independientes del jugador. El fit en si
se calcula bajo demanda (analysis/tactical_fit.py).

5 ejes, todos desde las stats PROPIAS del equipo (is_conceded = false):
  - possession          = media de ball-possession
  - pass_accuracy       = media de successful-passes-percentage
  - crossing_frequency  = media de total-crosses por partido
  - press_intensity     = media de (tackles + interceptions) por partido
  - directness          = SUM(long-passes) / SUM(passes) * 100

Filas generadas por equipo:
  - 1 agregado (formation = NULL): todos sus partidos.
  - 1 por formacion con >= min_matches partidos (5 por defecto = criterio
    de Fase 7). Por debajo del umbral no se emite fila de formacion; el
    consumidor cae al agregado.

Percentil: para CADA fila (agregado o formacion), el pool de referencia
son los 20 AGREGADOS de equipo. Metodo Hazen:
    100 * (nº agregados con valor < v + 0.5 * nº con valor = v) / 20
-> los 20 agregados quedan repartidos en [2.5, 97.5]; las formaciones
interpolan sobre esa misma escala.

Uso:
    python -m analysis.team_style                 # umbral 5
    python -m analysis.team_style --min-matches 4
    python -m analysis.team_style --dry-run
"""

from __future__ import annotations

import argparse
import time

from sqlalchemy import bindparam, text

from db.database import get_session

DEFAULT_MIN_MATCHES = 5

_AXIS_CODES = (
    "ball-possession", "successful-passes-percentage",
    "total-crosses", "tackles", "interceptions", "long-passes", "passes",
)

_RANKED_SQL = """
WITH own AS (
    SELECT tf.id AS tf_id, tf.team_id, tf.season_id, tf.formation,
           tst.code, tfs.value
    FROM team_fixtures tf
    JOIN team_fixture_statistics tfs
      ON tfs.team_fixture_id = tf.id AND tfs.is_conceded = false
    JOIN team_stat_types tst ON tst.id = tfs.team_stat_type_id
    WHERE (:season_id IS NULL OR tf.season_id = :season_id)
      AND tst.code IN :axis_codes
),
fx AS (
    SELECT tf_id, team_id, season_id, formation,
        MAX(value) FILTER (WHERE code = 'ball-possession')                AS poss,
        MAX(value) FILTER (WHERE code = 'successful-passes-percentage')   AS passacc,
        MAX(value) FILTER (WHERE code = 'total-crosses')                  AS crosses,
        MAX(value) FILTER (WHERE code = 'tackles')                        AS tackles,
        MAX(value) FILTER (WHERE code = 'interceptions')                  AS inters,
        MAX(value) FILTER (WHERE code = 'long-passes')                    AS longp,
        MAX(value) FILTER (WHERE code = 'passes')                         AS passes
    FROM own
    GROUP BY tf_id, team_id, season_id, formation
),
prof AS (
    -- por formacion, solo si llega al umbral
    SELECT team_id, season_id, formation, COUNT(*) AS n,
           AVG(poss)                              AS possession,
           AVG(passacc)                           AS pass_accuracy,
           AVG(crosses)                           AS crossing_frequency,
           AVG(tackles + inters)                  AS press_intensity,
           SUM(longp) / NULLIF(SUM(passes), 0) * 100.0 AS directness
    FROM fx
    GROUP BY team_id, season_id, formation
    HAVING COUNT(*) >= :min_matches
    UNION ALL
    -- agregado del equipo (formation NULL)
    SELECT team_id, season_id, NULL::varchar, COUNT(*) AS n,
           AVG(poss), AVG(passacc), AVG(crosses), AVG(tackles + inters),
           SUM(longp) / NULLIF(SUM(passes), 0) * 100.0
    FROM fx
    GROUP BY team_id, season_id
),
prof_long AS (
    SELECT team_id, season_id, formation, n, 'possession'         AS axis, possession         AS val FROM prof
    UNION ALL SELECT team_id, season_id, formation, n, 'pass_accuracy',      pass_accuracy      FROM prof
    UNION ALL SELECT team_id, season_id, formation, n, 'crossing_frequency', crossing_frequency FROM prof
    UNION ALL SELECT team_id, season_id, formation, n, 'press_intensity',    press_intensity    FROM prof
    UNION ALL SELECT team_id, season_id, formation, n, 'directness',         directness         FROM prof
),
ref AS (  -- los 20 agregados de equipo, por eje
    SELECT axis, val FROM prof_long WHERE formation IS NULL
),
ref_n AS (
    SELECT COUNT(DISTINCT team_id) AS n_teams FROM prof_long WHERE formation IS NULL
),
scored AS (
    SELECT p.team_id, p.season_id, p.formation, p.n, p.axis, p.val,
           100.0 * (
               (SELECT COUNT(*) FROM ref r WHERE r.axis = p.axis AND r.val < p.val)
               + 0.5 * (SELECT COUNT(*) FROM ref r WHERE r.axis = p.axis AND r.val = p.val)
           ) / (SELECT n_teams FROM ref_n) AS percentile
    FROM prof_long p
)
SELECT * FROM scored
"""

_INSERT_SQL = f"""
INSERT INTO team_style_axes
    (team_id, season_id, formation, style_axis, raw_value, percentile,
     n_matches, min_matches)
SELECT team_id, season_id, formation, axis,
       ROUND(val::numeric, 4),
       ROUND(percentile::numeric, 2),
       n, :min_matches
FROM ({_RANKED_SQL}) s
"""

_DELETE_SQL = """
DELETE FROM team_style_axes
WHERE (:season_id IS NULL OR season_id = :season_id)
"""

_SUMMARY_SQL = """
SELECT style_axis,
       COUNT(*) FILTER (WHERE formation IS NULL)     AS agregados,
       COUNT(*) FILTER (WHERE formation IS NOT NULL) AS por_formacion,
       ROUND(MIN(raw_value), 2) AS min_val,
       ROUND(MAX(raw_value), 2) AS max_val
FROM team_style_axes
WHERE (:season_id IS NULL OR season_id = :season_id)
GROUP BY style_axis
ORDER BY style_axis
"""


def recompute(session, min_matches=DEFAULT_MIN_MATCHES, season_id=None, dry_run=False):
    started = time.monotonic()
    p = {"min_matches": min_matches, "season_id": season_id,
         "axis_codes": tuple(_AXIS_CODES)}

    session.execute(text(_DELETE_SQL), p)
    session.execute(
        text(_INSERT_SQL).bindparams(bindparam("axis_codes", expanding=True)),
        p,
    )

    # resumen ANTES de cerrar la transaccion (en dry-run el rollback lo borraria)
    rows = session.execute(text(_SUMMARY_SQL), p).all()
    total = session.execute(
        text("SELECT COUNT(*), COUNT(DISTINCT (team_id, formation)) FROM team_style_axes "
             "WHERE (:s IS NULL OR season_id = :s)"), {"s": season_id}).one()

    if dry_run:
        session.rollback()
    else:
        session.commit()

    _print_summary(rows, total, min_matches, time.monotonic() - started, dry_run)
    return rows


def _print_summary(rows, total, min_matches, elapsed, dry_run):
    print("\n" + "=" * 66)
    print(f"  team_style_axes - {'DRY-RUN' if dry_run else 'ESCRITO'}  (umbral {min_matches} partidos/formacion)")
    print("=" * 66)
    print(f"  {'eje':<20} {'agregados':>10} {'x formacion':>12} {'min':>8} {'max':>8}")
    print("  " + "-" * 60)
    for axis, agg, byf, mn, mx in rows:
        print(f"  {axis:<20} {agg:>10} {byf:>12} {mn!s:>8} {mx!s:>8}")
    print("  " + "-" * 60)
    print(f"  {total[0]} filas | {total[1]} perfiles (equipo x formacion, incl. agregado)")
    print(f"  tiempo: {elapsed:.2f} s")
    print("=" * 66)


def main():
    ap = argparse.ArgumentParser(description="Fase 8: ejes de estilo por equipo/formacion")
    ap.add_argument("--min-matches", type=int, default=DEFAULT_MIN_MATCHES,
                    help="minimo de partidos para emitir fila por formacion (Fase 7 usa 5)")
    ap.add_argument("--season-id", type=int, default=None)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    session = get_session()
    try:
        recompute(session, min_matches=args.min_matches, season_id=args.season_id,
                  dry_run=args.dry_run)
    finally:
        session.close()


if __name__ == "__main__":
    main()
