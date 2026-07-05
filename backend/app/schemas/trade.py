from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

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
    stop_loss_price: float = 0
    take_profit_price: float = 0
    planned_risk_amount: float = Field(gt=0)
    planned_profit_amount: float = Field(gt=0)
    open_time: datetime
    close_time: datetime
    fee: float = 0
    status: TradeStatus | None = None
    strategy_tag: str | None = Field(default=None, max_length=64)
    exit_reason: str | None = Field(default=None, max_length=32)
    followed_plan: bool = True
    deviation_reason: str | None = Field(default=None, max_length=32)
    deviation_note: str | None = None
    note: str | None = None

    @model_validator(mode="after")
    def validate_times(self):
        if self.close_time < self.open_time:
            raise ValueError("平仓时间不能早于开仓时间")
        if not self.followed_plan and not self.deviation_reason:
            raise ValueError("未按计划执行时必须选择原因分类")
        if self.followed_plan:
            self.deviation_reason = None
            self.deviation_note = None
        return self


class TradeCreate(TradeBase):
    user_id: int | None = None


class TradeUpdate(TradeBase):
    pass


class TradeRead(TradeBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    holding_seconds: int
    account_equity_before: float
    risk_percent: float
    r_multiple: float
    planned_rr: float
    account_return_percent: float
    simulated_equity_before: float
    simulated_risk_amount: float
    simulated_profit_target: float
    simulated_pnl: float
    created_at: datetime
    updated_at: datetime
