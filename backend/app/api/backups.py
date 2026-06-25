from fastapi import APIRouter, Depends

from app.core.deps import require_super_admin
from app.models.user import User
from app.services.backup_service import create_backup, list_backups

router = APIRouter(prefix="/backups", tags=["backups"])


@router.get("")
def backups(_: User = Depends(require_super_admin)):
    return list_backups()


@router.post("/manual")
def manual_backup(_: User = Depends(require_super_admin)):
    target = create_backup()
    return {"message": "备份已创建", "name": target.name}
