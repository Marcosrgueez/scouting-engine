"""Schemas Pydantic de request/response para /players.

NO confundir con loaders/schemas.py, que valida el JSON crudo de
Sportmonks. Estos describen el contrato HTTP de la API.
"""

from __future__ import annotations

import datetime

from pydantic import BaseModel, Field


class PlayerListItem(BaseModel):
    id: int
    name: str
    bucket: str | None = Field(None, description="portero/central/lateral/centrocampista/extremo/delantero")
    side: str | None = Field(None, description="izquierda/derecha/centro/desconocido")
    position_label: str | None = None
    team_id: int | None = None
    team_name: str | None = None
    age: int | None = None
    minutes: int = Field(description="minutos totales en LaLiga 24/25 (suma de todas sus etapas)")
    birth_date: datetime.date | None = None
    nationality: str | None = None
    height_cm: int | None = None
    preferred_foot: str | None = Field(None, description="siempre null: Sportmonks no lo da en el include usado")
    photo_url: str | None = None


class PlayerListResponse(BaseModel):
    total_count: int
    offset: int
    limit: int
    items: list[PlayerListItem]


class PercentileItem(BaseModel):
    stat_type_code: str
    stat_type_label: str
    category: str
    metric_value: float = Field(description="valor per90 o raw que se ranqueó")
    percentile: float = Field(description="0-100, orientado: 100 = mejor de su bucket para esa métrica")
    pool_size: int


class RoleSummaryDriver(BaseModel):
    stat_type_code: str
    stat_type_label: str
    percentile: float
    contribution: float


class RoleSummary(BaseModel):
    text: str = Field(description="frase por plantilla fija (Fase 11), sin LLM")
    has_role: bool
    role_code: str | None = None
    role_label: str | None = None
    score: float | None = None
    drivers: list[RoleSummaryDriver] = Field(
        default_factory=list, description="métricas core que sostienen la frase"
    )


class PlayerProfile(BaseModel):
    id: int
    name: str
    bucket: str | None = None
    side: str | None = None
    position_label: str | None = None
    team_id: int | None = None
    team_name: str | None = None
    age: int | None = None
    birth_date: datetime.date | None = None
    nationality: str | None = None
    height_cm: int | None = None
    weight_kg: int | None = None
    preferred_foot: str | None = None
    photo_url: str | None = None
    minutes: int
    min_minutes_threshold: int = Field(
        description="umbral con el que se calcularon los percentiles (900). "
        "Si minutes < umbral, percentiles va vacío."
    )
    summary: RoleSummary
    percentiles: list[PercentileItem]


class SimilarPlayerItem(BaseModel):
    rank: int = Field(description="posición en el top-20 original del jugador; puede haber huecos si se filtró")
    similar_player_id: int
    name: str
    bucket: str | None = None
    side: str | None = None
    age: int | None = None
    team_name: str | None = None
    similarity_score: float = Field(description="cosine, 0-1")


class SimilarPlayersResponse(BaseModel):
    player_id: int
    player_name: str
    bucket: str | None = None
    filters_applied: dict[str, str | int | None]
    note: str
    items: list[SimilarPlayerItem]


class RoleScoreBreakdownItem(BaseModel):
    stat_type_code: str
    stat_type_label: str
    tier: str = Field(description="core/support/context (informativo)")
    percentile: float
    weight: float
    contribution: float = Field(description="percentile * weight")


class PlayerRoleScoreItem(BaseModel):
    role_id: int
    role_code: str
    role_label: str
    position_bucket: str
    score: float = Field(description="0-100")
    total_weight: float = Field(description="denominador efectivo; < peso total del rol si faltaban métricas")
    metrics_used: int
    breakdown: list[RoleScoreBreakdownItem]


class PlayerRolesResponse(BaseModel):
    player_id: int
    player_name: str
    bucket: str | None = None
    note: str
    items: list[PlayerRoleScoreItem]


# --- Fase 11: jugador -> mejores equipos (tactical fit invertido) ---

class BestTeamAxisItem(BaseModel):
    style_axis: str
    direction: str
    team_percentile: float
    team_raw_value: float
    effective_percentile: float
    weight: float
    contribution: float


class BestTeamItem(BaseModel):
    team_id: int
    team_name: str
    n_matches: int | None = None
    role_score: float
    style_component: float
    score: float = Field(description="tactical fit, 0-100")
    team_narrative: str = Field(description="descripción de estilo del equipo (Fase 11, por reglas)")
    breakdown: list[BestTeamAxisItem]


class RoleRef(BaseModel):
    role_id: int
    role_code: str
    role_label: str
    score: float


class BestTeamsResponse(BaseModel):
    player_id: int
    player_name: str
    role_id: int | None = None
    role_code: str | None = None
    role_label: str | None = None
    role_score: float | None = Field(None, description="fijo: el mismo para todos los equipos")
    available_roles: list[RoleRef] = Field(
        default_factory=list, description="roles con score; se puede forzar uno con ?role_id="
    )
    w_role: float | None = None
    w_style: float | None = None
    note: str
    count: int
    ranking: list[BestTeamItem] = Field(description="ordenado por score descendente")
