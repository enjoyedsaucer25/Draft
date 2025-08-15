from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Float, ForeignKey, JSON, UniqueConstraint, Index, DateTime, Boolean
from .db import Base
from datetime import datetime

class Player(Base):
    __tablename__ = "players"
    player_id: Mapped[str] = mapped_column(String, primary_key=True)  # Sleeper ID
    season: Mapped[int] = mapped_column(Integer, default=2025)
    clean_name: Mapped[str] = mapped_column(String, index=True)
    position: Mapped[str] = mapped_column(String, index=True)
    team: Mapped[str] = mapped_column(String, index=True, default="FA")
    bye_week: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str | None] = mapped_column(String, nullable=True)
    age: Mapped[float | None] = mapped_column(Float, nullable=True)
    height: Mapped[str | None] = mapped_column(String, nullable=True)
    weight: Mapped[str | None] = mapped_column(String, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ConsensusRank(Base):
    __tablename__ = "consensus_ranks"
    season: Mapped[int] = mapped_column(Integer, default=2025, primary_key=True)
    player_id: Mapped[str] = mapped_column(String, ForeignKey("players.player_id"), primary_key=True)
    ecr_rank: Mapped[int | None] = mapped_column(Integer, index=True)
    ecr_pos_rank: Mapped[str | None] = mapped_column(String, nullable=True)
    tier: Mapped[int | None] = mapped_column(Integer, index=True)
    source: Mapped[str] = mapped_column(String, default="fantasypros")
    asof_ts: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class ADP(Base):
    __tablename__ = "adp"
    season: Mapped[int] = mapped_column(Integer, default=2025, primary_key=True)
    player_id: Mapped[str] = mapped_column(String, ForeignKey("players.player_id"), primary_key=True)
    source: Mapped[str] = mapped_column(String, primary_key=True)  # fantasypros_half, fantasypros_bestball
    adp: Mapped[float | None] = mapped_column(Float, index=True)
    adp_pos_rank: Mapped[str | None] = mapped_column(String, nullable=True)
    sample_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    asof_ts: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

Index("ix_adp_player_source", ADP.player_id, ADP.source)

class Projection(Base):
    __tablename__ = "projections"
    season: Mapped[int] = mapped_column(Integer, default=2025, primary_key=True)
    player_id: Mapped[str] = mapped_column(String, ForeignKey("players.player_id"), primary_key=True)
    source: Mapped[str] = mapped_column(String, primary_key=True)
    pts: Mapped[float | None] = mapped_column(Float, nullable=True)
    data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    asof_ts: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Injury(Base):
    __tablename__ = "injuries"
    season: Mapped[int] = mapped_column(Integer, default=2025, primary_key=True)
    player_id: Mapped[str] = mapped_column(String, ForeignKey("players.player_id"), primary_key=True)
    status: Mapped[str | None] = mapped_column(String, nullable=True)
    risk_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    notes: Mapped[str | None] = mapped_column(String, nullable=True)
    source: Mapped[str] = mapped_column(String, default="news_free")
    asof_ts: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class News(Base):
    __tablename__ = "news"
    news_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[str | None] = mapped_column(String, ForeignKey("players.player_id"), nullable=True)
    team: Mapped[str | None] = mapped_column(String, nullable=True)
    headline: Mapped[str] = mapped_column(String)
    body: Mapped[str | None] = mapped_column(String, nullable=True)
    source: Mapped[str] = mapped_column(String)
    url: Mapped[str | None] = mapped_column(String, nullable=True)
    asof_ts: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class TeamLeague(Base):
    __tablename__ = "teams_league"
    team_slot_id: Mapped[int] = mapped_column(Integer, primary_key=True)  # 1..12
    team_name: Mapped[str] = mapped_column(String)
    draft_position: Mapped[int] = mapped_column(Integer)

class Pick(Base):
    __tablename__ = "picks"
    pick_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    round_no: Mapped[int] = mapped_column(Integer, index=True)
    overall_no: Mapped[int] = mapped_column(Integer, index=True)
    team_slot_id: Mapped[int] = mapped_column(Integer, ForeignKey("teams_league.team_slot_id"))
    player_id: Mapped[str] = mapped_column(String, ForeignKey("players.player_id"))
    ts: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

Index("ix_picks_team_overall", Pick.team_slot_id, Pick.overall_no)

class UserBoardOverride(Base):
    __tablename__ = "user_board_overrides"
    season: Mapped[int] = mapped_column(Integer, default=2025, primary_key=True)
    player_id: Mapped[str] = mapped_column(String, ForeignKey("players.player_id"), primary_key=True)
    tier_override: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rank_override: Mapped[int | None] = mapped_column(Integer, nullable=True)
    note_text: Mapped[str | None] = mapped_column(String, nullable=True)
    starred: Mapped[bool] = mapped_column(Boolean, default=False)
    updated_ts: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class BlendSettings(Base):
    __tablename__ = "blend_settings"
    setting_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sleeper_wt: Mapped[float] = mapped_column(Float, default=0.0)  # Sleeper ADP (placeholder)
    fpros_wt: Mapped[float] = mapped_column(Float, default=0.8)    # FantasyPros ADP/ECR
    udog_wt: Mapped[float] = mapped_column(Float, default=0.2)     # BestBall proxy
    smoothing_days: Mapped[int] = mapped_column(Integer, default=7)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    updated_ts: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class AppSettings(Base):
    __tablename__ = "app_settings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    quiet_mode: Mapped[bool] = mapped_column(Boolean, default=False)
    news_ttl_sec: Mapped[int] = mapped_column(Integer, default=90)
    data_ttl_min: Mapped[int] = mapped_column(Integer, default=10)
    theme: Mapped[str] = mapped_column(String, default="dark")
    last_refresh_ts: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
