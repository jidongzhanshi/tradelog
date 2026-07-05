from sqlalchemy.orm import Session

from app.models.settings import UserSetting
from app.models.trade import Trade, TradeStatus


def recalculate_user_trade_metrics(db: Session, user_id: int) -> None:
    setting = (
        db.query(UserSetting)
        .filter(UserSetting.user_id == user_id)
        .first()
    )
    equity = float(setting.initial_capital if setting else 0)
    simulated_equity = equity
    trades = (
        db.query(Trade)
        .filter(Trade.user_id == user_id)
        .order_by(Trade.close_time.asc(), Trade.id.asc())
        .all()
    )

    for trade in trades:
        pnl = float(trade.realized_pnl or 0)
        planned_risk = float(trade.planned_risk_amount or 0)
        planned_profit = float(trade.planned_profit_amount or 0)

        trade.account_equity_before = equity
        trade.risk_percent = planned_risk / equity * 100 if equity else 0
        trade.r_multiple = pnl / planned_risk if planned_risk else 0
        trade.account_return_percent = pnl / equity * 100 if equity else 0
        trade.planned_rr = planned_profit / planned_risk if planned_risk else 0
        trade.simulated_equity_before = simulated_equity
        trade.simulated_risk_amount = simulated_equity * 0.02 if simulated_equity > 0 else 0
        trade.simulated_profit_target = trade.simulated_risk_amount * trade.planned_rr
        trade.simulated_pnl = trade.simulated_risk_amount * trade.r_multiple
        trade.holding_seconds = max(
            0,
            int((trade.close_time - trade.open_time).total_seconds()),
        )
        trade.status = (
            TradeStatus.PROFIT
            if pnl > 0
            else TradeStatus.LOSS
            if pnl < 0
            else TradeStatus.FLAT
        )
        equity += pnl
        simulated_equity += trade.simulated_pnl

    db.flush()


def recalculate_all_trade_metrics(db: Session) -> None:
    user_ids = [
        row[0]
        for row in db.query(Trade.user_id).distinct().all()
    ]
    for user_id in user_ids:
        recalculate_user_trade_metrics(db, user_id)
