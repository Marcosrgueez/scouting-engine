"""Schemas Pydantic para /roles."""

from __future__ import annotations

from pydantic import BaseModel, Field


class RoleWeightItem(BaseModel):
    stat_type_code: str
    stat_type_label: str
    tier: str = Field(description="core (peso 3) / support (1.5) / context (0.5)")
    weight: float


class RoleStyleWeightItem(BaseModel):
    style_axis: str
    weight: float
    direction: str = Field(description="positive = percentil alto ayuda; negative = percentil alto perjudica (se usa 100-percentil)")


class RoleDefinition(BaseModel):
    id: int
    code: str
    label: str
    buckets: list[str] = Field(description="buckets de posición a los que aplica el rol")
    metric_weights: list[RoleWeightItem] = Field(
        description="pesos por métrica del Player Role Score (Fase 5)"
    )
    style_weights: list[RoleStyleWeightItem] = Field(
        description="matriz rol->eje de estilo del Tactical Fit (Fase 8)"
    )


class RolesResponse(BaseModel):
    items: list[RoleDefinition]
