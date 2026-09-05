"""Fase 16 - ETL del entrenador por equipo.

Descartado en la Fase 11 para "el entrenador de una temporada pasada"
(fechas de tenencia poco fiables). Reabierto tras verificar que:

  1. `active: true` es HOY fiable (una sola relación activa por equipo,
     fechas coherentes) -> sirve para "entrenador actual".
  2. Con fechas ya coherentes, reconstruir "quien dirigió la temporada
     mostrada" por solape de fechas también es viable -> `kind='season'`.

Un único endpoint por equipo (`/teams/{id}?include=coaches.coach`) trae
TODAS sus relaciones histéricas; de ahí se derivan las dos vistas sin
peticiones extra por temporada. Idempotente: DELETE de toda la tabla +
INSERT (grano por etapa, mismo patrón que `player_team_season`).

Uso:
    python -m loaders.etl_coaches --dry-run --limit 10   # prueba, cuida cuota
    python -m loaders.etl_coaches                         # las ~100 franquicias
    python -m loaders.etl_coaches --refetch                # ignora cache
"""

from __future__ import annotations

import argparse
import datetime
import json
import logging
import os
import time

from sqlalchemy import delete, select

from db.database import get_session
from db.models import Season, Team, TeamCoach

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("etl_coaches")

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _resolve_data_dir():
    configured = os.getenv("DATA_EXPERIMENT_DIR")
    candidates = []
    if configured:
        candidates.append(configured if os.path.isabs(configured) else os.path.join(_PROJECT_ROOT, configured))
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
_COACHES_DIR = os.path.join(_DATA_DIR, "raw_data", "sportmonks", "coaches")
SPORTMONKS_BASE = "https://api.sportmonks.com/v3/football"


def _sportmonks_token():
    for env_path in (os.path.join(_PROJECT_ROOT, ".env"), os.path.join(_DATA_DIR, ".env")):
        if os.path.isfile(env_path):
            for line in open(env_path, "r", encoding="utf-8"):
                if line.strip().startswith("SPORTMONKS_API_TOKEN="):
                    return line.split("=", 1)[1].strip()
    return os.getenv("SPORTMONKS_API_TOKEN")


def _fetch_or_cache(sm_team_id, refetch, token):
    import requests

    path = os.path.join(_COACHES_DIR, f"{sm_team_id}.json")
    if os.path.isfile(path) and not refetch:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    resp = requests.get(
        f"{SPORTMONKS_BASE}/teams/{sm_team_id}",
        params={"api_token": token, "include": "coaches.coach"},
        timeout=25,
    )
    resp.raise_for_status()
    payload = resp.json()
    if not os.path.isdir(_COACHES_DIR):
        os.makedirs(_COACHES_DIR)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    return payload


def _parse_date(s):
    if not s:
        return None
    try:
        return datetime.date.fromisoformat(s[:10])
    except ValueError:
        return None


def _parse_coaches(payload):
    out = []
    for c in payload.get("data", {}).get("coaches", []) or []:
        co = c.get("coach") or {}
        st, en = _parse_date(c.get("start")), _parse_date(c.get("end"))
        out.append({
            "name": co.get("name"),
            "sportmonks_coach_id": co.get("id"),
            "active": bool(c.get("active")),
            "start": st,
            "end": en,
        })
    return out


def _reconcile_season_stints(coaches, window_start, window_end):
    """Etapas que solapan [window_start, window_end], limpiadas de:
    - relaciones cuyo rango CONTIENE ESTRICTAMENTE el de otra que también
      solapa (contratos de banquillo/asistente de varios años que Sportmonks
      mezcla con las de primer entrenador -- ver docs/DECISIONS.md);
    - duplicados exactos y etapas consecutivas del mismo entrenador.
    Devuelve la lista ordenada por fecha de inicio (puede ser vacía: sin
    relación fiable que cubra la ventana -> no se fuerza un dato dudoso)."""
    if window_start is None or window_end is None:
        return []
    seen = set()
    cands = []
    for c in coaches:
        if c["start"] is None or c["end"] is None or c["start"] > c["end"]:
            continue
        if not (c["start"] <= window_end and c["end"] >= window_start):
            continue
        key = (c["name"], c["start"], c["end"])
        if key in seen:
            continue
        seen.add(key)
        cands.append(c)

    def _contains(a, b):
        return a["start"] <= b["start"] and a["end"] >= b["end"] and (a["start"], a["end"]) != (b["start"], b["end"])

    kept = [c for c in cands if not any(_contains(c, other) for other in cands if other is not c)]
    if not kept:
        kept = cands
    kept.sort(key=lambda c: (c["start"], c["end"]))

    merged = []
    for c in kept:
        if merged and merged[-1]["name"] == c["name"] and c["start"] <= merged[-1]["end"] + datetime.timedelta(days=1):
            merged[-1]["end"] = max(merged[-1]["end"], c["end"])
        else:
            merged.append(dict(c))
    return merged


def run(dry_run=False, limit=None, refetch=False, fetch_missing=True):
    started = time.monotonic()
    session = get_session()
    report = {
        "teams": 0, "current_found": 0, "current_missing": 0,
        "season_rows": 0, "season_pairs_with_data": 0, "season_pairs_without_data": 0,
        "fetched": 0,
    }
    try:
        teams = list(session.scalars(select(Team).order_by(Team.id)))
        if limit:
            teams = teams[:limit]
        seasons = {s.id: s for s in session.scalars(select(Season))}

        # (team_id, season_id) para los que el equipo jugo de verdad esa
        # temporada -- solo para esos tiene sentido reconstruir 'season'.
        from db.models import TeamFixture
        pairs = set(session.execute(select(TeamFixture.team_id, TeamFixture.season_id).distinct()).all())

        token = _sportmonks_token() if fetch_missing else None
        if fetch_missing and not token:
            raise RuntimeError("Falta SPORTMONKS_API_TOKEN para descargar entrenadores.")

        all_rows = []
        for t in teams:
            report["teams"] += 1
            path = os.path.join(_COACHES_DIR, f"{t.sportmonks_team_id}.json")
            was_cached = os.path.isfile(path) and not refetch
            payload = _fetch_or_cache(t.sportmonks_team_id, refetch, token)
            if not was_cached:
                report["fetched"] += 1
                time.sleep(0.12)
            coaches = _parse_coaches(payload)

            actives = [c for c in coaches if c["active"]]
            if actives:
                report["current_found"] += 1
                all_rows.append(dict(
                    team_id=t.id, kind="current", season_id=None, order_in_season=0,
                    sportmonks_coach_id=actives[0]["sportmonks_coach_id"],
                    coach_name=actives[0]["name"], start_date=actives[0]["start"], end_date=actives[0]["end"],
                ))
            else:
                report["current_missing"] += 1

            for sid in sorted(sid for (tid, sid) in pairs if tid == t.id):
                se = seasons.get(sid)
                if se is None:
                    continue
                stints = _reconcile_season_stints(coaches, se.start_date, se.end_date)
                if not stints:
                    report["season_pairs_without_data"] += 1
                    continue
                report["season_pairs_with_data"] += 1
                for i, st in enumerate(stints):
                    all_rows.append(dict(
                        team_id=t.id, kind="season", season_id=sid, order_in_season=i,
                        sportmonks_coach_id=st["sportmonks_coach_id"], coach_name=st["name"],
                        start_date=st["start"], end_date=st["end"],
                    ))
                    report["season_rows"] += 1

            if not dry_run and report["teams"] % 25 == 0:
                log.info("  ... %s/%s equipos", report["teams"], len(teams))

        if not dry_run:
            session.execute(delete(TeamCoach))
            if all_rows:
                session.execute(TeamCoach.__table__.insert(), all_rows)
            session.commit()
        else:
            session.rollback()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

    _print_report(report, time.monotonic() - started, dry_run)
    return report


def _print_report(report, elapsed, dry_run):
    print("\n" + "=" * 60)
    print("  ETL Entrenadores -", "DRY-RUN" if dry_run else "CARGA REAL")
    print("=" * 60)
    print(f"  equipos procesados............... {report['teams']}")
    print(f"  descargados de la API (no cache).. {report['fetched']}")
    print(f"  con entrenador actual (active).... {report['current_found']}")
    print(f"  SIN entrenador actual............. {report['current_missing']}")
    print(f"  pares equipo-temporada con dato... {report['season_pairs_with_data']}")
    print(f"  pares equipo-temporada SIN dato... {report['season_pairs_without_data']}")
    print(f"  filas 'season' insertadas......... {report['season_rows']}")
    print(f"  tiempo............................ {elapsed:.1f} s")
    print("=" * 60)


def main():
    ap = argparse.ArgumentParser(description="Fase 16: ETL del entrenador (current + season)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, help="solo los primeros N equipos (prueba, cuida cuota)")
    ap.add_argument("--refetch", action="store_true", help="ignora el cache y vuelve a pedir a la API")
    args = ap.parse_args()
    run(dry_run=args.dry_run, limit=args.limit, refetch=args.refetch)


if __name__ == "__main__":
    main()
