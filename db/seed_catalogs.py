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


def seed_static_catalogs(session):
    n_pos = seed_positions(session)
    n_stat = seed_stat_types(session)
    return {"positions": n_pos, "stat_types": n_stat}
