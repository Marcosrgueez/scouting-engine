"""Servicio de /scouting.

/scouting/tactical-fit llama a `analysis.tactical_fit.tactical_fit()` de la
Fase 8 — se calcula EN VIVO por request (función parametrizada), no se
precalcula ni se cachea.
"""

from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from analysis.narrative import team_style_narrative
from analysis.tactical_fit import DEFAULT_W_ROLE, DEFAULT_W_STYLE, tactical_fit
from db.models import Role, Season, Team, TeamStyleAxis


def _available_formations(db: Session, team_id: int, season_id: int) -> list[str]:
    rows = db.execute(
        select(TeamStyleAxis.formation)
        .where(
            TeamStyleAxis.team_id == team_id,
            TeamStyleAxis.season_id == season_id,
            TeamStyleAxis.formation.isnot(None),
        )
        .distinct()
        .order_by(TeamStyleAxis.formation)
    ).scalars().all()
    return list(rows)


def tactical_fit_ranking(
    db: Session, season: Season, *, team_id: int, role_id: int, formation: str | None
) -> dict:
    team = db.get(Team, team_id)
    if team is None:
        raise HTTPException(status_code=404, detail=f"Equipo {team_id} no encontrado")

    role = db.get(Role, role_id)
    if role is None:
        raise HTTPException(status_code=404, detail=f"Rol {role_id} no encontrado")

    has_aggregate = db.scalar(
        select(TeamStyleAxis.id)
        .where(
            TeamStyleAxis.team_id == team_id,
            TeamStyleAxis.season_id == season.id,
            TeamStyleAxis.formation.is_(None),
        )
        .limit(1)
    )
    if has_aggregate is None:
        raise HTTPException(
            status_code=422,
            detail=f"El equipo '{team.name}' no tiene perfil de estilo en {season.name} "
            "(¿jugó esa temporada?).",
        )

    if formation is not None:
        exists = db.scalar(
            select(TeamStyleAxis.id)
            .where(
                TeamStyleAxis.team_id == team_id,
                TeamStyleAxis.season_id == season.id,
                TeamStyleAxis.formation == formation,
            )
            .limit(1)
        )
        if exists is None:
            avail = _available_formations(db, team_id, season.id)
            raise HTTPException(
                status_code=422,
                detail=(
                    f"La formación '{formation}' de '{team.name}' no tiene muestra suficiente "
                    f"en {season.name} (mínimo 5 partidos). Formaciones con perfil: "
                    f"{avail or 'ninguna'}. Omite 'formation' para usar el agregado."
                ),
            )

    results, w_role, w_style = tactical_fit(
        db,
        team_id=team_id,
        role_code=role.code,
        formation=formation,
        by_formation=False,
        w_role=DEFAULT_W_ROLE,
        w_style=DEFAULT_W_STYLE,
        season_id=season.id,
    )

    style_axes = db.execute(
        select(TeamStyleAxis.style_axis, TeamStyleAxis.percentile).where(
            TeamStyleAxis.team_id == team_id,
            TeamStyleAxis.season_id == season.id,
            TeamStyleAxis.formation == formation
            if formation is not None
            else TeamStyleAxis.formation.is_(None),
        )
    ).all()
    team_narrative = team_style_narrative(
        [{"style_axis": a.style_axis, "percentile": float(a.percentile)} for a in style_axes],
        team.name,
    )

    n_matches = results[0]["n_matches"] if results else None
    ranking = [
        {
            "player_id": r["player_id"],
            "player_name": r["player_name"],
            "position_bucket": r["position_bucket"],
            "role_score": r["role_score"],
            "style_component": r["style_component"],
            "score": r["score"],
            "breakdown": r["breakdown"],
        }
        for r in results
    ]

    return {
        "team_id": team.id,
        "team_name": team.name,
        "season": season.name,
        "role_id": role.id,
        "role_code": role.code,
        "role_label": role.label,
        "formation": formation,
        "n_matches": n_matches,
        "team_narrative": team_narrative,
        "w_role": w_role,
        "w_style": w_style,
        "count": len(ranking),
        "ranking": ranking,
    }
