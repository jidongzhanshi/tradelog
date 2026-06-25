from collections import defaultdict
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.settings import UserSetting
from app.models.trade import Trade
from app.models.user import User


def range_start(range_key: str | None) -> datetime | None:
    now = datetime.now()
    if range_key == "today":
        return now.replace(hour=0, minute=0, second=0, microsecond=0)
    if range_key == "week":
        start = now - timedelta(days=now.weekday())
        return start.replace(hour=0, minute=0, second=0, microsecond=0)
    if range_key == "month":
        return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if range_key == "year":
        return now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    return None


def filter_trades_by_range(query, range_key: str | None):
    start = range_start(range_key)
    if start:
        return query.filter(Trade.close_time >= start)
    return query


def user_initial_capital(db: Session, user_id: int) -> float:
    setting = db.query(UserSetting).filter(UserSetting.user_id == user_id).first()
    return setting.initial_capital if setting else 0


def calculate_overview(trades: list[Trade], initial_capital: float, user: User | None = None) -> dict:
    sorted_trades = sorted(trades, key=lambda trade: trade.close_time)
    pnl_values = [trade.realized_pnl for trade in sorted_trades]
    wins = [value for value in pnl_values if value > 0]
    losses = [value for value in pnl_values if value < 0]
    total_profit = sum(wins)
    total_loss = sum(losses)
    total_pnl = sum(pnl_values)
    total_trades = len(sorted_trades)
    avg_profit = total_profit / len(wins) if wins else 0
    avg_loss_abs = abs(total_loss / len(losses)) if losses else 0
    equity_curve = build_equity_curve(sorted_trades, initial_capital)

    return {
        "user_id": user.id if user else None,
        "display_name": user.display_name if user else None,
        "initial_capital": initial_capital,
        "account_equity": initial_capital + total_pnl,
        "total_pnl": total_pnl,
        "total_return": (total_pnl / initial_capital * 100) if initial_capital else 0,
        "win_rate": (len(wins) / total_trades * 100) if total_trades else 0,
        "average_pnl_ratio": (avg_profit / avg_loss_abs) if avg_loss_abs else (999 if avg_profit else 0),
        "max_drawdown": calculate_max_drawdown(equity_curve),
        "total_trades": total_trades,
        "total_profit": total_profit,
        "total_loss": total_loss,
        "profit_factor": (total_profit / abs(total_loss)) if total_loss else (999 if total_profit else 0),
        "expectancy": total_pnl / total_trades if total_trades else 0,
        "max_consecutive_wins": max_streak(sorted_trades, True),
        "max_consecutive_losses": max_streak(sorted_trades, False),
    }


def build_equity_curve(trades: list[Trade], initial_capital: float) -> list[dict]:
    equity = initial_capital
    points = [{"time": "初始", "equity": equity, "pnl": 0}]
    for trade in sorted(trades, key=lambda item: item.close_time):
        equity += trade.realized_pnl
        points.append({
            "time": trade.close_time.isoformat(),
            "equity": equity,
            "pnl": trade.realized_pnl,
            "symbol": trade.symbol,
        })
    return points


def calculate_max_drawdown(points: list[dict]) -> float:
    peak = points[0]["equity"] if points else 0
    max_drawdown = 0
    for point in points:
        peak = max(peak, point["equity"])
        drawdown = ((peak - point["equity"]) / peak * 100) if peak else 0
        max_drawdown = max(max_drawdown, drawdown)
    return max_drawdown


def max_streak(trades: list[Trade], target_win: bool) -> int:
    current = 0
    best = 0
    for trade in trades:
        is_win = trade.realized_pnl > 0
        if is_win == target_win:
            current += 1
            best = max(best, current)
        else:
            current = 0
    return best


def monthly_pnl(trades: list[Trade]) -> list[dict]:
    grouped = defaultdict(float)
    for trade in trades:
        grouped[trade.close_time.strftime("%Y-%m")] += trade.realized_pnl
    return [{"month": key, "pnl": value} for key, value in sorted(grouped.items())]


def symbol_ranking(trades: list[Trade]) -> list[dict]:
    grouped = defaultdict(lambda: {"pnl": 0, "count": 0})
    for trade in trades:
        grouped[trade.symbol]["pnl"] += trade.realized_pnl
        grouped[trade.symbol]["count"] += 1
    return sorted(
        [{"symbol": key, **value} for key, value in grouped.items()],
        key=lambda item: item["pnl"],
        reverse=True,
    )


def direction_comparison(trades: list[Trade]) -> list[dict]:
    grouped = defaultdict(lambda: {"pnl": 0, "count": 0, "wins": 0})
    for trade in trades:
        key = trade.direction.value
        grouped[key]["pnl"] += trade.realized_pnl
        grouped[key]["count"] += 1
        grouped[key]["wins"] += 1 if trade.realized_pnl > 0 else 0
    return [
        {
            "direction": key,
            "pnl": value["pnl"],
            "count": value["count"],
            "win_rate": value["wins"] / value["count"] * 100 if value["count"] else 0,
        }
        for key, value in grouped.items()
    ]


def scatter_data(trades: list[Trade]) -> list[dict]:
    return [
        {
            "symbol": trade.symbol,
            "time": trade.close_time.isoformat(),
            "pnl": trade.realized_pnl,
            "roi": trade.roi_percent,
            "direction": trade.direction.value,
            "holding_seconds": trade.holding_seconds,
        }
        for trade in sorted(trades, key=lambda item: item.close_time)
    ]
