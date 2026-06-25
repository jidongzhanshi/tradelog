from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.trade import Trade
from app.models.user import User, UserRole
from app.services.export_service import trades_to_workbook
from app.services.stats_service import calculate_overview, filter_trades_by_range, user_initial_capital

router = APIRouter(prefix="/export", tags=["export"])


@router.get("/trades.xlsx")
def export_trades(
    range: str | None = Query(default=None),
    user_id: int | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    sheets = {}
    summaries = {}
    if current_user.role == UserRole.TRADER:
        users = [current_user]
    elif user_id:
        users = [db.get(User, user_id)]
    else:
        users = db.query(User).filter(User.role == UserRole.TRADER).all()

    for user in [item for item in users if item]:
        trades = filter_trades_by_range(db.query(Trade).filter(Trade.user_id == user.id), range).order_by(Trade.close_time.desc()).all()
        sheets[f"{user.display_name}交易明细"] = trades
        summaries[user.display_name] = calculate_overview(trades, user_initial_capital(db, user.id), user)

    stream = trades_to_workbook(sheets, summaries)
    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=tradelog.xlsx"},
    )
