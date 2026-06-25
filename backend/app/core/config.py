import os
import tempfile
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = Path(__file__).resolve().parents[3]
LOCAL_APP_DATA = Path(os.getenv("LOCALAPPDATA", Path.home() / "AppData" / "Local"))


def resolve_data_dir() -> Path:
    configured = os.getenv("TRADELOG_DATA_DIR")
    if configured:
        path = Path(configured)
        path.mkdir(parents=True, exist_ok=True)
        return path

    preferred = LOCAL_APP_DATA / "TradeLog" / "data"
    try:
        preferred.mkdir(parents=True, exist_ok=True)
        return preferred
    except OSError:
        fallback = Path(tempfile.gettempdir()) / "TradeLog" / "data"
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback


class Settings:
    app_name = "TradeLog"
    data_dir = resolve_data_dir()
    database_url = os.getenv("DATABASE_URL") or f"sqlite:///{(data_dir / 'tradelog.db').as_posix()}"
    secret_key = os.getenv("SECRET_KEY", "change-this-secret-in-production")
    access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))
    cors_origins = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "*").split(",")]
    default_admin_username = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
    default_admin_password = os.getenv("DEFAULT_ADMIN_PASSWORD", "admin123")
    backup_keep_days = int(os.getenv("BACKUP_KEEP_DAYS", "30"))


settings = Settings()
(settings.data_dir / "backups").mkdir(parents=True, exist_ok=True)
