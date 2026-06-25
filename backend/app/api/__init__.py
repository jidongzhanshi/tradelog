from app.api import auth, backups, export, settings, stats, trades, users

routers = [
    auth.router,
    users.router,
    trades.router,
    stats.router,
    settings.router,
    export.router,
    backups.router,
]
