"""Fase 11 - resúmenes narrativos por REGLAS (sin LLM).

Coherente con el resto del proyecto: plantillas fijas, deterministas y
auditables. Nada de generación con IA.

  - player_role_summary(session, player_id): frase de "qué es" un jugador,
    a partir de su mejor role score y las métricas core que más contribuyen.
  - team_style_narrative(axes, team_name): frase de estilo de un equipo, a
    partir de los ejes de team_style_axes más extremos.

El entrenador NO entra: la investigación de la Fase 11 (ver
data-experiment/docs/fase11_coach_investigation.md) concluyó que las fechas
de tenencia de Sportmonks no son fiables para fijar el entrenador de una
temporada pasada. La narrativa de equipo usa solo el nombre del equipo.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models import (
    Player,
    PlayerRoleScore,
    PlayerRoleScoreBreakdown,
    Role,
    StatType,
)

NO_ROLE_TEXT = (
    "Sin rol táctico definido — posición fuera del alcance actual de roles "
    "(delantero o portero), o minutos insuficientes en la temporada."
)

# nº de métricas core a citar en el resumen de jugador
_TOP_CORE = 3
_MIN_CORE = 2


def player_role_summary(session: Session, player_id: int, *, season_id: int | None = None) -> dict:
    """Devuelve {text, has_role, role_code?, role_label?, score?, drivers?}.

    drivers = [{stat_type_code, stat_type_label, percentile, contribution}]
    season_id: si se da, solo mira los role scores de esa temporada.
    """
    q = (
        select(
            PlayerRoleScore.id,
            PlayerRoleScore.role_id,
            Role.code,
            Role.label,
            PlayerRoleScore.score,
            Player.name,
        )
        .join(Role, Role.id == PlayerRoleScore.role_id)
        .join(Player, Player.id == PlayerRoleScore.player_id)
        .where(PlayerRoleScore.player_id == player_id)
        .order_by(PlayerRoleScore.score.desc())
        .limit(1)
    )
    if season_id is not None:
        q = q.where(PlayerRoleScore.season_id == season_id)
    top = session.execute(q).first()

    if top is None:
        return {"text": NO_ROLE_TEXT, "has_role": False}

    core = session.execute(
        select(
            StatType.code,
            StatType.label,
            PlayerRoleScoreBreakdown.percentile,
            PlayerRoleScoreBreakdown.contribution,
        )
        .join(StatType, StatType.id == PlayerRoleScoreBreakdown.stat_type_id)
        .where(
            PlayerRoleScoreBreakdown.player_role_score_id == top.id,
            PlayerRoleScoreBreakdown.tier == "core",
        )
        .order_by(PlayerRoleScoreBreakdown.contribution.desc())
    ).all()

    drivers = [
        {
            "stat_type_code": c.code,
            "stat_type_label": c.label,
            "percentile": float(c.percentile),
            "contribution": float(c.contribution),
        }
        for c in core[:_TOP_CORE]
    ]

    score = float(top.score)
    if len(drivers) >= _MIN_CORE:
        parts = [f"{d['stat_type_label']} (percentil {d['percentile']:.0f})" for d in drivers]
        if len(parts) == 2:
            frag = f"{parts[0]} y {parts[1]}"
        else:
            frag = ", ".join(parts[:-1]) + f" y {parts[-1]}"
        text = (
            f"{top.name} se perfila como {top.label} (score {score:.1f}): "
            f"destaca en {frag}."
        )
    else:
        text = f"{top.name} se perfila como {top.label} (score {score:.1f})."

    return {
        "text": text,
        "has_role": True,
        "role_code": top.code,
        "role_label": top.label,
        "score": round(score, 2),
        "drivers": drivers,
    }


# --- estilo de equipo -----------------------------------------------------

# umbral de percentil para mencionar un eje
_HIGH = 70
_LOW = 30

# (eje) -> (frase si percentil ALTO, frase si percentil BAJO)
_AXIS_PHRASES = {
    "possession": ("domina la posesión", "juega la mayor parte del tiempo sin balón"),
    "pass_accuracy": ("circula el balón con mucha precisión", "tiene poca precisión de pase"),
    "crossing_frequency": ("ataca sobre todo por bandas, con muchos centros", "apenas centra al área"),
    "press_intensity": (
        "es muy activo en acciones defensivas (entradas e intercepciones)",
        "hace pocas acciones defensivas",
    ),
    "directness": ("juega directo, con mucho balón largo", "elabora desde atrás, con poco balón largo"),
}
# orden fijo para que empates de "distancia a 50" queden estables
_AXIS_ORDER = ["possession", "pass_accuracy", "directness", "press_intensity", "crossing_frequency"]


def team_style_narrative(axes, team_name: str) -> str:
    """axes: iterable de dicts/objetos con .style_axis y .percentile.
    Combina los 1-2 ejes más alejados del percentil 50."""
    vals = {}
    for a in axes:
        axis = a["style_axis"] if isinstance(a, dict) else a.style_axis
        pct = float(a["percentile"] if isinstance(a, dict) else a.percentile)
        vals[axis] = pct

    extremes = sorted(
        (ax for ax, p in vals.items() if p >= _HIGH or p <= _LOW),
        key=lambda ax: (-abs(vals[ax] - 50), _AXIS_ORDER.index(ax) if ax in _AXIS_ORDER else 99),
    )[:2]

    if not extremes:
        return (
            f"El {team_name} no muestra un rasgo de estilo marcado: todos los ejes "
            f"quedan cerca de la media de la liga."
        )

    frags = []
    for ax in extremes:
        high = vals[ax] >= _HIGH
        frags.append(_AXIS_PHRASES[ax][0 if high else 1])

    if len(frags) == 1:
        body = frags[0]
    else:
        body = f"{frags[0]} y {frags[1]}"
    return f"El {team_name} {body}."
