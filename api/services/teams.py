"""Servicio de /teams.

/teams/{id}/style consulta `team_style_axes` (poblada por
analysis/team_style.py) y `team_fixtures` (grano crudo de la Fase 7, cuya
agregación por formación se hace por consulta).

Fase 12a: scoped por temporada.
"""

from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from analysis.narrative import team_style_narrative
from db.models import Season, Team, TeamFixture, TeamStyleAxis

# umbral de partidos por formación de la Fase 7.
STYLE_MIN_MATCHES = 5


def list_teams(db: Session, season: Season) -> dict:
    """Equipos que jugaron esa temporada (los que tienen team_fixtures)."""
    played = select(TeamFixture.team_id).where(TeamFixture.season_id == season.id).distinct().subquery()
    rows = db.execute(
        select(Team).join(played, played.c.team_id == Team.id).order_by(Team.name)
    ).scalars().all()
    return {
        "season": season.name,
        "competition": season.competition.name,
        "items": [
            {"id": t.id, "name": t.name, "country": t.country, "sportmonks_team_id": t.sportmonks_team_id}
            for t in rows
        ],
    }


def get_team_style(db: Session, season: Season, team_id: int) -> dict:
    team = db.get(Team, team_id)
    if team is None:
        raise HTTPException(status_code=404, detail=f"Equipo {team_id} no encontrado")

    axis_rows = db.execute(
        select(
            TeamStyleAxis.formation, TeamStyleAxis.style_axis,
            TeamStyleAxis.raw_value, TeamStyleAxis.percentile, TeamStyleAxis.n_matches,
        )
        .where(TeamStyleAxis.team_id == team_id, TeamStyleAxis.season_id == season.id)
        .order_by(TeamStyleAxis.formation.nulls_first(), TeamStyleAxis.style_axis)
    ).all()

    profiles: dict[str | None, dict] = {}
    for r in axis_rows:
        prof = profiles.setdefault(r.formation, {"formation": r.formation, "n_matches": r.n_matches, "axes": []})
        prof["axes"].append(
            {"style_axis": r.style_axis, "raw_value": float(r.raw_value), "percentile": float(r.percentile)}
        )

    aggregate = profiles.pop(None, None)
    if aggregate is None:
        raise HTTPException(
            status_code=404,
            detail=f"El equipo '{team.name}' no tiene perfil de estilo en {season.name} "
            "(¿jugó esa temporada? ¿corrió analysis/team_style.py?).",
        )
    by_formation = sorted(profiles.values(), key=lambda p: -p["n_matches"])

    materialized = {p["formation"] for p in by_formation}
    below = db.execute(
        select(TeamFixture.formation, func.count().label("n"))
        .where(TeamFixture.team_id == team_id, TeamFixture.season_id == season.id)
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
        "season": season.name,
        "competition": season.competition.name,
        "min_matches": STYLE_MIN_MATCHES,
        "narrative": team_style_narrative(aggregate["axes"], team.name),
        "aggregate": aggregate,
        "by_formation": by_formation,
        "formations_below_threshold": formations_below,
    }
