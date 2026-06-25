from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.trade import ContractType, Direction, MarginMode, TradeStatus


class TradeBase(BaseModel):
    symbol: str
    base_asset: str
    quote_asset: str = "USDT"
    direction: Direction
    order_side: str | None = None
    contract_type: ContractType = ContractType.PERPETUAL
    margin_mode: MarginMode = MarginMode.CROSS
    leverage: float = 1
    realized_pnl: float = 0
    roi_percent: float = 0
    position_size: float = 0
    max_position_size: float = 0
    avg_open_price: float = 0
    avg_close_price: float = 0
    open_time: datetime
    close_time: datetime
    fee: float = 0
    status: TradeStatus | None = None
    note: str | None = None


class TradeCreate(TradeBase):
    user_id: int | None = None


class TradeUpdate(TradeBase):
    pass


class TradeRead(TradeBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    holding_seconds: int
    created_at: datetime
    updated_at: datetime
