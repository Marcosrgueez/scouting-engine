"""Fase 2 - ETL masivo del roster de LaLiga a PostgreSQL.

Reutiliza el JSON ya descargado en ../data-experiment/raw_data/sportmonks/
(roster, positions_map, player_stats de los ~762 jugadores). Solo llama a
la API de Sportmonks para lo que falte, y solo si se pasa --fetch-missing.

Pipeline por jugador:
    player_stats/{id}.json
      -> validacion Pydantic (loaders/schemas.py)  [si falla: log + skip]
      -> upsert players               (por sportmonks_player_id)
      -> upsert player_team_season    (por player_id + season_id + order_in_season)
      -> upsert player_statistics     (por player_team_season_id + stat_type_id,
                                       is_imputed_zero donde Sportmonks omitio)

Idempotente: relanzarlo no duplica nada. Cada jugador se procesa "borrar
sus etapas y stats + reinsertar", con commits por lotes, asi que si se
corta a la mitad se puede relanzar sin limpiar la BD.

Uso:
    python -m loaders.etl_laliga --dry-run --limit 14      # prueba
    python -m loaders.etl_laliga --dry-run                 # dry-run completo
    python -m loaders.etl_laliga                           # carga real
    python -m loaders.etl_laliga --players 96611,26491     # jugadores sueltos
"""

from __future__ import annotations

import argparse
import datetime
import json
import logging
import os
import time
from collections import Counter

from pydantic import ValidationError
from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from db.database import get_session
from db.models import (
    Competition,
    Player,
    PlayerStatistic,
    PlayerTeamSeason,
    Position,
    Season,
    StatType,
    Team,
)
from loaders.schemas import Context, PlayerStatsFile, PositionMeta, TeamRaw
from loaders.sportmonks_mapping import build_stat_rows, details_to_code_value

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("etl_laliga")

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _resolve_data_dir():
    """Localiza data-experiment/. Funciona tanto desde scouting-engine/ como
    desde un worktree en scouting-engine/.claude/worktrees/<name>/."""
    configured = os.getenv("DATA_EXPERIMENT_DIR")
    candidates = []
    if configured:
        candidates.append(configured if os.path.isabs(configured)
                          else os.path.join(_PROJECT_ROOT, configured))
    # sube directorios buscando un hermano "data-experiment"
    here = _PROJECT_ROOT
    for _ in range(5):
        candidates.append(os.path.join(here, "data-experiment"))
        here = os.path.dirname(here)
    for cand in candidates:
        cand = os.path.normpath(cand)
        if os.path.isdir(os.path.join(cand, "raw_data", "sportmonks")):
            return cand
    raise RuntimeError(
        "No encuentro data-experiment/raw_data/sportmonks/. Ajusta DATA_EXPERIMENT_DIR en el .env."
    )


_DATA_DIR = _resolve_data_dir()
_SM_DIR = os.path.join(_DATA_DIR, "raw_data", "sportmonks")
_STATS_DIR = os.path.join(_SM_DIR, "player_stats")

COMMIT_EVERY = 50
# sportmonks country_id -> nombre. 32 España (LaLiga/Segunda), 462 Inglaterra,
# 251 Italia, 11 Alemania (Fase 13). Si falta, el equipo queda con country NULL.
COUNTRY_BY_ID = {32: "Spain", 462: "England", 251: "Italy", 11: "Germany"}


def _load_json(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _roster_player_ids(sm_dir=_SM_DIR):
    """IDs de jugador del roster de Sportmonks (players_raw.json)."""
    roster = _load_json(os.path.join(sm_dir, "players_raw.json"))
    ids = []
    seen = set()
    for team in roster.get("teams", []):
        for row in team.get("raw_response", {}).get("data", []):
            pid = (row.get("player") or {}).get("id")
            if pid is not None and pid not in seen:
                seen.add(pid)
                ids.append(pid)
    return sorted(ids)


def _roster_team_ids(sm_dir=_SM_DIR):
    """sportmonks_team_id de los equipos CON plantilla poblada (>=1 jugador).

    Fase 12b: teams.json de Segunda trae un placeholder "TBC" y puede traer
    filiales sin plantilla; esos no deben entrar en `teams`.
    """
    roster = _load_json(os.path.join(sm_dir, "players_raw.json"))
    out = set()
    for team in roster.get("teams", []):
        rows = team.get("raw_response", {}).get("data", [])
        if any((r.get("player") or {}).get("id") for r in rows):
            out.add(team.get("team_id"))
    return out


def _sportmonks_token():
    # El token vive en el .env del experimento; solo se necesita si falta
    # algun archivo de stats y se pide --fetch-missing.
    for env_path in (os.path.join(_PROJECT_ROOT, ".env"), os.path.join(_DATA_DIR, ".env")):
        if os.path.isfile(env_path):
            for line in open(env_path, "r", encoding="utf-8"):
                if line.strip().startswith("SPORTMONKS_API_TOKEN="):
                    return line.split("=", 1)[1].strip()
    return os.getenv("SPORTMONKS_API_TOKEN")


def _fetch_player_stats(player_id, season_id, token, stats_dir=_STATS_DIR):
    import requests

    url = f"https://api.sportmonks.com/v3/football/players/{player_id}"
    params = {
        "api_token": token,
        "include": "statistics.details.type",
        "filters": f"playerStatisticSeasons:{season_id}",
    }
    resp = requests.get(url, params=params, timeout=20)
    resp.raise_for_status()
    payload = resp.json()
    if not os.path.isdir(stats_dir):
        os.makedirs(stats_dir)
    out_path = os.path.join(stats_dir, f"{player_id}.json")
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    return payload


# ---------------------------------------------------------------------------
# Upserts
# ---------------------------------------------------------------------------

def _upsert_returning_id(session, model, values, index_elements, update_cols):
    stmt = (
        pg_insert(model)
        .values(**values)
        .on_conflict_do_update(
            index_elements=index_elements,
            set_={col: values[col] for col in update_cols},
        )
        .returning(model.id)
    )
    return session.execute(stmt).scalar_one()


# ---------------------------------------------------------------------------
# ETL
# ---------------------------------------------------------------------------

def run(dry_run=False, limit=None, only_players=None, fetch_missing=False, season_dir=None):
    started = time.monotonic()

    # season_dir="s25659" -> raw_data/sportmonks/s25659/ (Fase 12a, multi-temporada).
    # None -> el layout plano de 2024/25 (Fases 0-8).
    sm_dir = os.path.join(_SM_DIR, season_dir) if season_dir else _SM_DIR
    stats_dir = os.path.join(sm_dir, "player_stats")

    context = Context.model_validate(_load_json(os.path.join(sm_dir, "context.json")))
    teams_raw = [TeamRaw.model_validate(t) for t in _load_json(os.path.join(sm_dir, "teams.json"))["data"]]
    teams_by_sm_id = {t.id: t for t in teams_raw}
    positions_meta = {
        pid: PositionMeta.model_validate(meta)
        for pid, meta in _load_json(os.path.join(sm_dir, "positions_map.json"))["players"].items()
    }

    if only_players:
        target_ids = list(only_players)
    else:
        target_ids = _roster_player_ids(sm_dir)
        if limit:
            target_ids = target_ids[:limit]

    log.info("ETL LaLiga | season_id=%s | %s jugadores objetivo | dry_run=%s",
             context.season_id, len(target_ids), dry_run)

    report = {
        "targeted": len(target_ids),
        "missing_file": [],
        "fetched": 0,
        "loaded": 0,
        "no_stints": 0,
        "rejected": Counter(),
        "rejected_ids": [],
        "multi_stint_players": 0,
        "player_team_season_rows": 0,
        "stat_rows": 0,
        "imputed_zero_rows": 0,
        "orphan_team_ids": Counter(),
    }

    session = get_session()
    token = None
    try:
        # --- catalogos ---
        pos_seed_count = session.scalar(select(Position).limit(1))
        stat_seed_count = session.scalar(select(StatType).limit(1))
        if pos_seed_count is None or stat_seed_count is None:
            raise RuntimeError(
                "Catalogos positions/stat_types vacios. Ejecuta 'python -m db.create_schema' primero."
            )
        stat_types = list(session.scalars(select(StatType)).all())
        position_id_by_sm = {
            p.sportmonks_position_id: p.id
            for p in session.scalars(select(Position)).all()
            if p.sportmonks_position_id is not None
        }

        # --- competition + season (los crea el ETL desde context.json) ---
        # Fase 12b: el tier viene del context (scripts/10). Fallback por
        # league_id para el context plano de 2024/25, que no lo trae.
        tier = context.tier if context.tier is not None else (2 if context.league_id == 567 else 1)
        competition_id = _upsert_returning_id(
            session, Competition,
            {"name": context.league_name, "country": context.country or "Spain", "tier": tier,
             "sportmonks_league_id": context.league_id},
            ["sportmonks_league_id"], ["name", "country", "tier"],
        )
        # Fase 12b: la competición vive en la temporada (un season_id de
        # Sportmonks es siempre de una liga).
        season_id = _upsert_returning_id(
            session, Season,
            {"name": context.season_name or "2024/2025",
             "competition_id": competition_id,
             "start_date": context.start_date or datetime.date(2024, 8, 15),
             "end_date": context.end_date or datetime.date(2025, 5, 25),
             "sportmonks_season_id": context.season_id},
            ["sportmonks_season_id"], ["name", "competition_id", "start_date", "end_date"],
        )

        # --- teams (solo los que tienen plantilla poblada) ---
        # Fase 12b: sin competition_id (la división vive en la temporada). El
        # upsert por sportmonks_team_id reutiliza la fila si el equipo ya
        # existe de otra temporada/liga (p.ej. Valladolid: LaLiga 24/25 ->
        # Segunda 25/26) sin duplicar.
        roster_team_ids = _roster_team_ids(sm_dir)
        team_id_by_sm = {}
        skipped_teams = []
        for traw in teams_raw:
            if roster_team_ids and traw.id not in roster_team_ids:
                skipped_teams.append(traw.name)
                continue
            team_id_by_sm[traw.id] = _upsert_returning_id(
                session, Team,
                {"name": traw.name, "country": COUNTRY_BY_ID.get(traw.country_id),
                 "sportmonks_team_id": traw.id},
                ["sportmonks_team_id"], ["name", "country"],
            )
        if skipped_teams:
            log.info("equipos sin plantilla, omitidos: %s", skipped_teams)

        # --- jugadores ---
        for i, sm_pid in enumerate(target_ids, 1):
            stats_path = os.path.join(stats_dir, f"{sm_pid}.json")
            if not os.path.isfile(stats_path):
                if fetch_missing:
                    if token is None:
                        token = _sportmonks_token()
                    if not token:
                        log.error("No hay SPORTMONKS_API_TOKEN; no se puede descargar %s", sm_pid)
                        report["missing_file"].append(sm_pid)
                        continue
                    log.info("descargando stats que faltaban para %s", sm_pid)
                    _fetch_player_stats(sm_pid, context.season_id, token, stats_dir)
                    report["fetched"] += 1
                else:
                    report["missing_file"].append(sm_pid)
                    continue

            raw = _load_json(stats_path)
            try:
                psf = PlayerStatsFile.model_validate(raw)
            except ValidationError as exc:
                first = exc.errors()[0]
                key = f"{'.'.join(str(p) for p in first['loc'])}: {first['type']}"
                report["rejected"][key] += 1
                report["rejected_ids"].append(sm_pid)
                log.warning("jugador %s rechazado por validacion (%s)", sm_pid, key)
                continue

            profile = psf.data
            meta = positions_meta.get(str(sm_pid), PositionMeta())
            bucket = meta.bucket
            is_goalkeeper = bucket == "portero"
            detailed_pos_id = meta.detailed_position_id or profile.detailed_position_id
            primary_position_id = position_id_by_sm.get(detailed_pos_id)

            player_pk = _upsert_returning_id(
                session, Player,
                {
                    "sportmonks_player_id": profile.id,
                    "apifootball_player_id": None,
                    "name": profile.best_name,
                    "birth_date": profile.date_of_birth,
                    "nationality": str(profile.nationality_id) if profile.nationality_id is not None else None,
                    "height_cm": profile.height,
                    "weight_kg": profile.weight,
                    "preferred_foot": None,
                    "primary_position_id": primary_position_id,
                    "photo_url": profile.image_path,
                },
                ["sportmonks_player_id"],
                ["name", "birth_date", "nationality", "height_cm", "weight_kg",
                 "primary_position_id", "photo_url"],
            )

            # idempotencia: se borran las etapas y stats de este jugador EN
            # ESTA TEMPORADA y se reinsertan (el cascade borra las
            # player_statistics). Scoped por season_id: un jugador que jugo
            # varias temporadas conserva las de las otras (Fase 12a).
            session.execute(
                delete(PlayerTeamSeason).where(
                    PlayerTeamSeason.player_id == player_pk,
                    PlayerTeamSeason.season_id == season_id,
                )
            )

            entries = sorted(profile.statistics, key=lambda e: e.team_id)
            if not entries:
                report["no_stints"] += 1
            if len(entries) > 1:
                report["multi_stint_players"] += 1

            for order, entry in enumerate(entries):
                team_pk = team_id_by_sm.get(entry.team_id)
                if team_pk is None:
                    # equipo visto en stats pero no en teams.json (no deberia
                    # pasar: las stats vienen filtradas a la temporada de LaLiga)
                    report["orphan_team_ids"][entry.team_id] += 1
                    traw = teams_by_sm_id.get(entry.team_id)
                    team_pk = _upsert_returning_id(
                        session, Team,
                        {"name": traw.name if traw else f"team-{entry.team_id}",
                         "country": COUNTRY_BY_ID.get(traw.country_id) if traw else None,
                         "sportmonks_team_id": entry.team_id},
                        ["sportmonks_team_id"], ["name"],
                    )
                    team_id_by_sm[entry.team_id] = team_pk

                pts_pk = _upsert_returning_id(
                    session, PlayerTeamSeason,
                    {"player_id": player_pk, "team_id": team_pk, "season_id": season_id,
                     "competition_id": competition_id, "order_in_season": order,
                     "date_from": None, "date_to": None},
                    ["player_id", "season_id", "order_in_season"],
                    ["team_id", "competition_id"],
                )
                report["player_team_season_rows"] += 1

                code_value = details_to_code_value(entry.details)
                rows = build_stat_rows(code_value, stat_types, is_goalkeeper)
                if rows:
                    values = [dict(player_team_season_id=pts_pk, **r) for r in rows]
                    stmt = pg_insert(PlayerStatistic).values(values)
                    stmt = stmt.on_conflict_do_update(
                        index_elements=["player_team_season_id", "stat_type_id"],
                        set_={"value": stmt.excluded.value,
                              "is_imputed_zero": stmt.excluded.is_imputed_zero},
                    )
                    session.execute(stmt)
                    report["stat_rows"] += len(rows)
                    report["imputed_zero_rows"] += sum(1 for r in rows if r["is_imputed_zero"])

            report["loaded"] += 1

            if not dry_run and i % COMMIT_EVERY == 0:
                session.commit()
                log.info("  ... %s/%s jugadores (commit)", i, len(target_ids))

        if dry_run:
            session.rollback()
            log.info("DRY-RUN: rollback, nada escrito en la BD")
        else:
            session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

    _print_report(report, time.monotonic() - started, dry_run)
    return report


def _print_report(report, elapsed, dry_run):
    print("\n" + "=" * 60)
    print("  ETL LaLiga -", "DRY-RUN" if dry_run else "CARGA REAL")
    print("=" * 60)
    print(f"  jugadores objetivo........... {report['targeted']}")
    print(f"  cargados.................... {report['loaded']}")
    print(f"  rechazados por validacion... {sum(report['rejected'].values())}")
    for key, n in report["rejected"].most_common():
        print(f"      - {key}: {n}")
    if report["missing_file"]:
        print(f"  sin archivo de stats....... {len(report['missing_file'])} {report['missing_file'][:10]}")
    if report["fetched"]:
        print(f"  descargados de la API...... {report['fetched']}")
    print(f"  jugadores sin ninguna etapa. {report['no_stints']}")
    print(f"  jugadores multi-etapa...... {report['multi_stint_players']}")
    print(f"  filas player_team_season... {report['player_team_season_rows']}")
    print(f"  filas player_statistics.... {report['stat_rows']}")
    print(f"      de ellas imputadas a 0. {report['imputed_zero_rows']}")
    if report["orphan_team_ids"]:
        print(f"  team_ids fuera de teams.json: {dict(report['orphan_team_ids'])}")
    print(f"  tiempo total............... {elapsed:.1f} s")
    print("=" * 60)


def main():
    ap = argparse.ArgumentParser(description="ETL masivo del roster de LaLiga")
    ap.add_argument("--dry-run", action="store_true", help="valida y mapea todo pero hace rollback")
    ap.add_argument("--limit", type=int, help="procesar solo los primeros N jugadores del roster")
    ap.add_argument("--players", help="lista de sportmonks_player_id separados por coma")
    ap.add_argument("--fetch-missing", action="store_true",
                    help="descargar de Sportmonks los stats que falten (cuida la cuota)")
    ap.add_argument("--season-dir", default=None,
                    help="subdirectorio de raw_data/sportmonks/ (ej 's25659' para LaLiga 25/26). "
                         "Sin esto, el layout plano de 2024/25.")
    args = ap.parse_args()

    only_players = None
    if args.players:
        only_players = [int(x) for x in args.players.split(",") if x.strip()]

    run(dry_run=args.dry_run, limit=args.limit, only_players=only_players,
        fetch_missing=args.fetch_missing, season_dir=args.season_dir)


if __name__ == "__main__":
    main()
