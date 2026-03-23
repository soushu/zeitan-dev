"""SQLAlchemy 2.0 ORM モデル定義."""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.utils.database import Base


class CalcSession(Base):
    """計算セッションテーブル."""

    __tablename__ = "calc_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    calc_method: Mapped[str] = mapped_column(String(50), nullable=False)
    total_profit_loss: Mapped[float] = mapped_column(Float, nullable=False)
    transaction_count: Mapped[int] = mapped_column(Integer, nullable=False)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # リレーション（cascade: セッション削除時に関連データも削除）
    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction", back_populates="session", cascade="all, delete-orphan"
    )
    results: Mapped[list["TradeResultRecord"]] = relationship(
        "TradeResultRecord", back_populates="session", cascade="all, delete-orphan"
    )


class Transaction(Base):
    """取引データテーブル."""

    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("calc_sessions.id"), nullable=False
    )
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    exchange: Mapped[str] = mapped_column(String(100), nullable=False)
    symbol: Mapped[str] = mapped_column(String(50), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    fee: Mapped[float] = mapped_column(Float, nullable=False)

    session: Mapped["CalcSession"] = relationship(
        "CalcSession", back_populates="transactions"
    )


class TradeResultRecord(Base):
    """計算結果テーブル."""

    __tablename__ = "trade_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("calc_sessions.id"), nullable=False
    )
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    exchange: Mapped[str] = mapped_column(String(100), nullable=False)
    symbol: Mapped[str] = mapped_column(String(50), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    fee: Mapped[float] = mapped_column(Float, nullable=False)
    profit_loss: Mapped[float] = mapped_column(Float, nullable=False)
    # MovingAverage 用
    average_cost_after: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    # TotalAverage 用
    average_cost_used: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    session: Mapped["CalcSession"] = relationship(
        "CalcSession", back_populates="results"
    )
