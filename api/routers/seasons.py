"""Router /seasons — (competición, temporada) disponibles (Fase 12a/12b)."""

from __future__ import annotations

import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.dependencies import _all_seasons, default_season, get_db

router = APIRouter(prefix="/seasons", tags=["meta"])


class SeasonItem(BaseModel):
    id: int
    name: str
    competition: str
    competition_id: int
    tier: int | None = None
    sportmonks_season_id: int
    start_date: datetime.date | None = None
    end_date: datetime.date | None = None
    is_default: bool


class SeasonsResponse(BaseModel):
    default: int  # id interno de la temporada por defecto
    items: list[SeasonItem]


@router.get("", response_model=SeasonsResponse, summary="Temporadas cargadas (para el selector del frontend)")
def list_seasons(db: Session = Depends(get_db)):
    seasons = _all_seasons(db)  # competición principal primero, más reciente antes
    default = default_season(db)
    return {
        "default": default.id if default else 0,
        "items": [
            {
                "id": s.id,
                "name": s.name,
                "competition": s.competition.name,
                "competition_id": s.competition_id,
                "tier": s.competition.tier,
                "sportmonks_season_id": s.sportmonks_season_id,
                "start_date": s.start_date,
                "end_date": s.end_date,
                "is_default": bool(default and s.id == default.id),
            }
            for s in seasons
        ],
    }
