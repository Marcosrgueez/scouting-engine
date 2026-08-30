"""Poblacion de los catalogos ESTATICOS: positions y stat_types.

Estos dos catalogos no dependen de que datos se carguen: salen de lo que
ya sabemos de Sportmonks tras el experimento de Fase 0
(data-experiment/config.py -> STAT_FIELD_MAP / STAT_FIELD_MAP_EXTRA, y
data-experiment/raw_data/sportmonks/positions_map.json).

competitions / seasons / teams los puebla cada loader segun lo que carga.

Es idempotente: si el catalogo ya tiene filas, no hace nada.
"""

from sqlalchemy import select

from db.models import Position, StatType

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
# (code Sportmonks, label ES, category, valid_for)
# category: participacion | pase | creacion | finalizacion | duelo | regate
#           | defensa | disciplina | posesion | porteria
# valid_for: 'all' salvo las 3 de porteria (saves, goals-conceded,
#            cleansheets) -> 'goalkeeper_only'. saves siempre es 0 para
#            jugadores de campo, no tiene sentido imputarlo.
STAT_TYPES = [
    # --- STAT_FIELD_MAP (ya usados en el experimento) ---
    ("appearances", "apariciones", "participacion", "all"),
    ("minutes-played", "minutos jugados", "participacion", "all"),
    ("rating", "rating medio", "participacion", "all"),
    ("goals", "goles", "finalizacion", "all"),
    ("assists", "asistencias", "creacion", "all"),
    ("shots-total", "tiros totales", "finalizacion", "all"),
    ("shots-on-target", "tiros a puerta", "finalizacion", "all"),
    ("passes", "pases totales", "pase", "all"),
    ("key-passes", "pases clave", "creacion", "all"),
    ("accurate-passes-percentage", "precision de pases (%)", "pase", "all"),
    ("tackles", "entradas", "defensa", "all"),
    ("interceptions", "intercepciones", "defensa", "all"),
    ("duels-won", "duelos ganados", "duelo", "all"),
    ("successful-dribbles", "regates exitosos", "regate", "all"),
    ("yellowcards", "tarjetas amarillas", "disciplina", "all"),
    ("redcards", "tarjetas rojas", "disciplina", "all"),
    ("saves", "paradas", "porteria", "goalkeeper_only"),
    ("goals-conceded", "goles encajados", "porteria", "goalkeeper_only"),
    ("cleansheets", "porteria a cero", "porteria", "goalkeeper_only"),
    # --- STAT_FIELD_MAP_EXTRA (metricas nuevas medidas en la ultima pasada) ---
    ("fouls", "faltas cometidas", "disciplina", "all"),
    ("fouls-drawn", "faltas recibidas", "duelo", "all"),
    ("dispossessed", "perdidas de posesion", "posesion", "all"),
    ("shots-blocked", "tiros propios bloqueados", "finalizacion", "all"),
    ("blocked-shots", "tiros rivales bloqueados", "defensa", "all"),
    ("total-crosses", "centros totales", "pase", "all"),
    ("accurate-crosses", "centros precisos", "pase", "all"),
    ("aeriels-won", "duelos aereos ganados", "duelo", "all"),
    ("dribble-attempts", "regates intentados", "regate", "all"),
    ("dribbled-past", "regateado (superado)", "defensa", "all"),
    ("long-balls", "balones largos", "pase", "all"),
    ("long-balls-won", "balones largos ganados", "pase", "all"),
    ("through-balls", "pases al hueco", "creacion", "all"),
    ("through-balls-won", "pases al hueco exitosos", "creacion", "all"),
    ("big-chances-created", "grandes ocasiones creadas", "creacion", "all"),
    ("big-chances-missed", "grandes ocasiones falladas", "finalizacion", "all"),
    ("clearances", "despejes", "defensa", "all"),
    ("offsides", "fueras de juego", "finalizacion", "all"),
    ("hit-woodwork", "al palo", "finalizacion", "all"),
    ("penalties", "penaltis", "finalizacion", "all"),
]


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
    for code, label, category, valid_for in STAT_TYPES:
        session.add(StatType(
            code=code, label=label, category=category,
            valid_for=valid_for, source_provider="sportmonks",
        ))
    session.flush()
    return len(STAT_TYPES)


def seed_static_catalogs(session):
    n_pos = seed_positions(session)
    n_stat = seed_stat_types(session)
    return {"positions": n_pos, "stat_types": n_stat}
