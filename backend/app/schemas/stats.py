from pydantic import BaseModel


class OverviewStats(BaseModel):
    user_id: int | None = None
    display_name: str | None = None
    initial_capital: float
    account_equity: float
    total_pnl: float
    total_return: float
    win_rate: float
    average_pnl_ratio: float
    max_drawdown: float
    total_trades: int
    total_profit: float
    total_loss: float
    profit_factor: float
    expectancy: float
    total_r: float
    average_r: float
    average_risk_percent: float
    over_risk_count: int
    followed_plan_count: int
    deviation_count: int
    plan_adherence_rate: float
    followed_plan_average_r: float
    deviated_average_r: float
    simulated_total_pnl: float
    simulated_equity: float
    simulated_return: float
    max_consecutive_wins: int
    max_consecutive_losses: int


class ComparisonResponse(BaseModel):
    users: list[OverviewStats]
    combined: OverviewStats
