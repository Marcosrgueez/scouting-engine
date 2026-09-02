"""Fase 12b - migración de esquema (sin Alembic todavía).

Mueve la competición de `teams` (atributo fijo, incorrecto: un equipo cambia
de división entre temporadas) a `seasons` (un season_id de Sportmonks es
siempre de una liga). Ver docs/session_notes.md (Fase 12b).

  1. seasons.competition_id  -> nueva FK NOT NULL (backfill = La Liga, id 564)
  2. uq_season_competition_name  -> (competition_id, name)
  3. teams.competition_id    -> DROP (columna muerta: nadie la leía)

Idempotente: se puede relanzar. NO toca datos de jugador/equipo/fixtures.

Uso:
    python -m db.migrate_fase12b            # aplica
    python -m db.migrate_fase12b --dry-run  # enseña el plan y hace rollback
"""

from __future__ import annotations

import sys

from sqlalchemy import inspect, text

from db.database import engine

LALIGA_SPORTMONKS_LEAGUE_ID = 564


def _cols(conn, table):
    return {c["name"] for c in inspect(conn).get_columns(table)}


def _constraints(conn, table):
    insp = inspect(conn)
    names = {c["name"] for c in insp.get_unique_constraints(table)}
    return names


def run(dry_run=False):
    steps: list[str] = []
    conn = engine.connect()
    trans = conn.begin()
    try:
        seasons_cols = _cols(conn, "seasons")
        teams_cols = _cols(conn, "teams")

        # 1. seasons.competition_id
        if "competition_id" not in seasons_cols:
            steps.append("ADD seasons.competition_id (nullable)")
            if not dry_run:
                conn.execute(text(
                    "ALTER TABLE seasons ADD COLUMN competition_id integer REFERENCES competitions(id)"
                ))

        # el resto solo tiene sentido si la columna ya existe (en dry-run sin
        # la columna todavía, el paso 1 no la ha creado -> se salta aquí).
        col_exists = "competition_id" in seasons_cols or not dry_run
        if col_exists:
            laliga_id = conn.execute(text(
                "SELECT id FROM competitions WHERE sportmonks_league_id = :l"
            ), {"l": LALIGA_SPORTMONKS_LEAGUE_ID}).scalar()

            null_count = conn.execute(text(
                "SELECT count(*) FROM seasons WHERE competition_id IS NULL"
            )).scalar()
            if null_count:
                if laliga_id is None:
                    raise RuntimeError(
                        "No hay competición La Liga (sportmonks_league_id 564) para el backfill. "
                        "Ejecuta el ETL de LaLiga primero."
                    )
                steps.append(f"BACKFILL {null_count} seasons.competition_id -> La Liga (id {laliga_id})")
                if not dry_run:
                    conn.execute(text(
                        "UPDATE seasons SET competition_id = :c WHERE competition_id IS NULL"
                    ), {"c": laliga_id})

            remaining_null = conn.execute(text(
                "SELECT count(*) FROM seasons WHERE competition_id IS NULL"
            )).scalar()
            is_notnull = conn.execute(text(
                "SELECT attnotnull FROM pg_attribute "
                "WHERE attrelid = 'seasons'::regclass AND attname = 'competition_id'"
            )).scalar()
            if remaining_null == 0 and not is_notnull:
                steps.append("SET seasons.competition_id NOT NULL")
                if not dry_run:
                    conn.execute(text("ALTER TABLE seasons ALTER COLUMN competition_id SET NOT NULL"))

        # 2. unique (competition_id, name)
        if "uq_season_competition_name" not in _constraints(conn, "seasons"):
            steps.append("ADD uq_season_competition_name (competition_id, name)")
            if not dry_run:
                conn.execute(text(
                    "ALTER TABLE seasons ADD CONSTRAINT uq_season_competition_name "
                    "UNIQUE (competition_id, name)"
                ))

        # 3. drop teams.competition_id
        if "competition_id" in teams_cols:
            steps.append("DROP teams.competition_id")
            if not dry_run:
                conn.execute(text("ALTER TABLE teams DROP COLUMN competition_id"))

        if dry_run:
            trans.rollback()
        else:
            trans.commit()
    except Exception:
        trans.rollback()
        raise
    finally:
        conn.close()

    print("=" * 60)
    print("  migración Fase 12b -", "DRY-RUN (rollback)" if dry_run else "APLICADA")
    print("=" * 60)
    if steps:
        for s in steps:
            print(f"  - {s}")
    else:
        print("  nada que hacer (ya migrado)")
    print("=" * 60)


if __name__ == "__main__":
    run(dry_run="--dry-run" in sys.argv[1:])
