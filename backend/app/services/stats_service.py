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
    r_values = [float(trade.r_multiple or 0) for trade in sorted_trades]
    win_r_values = [value for value in r_values if value > 0]
    loss_r_values = [value for value in r_values if value < 0]
    total_r = sum(r_values)
    risk_percent_values = [float(trade.risk_percent or 0) for trade in sorted_trades]
    followed_trades = [trade for trade in sorted_trades if trade.followed_plan]
    deviated_trades = [trade for trade in sorted_trades if not trade.followed_plan]
    followed_r = [float(trade.r_multiple or 0) for trade in followed_trades]
    deviated_r = [float(trade.r_multiple or 0) for trade in deviated_trades]
    simulated_total_pnl = sum(float(trade.simulated_pnl or 0) for trade in sorted_trades)
    avg_win_r = sum(win_r_values) / len(win_r_values) if win_r_values else 0
    avg_loss_r_abs = abs(sum(loss_r_values) / len(loss_r_values)) if loss_r_values else 0
    equity_curve = build_equity_curve(sorted_trades, initial_capital)

    return {
        "user_id": user.id if user else None,
        "display_name": user.display_name if user else None,
        "initial_capital": initial_capital,
        "account_equity": initial_capital + total_pnl,
        "total_pnl": total_pnl,
        "total_return": (total_pnl / initial_capital * 100) if initial_capital else 0,
        "win_rate": (len(wins) / total_trades * 100) if total_trades else 0,
        "average_pnl_ratio": (avg_win_r / avg_loss_r_abs) if avg_loss_r_abs else (999 if avg_win_r else 0),
        "max_drawdown": calculate_max_drawdown(equity_curve),
        "total_trades": total_trades,
        "total_profit": total_profit,
        "total_loss": total_loss,
        "profit_factor": (total_profit / abs(total_loss)) if total_loss else (999 if total_profit else 0),
        "expectancy": total_pnl / total_trades if total_trades else 0,
        "total_r": total_r,
        "average_r": total_r / total_trades if total_trades else 0,
        "average_risk_percent": sum(risk_percent_values) / total_trades if total_trades else 0,
        "over_risk_count": sum(1 for value in risk_percent_values if value > 2.000001),
        "followed_plan_count": len(followed_trades),
        "deviation_count": len(deviated_trades),
        "plan_adherence_rate": len(followed_trades) / total_trades * 100 if total_trades else 0,
        "followed_plan_average_r": sum(followed_r) / len(followed_r) if followed_r else 0,
        "deviated_average_r": sum(deviated_r) / len(deviated_r) if deviated_r else 0,
        "simulated_total_pnl": simulated_total_pnl,
        "simulated_equity": initial_capital + simulated_total_pnl,
        "simulated_return": simulated_total_pnl / initial_capital * 100 if initial_capital else 0,
        "max_consecutive_wins": max_streak(sorted_trades, True),
        "max_consecutive_losses": max_streak(sorted_trades, False),
    }


def build_equity_curve(trades: list[Trade], initial_capital: float) -> list[dict]:
    equity = initial_capital
    simulated_equity = initial_capital
    points = [{
        "time": "初始",
        "equity": equity,
        "simulated_equity": simulated_equity,
        "pnl": 0,
        "simulated_pnl": 0,
    }]
    for trade in sorted(trades, key=lambda item: item.close_time):
        equity += trade.realized_pnl
        simulated_equity += trade.simulated_pnl
        points.append({
            "time": trade.close_time.isoformat(),
            "equity": equity,
            "simulated_equity": simulated_equity,
            "pnl": trade.realized_pnl,
            "simulated_pnl": trade.simulated_pnl,
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
    grouped = defaultdict(lambda: {"pnl": 0.0, "simulated_pnl": 0.0, "r": 0.0})
    for trade in trades:
        month = trade.close_time.strftime("%Y-%m")
        grouped[month]["pnl"] += trade.realized_pnl
        grouped[month]["simulated_pnl"] += trade.simulated_pnl
        grouped[month]["r"] += trade.r_multiple
    return [{"month": key, **value} for key, value in sorted(grouped.items())]


def symbol_ranking(trades: list[Trade]) -> list[dict]:
    grouped = defaultdict(lambda: {"pnl": 0.0, "total_r": 0.0, "count": 0})
    for trade in trades:
        grouped[trade.symbol]["pnl"] += trade.realized_pnl
        grouped[trade.symbol]["total_r"] += trade.r_multiple
        grouped[trade.symbol]["count"] += 1
    rows = [
        {
            "symbol": key,
            **value,
            "average_r": value["total_r"] / value["count"] if value["count"] else 0,
        }
        for key, value in grouped.items()
    ]
    return sorted(
        rows,
        key=lambda item: item["total_r"],
        reverse=True,
    )


def direction_comparison(trades: list[Trade]) -> list[dict]:
    grouped = defaultdict(lambda: {"pnl": 0.0, "total_r": 0.0, "count": 0, "wins": 0})
    for trade in trades:
        key = trade.direction.value
        grouped[key]["pnl"] += trade.realized_pnl
        grouped[key]["total_r"] += trade.r_multiple
        grouped[key]["count"] += 1
        grouped[key]["wins"] += 1 if trade.realized_pnl > 0 else 0
    return [
        {
            "direction": key,
            "pnl": value["pnl"],
            "count": value["count"],
            "win_rate": value["wins"] / value["count"] * 100 if value["count"] else 0,
            "total_r": value["total_r"],
            "average_r": value["total_r"] / value["count"] if value["count"] else 0,
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
            "r_multiple": trade.r_multiple,
            "direction": trade.direction.value,
            "holding_seconds": trade.holding_seconds,
        }
        for trade in sorted(trades, key=lambda item: item.close_time)
    ]


def build_r_curve(trades: list[Trade]) -> list[dict]:
    cumulative_r = 0.0
    points = [{"time": "初始", "cumulative_r": 0.0, "r": 0.0}]
    for trade in sorted(trades, key=lambda item: item.close_time):
        cumulative_r += trade.r_multiple
        points.append({
            "time": trade.close_time.isoformat(),
            "cumulative_r": cumulative_r,
            "r": trade.r_multiple,
            "symbol": trade.symbol,
        })
    return points


def r_distribution(trades: list[Trade]) -> list[dict]:
    buckets = {
        "lte_minus_1": 0,
        "minus_1_to_0": 0,
        "0_to_1": 0,
        "1_to_2": 0,
        "gte_2": 0,
    }
    for trade in trades:
        value = trade.r_multiple
        if value <= -1:
            buckets["lte_minus_1"] += 1
        elif value < 0:
            buckets["minus_1_to_0"] += 1
        elif value < 1:
            buckets["0_to_1"] += 1
        elif value < 2:
            buckets["1_to_2"] += 1
        else:
            buckets["gte_2"] += 1
    return [{"bucket": key, "count": value} for key, value in buckets.items()]


def rolling_average_r(trades: list[Trade], window: int = 20) -> list[dict]:
    ordered = sorted(trades, key=lambda item: item.close_time)
    points = []
    for index, trade in enumerate(ordered):
        values = [
            item.r_multiple
            for item in ordered[max(0, index - window + 1):index + 1]
        ]
        points.append({
            "time": trade.close_time.isoformat(),
            "average_r": sum(values) / len(values),
            "sample_size": len(values),
        })
    return points


def risk_percent_trend(trades: list[Trade]) -> list[dict]:
    return [
        {
            "time": trade.close_time.isoformat(),
            "symbol": trade.symbol,
            "risk_percent": trade.risk_percent,
            "followed_plan": trade.followed_plan,
        }
        for trade in sorted(trades, key=lambda item: item.close_time)
    ]


def plan_execution_comparison(trades: list[Trade]) -> list[dict]:
    groups = (
        ("followed", [trade.r_multiple for trade in trades if trade.followed_plan]),
        ("deviated", [trade.r_multiple for trade in trades if not trade.followed_plan]),
    )
    return [
        {
            "group": group,
            "count": len(values),
            "average_r": sum(values) / len(values) if values else 0,
        }
        for group, values in groups
    ]


def deviation_reason_distribution(trades: list[Trade]) -> list[dict]:
    grouped = defaultdict(int)
    for trade in trades:
        if not trade.followed_plan and trade.deviation_reason:
            grouped[trade.deviation_reason] += 1
    return [
        {"reason": reason, "count": count}
        for reason, count in sorted(grouped.items(), key=lambda item: item[1], reverse=True)
    ]
