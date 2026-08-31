"""Servicio de /teams.

/teams/{id}/style consulta `team_style_axes` (poblada por
analysis/team_style.py) y `team_fixtures` (grano crudo de la Fase 7, cuya
agregación por formación se hace por consulta, tal como se diseñó).
"""

from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from db.models import Team, TeamFixture, TeamStyleAxis

# umbral de partidos por formación de la Fase 7.
STYLE_MIN_MATCHES = 5


def list_teams(db: Session) -> dict:
    rows = db.execute(select(Team).order_by(Team.name)).scalars().all()
    return {
        "items": [
            {
                "id": t.id,
                "name": t.name,
                "country": t.country,
                "sportmonks_team_id": t.sportmonks_team_id,
            }
            for t in rows
        ]
    }


def get_team_style(db: Session, team_id: int) -> dict:
    team = db.get(Team, team_id)
    if team is None:
        raise HTTPException(status_code=404, detail=f"Equipo {team_id} no encontrado")

    axis_rows = db.execute(
        select(
            TeamStyleAxis.formation,
            TeamStyleAxis.style_axis,
            TeamStyleAxis.raw_value,
            TeamStyleAxis.percentile,
            TeamStyleAxis.n_matches,
        )
        .where(TeamStyleAxis.team_id == team_id)
        .order_by(TeamStyleAxis.formation.nulls_first(), TeamStyleAxis.style_axis)
    ).all()

    # agrupa por formación (None = agregado)
    profiles: dict[str | None, dict] = {}
    for r in axis_rows:
        prof = profiles.setdefault(r.formation, {"formation": r.formation, "n_matches": r.n_matches, "axes": []})
        prof["axes"].append(
            {
                "style_axis": r.style_axis,
                "raw_value": float(r.raw_value),
                "percentile": float(r.percentile),
            }
        )

    aggregate = profiles.pop(None, None)
    if aggregate is None:
        # no debería pasar si la Fase 7/8 corrió; lo tratamos como dato ausente
        raise HTTPException(
            status_code=404,
            detail=f"El equipo {team_id} no tiene perfil de estilo calculado (¿corrió analysis/team_style.py?)",
        )
    by_formation = sorted(profiles.values(), key=lambda p: -p["n_matches"])

    # formaciones que el equipo usó pero que NO llegaron al umbral -> nunca
    # se materializaron en team_style_axes. Se listan aparte (nombre + nº),
    # sin ejes de estilo.
    materialized = {p["formation"] for p in by_formation}
    below = db.execute(
        select(TeamFixture.formation, func.count().label("n"))
        .where(TeamFixture.team_id == team_id)
        .group_by(TeamFixture.formation)
        .having(func.count() < STYLE_MIN_MATCHES)
        .order_by(func.count().desc())
    ).all()
    formations_below = [
        {"formation": b.formation, "n_matches": b.n}
        for b in below
        if b.formation not in materialized
    ]

    return {
        "team_id": team.id,
        "team_name": team.name,
        "min_matches": STYLE_MIN_MATCHES,
        "aggregate": aggregate,
        "by_formation": by_formation,
        "formations_below_threshold": formations_below,
    }
