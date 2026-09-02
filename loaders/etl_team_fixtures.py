"""Fase 7 - ETL del Team Style Profile (datos de partido de LaLiga).

Descarga la temporada completa de Sportmonks via el metodo bulk paginado
(ver data-experiment/docs/fase7_fixtures_investigation.md), guarda el JSON
crudo en data-experiment/raw_data/sportmonks/fixtures/ y carga:

    team_fixtures            (1 fila por equipo y partido: formacion, venue,
                              goles, resultado)
    team_fixture_statistics  (stats propias -> is_conceded=False; stats del
                              rival del mismo partido -> is_conceded=True)

Grano CRUDO por partido. La agregacion por formacion (V/E/D, medias, por
venue) se hace por consulta (GROUP BY), NO aqui -- mismo principio que
player_team_season / player_statistics en la Fase 2.

Constraints de carga (decisiones de Fase 7, no reabrir):
  - goals_for / goals_against SIEMPRE de scores[] (description='CURRENT'),
    NUNCA del bloque statistics ('goals' se omite cuando un equipo marca 0).
  - Ceros omitidos por Sportmonks: se imputan 0 explicito con
    is_imputed_zero=True, igual que player_statistics. Solo para stats
    'count'; las 'percentage' (posesion, precision de pases) no se imputan.
  - Solo entran los 15 team_stat_types del catalogo (los fiables en 50/50
    partidos de la muestra).

Idempotente: DELETE scoped por season_id (+ cascade a team_fixture_statistics)
+ INSERT. Mismo patron que el resto de fases. No upsert: el conjunto de
stats presentes de un partido puede cambiar entre descargas y un upsert
dejaria filas viejas.

Uso:
    python -m loaders.etl_team_fixtures --dry-run     # descarga (si falta) + carga + rollback
    python -m loaders.etl_team_fixtures               # carga real
    python -m loaders.etl_team_fixtures --refetch     # fuerza volver a bajar las 8 paginas
    python -m loaders.etl_team_fixtures --offline     # falla si no hay JSON cacheado
"""

from __future__ import annotations

import argparse
import datetime
import json
import logging
import os
import time
from collections import Counter, defaultdict

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from db.database import get_session
from db.models import (
    Competition,
    Season,
    Team,
    TeamFixture,
    TeamFixtureStatistic,
    TeamStatType,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("etl_team_fixtures")

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SPORTMONKS_BASE = "https://api.sportmonks.com/v3/football"
BULK_INCLUDE = "participants;formations;statistics.type;scores;state"
PER_PAGE = 50
# lineups NO se incluye a proposito: el esquema de Fase 7 no lo usa
# (la formacion viene de `formations`, no de `lineups`) e inflaba el JSON
# ~20x. Si Fase 8 necesita datos por jugador y partido, son 8 peticiones
# baratas mas en su momento.

FT_STATES = {"FT", "AET", "FT_PEN", "AWARDED"}


# ---------------------------------------------------------------------------
# Rutas / IO
# ---------------------------------------------------------------------------

def _resolve_data_dir():
    configured = os.getenv("DATA_EXPERIMENT_DIR")
    candidates = []
    if configured:
        candidates.append(configured if os.path.isabs(configured)
                          else os.path.join(_PROJECT_ROOT, configured))
    here = _PROJECT_ROOT
    for _ in range(5):
        candidates.append(os.path.join(here, "data-experiment"))
        here = os.path.dirname(here)
    for cand in candidates:
        cand = os.path.normpath(cand)
        if os.path.isdir(os.path.join(cand, "raw_data", "sportmonks")):
            return cand
    raise RuntimeError("No encuentro data-experiment/raw_data/sportmonks/.")


_DATA_DIR = _resolve_data_dir()
_SM_DIR = os.path.join(_DATA_DIR, "raw_data", "sportmonks")
_FIXTURES_DIR = os.path.join(_SM_DIR, "fixtures")


def _fixtures_dir(season_dir=None):
    # season_dir="s25659" -> raw_data/sportmonks/s25659/fixtures/ (Fase 12a).
    # None -> raw_data/sportmonks/fixtures/ (2024/25, Fases 0-8).
    return os.path.join(_SM_DIR, season_dir, "fixtures") if season_dir else _FIXTURES_DIR


def _load_json(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _sportmonks_token():
    for env_path in (os.path.join(_PROJECT_ROOT, ".env"), os.path.join(_DATA_DIR, ".env")):
        if os.path.isfile(env_path):
            for line in open(env_path, "r", encoding="utf-8"):
                if line.strip().startswith("SPORTMONKS_API_TOKEN="):
                    return line.split("=", 1)[1].strip()
    return os.getenv("SPORTMONKS_API_TOKEN")


# ---------------------------------------------------------------------------
# Descarga (bulk paginado)
# ---------------------------------------------------------------------------

def _download_all_pages(sportmonks_season_id, token, fixtures_dir):
    import requests

    if not os.path.isdir(fixtures_dir):
        os.makedirs(fixtures_dir)

    pages = []
    page = 1
    while True:
        params = {
            "api_token": token,
            "filters": f"fixtureSeasons:{sportmonks_season_id}",
            "include": BULK_INCLUDE,
            "per_page": PER_PAGE,
            "page": page,
        }
        resp = requests.get(f"{SPORTMONKS_BASE}/fixtures", params=params, timeout=40)
        resp.raise_for_status()
        payload = resp.json()
        with open(os.path.join(fixtures_dir, f"page_{page:02d}.json"), "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)
        pages.append(payload)
        pg = payload.get("pagination", {})
        rl = payload.get("rate_limit", {})
        log.info("  pagina %s: %s fixtures  [quedan %s peticiones]",
                 page, len(payload.get("data", [])), rl.get("remaining"))
        if not pg.get("has_more"):
            break
        page += 1
    return pages


def _load_cached_pages(fixtures_dir):
    if not os.path.isdir(fixtures_dir):
        return []
    files = sorted(f for f in os.listdir(fixtures_dir) if f.startswith("page_") and f.endswith(".json"))
    return [_load_json(os.path.join(fixtures_dir, f)) for f in files]


def _get_fixtures(sportmonks_season_id, refetch, offline, fixtures_dir):
    cached = _load_cached_pages(fixtures_dir)
    if cached and not refetch:
        log.info("usando %s paginas cacheadas en %s", len(cached), fixtures_dir)
        pages = cached
    elif offline:
        raise RuntimeError(f"--offline y no hay paginas en {fixtures_dir}. Quita --offline para descargar.")
    else:
        token = _sportmonks_token()
        if not token:
            raise RuntimeError("Falta SPORTMONKS_API_TOKEN (en scouting-engine/.env o data-experiment/.env).")
        log.info("descargando la temporada completa (bulk, per_page=%s)...", PER_PAGE)
        pages = _download_all_pages(sportmonks_season_id, token, fixtures_dir)

    fixtures = []
    for pg in pages:
        fixtures.extend(pg.get("data", []))
    return fixtures


# ---------------------------------------------------------------------------
# Parseo de un fixture -> 2 filas team_fixtures + sus stats
# ---------------------------------------------------------------------------

def _parse_scores(fixture):
    """{'home': goles, 'away': goles} desde scores[] description='CURRENT'."""
    out = {}
    for sc in fixture.get("scores", []):
        if sc.get("description") == "CURRENT":
            s = sc.get("score", {})
            if s.get("participant") in ("home", "away") and s.get("goals") is not None:
                out[s["participant"]] = int(s["goals"])
    return out


def _parse_participants(fixture):
    """{'home': sm_team_id, 'away': sm_team_id} y {sm_team_id: name}."""
    loc_to_team = {}
    names = {}
    for p in fixture.get("participants", []):
        loc = (p.get("meta") or {}).get("location")
        if loc in ("home", "away"):
            loc_to_team[loc] = p["id"]
            names[p["id"]] = p.get("name")
    return loc_to_team, names


def _parse_formations(fixture):
    """{sm_team_id: 'formation'}."""
    return {fm["participant_id"]: fm.get("formation")
            for fm in fixture.get("formations", [])
            if fm.get("participant_id") is not None}


def _parse_statistics(fixture, wanted_codes):
    """{sm_team_id: {code: value}} filtrado a wanted_codes."""
    out = defaultdict(dict)
    for st in fixture.get("statistics", []):
        code = (st.get("type") or {}).get("code")
        if code not in wanted_codes:
            continue
        pid = st.get("participant_id")
        val = (st.get("data") or {}).get("value")
        if pid is None or val is None:
            continue
        out[pid][code] = val
    return out


def _result(gf, ga):
    if gf > ga:
        return "win"
    if gf < ga:
        return "loss"
    return "draw"


def _stat_rows(own_codes, opp_codes, team_stat_types):
    """Filas para un team_fixture: propias (is_conceded=False) + concedidas
    (is_conceded=True). Imputa 0 en 'count' ausentes; omite 'percentage'
    ausentes."""
    rows = []
    for tst in team_stat_types:
        for conceded, present in ((False, own_codes), (True, opp_codes)):
            if tst.code in present:
                rows.append({"team_stat_type_id": tst.id, "value": float(present[tst.code]),
                             "is_imputed_zero": False, "is_conceded": conceded})
            elif tst.unit == "count":
                rows.append({"team_stat_type_id": tst.id, "value": 0.0,
                             "is_imputed_zero": True, "is_conceded": conceded})
            # percentage ausente -> sin fila
    return rows


# ---------------------------------------------------------------------------
# ETL
# ---------------------------------------------------------------------------

def run(dry_run=False, refetch=False, offline=False, sportmonks_season_id=None, season_dir=None):
    started = time.monotonic()
    session = get_session()
    fixtures_dir = _fixtures_dir(season_dir)
    report = {
        "fixtures_total": 0,
        "fixtures_loaded": 0,
        "team_fixture_rows": 0,
        "stat_rows": 0,
        "imputed_zero_rows": 0,
        "skipped_not_ft": [],
        "missing_score": [],
        "missing_formation": Counter(),   # fixture_id -> nº equipos sin formacion
        "missing_all_stats": [],
        "orphan_team_ids": Counter(),
        "formations_seen": Counter(),
    }

    try:
        if sportmonks_season_id is not None:
            season = session.scalar(
                select(Season).where(Season.sportmonks_season_id == sportmonks_season_id)
            )
        else:
            seasons = session.scalars(select(Season)).all()
            if len(seasons) > 1:
                raise RuntimeError(
                    "Hay varias temporadas cargadas; pasa --sportmonks-season-id "
                    f"(disponibles: {[(s.name, s.sportmonks_season_id) for s in seasons]})."
                )
            season = seasons[0] if seasons else None
        competition = session.scalar(select(Competition))
        if season is None or competition is None:
            raise RuntimeError("Faltan season/competition. Ejecuta la Fase 2 (loaders.etl_laliga) primero.")

        team_stat_types = list(session.scalars(select(TeamStatType)).all())
        if not team_stat_types:
            raise RuntimeError("team_stat_types vacio. Ejecuta 'python -m db.create_schema' primero.")
        wanted_codes = {t.code for t in team_stat_types}

        team_pk_by_sm = {
            t.sportmonks_team_id: t.id
            for t in session.scalars(select(Team)).all()
        }

        fixtures = _get_fixtures(season.sportmonks_season_id, refetch, offline, fixtures_dir)
        report["fixtures_total"] = len(fixtures)

        # --- idempotencia: borra la temporada y recarga ---
        session.execute(delete(TeamFixture).where(TeamFixture.season_id == season.id))

        tf_values = []          # filas team_fixtures pendientes de insertar
        tf_stat_plan = []       # (sportmonks_fixture_id, team_sm_id, [stat rows])

        for fx in fixtures:
            fid = fx["id"]
            state = (fx.get("state") or {}).get("state")
            if state not in FT_STATES:
                report["skipped_not_ft"].append((fid, state))
                continue

            loc_to_team, names = _parse_participants(fx)
            scores = _parse_scores(fx)
            if "home" not in loc_to_team or "away" not in loc_to_team:
                report["missing_score"].append(fid)
                continue
            if "home" not in scores or "away" not in scores:
                report["missing_score"].append(fid)
                continue

            formations = _parse_formations(fx)
            stats_by_team = _parse_statistics(fx, wanted_codes)
            if not stats_by_team:
                report["missing_all_stats"].append(fid)

            starting_at = None
            if fx.get("starting_at"):
                try:
                    starting_at = datetime.datetime.fromisoformat(fx["starting_at"])
                except ValueError:
                    starting_at = None

            missing_form_here = 0
            for venue in ("home", "away"):
                other = "away" if venue == "home" else "home"
                team_sm = loc_to_team[venue]
                opp_sm = loc_to_team[other]
                team_pk = team_pk_by_sm.get(team_sm)
                opp_pk = team_pk_by_sm.get(opp_sm)
                if team_pk is None:
                    report["orphan_team_ids"][team_sm] += 1
                    continue
                if opp_pk is None:
                    report["orphan_team_ids"][opp_sm] += 1
                    continue

                formation = formations.get(team_sm)
                if formation is None:
                    missing_form_here += 1
                else:
                    report["formations_seen"][formation] += 1

                gf, ga = scores[venue], scores[other]
                tf_values.append({
                    "team_id": team_pk,
                    "opponent_team_id": opp_pk,
                    "season_id": season.id,
                    "competition_id": competition.id,
                    "sportmonks_fixture_id": fid,
                    "starting_at": starting_at,
                    "venue": venue,
                    "formation": formation,
                    "goals_for": gf,
                    "goals_against": ga,
                    "result": _result(gf, ga),
                })
                rows = _stat_rows(stats_by_team.get(team_sm, {}),
                                  stats_by_team.get(opp_sm, {}),
                                  team_stat_types)
                tf_stat_plan.append((fid, team_sm, rows))

            if missing_form_here:
                report["missing_formation"][fid] = missing_form_here
            report["fixtures_loaded"] += 1

        # --- insert team_fixtures (bulk, con RETURNING para el id) ---
        tf_id_by_key = {}
        if tf_values:
            stmt = pg_insert(TeamFixture).values(tf_values).returning(
                TeamFixture.id, TeamFixture.sportmonks_fixture_id, TeamFixture.team_id
            )
            for row_id, sm_fid, team_pk in session.execute(stmt):
                tf_id_by_key[(sm_fid, team_pk)] = row_id
        report["team_fixture_rows"] = len(tf_values)

        # --- insert team_fixture_statistics ---
        stat_values = []
        for sm_fid, team_sm, rows in tf_stat_plan:
            team_pk = team_pk_by_sm.get(team_sm)
            tf_id = tf_id_by_key.get((sm_fid, team_pk))
            if tf_id is None:
                continue
            for r in rows:
                stat_values.append(dict(team_fixture_id=tf_id, **r))
        if stat_values:
            # trocea el insert para no pasar un statement gigante
            for i in range(0, len(stat_values), 5000):
                session.execute(pg_insert(TeamFixtureStatistic).values(stat_values[i:i + 5000]))
        report["stat_rows"] = len(stat_values)
        report["imputed_zero_rows"] = sum(1 for r in stat_values if r["is_imputed_zero"])

        if dry_run:
            session.rollback()
            log.info("DRY-RUN: rollback, nada escrito")
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
    print("\n" + "=" * 64)
    print("  ETL Team Fixtures (Fase 7) -", "DRY-RUN" if dry_run else "CARGA REAL")
    print("=" * 64)
    print(f"  fixtures en el JSON............ {report['fixtures_total']}")
    print(f"  fixtures cargados............. {report['fixtures_loaded']}")
    print(f"  filas team_fixtures.......... {report['team_fixture_rows']}")
    print(f"  filas team_fixture_statistics {report['stat_rows']}")
    print(f"      de ellas imputadas a 0... {report['imputed_zero_rows']}")
    print(f"  formaciones distintas vistas. {len(report['formations_seen'])}")
    if report["skipped_not_ft"]:
        print(f"  fixtures NO terminados (skip): {len(report['skipped_not_ft'])} {report['skipped_not_ft'][:5]}")
    if report["missing_score"]:
        print(f"  fixtures sin marcador limpio.. {len(report['missing_score'])} {report['missing_score'][:5]}")
    if report["missing_formation"]:
        print(f"  fixtures con formacion incompleta: {len(report['missing_formation'])} "
              f"(equipos afectados: {sum(report['missing_formation'].values())})")
        print(f"      {dict(list(report['missing_formation'].items())[:10])}")
    else:
        print(f"  fixtures con formacion incompleta: 0")
    if report["missing_all_stats"]:
        print(f"  fixtures SIN ninguna stat de equipo: {len(report['missing_all_stats'])} {report['missing_all_stats'][:5]}")
    else:
        print(f"  fixtures sin ninguna stat de equipo: 0")
    if report["orphan_team_ids"]:
        print(f"  team_ids fuera de teams: {dict(report['orphan_team_ids'])}")
    print(f"  tiempo........................ {elapsed:.1f} s")
    print("=" * 64)


def main():
    ap = argparse.ArgumentParser(description="Fase 7: ETL Team Style Profile")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--refetch", action="store_true", help="fuerza volver a descargar las 8 paginas")
    ap.add_argument("--offline", action="store_true", help="falla si no hay JSON cacheado (no descarga)")
    ap.add_argument("--sportmonks-season-id", type=int, default=None,
                    help="obligatorio si hay >1 temporada cargada (LaLiga 25/26 = 25659)")
    ap.add_argument("--season-dir", default=None,
                    help="subdirectorio de raw_data/sportmonks/ para el cache de fixtures (ej 's25659')")
    args = ap.parse_args()
    run(dry_run=args.dry_run, refetch=args.refetch, offline=args.offline,
        sportmonks_season_id=args.sportmonks_season_id, season_dir=args.season_dir)


if __name__ == "__main__":
    main()
