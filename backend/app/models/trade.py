from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SqlEnum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Direction(str, Enum):
    LONG = "long"
    SHORT = "short"


class ContractType(str, Enum):
    PERPETUAL = "perpetual"
    DELIVERY = "delivery"


class MarginMode(str, Enum):
    CROSS = "cross"
    ISOLATED = "isolated"


class TradeStatus(str, Enum):
    PROFIT = "profit"
    LOSS = "loss"
    FLAT = "flat"


class Trade(Base):
    __tablename__ = "trades"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    symbol: Mapped[str] = mapped_column(String(32), index=True)
    base_asset: Mapped[str] = mapped_column(String(16))
    quote_asset: Mapped[str] = mapped_column(String(16), default="USDT")
    direction: Mapped[Direction] = mapped_column(SqlEnum(Direction))
    order_side: Mapped[str | None] = mapped_column(String(16), nullable=True)
    contract_type: Mapped[ContractType] = mapped_column(SqlEnum(ContractType), default=ContractType.PERPETUAL)
    margin_mode: Mapped[MarginMode] = mapped_column(SqlEnum(MarginMode), default=MarginMode.CROSS)
    leverage: Mapped[float] = mapped_column(Float, default=1)
    realized_pnl: Mapped[float] = mapped_column(Float, default=0)
    roi_percent: Mapped[float] = mapped_column(Float, default=0)
    position_size: Mapped[float] = mapped_column(Float, default=0)
    max_position_size: Mapped[float] = mapped_column(Float, default=0)
    avg_open_price: Mapped[float] = mapped_column(Float, default=0)
    avg_close_price: Mapped[float] = mapped_column(Float, default=0)
    open_time: Mapped[datetime] = mapped_column(DateTime, index=True)
    close_time: Mapped[datetime] = mapped_column(DateTime, index=True)
    holding_seconds: Mapped[int] = mapped_column(Integer, default=0)
    fee: Mapped[float] = mapped_column(Float, default=0)
    status: Mapped[TradeStatus] = mapped_column(SqlEnum(TradeStatus), default=TradeStatus.FLAT)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="trades")
