"""Schemas Pydantic para /scouting."""

from __future__ import annotations

from pydantic import BaseModel, Field


class TacticalFitRequest(BaseModel):
    team_id: int
    role_id: int
    formation: str | None = Field(
        None,
        description="formación concreta del equipo (ej '4-3-3'). Si se omite, se usa el agregado del equipo. "
        "Si se pasa una formación sin muestra suficiente (>= 5 partidos), la respuesta es 422 con la lista "
        "de formaciones disponibles.",
    )


class TacticalFitBreakdownItem(BaseModel):
    style_axis: str
    direction: str
    team_percentile: float = Field(description="percentil bruto del equipo en ese eje")
    team_raw_value: float
    effective_percentile: float = Field(description="team_percentile, o 100-team_percentile si direction=negative")
    weight: float
    contribution: float = Field(description="effective_percentile * weight")


class TacticalFitRankingItem(BaseModel):
    player_id: int
    player_name: str
    position_bucket: str
    role_score: float = Field(description="Player Role Score del jugador en el rol (Fase 5), 0-100")
    style_component: float = Field(description="compatibilidad del jugador-rol con el estilo del equipo, 0-100")
    score: float = Field(description="tactical_fit = w_role*role_score + w_style*style_component, 0-100")
    breakdown: list[TacticalFitBreakdownItem]


class TacticalFitResponse(BaseModel):
    team_id: int
    team_name: str
    season: str
    competition: str
    role_id: int
    role_code: str
    role_label: str
    formation: str | None = Field(description="null = se usó el agregado del equipo")
    n_matches: int | None = Field(description="partidos que sostienen el perfil de estilo usado")
    team_narrative: str = Field(description="descripción del estilo del equipo por reglas (Fase 11), sin LLM")
    w_role: float
    w_style: float
    count: int
    ranking: list[TacticalFitRankingItem] = Field(description="ordenado por score descendente")
