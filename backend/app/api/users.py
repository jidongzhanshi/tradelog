from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_read_all, require_super_admin
from app.core.security import hash_password
from app.models.settings import UserSetting
from app.models.user import User, UserRole
from app.schemas.user import ResetPasswordRequest, UserCreate, UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserRead])
def list_users(_: User = Depends(require_read_all), db: Session = Depends(get_db)):
    return db.query(User).order_by(User.created_at.desc()).all()


@router.post("", response_model=UserRead)
def create_user(payload: UserCreate, _: User = Depends(require_super_admin), db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    user = User(
        username=payload.username,
        display_name=payload.display_name,
        role=payload.role,
        is_active=payload.is_active,
        password_hash=hash_password(payload.password),
        must_change_password=True,
    )
    db.add(user)
    db.flush()
    db.add(UserSetting(user_id=user.id, initial_capital=0, currency="USDT"))
    db.commit()
    db.refresh(user)
    return user


@router.put("/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    payload: UserUpdate,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if user_id == current_user.id:
        if payload.role is not None and payload.role != UserRole.SUPER_ADMIN:
            raise HTTPException(status_code=400, detail="不能降低当前登录管理员的权限")
        if payload.is_active is False:
            raise HTTPException(status_code=400, detail="不能禁用当前登录的管理员")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user


@router.post("/{user_id}/reset-password")
def reset_password(
    user_id: int,
    payload: ResetPasswordRequest,
    _: User = Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    user.password_hash = hash_password(payload.password)
    user.must_change_password = payload.must_change_password
    db.commit()
    return {"message": "密码已重置"}


@router.delete("/{user_id}")
def delete_user(user_id: int, current_user: User = Depends(require_super_admin), db: Session = Depends(get_db)):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能删除当前登录的超级管理员")
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    db.delete(user)
    db.commit()
    return {"message": "用户已删除"}
