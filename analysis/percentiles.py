"""Fase 3 - normalizacion per-90 y percentiles por bucket de posicion.

Puebla la tabla `player_percentiles` de forma idempotente. El umbral de
minutos es un PARAMETRO de esta funcion, no una constante ni una columna
de config (asi se revisa sin tocar el pipeline cuando lleguen mas ligas).

Que se normaliza como que (viene de stat_types.normalization):
  - 'per90': todos los contadores -> (suma / minutos_totales) * 90.
  - 'raw'  : accurate-passes-percentage (ya es %) y rating (media 0-10)
             -> media PONDERADA POR MINUTOS entre las etapas del jugador.
  - 'none' : minutes-played (es el propio umbral) y appearances
             (disponibilidad, no rendimiento) -> NO entran.

Percentil: PERCENT_RANK dentro de (season, competition, position_bucket,
stat_type), sobre los jugadores con >= min_minutes. Se guarda ORIENTADO
segun stat_types.direction -> percentil 100 = mejor de su bucket siempre.
Los ceros imputados (is_imputed_zero) cuentan como el 0 que son.

Uso:
    python -m analysis.percentiles                       # todo, umbral 900
    python -m analysis.percentiles --min-minutes 750
    python -m analysis.percentiles --season-id 5 --competition-id 1
    python -m analysis.percentiles --dry-run
"""

from __future__ import annotations

import argparse
import time

from sqlalchemy import text

from db.database import get_session

DEFAULT_MIN_MINUTES = 900

# El calculo entero: minutos por etapa -> total por jugador -> filtro por
# umbral -> metrica agregada (per90 o media ponderada) -> PERCENT_RANK
# orientado por bucket. Un solo SELECT.
_RANKED_SQL = """
WITH params AS (
    SELECT CAST(:min_minutes AS integer) AS min_minutes
),
stint_minutes AS (
    SELECT ps.player_team_season_id AS pts_id, ps.value AS mins
    FROM player_statistics ps
    JOIN stat_types st ON st.id = ps.stat_type_id
    WHERE st.code = 'minutes-played'
),
pts_scoped AS (
    SELECT pts.*
    FROM player_team_season pts
    WHERE (:season_id IS NULL OR pts.season_id = :season_id)
      AND (:competition_id IS NULL OR pts.competition_id = :competition_id)
),
player_minutes AS (
    SELECT pts.player_id, pts.season_id, pts.competition_id,
           SUM(sm.mins) AS minutes
    FROM pts_scoped pts
    JOIN stint_minutes sm ON sm.pts_id = pts.id
    GROUP BY pts.player_id, pts.season_id, pts.competition_id
),
eligible AS (
    SELECT pm.*
    FROM player_minutes pm, params
    WHERE pm.minutes >= params.min_minutes
),
player_metric AS (
    SELECT
        e.player_id, e.season_id, e.competition_id,
        pos.bucket AS position_bucket,
        ps.stat_type_id, st.normalization, st.direction,
        CASE st.normalization
            WHEN 'per90' THEN SUM(ps.value) / NULLIF(e.minutes, 0) * 90.0
            WHEN 'raw'   THEN SUM(ps.value * sm.mins) / NULLIF(SUM(sm.mins), 0)
        END AS metric_value
    FROM eligible e
    JOIN pts_scoped pts     ON pts.player_id = e.player_id AND pts.season_id = e.season_id
    JOIN stint_minutes sm   ON sm.pts_id = pts.id
    JOIN player_statistics ps ON ps.player_team_season_id = pts.id
    JOIN stat_types st      ON st.id = ps.stat_type_id AND st.normalization IN ('per90', 'raw')
    JOIN players p          ON p.id = e.player_id
    JOIN positions pos      ON pos.id = p.primary_position_id
    WHERE (st.valid_for = 'all' OR pos.bucket = 'portero')
    GROUP BY e.player_id, e.season_id, e.competition_id, pos.bucket,
             ps.stat_type_id, st.normalization, st.direction, e.minutes
),
ranked AS (
    SELECT
        pm.player_id, pm.season_id, pm.competition_id, pm.position_bucket,
        pm.stat_type_id, pm.metric_value,
        COUNT(*) OVER w AS pool_size,
        CASE
            WHEN COUNT(*) OVER w <= 1 THEN 50.0
            WHEN pm.direction = 'lower_better'
                THEN (1 - PERCENT_RANK() OVER (PARTITION BY pm.season_id, pm.competition_id,
                          pm.position_bucket, pm.stat_type_id ORDER BY pm.metric_value)) * 100
            ELSE PERCENT_RANK() OVER (PARTITION BY pm.season_id, pm.competition_id,
                     pm.position_bucket, pm.stat_type_id ORDER BY pm.metric_value) * 100
        END AS percentile
    FROM player_metric pm
    WHERE pm.metric_value IS NOT NULL
    WINDOW w AS (PARTITION BY pm.season_id, pm.competition_id, pm.position_bucket, pm.stat_type_id)
)
SELECT * FROM ranked
"""

_INSERT_SQL = f"""
INSERT INTO player_percentiles
    (player_id, season_id, competition_id, stat_type_id, position_bucket,
     metric_value, percentile, pool_size, min_minutes)
SELECT
    player_id, season_id, competition_id, stat_type_id, position_bucket,
    ROUND(metric_value::numeric, 4),
    ROUND(percentile::numeric, 2),
    pool_size,
    :min_minutes
FROM ({_RANKED_SQL}) r
"""

_DELETE_SQL = """
DELETE FROM player_percentiles
WHERE (:season_id IS NULL OR season_id = :season_id)
  AND (:competition_id IS NULL OR competition_id = :competition_id)
"""

_SUMMARY_SQL = """
SELECT position_bucket,
       COUNT(DISTINCT player_id)  AS jugadores,
       COUNT(*)                   AS filas,
       COUNT(DISTINCT stat_type_id) AS metricas
FROM player_percentiles
WHERE (:season_id IS NULL OR season_id = :season_id)
  AND (:competition_id IS NULL OR competition_id = :competition_id)
GROUP BY position_bucket
ORDER BY CASE position_bucket
    WHEN 'portero' THEN 1 WHEN 'central' THEN 2 WHEN 'lateral' THEN 3
    WHEN 'centrocampista' THEN 4 WHEN 'extremo' THEN 5 WHEN 'delantero' THEN 6
    ELSE 9 END
"""

# jugadores con minutos suficientes pero SIN posicion -> no entran
_ORPHANS_SQL = """
WITH sm AS (
    SELECT ps.player_team_season_id AS pts_id, ps.value AS mins
    FROM player_statistics ps JOIN stat_types st ON st.id = ps.stat_type_id
    WHERE st.code = 'minutes-played'
)
SELECT COUNT(*) FROM (
    SELECT pts.player_id, SUM(sm.mins) minutes
    FROM player_team_season pts JOIN sm ON sm.pts_id = pts.id
    JOIN players p ON p.id = pts.player_id
    WHERE p.primary_position_id IS NULL
      AND (:season_id IS NULL OR pts.season_id = :season_id)
      AND (:competition_id IS NULL OR pts.competition_id = :competition_id)
    GROUP BY pts.player_id
) x WHERE minutes >= :min_minutes
"""


def recompute(session, min_minutes=DEFAULT_MIN_MINUTES, season_id=None,
              competition_id=None, dry_run=False):
    started = time.monotonic()
    p = {"min_minutes": min_minutes, "season_id": season_id, "competition_id": competition_id}

    session.execute(text(_DELETE_SQL), p)
    session.execute(text(_INSERT_SQL), p)

    rows = session.execute(text(_SUMMARY_SQL), p).all()
    orphans = session.execute(text(_ORPHANS_SQL), p).scalar_one()

    if dry_run:
        session.rollback()
    else:
        session.commit()

    elapsed = time.monotonic() - started
    _print_summary(rows, orphans, min_minutes, elapsed, dry_run)
    return rows


def _print_summary(rows, orphans, min_minutes, elapsed, dry_run):
    print("\n" + "=" * 58)
    print(f"  player_percentiles - {'DRY-RUN' if dry_run else 'ESCRITO'}  (umbral {min_minutes} min)")
    print("=" * 58)
    print(f"  {'bucket':<16} {'jugadores':>9} {'filas':>8} {'metricas':>9}")
    total_players = total_rows = 0
    for bucket, jug, filas, metr in rows:
        print(f"  {bucket:<16} {jug:>9} {filas:>8} {metr:>9}")
        total_players += jug
        total_rows += filas
    print("  " + "-" * 44)
    print(f"  {'TOTAL':<16} {total_players:>9} {total_rows:>8}")
    print(f"\n  jugadores con >= {min_minutes} min pero SIN posicion (excluidos): {orphans}")
    print(f"  tiempo: {elapsed:.2f} s")
    print("=" * 58)


def main():
    ap = argparse.ArgumentParser(description="Fase 3: per90 + percentiles por bucket")
    ap.add_argument("--min-minutes", type=int, default=DEFAULT_MIN_MINUTES)
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
