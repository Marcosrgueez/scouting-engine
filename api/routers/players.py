"""Router /players."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api.dependencies import get_db
from api.schemas.players import (
    PlayerListResponse,
    PlayerProfile,
    PlayerRolesResponse,
    SimilarPlayersResponse,
)
from api.services import players as svc
from db.models import POSITION_BUCKETS, POSITION_SIDES

router = APIRouter(prefix="/players", tags=["players"])


@router.get("", response_model=PlayerListResponse, summary="Lista paginada de jugadores")
def list_players(
    db: Session = Depends(get_db),
    bucket: str | None = Query(None, description=f"uno de {POSITION_BUCKETS}"),
    team_id: int | None = Query(None, description="equipo actual del jugador"),
    min_minutes: int = Query(900, ge=0, description="minutos totales mínimos en LaLiga 24/25"),
    age_min: int | None = Query(None, ge=14, le=50),
    age_max: int | None = Query(None, ge=14, le=50),
    side: str | None = Query(None, description=f"uno de {POSITION_SIDES}"),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    if bucket is not None and bucket not in POSITION_BUCKETS:
        raise HTTPException(422, f"bucket inválido; usa uno de {POSITION_BUCKETS}")
    if side is not None and side not in POSITION_SIDES:
        raise HTTPException(422, f"side inválido; usa uno de {POSITION_SIDES}")
    return svc.list_players(
        db,
        bucket=bucket,
        team_id=team_id,
        min_minutes=min_minutes,
        age_min=age_min,
        age_max=age_max,
        side=side,
        offset=offset,
        limit=limit,
    )


@router.get("/{player_id}", response_model=PlayerProfile, summary="Perfil completo de un jugador")
def get_player(player_id: int, db: Session = Depends(get_db)):
    return svc.get_player_profile(db, player_id)


@router.get(
    "/{player_id}/similar",
    response_model=SimilarPlayersResponse,
    summary="Top-20 más similar (ya calculado), con filtros de edad/lado sobre el resultado",
)
def get_similar(
    player_id: int,
    db: Session = Depends(get_db),
    age_max: int | None = Query(None, ge=14, le=50),
    side: str | None = Query(None, description=f"uno de {POSITION_SIDES}"),
):
    if side is not None and side not in POSITION_SIDES:
        raise HTTPException(422, f"side inválido; usa uno de {POSITION_SIDES}")
    return svc.get_similar_players(db, player_id, age_max=age_max, side=side)


@router.get(
    "/{player_id}/roles",
    response_model=PlayerRolesResponse,
    summary="Role scores del jugador con desglose por métrica",
)
def get_roles(player_id: int, db: Session = Depends(get_db)):
    return svc.get_player_roles(db, player_id)
