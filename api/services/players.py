"""Servicio de /players.

Consulta las tablas que los módulos de `analysis/` ya poblaron
(`player_percentiles`, `player_similarity`, `player_role_scores`,
`player_role_score_breakdown`). NO recalcula nada.

Fase 12a: todo scoped por temporada. `season` (un objeto Season) llega
resuelto desde la dependency `resolve_season`.
"""

from __future__ import annotations

import datetime

from fastapi import HTTPException
from sqlalchemy import Integer, cast, func, literal, select
from sqlalchemy.orm import Session, aliased

from analysis.narrative import player_role_summary, team_style_narrative
from analysis.tactical_fit import tactical_fit
from api.dependencies import CROSS_COMPETITION_WARNING, sibling_season_ids
from db.models import (
    Player,
    PlayerPercentile,
    PlayerRoleScore,
    PlayerRoleScoreBreakdown,
    PlayerSimilarity,
    PlayerStatistic,
    PlayerTeamSeason,
    Position,
    Role,
    Season,
    StatType,
    Team,
    TeamStyleAxis,
)

# umbral con el que analysis/percentiles.py y role_scores.py se ejecutaron.
PERCENTILE_MIN_MINUTES = 900


def _age_ref(season: Season) -> datetime.date:
    return season.end_date or datetime.date(2025, 5, 31)


def _age_of(birth_date: datetime.date | None, ref: datetime.date) -> int | None:
    if birth_date is None:
        return None
    return ref.year - birth_date.year - ((ref.month, ref.day) < (birth_date.month, birth_date.day))


def _age_expr(col, ref: datetime.date):
    return cast(func.date_part("year", func.age(literal(ref), col)), Integer)


def _minutes_subq(season_id: int):
    """minutos totales del jugador EN ESTA TEMPORADA."""
    return (
        select(
            PlayerTeamSeason.player_id.label("player_id"),
            func.coalesce(func.sum(PlayerStatistic.value), 0).label("minutes"),
        )
        .join(PlayerStatistic, PlayerStatistic.player_team_season_id == PlayerTeamSeason.id)
        .join(StatType, StatType.id == PlayerStatistic.stat_type_id)
        .where(StatType.code == "minutes-played", PlayerTeamSeason.season_id == season_id)
        .group_by(PlayerTeamSeason.player_id)
        .subquery()
    )


def _latest_team_subq(season_id: int):
    """equipo del jugador EN ESTA TEMPORADA (etapa con mayor order_in_season)."""
    return (
        select(
            PlayerTeamSeason.player_id.label("player_id"),
            Team.id.label("team_id"),
            Team.name.label("team_name"),
            func.row_number()
            .over(
                partition_by=PlayerTeamSeason.player_id,
                order_by=PlayerTeamSeason.order_in_season.desc(),
            )
            .label("rn"),
        )
        .join(Team, Team.id == PlayerTeamSeason.team_id)
        .where(PlayerTeamSeason.season_id == season_id)
        .subquery()
    )


def _base_player_select(season_id: int):
    latest = _latest_team_subq(season_id)
    minutes = _minutes_subq(season_id)
    sel = (
        select(
            Player,
            Position.bucket.label("bucket"),
            Position.lado.label("side"),
            Position.label.label("position_label"),
            latest.c.team_id,
            latest.c.team_name,
            func.coalesce(minutes.c.minutes, 0).label("minutes"),
        )
        .outerjoin(Position, Position.id == Player.primary_position_id)
        .outerjoin(minutes, minutes.c.player_id == Player.id)
        .outerjoin(latest, (latest.c.player_id == Player.id) & (latest.c.rn == 1))
    )
    return sel, latest, minutes


def list_players(
    db: Session,
    season: Season,
    *,
    bucket: str | None = None,
    team_id: int | None = None,
    min_minutes: int = 900,
    age_min: int | None = None,
    age_max: int | None = None,
    side: str | None = None,
    offset: int = 0,
    limit: int = 50,
) -> dict:
    ref = _age_ref(season)
    base, latest, minutes = _base_player_select(season.id)
    age_col = _age_expr(Player.birth_date, ref)

    filters = [func.coalesce(minutes.c.minutes, 0) >= min_minutes]
    # solo jugadores con etapa en esta temporada
    filters.append(minutes.c.player_id.isnot(None))
    if bucket is not None:
        filters.append(Position.bucket == bucket)
    if side is not None:
        filters.append(Position.lado == side)
    if team_id is not None:
        filters.append(latest.c.team_id == team_id)
    if age_min is not None:
        filters.append(age_col >= age_min)
    if age_max is not None:
        filters.append(age_col <= age_max)

    count_q = (
        select(func.count())
        .select_from(Player)
        .outerjoin(Position, Position.id == Player.primary_position_id)
        .outerjoin(minutes, minutes.c.player_id == Player.id)
        .outerjoin(latest, (latest.c.player_id == Player.id) & (latest.c.rn == 1))
        .where(*filters)
    )
    total_count = db.scalar(count_q) or 0

    rows = db.execute(
        base.where(*filters)
        .order_by(func.coalesce(minutes.c.minutes, 0).desc(), Player.name)
        .offset(offset)
        .limit(limit)
    ).all()

    items = [
        {
            "id": r[0].id,
            "name": r[0].name,
            "bucket": r.bucket,
            "side": r.side,
            "position_label": r.position_label,
            "team_id": r.team_id,
            "team_name": r.team_name,
            "age": _age_of(r[0].birth_date, ref),
            "minutes": int(r.minutes),
            "birth_date": r[0].birth_date,
            "nationality": r[0].nationality,
            "height_cm": r[0].height_cm,
            "preferred_foot": r[0].preferred_foot,
            "photo_url": r[0].photo_url,
        }
        for r in rows
    ]
    return {"total_count": total_count, "offset": offset, "limit": limit, "items": items}


def _load_player_row(db: Session, season: Season, player_id: int):
    base, _, _ = _base_player_select(season.id)
    row = db.execute(base.where(Player.id == player_id)).first()
    if row is None:
        raise HTTPException(status_code=404, detail=f"Jugador {player_id} no encontrado")
    return row


def get_player_profile(db: Session, season: Season, player_id: int) -> dict:
    ref = _age_ref(season)
    row = _load_player_row(db, season, player_id)
    p: Player = row[0]

    pctls = db.execute(
        select(
            StatType.code, StatType.label, StatType.category,
            PlayerPercentile.metric_value, PlayerPercentile.percentile, PlayerPercentile.pool_size,
        )
        .join(StatType, StatType.id == PlayerPercentile.stat_type_id)
        .where(PlayerPercentile.player_id == player_id, PlayerPercentile.season_id == season.id)
        .order_by(StatType.category, StatType.code)
    ).all()

    return {
        "id": p.id, "name": p.name, "bucket": row.bucket, "side": row.side,
        "season": season.name, "competition": season.competition.name,
        "position_label": row.position_label, "team_id": row.team_id, "team_name": row.team_name,
        "age": _age_of(p.birth_date, ref), "birth_date": p.birth_date, "nationality": p.nationality,
        "height_cm": p.height_cm, "weight_kg": p.weight_kg, "preferred_foot": p.preferred_foot,
        "photo_url": p.photo_url, "minutes": int(row.minutes),
        "min_minutes_threshold": PERCENTILE_MIN_MINUTES,
        "summary": player_role_summary(db, player_id, season_id=season.id),
        "percentiles": [
            {
                "stat_type_code": c.code, "stat_type_label": c.label, "category": c.category,
                "metric_value": float(c.metric_value), "percentile": float(c.percentile),
                "pool_size": c.pool_size,
            }
            for c in pctls
        ],
    }


def get_similar_players(
    db: Session, season: Season, player_id: int, *, age_max: int | None = None, side: str | None = None
) -> dict:
    ref = _age_ref(season)
    row = _load_player_row(db, season, player_id)
    p: Player = row[0]

    sp = aliased(Player)
    latest = _latest_team_subq(season.id)
    q = (
        select(
            PlayerSimilarity.rank, PlayerSimilarity.similar_player_id, PlayerSimilarity.similarity_score,
            sp.name.label("name"), sp.birth_date.label("birth_date"),
            Position.bucket, Position.lado, Team.name.label("team_name"),
        )
        .join(sp, sp.id == PlayerSimilarity.similar_player_id)
        .outerjoin(Position, Position.id == sp.primary_position_id)
        .outerjoin(latest, (latest.c.player_id == sp.id) & (latest.c.rn == 1))
        .outerjoin(Team, Team.id == latest.c.team_id)
        .where(PlayerSimilarity.player_id == player_id, PlayerSimilarity.season_id == season.id)
        .order_by(PlayerSimilarity.rank)
    )
    if side is not None:
        q = q.where(Position.lado == side)
    if age_max is not None:
        q = q.where(_age_expr(sp.birth_date, ref) <= age_max)

    rows = db.execute(q).all()
    items = [
        {
            "rank": r.rank, "similar_player_id": r.similar_player_id, "name": r.name,
            "bucket": r.bucket, "side": r.lado, "age": _age_of(r.birth_date, ref),
            "team_name": r.team_name, "similarity_score": float(r.similarity_score),
        }
        for r in rows
    ]

    total = db.scalar(
        select(func.count()).where(
            PlayerSimilarity.player_id == player_id, PlayerSimilarity.season_id == season.id
        )
    )
    note = (
        f"Este jugador no tiene similares en {season.name}: no llegó al umbral de "
        f"{PERCENTILE_MIN_MINUTES} minutos, o no jugó esa temporada."
        if total == 0
        else "Top-20 ya calculado (cosine sobre percentiles del bucket). Los filtros de edad/lado "
        "se aplican sobre ese top-20; los rank conservan su número original. La similitud no cambia."
    )
    return {
        "player_id": p.id, "player_name": p.name, "bucket": row.bucket,
        "filters_applied": {"age_max": age_max, "side": side},
        "note": note, "items": items,
    }


def get_player_roles(db: Session, season: Season, player_id: int) -> dict:
    row = _load_player_row(db, season, player_id)
    p: Player = row[0]

    scores = db.execute(
        select(
            PlayerRoleScore.id, PlayerRoleScore.role_id, Role.code, Role.label,
            PlayerRoleScore.position_bucket, PlayerRoleScore.score,
            PlayerRoleScore.total_weight, PlayerRoleScore.metrics_used,
        )
        .join(Role, Role.id == PlayerRoleScore.role_id)
        .where(PlayerRoleScore.player_id == player_id, PlayerRoleScore.season_id == season.id)
        .order_by(PlayerRoleScore.score.desc())
    ).all()

    breakdowns: dict[int, list] = {}
    if scores:
        for b in db.execute(
            select(
                PlayerRoleScoreBreakdown.player_role_score_id, StatType.code, StatType.label,
                PlayerRoleScoreBreakdown.tier, PlayerRoleScoreBreakdown.percentile,
                PlayerRoleScoreBreakdown.weight, PlayerRoleScoreBreakdown.contribution,
            )
            .join(StatType, StatType.id == PlayerRoleScoreBreakdown.stat_type_id)
            .where(PlayerRoleScoreBreakdown.player_role_score_id.in_([s.id for s in scores]))
            .order_by(PlayerRoleScoreBreakdown.contribution.desc())
        ).all():
            breakdowns.setdefault(b.player_role_score_id, []).append(
                {
                    "stat_type_code": b.code, "stat_type_label": b.label, "tier": b.tier,
                    "percentile": float(b.percentile), "weight": float(b.weight),
                    "contribution": float(b.contribution),
                }
            )

    items = [
        {
            "role_id": s.role_id, "role_code": s.code, "role_label": s.label,
            "position_bucket": s.position_bucket, "score": float(s.score),
            "total_weight": float(s.total_weight), "metrics_used": s.metrics_used,
            "breakdown": breakdowns.get(s.id, []),
        }
        for s in scores
    ]
    note = (
        "Sin role scores: no llega al umbral de minutos, o su bucket (delantero/portero) no "
        "tiene ninguno de los 4 roles construibles plenos."
        if not items
        else "Role scores en los roles que aplican a su bucket, con desglose por métrica."
    )
    return {"player_id": p.id, "player_name": p.name, "bucket": row.bucket, "note": note, "items": items}


# ---------------------------------------------------------------------------
# Fase 11 - Tactical Fit invertido (Fase 12a: scoped por temporada)
# ---------------------------------------------------------------------------

def _team_narratives(db: Session, season_ids: list[int]):
    rows = db.execute(
        select(TeamStyleAxis.team_id, Team.name, TeamStyleAxis.style_axis, TeamStyleAxis.percentile)
        .join(Team, Team.id == TeamStyleAxis.team_id)
        .where(TeamStyleAxis.formation.is_(None), TeamStyleAxis.season_id.in_(season_ids))
    ).all()
    by_team, names = {}, {}
    for r in rows:
        by_team.setdefault(r.team_id, []).append(
            {"style_axis": r.style_axis, "percentile": float(r.percentile)}
        )
        names[r.team_id] = r.name
    return {tid: team_style_narrative(axes, names[tid]) for tid, axes in by_team.items()}


def get_best_teams(
    db: Session, season: Season, player_id: int, *,
    role_id: int | None = None, cross_competition: bool = False,
) -> dict:
    p: Player = _load_player_row(db, season, player_id)[0]

    scored = db.execute(
        select(PlayerRoleScore.role_id, Role.code, Role.label, PlayerRoleScore.score)
        .join(Role, Role.id == PlayerRoleScore.role_id)
        .where(PlayerRoleScore.player_id == player_id, PlayerRoleScore.season_id == season.id)
        .order_by(PlayerRoleScore.score.desc())
    ).all()

    if not scored:
        return {
            "player_id": p.id, "player_name": p.name,
            "season": season.name, "competition": season.competition.name,
            "role_id": None, "role_code": None,
            "role_label": None, "role_score": None, "available_roles": [],
            "cross_competition": cross_competition, "warning": None,
            "note": f"Sin role score en {season.competition.name} {season.name}: posición fuera de "
            "los 4 roles, umbral de minutos no alcanzado, o no jugó esa temporada.",
            "count": 0, "ranking": [],
        }

    available = [
        {"role_id": s.role_id, "role_code": s.code, "role_label": s.label, "score": float(s.score)}
        for s in scored
    ]
    if role_id is not None:
        chosen = next((s for s in scored if s.role_id == role_id), None)
        if chosen is None:
            raise HTTPException(
                status_code=422,
                detail=f"El jugador {player_id} no tiene score en el rol {role_id} en {season.name}. "
                f"Roles con score: {[a['role_id'] for a in available]}.",
            )
    else:
        chosen = scored[0]

    # el role_score del jugador sale de SU temporada; los equipos pueden ser
    # de todas las competiciones del mismo año si cross_competition.
    team_season_ids = sibling_season_ids(db, season) if cross_competition else [season.id]
    results, w_role, w_style = tactical_fit(
        db, player_id=player_id, role_code=chosen.code, by_formation=False,
        player_season_ids=[season.id], team_season_ids=team_season_ids,
    )
    narratives = _team_narratives(db, team_season_ids)
    ranking = [
        {
            "team_id": r["team_id"], "team_name": r["team_name"],
            "competition": r["team_competition"], "n_matches": r["n_matches"],
            "role_score": r["role_score"], "style_component": r["style_component"], "score": r["score"],
            "team_narrative": narratives.get(r["team_id"], ""), "breakdown": r["breakdown"],
        }
        for r in results
    ]
    note = (
        f"Encaje del jugador ({season.competition.name} {season.name}) en cada equipo de "
        f"{season.competition.name} ({season.name}) con su rol. role_score fijo; lo que cambia el "
        "orden es el estilo del equipo."
    )
    if cross_competition:
        note = (
            f"Encaje del jugador ({season.competition.name} {season.name}) en equipos de las "
            "5 competiciones. role_score fijo; lo que cambia el orden es el estilo del equipo."
        )
    return {
        "player_id": p.id, "player_name": p.name,
        "season": season.name, "competition": season.competition.name,
        "role_id": chosen.role_id, "role_code": chosen.code,
        "role_label": chosen.label, "role_score": float(chosen.score), "available_roles": available,
        "w_role": w_role, "w_style": w_style,
        "cross_competition": cross_competition,
        "warning": CROSS_COMPETITION_WARNING if cross_competition else None,
        "note": note,
        "count": len(ranking), "ranking": ranking,
    }
