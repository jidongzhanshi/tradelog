from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import can_manage_trade_owner, get_current_user
from app.models.trade import Trade, TradeStatus
from app.models.user import User, UserRole
from app.schemas.trade import TradeCreate, TradeRead, TradeUpdate
from app.services.stats_service import filter_trades_by_range

router = APIRouter(prefix="/trades", tags=["trades"])


@router.get("", response_model=list[TradeRead])
def list_trades(
    range: str | None = Query(default=None),
    user_id: int | None = Query(default=None),
    symbol: str | None = Query(default=None),
    direction: str | None = Query(default=None),
    status: str | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Trade)
    if current_user.role == UserRole.TRADER:
        query = query.filter(Trade.user_id == current_user.id)
    elif user_id:
        query = query.filter(Trade.user_id == user_id)
    query = filter_trades_by_range(query, range)
    if symbol:
        query = query.filter(Trade.symbol == symbol.upper())
    if direction:
        query = query.filter(Trade.direction == direction)
    if status:
        query = query.filter(Trade.status == status)
    return query.order_by(Trade.close_time.desc()).all()


@router.post("", response_model=TradeRead)
def create_trade(
    payload: TradeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role == UserRole.SUPER_ADMIN and not payload.user_id:
        raise HTTPException(status_code=400, detail="管理员新增交易时必须选择归属交易账号")
    owner_id = payload.user_id if current_user.role == UserRole.SUPER_ADMIN else current_user.id
    if current_user.role == UserRole.SUPER_ADMIN:
        owner = db.get(User, owner_id)
        if not owner or owner.role != UserRole.TRADER:
            raise HTTPException(status_code=400, detail="交易只能归属到交易账号")
    if not can_manage_trade_owner(current_user, owner_id):
        raise HTTPException(status_code=403, detail="无权为该用户新增交易")
    trade = Trade(**prepare_trade_payload(payload), user_id=owner_id)
    db.add(trade)
    db.commit()
    db.refresh(trade)
    return trade


@router.get("/{trade_id}", response_model=TradeRead)
def get_trade(trade_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    trade = db.get(Trade, trade_id)
    if not trade:
        raise HTTPException(status_code=404, detail="交易不存在")
    if current_user.role == UserRole.TRADER and trade.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权查看该交易")
    return trade


@router.put("/{trade_id}", response_model=TradeRead)
def update_trade(
    trade_id: int,
    payload: TradeUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    trade = db.get(Trade, trade_id)
    if not trade:
        raise HTTPException(status_code=404, detail="交易不存在")
    if not can_manage_trade_owner(current_user, trade.user_id):
        raise HTTPException(status_code=403, detail="无权编辑该交易")
    for key, value in prepare_trade_payload(payload).items():
        setattr(trade, key, value)
    trade.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(trade)
    return trade


@router.delete("/{trade_id}")
def delete_trade(trade_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    trade = db.get(Trade, trade_id)
    if not trade:
        raise HTTPException(status_code=404, detail="交易不存在")
    if not can_manage_trade_owner(current_user, trade.user_id):
        raise HTTPException(status_code=403, detail="无权删除该交易")
    db.delete(trade)
    db.commit()
    return {"message": "交易已删除"}


def prepare_trade_payload(payload: TradeCreate | TradeUpdate) -> dict:
    data = payload.model_dump(exclude={"user_id"})
    data["symbol"] = data["symbol"].upper()
    data["base_asset"] = data["base_asset"].upper()
    data["quote_asset"] = "USDT"
    data["open_time"] = normalize_datetime(data["open_time"])
    data["close_time"] = normalize_datetime(data["close_time"])
    data["holding_seconds"] = max(0, int((data["close_time"] - data["open_time"]).total_seconds()))
    if not data.get("status"):
        pnl = data.get("realized_pnl", 0)
        data["status"] = TradeStatus.PROFIT if pnl > 0 else TradeStatus.LOSS if pnl < 0 else TradeStatus.FLAT
    return data


def normalize_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value
    return value.astimezone(timezone.utc).replace(tzinfo=None)
