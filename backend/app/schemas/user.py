from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.user import UserRole


class UserBase(BaseModel):
    username: str
    display_name: str
    role: UserRole
    is_active: bool = True


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    display_name: str | None = None
    role: UserRole | None = None
    is_active: bool | None = None


class ResetPasswordRequest(BaseModel):
    password: str
    must_change_password: bool = True


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    must_change_password: bool
    created_at: datetime
    updated_at: datetime
