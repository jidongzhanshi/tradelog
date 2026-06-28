from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.settings import UserSetting
from app.models.user import User, UserRole
from app.schemas.settings import SettingRead, SettingUpdate

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=SettingRead)
def get_settings(
    user_id: int | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    target_id = user_id if current_user.role == UserRole.SUPER_ADMIN and user_id else current_user.id
    return ensure_setting(db, target_id)


@router.put("", response_model=SettingRead)
def update_settings(
    payload: SettingUpdate,
    user_id: int | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    target_id = user_id if current_user.role == UserRole.SUPER_ADMIN and user_id else current_user.id
    setting = ensure_setting(db, target_id)
    setting.initial_capital = payload.initial_capital
    setting.currency = "USDT"
    db.commit()
    db.refresh(setting)
    return setting


def ensure_setting(db: Session, user_id: int) -> UserSetting:
    setting = db.query(UserSetting).filter(UserSetting.user_id == user_id).first()
    if not setting:
        setting = UserSetting(user_id=user_id, initial_capital=0, currency="USDT")
        db.add(setting)
        db.commit()
        db.refresh(setting)
    return setting
