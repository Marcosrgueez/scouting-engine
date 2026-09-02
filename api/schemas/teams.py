"""Schemas Pydantic para /teams."""

from __future__ import annotations

from pydantic import BaseModel, Field


class TeamListItem(BaseModel):
    id: int
    name: str
    country: str | None = None
    sportmonks_team_id: int


class TeamListResponse(BaseModel):
    season: str
    competition: str
    items: list[TeamListItem]


class StyleAxisItem(BaseModel):
    style_axis: str = Field(description="possession/pass_accuracy/crossing_frequency/press_intensity/directness")
    raw_value: float = Field(description="valor bruto del eje (posesión media %, centros/partido, ratio*100...)")
    percentile: float = Field(description="0-100 entre los equipos de esa competición y temporada (pool = agregados de equipo)")


class TeamStyleProfile(BaseModel):
    formation: str | None = Field(description="null = agregado de todos los partidos del equipo")
    n_matches: int
    axes: list[StyleAxisItem]


class FormationBelowThreshold(BaseModel):
    formation: str | None
    n_matches: int


class TeamStyleResponse(BaseModel):
    team_id: int
    team_name: str
    season: str
    competition: str
    min_matches: int = Field(description="umbral de partidos por formación (Fase 7); por debajo no hay perfil de estilo")
    narrative: str = Field(description="descripción del estilo por reglas (Fase 11), sin LLM")
    aggregate: TeamStyleProfile
    by_formation: list[TeamStyleProfile] = Field(
        description="una por cada formación con >= min_matches partidos"
    )
    formations_below_threshold: list[FormationBelowThreshold] = Field(
        description="formaciones que el equipo usó pero sin muestra suficiente: nombre y nº de partidos, "
        "sin ejes de estilo (nunca se materializaron en team_style_axes)"
    )
