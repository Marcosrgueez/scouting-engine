"""Dependencies compartidas de la API (Fase 9).

Solo la sesion de base de datos por request. La API NO reimplementa nada
de `analysis/`: los servicios llaman a esos modulos o consultan las tablas
que esos modulos ya poblaron.
"""

from __future__ import annotations

from collections.abc import Iterator

from sqlalchemy import select
from sqlalchemy.orm import Session

from db.database import SessionLocal
from db.models import Season

# Fecha de referencia para calcular edades. La temporada 2024/25 de LaLiga
# terminó el 2025-05-25 (ver loaders/etl_laliga.py). Se usa el fin de
# temporada, no "hoy", para que la edad sea la que el jugador tenía en la
# temporada analizada.
AGE_REFERENCE_DATE = "2025-05-25"


def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_season_id(db: Session) -> int | None:
    """El id de la única temporada cargada. Todos los datos derivados
    (percentiles, role scores, similarity, team style) son de una sola
    temporada; si algún día hay más, esto pasará a ser un query param."""
    return db.scalar(select(Season.id).order_by(Season.id))
