from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_read_all
from app.models.trade import Trade
from app.models.user import User, UserRole
from app.schemas.stats import ComparisonResponse, OverviewStats
from app.services import stats_service

router = APIRouter(prefix="/stats", tags=["stats"])


def scoped_trades(db: Session, current_user: User, range_key: str | None, user_id: int | None = None) -> list[Trade]:
    query = db.query(Trade)
    if current_user.role == UserRole.TRADER:
        query = query.filter(Trade.user_id == current_user.id)
    elif user_id:
        query = query.filter(Trade.user_id == user_id)
    query = stats_service.filter_trades_by_range(query, range_key)
    return query.order_by(Trade.close_time.asc()).all()


@router.get("/overview", response_model=OverviewStats)
def overview(
    range: str | None = Query(default=None),
    user_id: int | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    target_user = current_user
    if current_user.role != UserRole.TRADER and user_id:
        target_user = db.get(User, user_id) or current_user
    trades = scoped_trades(db, current_user, range, target_user.id if current_user.role != UserRole.TRADER else None)
    initial_capital = stats_service.user_initial_capital(db, target_user.id)
    return stats_service.calculate_overview(trades, initial_capital, target_user)


@router.get("/charts")
def charts(
    range: str | None = Query(default=None),
    user_id: int | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    target_id = user_id if current_user.role != UserRole.TRADER else current_user.id
    trades = scoped_trades(db, current_user, range, target_id)
    if target_id:
        initial_capital = stats_service.user_initial_capital(db, target_id)
    elif current_user.role == UserRole.TRADER:
        initial_capital = stats_service.user_initial_capital(db, current_user.id)
    else:
        trader_users = db.query(User).filter(User.role == UserRole.TRADER).all()
        initial_capital = sum(stats_service.user_initial_capital(db, user.id) for user in trader_users)
    return {
        "equity_curve": stats_service.build_equity_curve(trades, initial_capital),
        "monthly_pnl": stats_service.monthly_pnl(trades),
        "symbol_ranking": stats_service.symbol_ranking(trades),
        "direction_comparison": stats_service.direction_comparison(trades),
        "scatter": stats_service.scatter_data(trades),
    }


@router.get("/comparison", response_model=ComparisonResponse)
def comparison(
    range: str | None = Query(default=None),
    _: User = Depends(require_read_all),
    db: Session = Depends(get_db),
):
    users = db.query(User).filter(User.role == UserRole.TRADER).all()
    user_stats = []
    all_trades = []
    combined_capital = 0
    for user in users:
        trades = stats_service.filter_trades_by_range(db.query(Trade).filter(Trade.user_id == user.id), range).all()
        all_trades.extend(trades)
        capital = stats_service.user_initial_capital(db, user.id)
        combined_capital += capital
        user_stats.append(stats_service.calculate_overview(trades, capital, user))
    combined = stats_service.calculate_overview(all_trades, combined_capital, None)
    combined["display_name"] = "合计"
    return {"users": user_stats, "combined": combined}
