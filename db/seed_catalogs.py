"""Poblacion de los catalogos ESTATICOS: positions, stat_types y roles.

Estos catalogos no dependen de que datos se carguen: salen de lo que ya
sabemos de Sportmonks tras el experimento de Fase 0
(data-experiment/config.py -> STAT_FIELD_MAP / STAT_FIELD_MAP_EXTRA,
data-experiment/raw_data/sportmonks/positions_map.json) y de la taxonomia
de roles cerrada en data-experiment/docs/roles_fase4_mapping.md.

competitions / seasons / teams los puebla cada loader segun lo que carga.

Es idempotente: si el catalogo ya tiene filas, no hace nada.
"""

from sqlalchemy import select

from db.models import (
    Position,
    Role,
    RoleBucket,
    RoleStyleWeight,
    RoleWeight,
    StatType,
    TeamStatType,
)

# --- positions -------------------------------------------------------------
# (sportmonks detailed_position_id, bucket, lado, label)
POSITIONS = [
    (24, "portero", "centro", "Goalkeeper"),
    (148, "central", "centro", "Centre Back"),
    (149, "centrocampista", "centro", "Defensive Midfield"),
    (150, "centrocampista", "centro", "Attacking Midfield"),
    (151, "delantero", "centro", "Centre Forward"),
    (152, "extremo", "izquierda", "Left Wing"),
    (153, "centrocampista", "centro", "Central Midfield"),
    (154, "lateral", "derecha", "Right Back"),
    (155, "lateral", "izquierda", "Left Back"),
    (156, "extremo", "derecha", "Right Wing"),
    (157, "centrocampista", "izquierda", "Left Midfield"),
    (158, "centrocampista", "derecha", "Right Midfield"),
    (163, "delantero", "centro", "Secondary Striker"),
]

# --- stat_types -----------------------------------------------------------
# (code Sportmonks, label ES, category, valid_for, normalization, direction)
#
# category:      participacion | pase | creacion | finalizacion | duelo |
#               regate | defensa | disciplina | posesion | porteria
# valid_for:     'all' salvo las 3 de porteria (saves, goals-conceded,
#               cleansheets) -> 'goalkeeper_only'.
# normalization: como se lleva la metrica a algo comparable (Fase 3):
#   'per90' -> (valor / minutos) * 90. Para todos los CONTADORES.
#   'raw'   -> el valor tal cual. Para % (accurate-passes-percentage) y
#              para el rating (que ya es una media 0-10).
#   'none'  -> NO entra en el calculo de percentiles. minutes-played es el
#              propio umbral; appearances es disponibilidad, no rendimiento.
# direction:     para orientar el percentil guardado (100 = mejor SIEMPRE):
#   'higher_better' por defecto; 'lower_better' para lo que penaliza
#   (tarjetas, faltas, perdidas, ser regateado, fueras de juego, grandes
#   ocasiones falladas, goles encajados).
STAT_TYPES = [
    # code, label, category, valid_for, normalization, direction
    # --- participacion (no entran en percentiles) ---
    ("appearances", "apariciones", "participacion", "all", "none", "higher_better"),
    ("minutes-played", "minutos jugados", "participacion", "all", "none", "higher_better"),
    ("rating", "rating medio", "participacion", "all", "raw", "higher_better"),
    # --- finalizacion ---
    ("goals", "goles", "finalizacion", "all", "per90", "higher_better"),
    ("shots-total", "tiros totales", "finalizacion", "all", "per90", "higher_better"),
    ("shots-on-target", "tiros a puerta", "finalizacion", "all", "per90", "higher_better"),
    ("shots-blocked", "tiros propios bloqueados", "finalizacion", "all", "per90", "higher_better"),
    ("big-chances-missed", "grandes ocasiones falladas", "finalizacion", "all", "per90", "lower_better"),
    ("offsides", "fueras de juego", "finalizacion", "all", "per90", "lower_better"),
    ("hit-woodwork", "al palo", "finalizacion", "all", "per90", "higher_better"),
    ("penalties", "penaltis (total)", "finalizacion", "all", "per90", "higher_better"),
    # --- creacion ---
    ("assists", "asistencias", "creacion", "all", "per90", "higher_better"),
    ("key-passes", "pases clave", "creacion", "all", "per90", "higher_better"),
    ("big-chances-created", "grandes ocasiones creadas", "creacion", "all", "per90", "higher_better"),
    ("through-balls", "pases al hueco", "creacion", "all", "per90", "higher_better"),
    ("through-balls-won", "pases al hueco exitosos", "creacion", "all", "per90", "higher_better"),
    # --- pase ---
    ("passes", "pases totales", "pase", "all", "per90", "higher_better"),
    ("accurate-passes-percentage", "precision de pases (%)", "pase", "all", "raw", "higher_better"),
    ("total-crosses", "centros totales", "pase", "all", "per90", "higher_better"),
    ("accurate-crosses", "centros precisos", "pase", "all", "per90", "higher_better"),
    ("long-balls", "balones largos", "pase", "all", "per90", "higher_better"),
    ("long-balls-won", "balones largos ganados", "pase", "all", "per90", "higher_better"),
    # --- defensa ---
    ("tackles", "entradas", "defensa", "all", "per90", "higher_better"),
    ("interceptions", "intercepciones", "defensa", "all", "per90", "higher_better"),
    ("blocked-shots", "tiros rivales bloqueados", "defensa", "all", "per90", "higher_better"),
    ("clearances", "despejes", "defensa", "all", "per90", "higher_better"),
    ("dribbled-past", "regateado (superado)", "defensa", "all", "per90", "lower_better"),
    # --- duelo ---
    ("duels-won", "duelos ganados", "duelo", "all", "per90", "higher_better"),
    ("aeriels-won", "duelos aereos ganados", "duelo", "all", "per90", "higher_better"),
    ("fouls-drawn", "faltas recibidas", "duelo", "all", "per90", "higher_better"),
    # --- regate ---
    ("successful-dribbles", "regates exitosos", "regate", "all", "per90", "higher_better"),
    ("dribble-attempts", "regates intentados", "regate", "all", "per90", "higher_better"),
    # --- disciplina ---
    ("yellowcards", "tarjetas amarillas", "disciplina", "all", "per90", "lower_better"),
    ("redcards", "tarjetas rojas", "disciplina", "all", "per90", "lower_better"),
    ("fouls", "faltas cometidas", "disciplina", "all", "per90", "lower_better"),
    # --- posesion ---
    ("dispossessed", "perdidas de posesion", "posesion", "all", "per90", "lower_better"),
    # --- porteria (solo porteros) ---
    ("saves", "paradas", "porteria", "goalkeeper_only", "per90", "higher_better"),
    ("goals-conceded", "goles encajados", "porteria", "goalkeeper_only", "per90", "lower_better"),
    ("cleansheets", "porteria a cero", "porteria", "goalkeeper_only", "per90", "higher_better"),
]


# --- roles (Fase 5) -----------------------------------------------------
# Los 4 roles "construibles plenos" confirmados en
# data-experiment/docs/roles_fase4_mapping.md (seccion 2). Pesos por nivel
# (decision de diseno, no se reabre): core 3, support 1.5, context 0.5.
#
# (code, label, [buckets de posicion], {tier: [codigos stat_types]})
TIER_WEIGHT = {"core": 3.0, "support": 1.5, "context": 0.5}

ROLES = [
    (
        "ball_winner", "Ball Winner",
        ["central", "centrocampista", "lateral"],
        {
            "core":    ["tackles", "interceptions", "duels-won"],
            "support": ["blocked-shots", "clearances"],
            "context": ["fouls", "yellowcards"],
        },
    ),
    (
        "deep_lying_playmaker", "Deep-Lying Playmaker",
        ["centrocampista"],
        {
            "core":    ["passes", "accurate-passes-percentage", "key-passes"],
            "support": ["long-balls", "long-balls-won"],
            "context": ["interceptions", "through-balls"],
        },
    ),
    (
        "advanced_playmaker", "Advanced Playmaker",
        ["centrocampista", "extremo"],
        {
            "core":    ["key-passes", "big-chances-created", "assists"],
            "support": ["successful-dribbles", "dribble-attempts"],
            "context": ["through-balls"],
        },
    ),
    (
        "ball_playing_cb", "Ball Playing CB",
        ["central"],
        {
            "core":    ["accurate-passes-percentage", "long-balls", "long-balls-won"],
            "support": ["aeriels-won", "clearances", "duels-won"],
            "context": ["passes", "tackles", "interceptions", "blocked-shots"],
        },
    ),
]


# --- team_stat_types (Fase 7) -----------------------------------------
# Las 15 stats de equipo por partido que entran en el Team Style Profile,
# de los 23 codes presentes en 50/50 partidos de la muestra (ver
# data-experiment/docs/fase7_fixtures_investigation.md). Fuera: throwins /
# goals-kicks (ruido situacional), duels-won / assists (casi vacios por
# partido, ~9/50). 'goals' NUNCA entra aqui: el marcador sale de scores[].
#
# unit:  'count' -> se imputa 0 si Sportmonks omite el detail;
#        'percentage' -> NO se imputa (si falta, no hay fila).
# stat_group: offensive | defensive | possession (agrupacion propia,
#        derivada del stat_group de Sportmonks: su 'overall' del bloque de
#        pase/posesion se mapea a 'possession').
# (code, label, unit, stat_group)
TEAM_STAT_TYPES = [
    ("ball-possession", "posesion (%)", "percentage", "possession"),
    ("passes", "pases totales", "count", "possession"),
    ("successful-passes-percentage", "precision de pases (%)", "percentage", "possession"),
    ("long-passes", "pases largos", "count", "possession"),
    ("shots-total", "tiros totales", "count", "offensive"),
    ("shots-on-target", "tiros a puerta", "count", "offensive"),
    ("shots-insidebox", "tiros dentro del area", "count", "offensive"),
    ("shots-outsidebox", "tiros fuera del area", "count", "offensive"),
    ("corners", "corners", "count", "offensive"),
    ("total-crosses", "centros totales", "count", "offensive"),
    ("accurate-crosses", "centros precisos", "count", "offensive"),
    ("successful-dribbles", "regates exitosos", "count", "offensive"),
    ("fouls", "faltas cometidas", "count", "defensive"),
    ("tackles", "entradas", "count", "defensive"),
    ("interceptions", "intercepciones", "count", "defensive"),
]


# --- role_style_weights (Fase 8) --------------------------------------
# Matriz de compatibilidad rol -> eje de estilo de equipo. Heuristica
# explicita (no hay datos de evento para aprenderla). Pesos planos (1.0):
# la matriz solo especifica signos y hay 1-3 ejes por rol, asi que tiers
# anadirian precision falsa (ver RoleStyleWeight en models.py).
# (role code, [(style_axis, direction), ...])
ROLE_STYLE_WEIGHTS = [
    ("deep_lying_playmaker", [
        ("possession", "positive"),
        ("pass_accuracy", "positive"),
        ("directness", "negative"),
    ]),
    ("ball_playing_cb", [
        ("possession", "positive"),
        ("pass_accuracy", "positive"),
    ]),
    ("advanced_playmaker", [
        ("crossing_frequency", "positive"),
    ]),
    ("ball_winner", [
        ("press_intensity", "positive"),
    ]),
]
ROLE_STYLE_WEIGHT_VALUE = 1.0


def seed_positions(session):
    existing = session.scalar(select(Position).limit(1))
    if existing is not None:
        return 0
    for sm_id, bucket, lado, label in POSITIONS:
        session.add(Position(
            sportmonks_position_id=sm_id, bucket=bucket, lado=lado, label=label,
        ))
    session.flush()
    return len(POSITIONS)


def seed_stat_types(session):
    existing = session.scalar(select(StatType).limit(1))
    if existing is not None:
        return 0
    for code, label, category, valid_for, normalization, direction in STAT_TYPES:
        session.add(StatType(
            code=code, label=label, category=category, valid_for=valid_for,
            normalization=normalization, direction=direction,
            source_provider="sportmonks",
        ))
    session.flush()
    return len(STAT_TYPES)


def seed_roles(session):
    existing = session.scalar(select(Role).limit(1))
    if existing is not None:
        return 0
    stat_id = {code: sid for code, sid in session.execute(select(StatType.code, StatType.id))}
    for code, label, buckets, tiers in ROLES:
        role = Role(code=code, label=label)
        session.add(role)
        session.flush()  # necesita role.id
        for bucket in buckets:
            session.add(RoleBucket(role_id=role.id, bucket=bucket))
        for tier, stat_codes in tiers.items():
            for stat_code in stat_codes:
                session.add(RoleWeight(
                    role_id=role.id,
                    stat_type_id=stat_id[stat_code],
                    weight=TIER_WEIGHT[tier],
                    tier=tier,
                ))
    session.flush()
    return len(ROLES)


def seed_team_stat_types(session):
    existing = session.scalar(select(TeamStatType).limit(1))
    if existing is not None:
        return 0
    for code, label, unit, group in TEAM_STAT_TYPES:
        session.add(TeamStatType(
            code=code, label=label, unit=unit, stat_group=group,
            source_provider="sportmonks",
        ))
    session.flush()
    return len(TEAM_STAT_TYPES)


def seed_role_style_weights(session):
    existing = session.scalar(select(RoleStyleWeight).limit(1))
    if existing is not None:
        return 0
    role_id_by_code = {code: rid for code, rid in session.execute(select(Role.code, Role.id))}
    n = 0
    for role_code, axes in ROLE_STYLE_WEIGHTS:
        role_id = role_id_by_code.get(role_code)
        if role_id is None:
            continue  # roles se siembran antes; si falta, seed_roles no corrio
        for axis, direction in axes:
            session.add(RoleStyleWeight(
                role_id=role_id, style_axis=axis,
                weight=ROLE_STYLE_WEIGHT_VALUE, direction=direction,
            ))
            n += 1
    session.flush()
    return n


def seed_static_catalogs(session):
    n_pos = seed_positions(session)
    n_stat = seed_stat_types(session)
    n_roles = seed_roles(session)
    n_team_stat = seed_team_stat_types(session)
    n_role_style = seed_role_style_weights(session)
    return {"positions": n_pos, "stat_types": n_stat, "roles": n_roles,
            "team_stat_types": n_team_stat, "role_style_weights": n_role_style}
