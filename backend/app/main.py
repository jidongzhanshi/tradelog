from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.api import routers
from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.core.migrations import run_migrations
from app.core.security import hash_password
from app.models import User, UserRole, UserSetting
from app.services.trade_metrics_service import recalculate_all_trade_metrics

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in routers:
    app.include_router(router, prefix="/api")


@app.exception_handler(Exception)
async def unhandled_exception_handler(_request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"{exc.__class__.__name__}: {exc}"},
    )


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)
    run_migrations()
    seed_default_admin()
    recalculate_existing_trade_metrics()


@app.get("/health")
def health():
    return {"status": "ok"}


def seed_default_admin() -> None:
    db = SessionLocal()
    try:
        exists = db.query(User).filter(User.username == settings.default_admin_username).first()
        if exists:
            return
        admin = User(
            username=settings.default_admin_username,
            display_name="超级管理员",
            role=UserRole.SUPER_ADMIN,
            password_hash=hash_password(settings.default_admin_password),
            is_active=True,
            must_change_password=True,
        )
        db.add(admin)
        db.flush()
        db.add(UserSetting(user_id=admin.id, initial_capital=0, currency="USDT"))
        db.commit()
    finally:
        db.close()


def recalculate_existing_trade_metrics() -> None:
    db = SessionLocal()
    try:
        recalculate_all_trade_metrics(db)
        db.commit()
    finally:
        db.close()
