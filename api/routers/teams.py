"""Router /teams."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.dependencies import get_db, resolve_season
from api.schemas.teams import TeamListResponse, TeamStyleResponse
from api.services import teams as svc
from db.models import Season

router = APIRouter(prefix="/teams", tags=["teams"])


@router.get("", response_model=TeamListResponse, summary="Equipos de la competición en la temporada")
def list_teams(db: Session = Depends(get_db), season: Season = Depends(resolve_season)):
    return svc.list_teams(db, season)


@router.get(
    "/{team_id}/style",
    response_model=TeamStyleResponse,
    summary="Perfil de estilo del equipo (agregado + por formación con >= 5 partidos)",
)
def get_team_style(
    team_id: int,
    db: Session = Depends(get_db),
    season: Season = Depends(resolve_season),
):
    return svc.get_team_style(db, season, team_id)
