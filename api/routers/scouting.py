"""Router /scouting."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.dependencies import get_db, resolve_season
from api.schemas.scouting import TacticalFitRequest, TacticalFitResponse
from api.services import scouting as svc
from db.models import Season

router = APIRouter(prefix="/scouting", tags=["scouting"])


@router.post(
    "/tactical-fit",
    response_model=TacticalFitResponse,
    summary="Ranking de jugadores por encaje táctico en un equipo+rol (Fase 8, en vivo)",
)
def tactical_fit(
    body: TacticalFitRequest,
    db: Session = Depends(get_db),
    season: Season = Depends(resolve_season),
):
    return svc.tactical_fit_ranking(
        db, season, team_id=body.team_id, role_id=body.role_id, formation=body.formation,
        cross_competition=body.cross_competition,
    )
