"""Router /seasons — temporadas disponibles (Fase 12a)."""

from __future__ import annotations

import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.dependencies import get_db, latest_season, _all_seasons

router = APIRouter(prefix="/seasons", tags=["meta"])


class SeasonItem(BaseModel):
    id: int
    name: str
    sportmonks_season_id: int
    start_date: datetime.date | None = None
    end_date: datetime.date | None = None
    is_default: bool


class SeasonsResponse(BaseModel):
    default: str
    items: list[SeasonItem]


@router.get("", response_model=SeasonsResponse, summary="Temporadas cargadas (para el selector del frontend)")
def list_seasons(db: Session = Depends(get_db)):
    seasons = _all_seasons(db)  # más reciente primero
    default = latest_season(db)
    return {
        "default": default.name if default else "",
        "items": [
            {
                "id": s.id,
                "name": s.name,
                "sportmonks_season_id": s.sportmonks_season_id,
                "start_date": s.start_date,
                "end_date": s.end_date,
                "is_default": bool(default and s.id == default.id),
            }
            for s in seasons
        ],
    }
