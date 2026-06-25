import shutil
from datetime import datetime, timedelta
from pathlib import Path

from app.core.config import settings


def create_backup() -> Path:
    db_path = Path(settings.database_url.replace("sqlite:///", ""))
    backup_dir = settings.data_dir / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    target = backup_dir / f"tradelog_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.db"
    if db_path.exists():
        shutil.copy2(db_path, target)
    return target


def list_backups() -> list[dict]:
    backup_dir = settings.data_dir / "backups"
    return [
        {"name": item.name, "size": item.stat().st_size, "created_at": datetime.fromtimestamp(item.stat().st_mtime)}
        for item in sorted(backup_dir.glob("*.db"), key=lambda path: path.stat().st_mtime, reverse=True)
    ]


def prune_backups() -> None:
    cutoff = datetime.now() - timedelta(days=settings.backup_keep_days)
    for item in (settings.data_dir / "backups").glob("*.db"):
        if datetime.fromtimestamp(item.stat().st_mtime) < cutoff:
            item.unlink(missing_ok=True)
