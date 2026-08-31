"""Modelos SQLAlchemy del motor de scouting.

Esquema pensado para:
  - guardar estadisticas de jugador-temporada de Sportmonks (fuente unica,
    ver data-experiment/docs/DECISIONS.md),
  - soportar que un jugador tenga VARIAS etapas en la misma temporada
    (cesiones / traspasos dentro de la liga) -> tabla player_team_season,
  - marcar los ceros que Sportmonks omite y que se imputan al cargar
    (player_statistics.is_imputed_zero),
  - marcar las stats que solo son validas para porteros
    (stat_types.valid_for = 'goalkeeper_only'),
  - Fase 3: percentiles por bucket de posicion -> tabla player_percentiles,
  - Fase 5: Player Role Score con pesos -> roles, role_buckets, role_weights,
    player_role_scores, player_role_score_breakdown,
  - Fase 6: Player Similarity Engine -> player_similarity,
  - Fase 7: Team Style Profile -> team_stat_types, team_fixtures,
    team_fixture_statistics (grano crudo por partido; la agregacion por
    formacion se hace por consulta),
  - Fase 8: Tactical Fit Score -> role_style_weights (catalogo),
    team_style_axes (percentiles de estilo precalculados). El
    tactical_fit en si es una funcion parametrizada bajo demanda
    (analysis/tactical_fit.py), NO una tabla.

Catalogos: competitions, seasons, teams, positions, stat_types, roles,
  role_buckets, role_weights, team_stat_types, role_style_weights.
Entidades: players, player_team_season, player_statistics, team_fixtures,
  team_fixture_statistics.
Derivado (Fase 3): player_percentiles.
Derivado (Fase 5): player_role_scores, player_role_score_breakdown.
Derivado (Fase 6): player_similarity.
Derivado (Fase 8): team_style_axes.
"""

from __future__ import annotations

import datetime
from typing import Optional

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.database import Base

POSITION_BUCKETS = ("portero", "central", "lateral", "centrocampista", "extremo", "delantero")
POSITION_SIDES = ("izquierda", "derecha", "centro", "desconocido")
STAT_VALID_FOR = ("all", "goalkeeper_only")
# Como se normaliza la metrica antes de calcular percentiles (Fase 3):
#   per90 = (valor / minutos) * 90   -> contadores
#   raw   = el valor tal cual         -> ya es %, o una media (rating)
#   none  = no entra en el calculo de percentiles (minutos, apariciones)
STAT_NORMALIZATION = ("per90", "raw", "none")
# Sentido de la metrica. Se usa para orientar el percentil guardado de
# forma que percentil alto = mejor rendimiento SIEMPRE.
STAT_DIRECTION = ("higher_better", "lower_better")
# Nivel de una metrica dentro de un rol (Fase 5). Es INFORMATIVO (lectura
# humana): el calculo del score usa solo role_weights.weight. El mapa
# tier -> peso vive en db/seed_catalogs.py (core 3, support 1.5, context 0.5).
ROLE_TIERS = ("core", "support", "context")
# Fase 7 - Team Style Profile.
TEAM_STAT_UNITS = ("count", "percentage")
TEAM_STAT_GROUPS = ("offensive", "defensive", "possession")
VENUES = ("home", "away")
MATCH_RESULTS = ("win", "draw", "loss")
# Fase 8 - Tactical Fit Score.
STYLE_AXES = (
    "possession", "pass_accuracy", "crossing_frequency",
    "press_intensity", "directness",
)
STYLE_DIRECTIONS = ("positive", "negative")


# ---------------------------------------------------------------------------
# Catalogos
# ---------------------------------------------------------------------------

class Competition(Base):
    __tablename__ = "competitions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    country: Mapped[Optional[str]] = mapped_column(String(80))
    tier: Mapped[Optional[int]] = mapped_column(Integer)
    sportmonks_league_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)

    teams: Mapped[list["Team"]] = relationship(back_populates="competition")


class Season(Base):
    __tablename__ = "seasons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(40), nullable=False)
    start_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    end_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    sportmonks_season_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    country: Mapped[Optional[str]] = mapped_column(String(80))
    competition_id: Mapped[Optional[int]] = mapped_column(ForeignKey("competitions.id"))
    sportmonks_team_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)

    competition: Mapped[Optional["Competition"]] = relationship(back_populates="teams")


class Position(Base):
    __tablename__ = "positions"
    __table_args__ = (
        CheckConstraint(f"bucket IN {POSITION_BUCKETS}", name="ck_positions_bucket"),
        CheckConstraint(f"lado IN {POSITION_SIDES}", name="ck_positions_lado"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    bucket: Mapped[str] = mapped_column(String(20), nullable=False)
    lado: Mapped[str] = mapped_column(String(12), nullable=False, default="centro")
    # sportmonks_position_id = el detailed_position_id de Sportmonks
    # (Centre Back, Left Back, Left Wing...). Puede ser NULL para el bucket
    # generico "desconocido".
    sportmonks_position_id: Mapped[Optional[int]] = mapped_column(Integer, unique=True)
    label: Mapped[str] = mapped_column(String(60), nullable=False)


class StatType(Base):
    __tablename__ = "stat_types"
    __table_args__ = (
        CheckConstraint(f"valid_for IN {STAT_VALID_FOR}", name="ck_stat_types_valid_for"),
        CheckConstraint(f"normalization IN {STAT_NORMALIZATION}", name="ck_stat_types_normalization"),
        CheckConstraint(f"direction IN {STAT_DIRECTION}", name="ck_stat_types_direction"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # code = el type.code tal cual de Sportmonks, ej. "big-chances-created".
    code: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    label: Mapped[str] = mapped_column(String(80), nullable=False)
    category: Mapped[str] = mapped_column(String(30), nullable=False)
    valid_for: Mapped[str] = mapped_column(String(20), nullable=False, default="all")
    normalization: Mapped[str] = mapped_column(String(10), nullable=False, default="per90")
    direction: Mapped[str] = mapped_column(String(15), nullable=False, default="higher_better")
    source_provider: Mapped[str] = mapped_column(String(20), nullable=False, default="sportmonks")


# ---------------------------------------------------------------------------
# Entidades
# ---------------------------------------------------------------------------

class Player(Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sportmonks_player_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    apifootball_player_id: Mapped[Optional[int]] = mapped_column(Integer, unique=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    birth_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    nationality: Mapped[Optional[str]] = mapped_column(String(80))
    height_cm: Mapped[Optional[int]] = mapped_column(Integer)
    weight_kg: Mapped[Optional[int]] = mapped_column(Integer)
    preferred_foot: Mapped[Optional[str]] = mapped_column(String(10))
    primary_position_id: Mapped[Optional[int]] = mapped_column(ForeignKey("positions.id"))
    photo_url: Mapped[Optional[str]] = mapped_column(String(255))

    primary_position: Mapped[Optional["Position"]] = relationship()
    team_seasons: Mapped[list["PlayerTeamSeason"]] = relationship(back_populates="player")


class PlayerTeamSeason(Base):
    """Una etapa de un jugador en un equipo dentro de una temporada.

    Un jugador puede tener varias filas en la misma temporada (cesion /
    traspaso dentro de la liga). Se numeran con `order_in_season` (0, 1,
    2...) por jugador-temporada, y el constraint unico va sobre
    (player_id, season_id, order_in_season). Se descarto usar `date_from`
    en el constraint porque Sportmonks no da fechas de etapa fiables y en
    Postgres `NULL != NULL` no desduplicaria. `date_from` / `date_to`
    quedan como columnas opcionales para rellenar mas adelante si hiciera
    falta.
    """

    __tablename__ = "player_team_season"
    __table_args__ = (
        UniqueConstraint(
            "player_id", "season_id", "order_in_season",
            name="uq_player_team_season",
        ),
        Index("ix_pts_player_id", "player_id"),
        Index("ix_pts_season_competition", "season_id", "competition_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), nullable=False)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    season_id: Mapped[int] = mapped_column(ForeignKey("seasons.id"), nullable=False)
    competition_id: Mapped[Optional[int]] = mapped_column(ForeignKey("competitions.id"))
    # 0 = primera (o unica) etapa del jugador en la temporada, 1 = segunda...
    order_in_season: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    date_from: Mapped[Optional[datetime.date]] = mapped_column(Date)
    date_to: Mapped[Optional[datetime.date]] = mapped_column(Date)

    player: Mapped["Player"] = relationship(back_populates="team_seasons")
    team: Mapped["Team"] = relationship()
    season: Mapped["Season"] = relationship()
    competition: Mapped[Optional["Competition"]] = relationship()
    statistics: Mapped[list["PlayerStatistic"]] = relationship(
        back_populates="player_team_season", cascade="all, delete-orphan"
    )


class PlayerStatistic(Base):
    __tablename__ = "player_statistics"
    __table_args__ = (
        UniqueConstraint(
            "player_team_season_id", "stat_type_id", name="uq_player_statistic"
        ),
        Index("ix_playerstat_stat_type", "stat_type_id"),
        Index("ix_playerstat_pts", "player_team_season_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # ON DELETE CASCADE: al reescribir las etapas de un jugador en el ETL
    # idempotente se borra su player_team_season y sus stats se van con el.
    player_team_season_id: Mapped[int] = mapped_column(
        ForeignKey("player_team_season.id", ondelete="CASCADE"), nullable=False
    )
    stat_type_id: Mapped[int] = mapped_column(ForeignKey("stat_types.id"), nullable=False)
    value: Mapped[float] = mapped_column(Numeric(12, 3), nullable=False)
    # True cuando el valor es un 0 que Sportmonks NO devolvio y que se
    # imputa al cargar (ver DECISIONS.md). Para el calculo de percentiles
    # de Fase 3 estos 0 SI cuentan.
    is_imputed_zero: Mapped[bool] = mapped_column(nullable=False, default=False)

    player_team_season: Mapped["PlayerTeamSeason"] = relationship(back_populates="statistics")
    stat_type: Mapped["StatType"] = relationship()


# ---------------------------------------------------------------------------
# Derivado (Fase 3)
# ---------------------------------------------------------------------------

class PlayerPercentile(Base):
    """Percentil de un jugador para una metrica, dentro de su bucket de
    posicion y su liga+temporada.

    La puebla analysis/percentiles.py de forma idempotente. NO se calcula
    para jugadores por debajo del umbral de minutos (parametro del
    recalculo, NO columna de config): esos simplemente no tienen filas
    aqui.

    `percentile` esta orientado: 100 = mejor de su bucket para esa metrica
    (ya aplicado stat_types.direction). `metric_value` es el valor que se
    ranqueo (per90 o raw). `min_minutes` es provenance: con que umbral se
    calculo esta fila.
    """

    __tablename__ = "player_percentiles"
    __table_args__ = (
        UniqueConstraint("player_id", "season_id", "stat_type_id", name="uq_player_percentile"),
        Index("ix_pctl_bucket_stat", "season_id", "competition_id", "position_bucket", "stat_type_id"),
        Index("ix_pctl_player", "player_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    season_id: Mapped[int] = mapped_column(ForeignKey("seasons.id"), nullable=False)
    competition_id: Mapped[Optional[int]] = mapped_column(ForeignKey("competitions.id"))
    stat_type_id: Mapped[int] = mapped_column(ForeignKey("stat_types.id"), nullable=False)
    position_bucket: Mapped[str] = mapped_column(String(20), nullable=False)
    metric_value: Mapped[float] = mapped_column(Numeric(14, 4), nullable=False)
    percentile: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    pool_size: Mapped[int] = mapped_column(Integer, nullable=False)
    min_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    computed_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    player: Mapped["Player"] = relationship()
    stat_type: Mapped["StatType"] = relationship()


# ---------------------------------------------------------------------------
# Fase 5 - Player Role Score
# ---------------------------------------------------------------------------

class Role(Base):
    """Un rol tactico 'construible pleno'
    (data-experiment/docs/roles_fase4_mapping.md, seccion 2). Catalogo
    estatico: lo puebla db/seed_catalogs.py junto con role_buckets y
    role_weights."""

    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # code = slug estable, ej. "ball_winner".
    code: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    label: Mapped[str] = mapped_column(String(80), nullable=False)

    buckets: Mapped[list["RoleBucket"]] = relationship(
        back_populates="role", cascade="all, delete-orphan"
    )
    weights: Mapped[list["RoleWeight"]] = relationship(
        back_populates="role", cascade="all, delete-orphan"
    )


class RoleBucket(Base):
    """Bucket(s) de posicion a los que aplica un rol. Un jugador solo
    recibe score en un rol si el bucket de su primary_position esta aqui.
    Tabla puente (se normaliza igual que el resto del esquema)."""

    __tablename__ = "role_buckets"
    __table_args__ = (
        UniqueConstraint("role_id", "bucket", name="uq_role_bucket"),
        CheckConstraint(f"bucket IN {POSITION_BUCKETS}", name="ck_role_buckets_bucket"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE"), nullable=False
    )
    bucket: Mapped[str] = mapped_column(String(20), nullable=False)

    role: Mapped["Role"] = relationship(back_populates="buckets")


class RoleWeight(Base):
    """Peso de una metrica dentro de un rol. `tier` (core/support/context)
    es informativo para lectura humana; el calculo usa solo `weight`."""

    __tablename__ = "role_weights"
    __table_args__ = (
        UniqueConstraint("role_id", "stat_type_id", name="uq_role_weight"),
        CheckConstraint(f"tier IN {ROLE_TIERS}", name="ck_role_weights_tier"),
        CheckConstraint("weight > 0", name="ck_role_weights_weight_positive"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE"), nullable=False
    )
    stat_type_id: Mapped[int] = mapped_column(ForeignKey("stat_types.id"), nullable=False)
    weight: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False)
    tier: Mapped[str] = mapped_column(String(10), nullable=False)

    role: Mapped["Role"] = relationship(back_populates="weights")
    stat_type: Mapped["StatType"] = relationship()


class PlayerRoleScore(Base):
    """Score de encaje 0-100 de un jugador en un rol, para una temporada.

    La puebla analysis/role_scores.py de forma idempotente a partir de
    player_percentiles (Fase 3). Grano = (player_id, season_id, role_id).

        score = SUM(percentil * peso) / SUM(peso)   -> ya en [0,100]

    sobre las metricas del rol PARA LAS QUE EL JUGADOR TIENE PERCENTIL. Si
    falta el percentil de una metrica, esa metrica se EXCLUYE del numerador
    y del denominador (no se imputa a 50) -> ver el modulo. `total_weight`
    es el denominador efectivo: si es menor que el peso total del rol, al
    jugador le faltaba alguna metrica. No se emite fila si `total_weight`
    cae por debajo de MIN_WEIGHT_COVERAGE del peso del rol.
    """

    __tablename__ = "player_role_scores"
    __table_args__ = (
        UniqueConstraint(
            "player_id", "season_id", "role_id", name="uq_player_role_score"
        ),
        CheckConstraint("score >= 0 AND score <= 100", name="ck_player_role_scores_range"),
        Index("ix_prs_role_rank", "season_id", "role_id", "score"),
        Index("ix_prs_player", "player_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    player_id: Mapped[int] = mapped_column(
        ForeignKey("players.id", ondelete="CASCADE"), nullable=False
    )
    season_id: Mapped[int] = mapped_column(ForeignKey("seasons.id"), nullable=False)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False)
    position_bucket: Mapped[str] = mapped_column(String(20), nullable=False)
    score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    # provenance: denominador efectivo, nº de metricas que contribuyeron y
    # umbral de minutos con el que se calcularon los percentiles de entrada.
    total_weight: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    metrics_used: Mapped[int] = mapped_column(Integer, nullable=False)
    min_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    computed_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    player: Mapped["Player"] = relationship()
    role: Mapped["Role"] = relationship()
    breakdown: Mapped[list["PlayerRoleScoreBreakdown"]] = relationship(
        back_populates="role_score", cascade="all, delete-orphan"
    )


class PlayerRoleScoreBreakdown(Base):
    """Una linea del desglose de un PlayerRoleScore: la contribucion de una
    metrica. Aqui se lee la explicabilidad ('por que 91 en Ball Winner').

        contribution   = percentile * weight
        score (padre)  = SUM(contribution) / SUM(weight)  sobre estas filas
    """

    __tablename__ = "player_role_score_breakdown"
    __table_args__ = (
        UniqueConstraint(
            "player_role_score_id", "stat_type_id", name="uq_role_score_breakdown"
        ),
        Index("ix_prsb_score", "player_role_score_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    player_role_score_id: Mapped[int] = mapped_column(
        ForeignKey("player_role_scores.id", ondelete="CASCADE"), nullable=False
    )
    stat_type_id: Mapped[int] = mapped_column(ForeignKey("stat_types.id"), nullable=False)
    tier: Mapped[str] = mapped_column(String(10), nullable=False)
    percentile: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    weight: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False)
    contribution: Mapped[float] = mapped_column(Numeric(9, 2), nullable=False)

    role_score: Mapped["PlayerRoleScore"] = relationship(back_populates="breakdown")
    stat_type: Mapped["StatType"] = relationship()


# ---------------------------------------------------------------------------
# Derivado (Fase 6) - Player Similarity Engine
# ---------------------------------------------------------------------------

class PlayerSimilarity(Base):
    """Top-20 jugadores mas similares a uno dado, dentro de su mismo bucket
    de posicion y temporada.

    Similaridad = cosine similarity sobre el vector de percentiles per90 de
    Fase 3 (TODAS las metricas del bucket: 34 de campo, 37 portero). Solo
    se compara dentro del mismo bucket (sin cross-posicion en esta fase).

    La puebla analysis/similarity.py de forma idempotente (DELETE scoped +
    INSERT). NO se guarda la matriz N^2: solo el top-20 por jugador. La
    tabla NO es simetrica (que B este en el top-20 de A no implica que A
    este en el de B, ni con el mismo score/rank).

    Los filtros de edad (birth_date) y lado (positions.lado) se aplican AL
    CONSULTAR esta tabla; NO entran en el calculo de similitud -> la
    similitud estadistica no cambia segun el filtro de busqueda posterior.

    Fuera de alcance (pendientes conocidos): pie dominante
    (players.preferred_foot sigue NULL) y valor de mercado (no esta en
    ninguna fuente). Ningun filtro puede apoyarse en ellos todavia.
    """

    __tablename__ = "player_similarity"
    __table_args__ = (
        UniqueConstraint(
            "player_id", "similar_player_id", "season_id",
            name="uq_player_similarity",
        ),
        CheckConstraint(
            "player_id <> similar_player_id", name="ck_player_similarity_distinct"
        ),
        CheckConstraint("rank >= 1 AND rank <= 20", name="ck_player_similarity_rank"),
        CheckConstraint(
            "similarity_score >= 0 AND similarity_score <= 1",
            name="ck_player_similarity_score",
        ),
        Index("ix_psim_player", "player_id", "season_id", "rank"),
        Index("ix_psim_similar", "similar_player_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    player_id: Mapped[int] = mapped_column(
        ForeignKey("players.id", ondelete="CASCADE"), nullable=False
    )
    similar_player_id: Mapped[int] = mapped_column(
        ForeignKey("players.id", ondelete="CASCADE"), nullable=False
    )
    season_id: Mapped[int] = mapped_column(ForeignKey("seasons.id"), nullable=False)
    position_bucket: Mapped[str] = mapped_column(String(20), nullable=False)
    similarity_score: Mapped[float] = mapped_column(Numeric(8, 6), nullable=False)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    # provenance: nº de metricas del vector y umbral de minutos de los
    # percentiles de entrada.
    n_features: Mapped[int] = mapped_column(Integer, nullable=False)
    min_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    computed_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    player: Mapped["Player"] = relationship(foreign_keys=[player_id])
    similar_player: Mapped["Player"] = relationship(foreign_keys=[similar_player_id])


# ---------------------------------------------------------------------------
# Fase 7 - Team Style Profile
# ---------------------------------------------------------------------------

class TeamStatType(Base):
    """Catalogo de estadisticas de EQUIPO por partido (Sportmonks
    fixture-statistics).

    Separado de stat_types (stats de jugador) a proposito: aunque varios
    `code` coinciden ('passes', 'tackles', 'interceptions', 'fouls',
    'shots-total'...), la entidad y la unidad son distintas -- aqui es un
    total de un equipo en UN partido, alli un valor per-90 de temporada de
    un jugador -- y las columnas de metadata de stat_types
    (normalization per90/raw/none, direction, valid_for='goalkeeper_only')
    no tienen sentido para una stat de equipo. Un unico stat_type_id
    tendria que significar dos cosas segun quien lo referencie.
    """

    __tablename__ = "team_stat_types"
    __table_args__ = (
        CheckConstraint(f"unit IN {TEAM_STAT_UNITS}", name="ck_team_stat_types_unit"),
        CheckConstraint(f"stat_group IN {TEAM_STAT_GROUPS}", name="ck_team_stat_types_group"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    label: Mapped[str] = mapped_column(String(80), nullable=False)
    # 'count' = contador (se imputa 0 si Sportmonks lo omite);
    # 'percentage' = %, NO se imputa (si falta, no hay fila).
    unit: Mapped[str] = mapped_column(String(12), nullable=False)
    stat_group: Mapped[str] = mapped_column(String(12), nullable=False)
    source_provider: Mapped[str] = mapped_column(String(20), nullable=False, default="sportmonks")


class TeamFixture(Base):
    """Una fila por (equipo, partido): formacion con la que salio, casa o
    fuera, y resultado. Grano CRUDO por partido -- la agregacion por
    formacion (V/E/D, medias, por venue...) se hace por consulta
    (GROUP BY), no en la carga (mismo principio que player_team_season /
    player_statistics).

    goals_for / goals_against SIEMPRE salen de scores[] (description=
    'CURRENT'), NUNCA del bloque statistics: Sportmonks omite 'goals'
    cuando un equipo marca 0. `result` se deriva de esos dos.

    Cada fixture de Sportmonks produce 2 filas aqui (una por equipo). Las
    stats del rival en ese mismo partido no crean una tercera fila: viven
    en team_fixture_statistics con is_conceded=True.
    """

    __tablename__ = "team_fixtures"
    __table_args__ = (
        UniqueConstraint("sportmonks_fixture_id", "team_id", name="uq_team_fixture"),
        CheckConstraint(f"venue IN {VENUES}", name="ck_team_fixtures_venue"),
        CheckConstraint(f"result IN {MATCH_RESULTS}", name="ck_team_fixtures_result"),
        CheckConstraint("goals_for >= 0 AND goals_against >= 0", name="ck_team_fixtures_goals"),
        Index("ix_tf_season_team", "season_id", "competition_id", "team_id"),
        Index("ix_tf_team_formation", "team_id", "formation"),
        Index("ix_tf_opponent", "opponent_team_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    opponent_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    season_id: Mapped[int] = mapped_column(ForeignKey("seasons.id"), nullable=False)
    competition_id: Mapped[int] = mapped_column(ForeignKey("competitions.id"), nullable=False)
    sportmonks_fixture_id: Mapped[int] = mapped_column(Integer, nullable=False)
    # provenance, util para "formacion a lo largo de la temporada".
    starting_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=False))
    venue: Mapped[str] = mapped_column(String(4), nullable=False)
    # NULL si Sportmonks no dio la formacion de ese equipo en ese partido.
    formation: Mapped[Optional[str]] = mapped_column(String(20))
    goals_for: Mapped[int] = mapped_column(Integer, nullable=False)
    goals_against: Mapped[int] = mapped_column(Integer, nullable=False)
    result: Mapped[str] = mapped_column(String(4), nullable=False)

    team: Mapped["Team"] = relationship(foreign_keys=[team_id])
    opponent: Mapped["Team"] = relationship(foreign_keys=[opponent_team_id])
    statistics: Mapped[list["TeamFixtureStatistic"]] = relationship(
        back_populates="team_fixture", cascade="all, delete-orphan"
    )


class TeamFixtureStatistic(Base):
    """Una estadistica de equipo en un partido.

    is_conceded = False -> stat propia del equipo de team_fixture.
    is_conceded = True  -> la MISMA stat del rival en ese mismo partido
                           (perfil defensivo; sale gratis del fixture).
    is_imputed_zero     -> Sportmonks omite el detail cuando vale 0 y aqui
                           se imputa 0 explicito (misma convencion que
                           player_statistics.is_imputed_zero). Solo aplica
                           a stats 'count'; las 'percentage' no se imputan.
    """

    __tablename__ = "team_fixture_statistics"
    __table_args__ = (
        UniqueConstraint(
            "team_fixture_id", "team_stat_type_id", "is_conceded",
            name="uq_team_fixture_statistic",
        ),
        Index("ix_tfs_fixture", "team_fixture_id"),
        Index("ix_tfs_stat_type", "team_stat_type_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    team_fixture_id: Mapped[int] = mapped_column(
        ForeignKey("team_fixtures.id", ondelete="CASCADE"), nullable=False
    )
    team_stat_type_id: Mapped[int] = mapped_column(
        ForeignKey("team_stat_types.id"), nullable=False
    )
    value: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    is_imputed_zero: Mapped[bool] = mapped_column(nullable=False, default=False)
    is_conceded: Mapped[bool] = mapped_column(nullable=False, default=False)

    team_fixture: Mapped["TeamFixture"] = relationship(back_populates="statistics")
    team_stat_type: Mapped["TeamStatType"] = relationship()


# ---------------------------------------------------------------------------
# Fase 8 - Tactical Fit Score
# ---------------------------------------------------------------------------

class RoleStyleWeight(Base):
    """Matriz de compatibilidad rol -> eje de estilo de equipo (explicita,
    heuristica documentada; no hay datos de evento para APRENDERLA).

    `direction` = 'negative' significa que un percentil ALTO del equipo en
    ese eje PERJUDICA el encaje (p.ej. directitud alta para un Deep-Lying
    Playmaker). En el calculo se usa (100 - percentil) para esos ejes.

    Pesos planos (todos 1.0): la matriz de diseno solo especifica signos, y
    con 1-3 ejes por rol los tiers (nucleo/apoyo/contexto) de la Fase 5
    anadirian precision falsa. La columna es numeric por si se afina luego.
    """

    __tablename__ = "role_style_weights"
    __table_args__ = (
        UniqueConstraint("role_id", "style_axis", name="uq_role_style_weight"),
        CheckConstraint(f"style_axis IN {STYLE_AXES}", name="ck_role_style_weights_axis"),
        CheckConstraint(f"direction IN {STYLE_DIRECTIONS}", name="ck_role_style_weights_direction"),
        CheckConstraint("weight > 0", name="ck_role_style_weights_weight_positive"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE"), nullable=False
    )
    style_axis: Mapped[str] = mapped_column(String(24), nullable=False)
    weight: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False)
    direction: Mapped[str] = mapped_column(String(8), nullable=False)

    role: Mapped["Role"] = relationship()


class TeamStyleAxis(Base):
    """Percentil de un eje de estilo para un (equipo, formacion) entre los
    20 equipos de LaLiga, en una temporada.

    formation = NULL -> agregado de todos los partidos del equipo.
    formation = '4-3-3' -> solo los partidos con esa formacion, y solo si
      llegan al umbral (min_matches, 5 por defecto = criterio de Fase 7).
    El pool de referencia del percentil son SIEMPRE los 20 agregados de
    equipo (formation NULL), tambien para las filas por formacion.

    La puebla analysis/team_style.py de forma idempotente (DELETE scoped +
    INSERT). El Tactical Fit Score se calcula sobre esta tabla bajo demanda
    (analysis/tactical_fit.py); no se materializa.
    """

    __tablename__ = "team_style_axes"
    __table_args__ = (
        UniqueConstraint(
            "team_id", "season_id", "formation", "style_axis",
            name="uq_team_style_axis",
            postgresql_nulls_not_distinct=True,
        ),
        CheckConstraint(f"style_axis IN {STYLE_AXES}", name="ck_team_style_axes_axis"),
        CheckConstraint("percentile >= 0 AND percentile <= 100", name="ck_team_style_axes_pctl"),
        Index("ix_tsa_team_season", "team_id", "season_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    season_id: Mapped[int] = mapped_column(ForeignKey("seasons.id"), nullable=False)
    formation: Mapped[Optional[str]] = mapped_column(String(20))
    style_axis: Mapped[str] = mapped_column(String(24), nullable=False)
    # valor bruto del eje (posesion media %, centros/partido, ratio de
    # directitud *100...). Se guarda para poder leer el perfil sin recalcular.
    raw_value: Mapped[float] = mapped_column(Numeric(10, 4), nullable=False)
    percentile: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    n_matches: Mapped[int] = mapped_column(Integer, nullable=False)
    min_matches: Mapped[int] = mapped_column(Integer, nullable=False)
    computed_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    team: Mapped["Team"] = relationship()
