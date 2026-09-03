"""Router /roles."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.dependencies import get_db
from api.schemas.roles import RolesResponse
from api.services import roles as svc

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get(
    "",
    response_model=RolesResponse,
    summary="Los 5 roles construibles plenos con su definición de pesos",
)
def list_roles(db: Session = Depends(get_db)):
    return svc.list_roles(db)
