"""Fase 6 - Player Similarity Engine.

Encuentra, para cada jugador, los 20 jugadores estadisticamente mas
similares dentro de su mismo bucket de posicion y temporada.

- **Vector de features:** los percentiles per90 de `player_percentiles`
  (Fase 3), TODAS las metricas del bucket (34 de campo; 37 para portero,
  con las 3 solo-portero). La cobertura de Fase 3 es del 100 % dentro de
  cada bucket -> todos los vectores del bucket estan alineados y completos.
- **Distancia:** cosine similarity sobre el vector de percentiles crudos
  (rango [0,100], todos positivos -> similitud en [0,1]).
- **Solo dentro del mismo bucket** (un central contra centrales). Sin
  comparacion cross-posicion en esta fase.
- **Almacenamiento:** NO se guarda la matriz N^2. Solo el top-20 por
  jugador (`player_similarity`), con su `rank` (1-20). La tabla NO es
  simetrica.

**Idempotencia: DELETE scoped + INSERT** (mismo patron que
analysis/percentiles.py y analysis/role_scores.py). Relanzar con el mismo
scope borra y reescribe; no hay upsert porque el top-20 de un jugador
puede cambiar de miembros entre pasadas y un upsert dejaria filas viejas
colgando.

**Filtros de edad y lado:** NO entran aqui. Se aplican al CONSULTAR la
tabla ya calculada (ver los ejemplos al final del modulo o el README): la
similitud estadistica entre dos jugadores no cambia segun el filtro que
se use despues para buscar candidatos.

**Fuera de alcance (pendientes):** pie dominante (`preferred_foot` NULL en
el 100 % del roster) y valor de mercado (sin fuente). Ningun filtro puede
apoyarse en ellos todavia.

Uso:
    python -m analysis.similarity                    # umbral 900 (como Fase 3)
    python -m analysis.similarity --min-minutes 750
    python -m analysis.similarity --season-id 1 --competition-id 1
    python -m analysis.similarity --dry-run
    python -m analysis.similarity --explain "Grimaldo"   # top-20 de un jugador
"""

from __future__ import annotations

import argparse
import time

from sqlalchemy import text

from db.database import get_session

DEFAULT_MIN_MINUTES = 900
TOP_N = 20

# vector de percentiles per90 por jugador (una fila por metrica del bucket).
_VEC_CTE = """
vec AS (
    SELECT pp.player_id, pp.season_id, pp.position_bucket,
           pp.stat_type_id, pp.percentile
    FROM player_percentiles pp
    WHERE pp.min_minutes = :min_minutes
      AND (:season_id IS NULL OR pp.season_id = :season_id)
      AND (:competition_id IS NULL OR pp.competition_id = :competition_id)
),
norm AS (
    SELECT player_id, season_id,
           sqrt(SUM(percentile * percentile)) AS mag,
           COUNT(*) AS n_features
    FROM vec
    GROUP BY player_id, season_id
),
pairs AS (
    SELECT a.player_id AS pid, b.player_id AS sid,
           a.season_id, a.position_bucket,
           SUM(a.percentile * b.percentile) AS dot,
           COUNT(*) AS shared_dims
    FROM vec a
    JOIN vec b
      ON b.season_id       = a.season_id
     AND b.position_bucket = a.position_bucket
     AND b.stat_type_id    = a.stat_type_id
     AND b.player_id      <> a.player_id
    GROUP BY a.player_id, b.player_id, a.season_id, a.position_bucket
),
sim AS (
    SELECT p.pid, p.sid, p.season_id, p.position_bucket, p.shared_dims,
           p.dot / NULLIF(na.mag * nb.mag, 0) AS similarity
    FROM pairs p
    JOIN norm na ON na.player_id = p.pid AND na.season_id = p.season_id
    JOIN norm nb ON nb.player_id = p.sid AND nb.season_id = p.season_id
),
ranked AS (
    SELECT pid, sid, season_id, position_bucket, shared_dims, similarity,
           ROW_NUMBER() OVER (
               PARTITION BY pid, season_id
               ORDER BY similarity DESC, sid
           ) AS rnk
    FROM sim
    WHERE similarity IS NOT NULL
)
"""

_INSERT_SQL = f"""
WITH {_VEC_CTE}
INSERT INTO player_similarity
    (player_id, similar_player_id, season_id, position_bucket,
     similarity_score, rank, n_features, min_minutes)
SELECT r.pid, r.sid, r.season_id, r.position_bucket,
       ROUND(r.similarity::numeric, 6), r.rnk, r.shared_dims, :min_minutes
FROM ranked r
WHERE r.rnk <= :top_n
"""

_DELETE_SQL = """
DELETE FROM player_similarity
WHERE (:season_id IS NULL OR season_id = :season_id)
"""

_SUMMARY_SQL = """
SELECT ps.position_bucket,
       COUNT(DISTINCT ps.player_id)     AS jugadores,
       COUNT(*)                         AS filas,
       ROUND(AVG(ps.similarity_score), 4) AS sim_media,
       ROUND(MIN(ps.similarity_score), 4) AS sim_min,
       ROUND(MAX(ps.similarity_score), 4) AS sim_max,
       MAX(ps.n_features)               AS n_features
FROM player_similarity ps
WHERE (:season_id IS NULL OR ps.season_id = :season_id)
GROUP BY ps.position_bucket
ORDER BY CASE ps.position_bucket
    WHEN 'portero' THEN 1 WHEN 'central' THEN 2 WHEN 'lateral' THEN 3
    WHEN 'centrocampista' THEN 4 WHEN 'extremo' THEN 5 WHEN 'delantero' THEN 6
    ELSE 9 END
"""

# jugadores del pool (>=900 min, con bucket) que NO tienen top-20 -> deberia
# ser solo los buckets con < 2 jugadores (imposible comparar).
_UNSCORED_SQL = """
SELECT COUNT(*) FROM (
    SELECT DISTINCT pp.player_id
    FROM player_percentiles pp
    WHERE pp.min_minutes = :min_minutes
      AND (:season_id IS NULL OR pp.season_id = :season_id)
      AND (:competition_id IS NULL OR pp.competition_id = :competition_id)
) pool
WHERE pool.player_id NOT IN (
    SELECT player_id FROM player_similarity
    WHERE (:season_id IS NULL OR season_id = :season_id)
)
"""

_EXPLAIN_SQL = """
SELECT ps.rank, sp.name AS similar, ps.similarity_score,
       pos.bucket, pos.lado,
       date_part('year', age(DATE '2025-05-25', sp.birth_date))::int AS edad
FROM player_similarity ps
JOIN players p  ON p.id = ps.player_id
JOIN players sp ON sp.id = ps.similar_player_id
LEFT JOIN positions pos ON pos.id = sp.primary_position_id
WHERE p.name ILIKE :name
  AND (:season_id IS NULL OR ps.season_id = :season_id)
ORDER BY ps.rank
"""


def recompute(session, min_minutes=DEFAULT_MIN_MINUTES, season_id=None,
              competition_id=None, dry_run=False):
    started = time.monotonic()
    p = {
        "min_minutes": min_minutes,
        "season_id": season_id,
        "competition_id": competition_id,
        "top_n": TOP_N,
    }

    session.execute(text(_DELETE_SQL), p)
    session.execute(text(_INSERT_SQL), p)

    rows = session.execute(text(_SUMMARY_SQL), p).all()
    unscored = session.execute(text(_UNSCORED_SQL), p).scalar_one()

    if dry_run:
        session.rollback()
    else:
        session.commit()

    elapsed = time.monotonic() - started
    _print_summary(rows, unscored, min_minutes, elapsed, dry_run)
    return rows


def _print_summary(rows, unscored, min_minutes, elapsed, dry_run):
    print("\n" + "=" * 74)
    print(f"  player_similarity - {'DRY-RUN' if dry_run else 'ESCRITO'}  "
          f"(percentiles con umbral {min_minutes} min, top-{TOP_N})")
    print("=" * 74)
    print(f"  {'bucket':<16} {'jug':>4} {'filas':>6} {'feat':>5} "
          f"{'sim.media':>10} {'sim.min':>9} {'sim.max':>9}")
    print("  " + "-" * 66)
    total_j = total_f = 0
    for bucket, jug, filas, media, mn, mx, feat in rows:
        print(f"  {bucket:<16} {jug:>4} {filas:>6} {feat:>5} "
              f"{media!s:>10} {mn!s:>9} {mx!s:>9}")
        total_j += jug
        total_f += filas
    print("  " + "-" * 66)
    print(f"  TOTAL: {total_f} filas, {total_j} jugadores con top-{TOP_N}")
    print(f"  jugadores del pool sin top-{TOP_N} (bucket con <2 jugadores): {unscored}")
    print(f"  tiempo: {elapsed:.2f} s")
    print("=" * 74)


def explain(session, name, season_id=None):
    rows = session.execute(text(_EXPLAIN_SQL), {"name": f"%{name}%", "season_id": season_id}).all()
    if not rows:
        print(f"  sin resultados para '{name}'")
        return
    print(f"\n  Top-{TOP_N} mas similares a '{name}':")
    print(f"  {'#':>2}  {'jugador':<26} {'sim':>8}  {'bucket':<14} {'lado':<11} {'edad':>4}")
    print("  " + "-" * 70)
    for rank, similar, score, bucket, lado, edad in rows:
        print(f"  {rank:>2}  {similar:<26} {score!s:>8}  {bucket or '?':<14} "
              f"{lado or '?':<11} {edad if edad is not None else '?':>4}")


def main():
    ap = argparse.ArgumentParser(description="Fase 6: Player Similarity Engine (cosine, top-20)")
    ap.add_argument("--min-minutes", type=int, default=DEFAULT_MIN_MINUTES,
                    help="umbral con el que se calcularon los percentiles de entrada")
    ap.add_argument("--season-id", type=int, default=None)
    ap.add_argument("--competition-id", type=int, default=None)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--explain", metavar="NOMBRE", default=None,
                    help="imprime el top-20 ya calculado de un jugador (ILIKE)")
    args = ap.parse_args()

    session = get_session()
    try:
        if args.explain:
            explain(session, args.explain, season_id=args.season_id)
        else:
            recompute(session, min_minutes=args.min_minutes, season_id=args.season_id,
                      competition_id=args.competition_id, dry_run=args.dry_run)
    finally:
        session.close()


if __name__ == "__main__":
    main()
