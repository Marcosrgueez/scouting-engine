"""Router /teams."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.dependencies import get_db
from api.schemas.teams import TeamListResponse, TeamStyleResponse
from api.services import teams as svc

router = APIRouter(prefix="/teams", tags=["teams"])


@router.get("", response_model=TeamListResponse, summary="Los 20 equipos de LaLiga 24/25")
def list_teams(db: Session = Depends(get_db)):
    return svc.list_teams(db)


@router.get(
    "/{team_id}/style",
    response_model=TeamStyleResponse,
    summary="Perfil de estilo del equipo (agregado + por formación con >= 5 partidos)",
)
def get_team_style(team_id: int, db: Session = Depends(get_db)):
    return svc.get_team_style(db, team_id)
