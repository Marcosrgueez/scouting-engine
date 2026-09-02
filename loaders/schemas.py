"""Modelos Pydantic para el JSON YA DESCARGADO de Sportmonks.

Doble funcion:
  1. validar que cada archivo tiene la forma esperada antes de mapearlo a
     SQLAlchemy (si no valida -> se registra y se salta, no tumba el ETL),
  2. ser el primer borrador del mapper JSON externo -> esquema interno.

Fuentes:
  - raw_data/sportmonks/player_stats/{id}.json  -> PlayerStatsFile
  - raw_data/sportmonks/positions_map.json      -> PositionMeta (por jugador)
  - raw_data/sportmonks/teams.json              -> TeamRaw
  - raw_data/sportmonks/context.json            -> Context
"""

from __future__ import annotations

import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

_LENIENT = ConfigDict(extra="ignore", str_strip_whitespace=True)


class Context(BaseModel):
    model_config = _LENIENT
    league_id: int
    league_name: str = "La Liga"
    tier: Optional[int] = None  # 1 = Primera, 2 = Segunda (Fase 12b). scripts/10 lo trae.
    country: Optional[str] = None  # Fase 13: país de la competición. scripts/10 lo trae.
    season_id: int
    season_name: str = ""
    # Fase 12a: fechas de la temporada (las trae scripts/10). El context
    # plano de 2024/25 no las tiene -> el ETL usa un fallback.
    start_date: Optional[datetime.date] = None
    end_date: Optional[datetime.date] = None


class TeamRaw(BaseModel):
    model_config = _LENIENT
    id: int
    name: str
    country_id: Optional[int] = None
    short_code: Optional[str] = None


class PositionMeta(BaseModel):
    model_config = _LENIENT
    bucket: Optional[str] = None
    lado: Optional[str] = None
    detailed_position_id: Optional[int] = None
    detailed_position_name: Optional[str] = None
    position_id: Optional[int] = None


class StatTypeRef(BaseModel):
    model_config = _LENIENT
    code: Optional[str] = None


class StatDetail(BaseModel):
    model_config = _LENIENT
    type: StatTypeRef
    # En Sportmonks SIEMPRE es un dict ({total: N} / {average: N} / ...).
    value: Any = None

    @property
    def code(self) -> Optional[str]:
        return self.type.code


class StatEntry(BaseModel):
    """Una etapa jugador-equipo dentro de la temporada."""
    model_config = _LENIENT
    team_id: int
    season_id: int
    has_values: bool = True
    details: list[StatDetail] = []


class PlayerProfile(BaseModel):
    model_config = _LENIENT
    id: int
    name: Optional[str] = None
    display_name: Optional[str] = None
    common_name: Optional[str] = None
    date_of_birth: Optional[datetime.date] = None
    nationality_id: Optional[int] = None
    height: Optional[int] = None
    weight: Optional[int] = None
    position_id: Optional[int] = None
    detailed_position_id: Optional[int] = None
    image_path: Optional[str] = None
    statistics: list[StatEntry] = []

    @field_validator("date_of_birth", mode="before")
    @classmethod
    def _parse_dob(cls, v):
        if v in (None, "", "0000-00-00"):
            return None
        if isinstance(v, datetime.date):
            return v
        try:
            return datetime.date.fromisoformat(str(v)[:10])
        except ValueError:
            return None  # fecha corrupta -> se pierde el dato, no invalida al jugador

    @model_validator(mode="after")
    def _has_a_name(self):
        if not (self.name or self.display_name or self.common_name):
            raise ValueError("jugador sin ningun nombre (name/display_name/common_name)")
        return self

    @property
    def best_name(self) -> str:
        return self.display_name or self.name or self.common_name or f"player-{self.id}"


class PlayerStatsFile(BaseModel):
    """El archivo raw_data/sportmonks/player_stats/{id}.json completo."""
    model_config = _LENIENT
    data: PlayerProfile
