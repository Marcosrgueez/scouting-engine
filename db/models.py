"""Modelos SQLAlchemy del motor de scouting (Fase 1).

Esquema pensado para:
  - guardar estadisticas de jugador-temporada de Sportmonks (fuente unica,
    ver data-experiment/docs/DECISIONS.md),
  - soportar que un jugador tenga VARIAS etapas en la misma temporada
    (cesiones / traspasos dentro de la liga) -> tabla player_team_season,
  - marcar los ceros que Sportmonks omite y que se imputan al cargar
    (player_statistics.is_imputed_zero),
  - marcar las stats que solo son validas para porteros
    (stat_types.valid_for = 'goalkeeper_only').

Catalogos: competitions, seasons, teams, positions, stat_types.
Entidades: players, player_team_season, player_statistics.
"""

from __future__ import annotations

import datetime
from typing import Optional

from sqlalchemy import (
    CheckConstraint,
    Date,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.database import Base

POSITION_BUCKETS = ("portero", "central", "lateral", "centrocampista", "extremo", "delantero")
POSITION_SIDES = ("izquierda", "derecha", "centro", "desconocido")
STAT_VALID_FOR = ("all", "goalkeeper_only")


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
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # code = el type.code tal cual de Sportmonks, ej. "big-chances-created".
    code: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    label: Mapped[str] = mapped_column(String(80), nullable=False)
    category: Mapped[str] = mapped_column(String(30), nullable=False)
    valid_for: Mapped[str] = mapped_column(String(20), nullable=False, default="all")
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
