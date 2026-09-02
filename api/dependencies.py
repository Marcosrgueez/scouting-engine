"""Dependencies compartidas de la API.

- get_db: sesión de BD por request.
- resolve_season: Fase 12a/12b — con >1 (competición, temporada) cargada,
  cada endpoint acepta `?season=` (id interno, sportmonks_season_id, o el
  nombre '2025/2026') y opcionalmente `?competition=` (id, sportmonks_league_id
  o nombre) para desambiguar cuando el nombre de temporada se repite entre
  ligas (LaLiga 25/26 vs Segunda 25/26). Por defecto: la temporada más
  reciente de la competición de menor tier (Primera antes que Segunda).

La API NO reimplementa nada de `analysis/`.
"""

from __future__ import annotations

import datetime
from collections.abc import Iterator

from fastapi import Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from db.database import SessionLocal
from db.models import Competition, Season


def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _all_seasons(db: Session) -> list[Season]:
    """Todas las temporadas, orden de presentación: competición de menor tier
    primero, y dentro de cada una la más reciente antes."""
    return list(
        db.scalars(
            select(Season)
            .join(Competition, Competition.id == Season.competition_id)
            .order_by(
                Competition.tier.asc().nullslast(),
                Season.end_date.desc().nullslast(),
                Season.id.desc(),
            )
        )
    )


def default_season(db: Session) -> Season | None:
    seasons = _all_seasons(db)
    return seasons[0] if seasons else None


# alias histórico (routers/seasons.py)
latest_season = default_season


def _match_competition(db: Session, key: str) -> Competition | None:
    k = key.strip()
    for c in db.scalars(select(Competition)):
        if k in (str(c.id), str(c.sportmonks_league_id)) or k.lower() == c.name.lower():
            return c
    return None


def resolve_season(
    db: Session = Depends(get_db),
    season: str | None = Query(
        None,
        description="temporada: id interno, sportmonks_season_id o nombre ('2025/2026'). "
        "Por defecto, la más reciente de la competición principal (menor tier).",
    ),
    competition: str | None = Query(
        None,
        description="competición: id interno, sportmonks_league_id o nombre ('La Liga', 'La Liga 2'). "
        "Solo hace falta para desambiguar un nombre de temporada repetido entre ligas.",
    ),
) -> Season:
    """Resuelve la temporada de un request. 404 si no existe / es ambigua."""
    seasons = _all_seasons(db)
    if not seasons:
        raise HTTPException(status_code=503, detail="No hay ninguna temporada cargada.")

    comp = None
    if competition is not None:
        comp = _match_competition(db, competition)
        if comp is None:
            raise HTTPException(status_code=404, detail=f"Competición {competition!r} no encontrada.")
        seasons = [s for s in seasons if s.competition_id == comp.id]
        if not seasons:
            raise HTTPException(status_code=404, detail=f"No hay temporadas cargadas de {comp.name!r}.")

    if season is None:
        return seasons[0]

    key = season.strip()
    # id interno / sportmonks_season_id: siempre inequívocos
    for s in seasons:
        if key in (str(s.id), str(s.sportmonks_season_id)):
            return s
    # por nombre: puede repetirse entre competiciones
    by_name = [s for s in seasons if s.name == key]
    if len(by_name) == 1:
        return by_name[0]
    if len(by_name) > 1:
        # ya venían ordenadas por tier asc -> la de la competición principal;
        # se avisa de cómo desambiguar del todo.
        raise HTTPException(
            status_code=409,
            detail=(
                f"La temporada {season!r} existe en varias competiciones: "
                f"{[_c.name for _c in db.scalars(select(Competition).where(Competition.id.in_([s.competition_id for s in by_name])))]}. "
                "Añade ?competition= o usa el sportmonks_season_id."
            ),
        )
    raise HTTPException(
        status_code=404,
        detail=f"Temporada {season!r} no encontrada. Disponibles: "
        f"{[(s.name, s.sportmonks_season_id) for s in seasons]}.",
    )


def age_reference_date(season: Season) -> datetime.date:
    """Fecha para calcular edades: fin de la temporada analizada (no 'hoy'),
    para que la edad sea la que el jugador tenía esa temporada."""
    return season.end_date or datetime.date(season.name and int(season.name[:4]) + 1 or 2025, 5, 31)
