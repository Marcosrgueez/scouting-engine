"""Dependencies compartidas de la API.

- get_db: sesión de BD por request.
- resolve_season: Fase 12a — con >1 temporada cargada, cada endpoint
  acepta `?season=` (id interno, sportmonks_season_id, o el nombre
  '2025/2026'); por defecto la MÁS RECIENTE completa.

La API NO reimplementa nada de `analysis/`.
"""

from __future__ import annotations

import datetime
from collections.abc import Iterator

from fastapi import Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from db.database import SessionLocal
from db.models import Season


def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _all_seasons(db: Session) -> list[Season]:
    # más reciente primero (por end_date, luego por id)
    return list(db.scalars(select(Season).order_by(Season.end_date.desc().nullslast(), Season.id.desc())))


def latest_season(db: Session) -> Season | None:
    seasons = _all_seasons(db)
    return seasons[0] if seasons else None


def resolve_season(
    db: Session = Depends(get_db),
    season: str | None = Query(
        None,
        description="temporada: id interno, sportmonks_season_id o nombre ('2025/2026'). "
        "Por defecto, la más reciente cargada.",
    ),
) -> Season:
    """Resuelve la temporada de un request. 404 si `season` no existe."""
    seasons = _all_seasons(db)
    if not seasons:
        raise HTTPException(status_code=503, detail="No hay ninguna temporada cargada.")
    if season is None:
        return seasons[0]
    key = season.strip()
    for s in seasons:
        if key in (str(s.id), str(s.sportmonks_season_id), s.name):
            return s
    raise HTTPException(
        status_code=404,
        detail=f"Temporada {season!r} no encontrada. Disponibles: "
        f"{[s.name for s in seasons]}.",
    )


def age_reference_date(season: Season) -> datetime.date:
    """Fecha para calcular edades: fin de la temporada analizada (no 'hoy'),
    para que la edad sea la que el jugador tenía esa temporada."""
    return season.end_date or datetime.date(season.name and int(season.name[:4]) + 1 or 2025, 5, 31)
