from pydantic import BaseModel, ConfigDict


class SettingUpdate(BaseModel):
    initial_capital: float
    currency: str = "USDT"


class SettingRead(SettingUpdate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
