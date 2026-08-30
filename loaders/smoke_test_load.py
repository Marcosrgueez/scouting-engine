"""Smoke test: carga los 13 jugadores de prueba del experimento de Fase 0
en el esquema nuevo, con toda su complejidad real:

  - multi-etapa: un jugador con >1 equipo en la temporada -> varias filas
    en player_team_season y sus stats por separado. NINGUNO de los 13 de
    prueba es multi-etapa, asi que se anyade explicitamente a Arnaut
    Danjuma (Villarreal -> Girona en 2024/25) SOLO para ejercitar ese
    camino. Va marcado en el resumen.
  - ceros omitidos: Sportmonks no devuelve el detail cuando vale 0; aqui se
    imputa value=0 con is_imputed_zero=True (salvo campos "base", que si
    faltan es que el jugador no jugo -> no se imputan).
  - stats solo-portero: saves / goals-conceded / cleansheets solo se
    cargan para jugadores cuyo bucket de posicion es "portero".

NO es la Fase 2 (ETL del roster completo). Es la prueba de que el esquema
aguanta datos reales antes de construir el pipeline masivo.

Uso:
    python -m loaders.smoke_test_load
"""

import datetime
import json
import os

from sqlalchemy import delete, select

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
from db.seed_catalogs import seed_static_catalogs

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DATA_DIR = os.getenv("DATA_EXPERIMENT_DIR", "../data-experiment")
if not os.path.isabs(_DATA_DIR):
    _DATA_DIR = os.path.normpath(os.path.join(_PROJECT_ROOT, _DATA_DIR))
_SM_DIR = os.path.join(_DATA_DIR, "raw_data", "sportmonks")
_MAPPING_PATH = os.path.join(_DATA_DIR, "raw_data", "player_id_mapping.json")

# Jugadores extra (fuera de los 13) SOLO para ejercitar el camino multi-etapa.
EXTRA_MULTI_STAGE_SM_IDS = [26491]  # Arnaut Danjuma: Villarreal -> Girona 2024/25

# country_id de Sportmonks -> nombre. Minimo; el resto se deja NULL (la
# resolucion completa de paises es pendiente de Fase 2, igual que posiciones).
COUNTRY_BY_ID = {32: "Spain"}

# Campos que Sportmonks NUNCA omite si el jugador jugo. Si faltan, NO se
# imputan (ver data-experiment/docs/DECISIONS.md).
BASE_CODES = {
    "minutes-played", "appearances", "passes",
    "accurate-passes-percentage", "rating", "duels-won",
}


def _load_json(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _unwrap(value):
    # En Sportmonks el value de cada detail es siempre dict.
    if not isinstance(value, dict):
        return value
    if "total" in value:
        return value["total"]
    if "average" in value:
        return value["average"]
    if len(value) == 1:
        only = next(iter(value.values()))
        return only if isinstance(only, (int, float)) else None
    return None


def _to_number(value):
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            return None
    return None


def _parse_date(text):
    if not text:
        return None
    try:
        return datetime.date.fromisoformat(str(text)[:10])
    except ValueError:
        return None


def _get_or_create_team(session, teams_by_sm_id, cache, competition, sportmonks_team_id):
    if sportmonks_team_id in cache:
        return cache[sportmonks_team_id]
    team = session.scalar(select(Team).where(Team.sportmonks_team_id == sportmonks_team_id))
    if team is None:
        raw = teams_by_sm_id.get(sportmonks_team_id, {})
        team = Team(
            name=raw.get("name", "team-" + str(sportmonks_team_id)),
            country=COUNTRY_BY_ID.get(raw.get("country_id")),
            competition_id=competition.id,
            sportmonks_team_id=sportmonks_team_id,
        )
        session.add(team)
        session.flush()
    cache[sportmonks_team_id] = team
    return team


def main():
    context = _load_json(os.path.join(_SM_DIR, "context.json"))
    teams_raw = _load_json(os.path.join(_SM_DIR, "teams.json"))["data"]
    teams_by_sm_id = {t["id"]: t for t in teams_raw}
    positions_map = _load_json(os.path.join(_SM_DIR, "positions_map.json"))["players"]
    mapping = _load_json(_MAPPING_PATH)

    sm_id_to_af_id = {}
    for entry in mapping:
        sm_pid = entry.get("sportmonks", {}).get("player_id")
        af_pid = entry.get("apifootball", {}).get("player_id")
        if sm_pid is not None:
            sm_id_to_af_id[sm_pid] = af_pid

    test_player_sm_ids = [pid for pid in sm_id_to_af_id.keys()]
    all_sm_ids = test_player_sm_ids + [
        pid for pid in EXTRA_MULTI_STAGE_SM_IDS if pid not in test_player_sm_ids
    ]

    session = get_session()
    report = {
        "players": 0, "player_team_season": 0, "player_statistics": 0,
        "imputed_zero": 0, "gk_only_rows": 0, "multi_stage_players": [],
        "no_position": [],
    }
    try:
        # 1. limpiar SOLO las entidades (catalogos se conservan)
        session.execute(delete(PlayerStatistic))
        session.execute(delete(PlayerTeamSeason))
        session.execute(delete(Player))
        session.flush()

        # 2. catalogos estaticos (idempotente)
        seed_static_catalogs(session)

        positions_by_sm_id = {}
        position_bucket_by_id = {}
        for pos in session.scalars(select(Position)).all():
            positions_by_sm_id[pos.sportmonks_position_id] = pos
            position_bucket_by_id[pos.id] = pos.bucket

        stat_types = session.scalars(select(StatType)).all()

        # 3. competition + season
        competition = session.scalar(
            select(Competition).where(Competition.sportmonks_league_id == context["league_id"])
        )
        if competition is None:
            competition = Competition(
                name=context.get("league_name", "La Liga"),
                country="Spain", tier=1,
                sportmonks_league_id=context["league_id"],
            )
            session.add(competition)
            session.flush()

        season = session.scalar(
            select(Season).where(Season.sportmonks_season_id == context["season_id"])
        )
        if season is None:
            season = Season(
                name=context.get("season_name", "2024/2025"),
                start_date=datetime.date(2024, 8, 15),
                end_date=datetime.date(2025, 5, 25),
                sportmonks_season_id=context["season_id"],
            )
            session.add(season)
            session.flush()

        team_cache = {}

        for sm_pid in all_sm_ids:
            stats_path = os.path.join(_SM_DIR, "player_stats", str(sm_pid) + ".json")
            if not os.path.isfile(stats_path):
                print("  [skip] no hay stats para sportmonks_player_id", sm_pid)
                continue
            data = _load_json(stats_path).get("data", {})

            pos_meta = positions_map.get(str(sm_pid), {})
            detailed_id = pos_meta.get("detailed_position_id")
            position = positions_by_sm_id.get(detailed_id)
            if position is None:
                report["no_position"].append((sm_pid, data.get("display_name"), detailed_id))
            bucket = position_bucket_by_id.get(position.id) if position is not None else None
            is_goalkeeper = bucket == "portero"

            player = Player(
                sportmonks_player_id=data.get("id", sm_pid),
                apifootball_player_id=sm_id_to_af_id.get(sm_pid),
                name=data.get("display_name") or data.get("name") or ("player-" + str(sm_pid)),
                birth_date=_parse_date(data.get("date_of_birth")),
                nationality=str(data["nationality_id"]) if data.get("nationality_id") is not None else None,
                height_cm=data.get("height"),
                weight_kg=data.get("weight"),
                preferred_foot=None,  # Sportmonks no lo da en este include
                primary_position_id=position.id if position is not None else None,
                photo_url=data.get("image_path"),
            )
            session.add(player)
            session.flush()
            report["players"] += 1

            statistics = data.get("statistics", []) or []
            if len(statistics) > 1:
                report["multi_stage_players"].append(
                    (player.name, len(statistics),
                     [teams_by_sm_id.get(s.get("team_id"), {}).get("name") for s in statistics])
                )

            for stat_entry in statistics:
                team = _get_or_create_team(
                    session, teams_by_sm_id, team_cache, competition, stat_entry.get("team_id")
                )
                pts = PlayerTeamSeason(
                    player_id=player.id,
                    team_id=team.id,
                    season_id=season.id,
                    competition_id=competition.id,
                    date_from=None,
                    date_to=None,
                )
                session.add(pts)
                session.flush()
                report["player_team_season"] += 1

                details = {}
                for det in stat_entry.get("details", []):
                    code = det.get("type", {}).get("code")
                    if code:
                        details[code] = _unwrap(det.get("value"))

                for st in stat_types:
                    if st.valid_for == "goalkeeper_only" and not is_goalkeeper:
                        continue
                    if st.code in details:
                        number = _to_number(details[st.code])
                        if number is None:
                            continue
                        session.add(PlayerStatistic(
                            player_team_season_id=pts.id, stat_type_id=st.id,
                            value=number, is_imputed_zero=False,
                        ))
                        report["player_statistics"] += 1
                        if st.valid_for == "goalkeeper_only":
                            report["gk_only_rows"] += 1
                    else:
                        if st.code in BASE_CODES:
                            continue  # falta base -> no se imputa
                        session.add(PlayerStatistic(
                            player_team_season_id=pts.id, stat_type_id=st.id,
                            value=0, is_imputed_zero=True,
                        ))
                        report["player_statistics"] += 1
                        report["imputed_zero"] += 1
                        if st.valid_for == "goalkeeper_only":
                            report["gk_only_rows"] += 1

        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

    print("\n=== smoke_test_load - resumen ===")
    print("players................", report["players"])
    print("player_team_season.....", report["player_team_season"])
    print("player_statistics......", report["player_statistics"],
          "(de los cuales imputados a 0:", report["imputed_zero"], ")")
    print("filas de stats solo-portero:", report["gk_only_rows"])
    if report["multi_stage_players"]:
        print("jugadores multi-etapa cargados:")
        for name, n, teams in report["multi_stage_players"]:
            print("  -", name, "->", n, "etapas:", ", ".join(str(t) for t in teams))
    else:
        print("jugadores multi-etapa cargados: NINGUNO")
    if report["no_position"]:
        print("jugadores sin posicion mapeada:", report["no_position"])
    print("=================================")


if __name__ == "__main__":
    main()
