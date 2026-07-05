from collections.abc import Callable

from sqlalchemy import text
from sqlalchemy.engine import Connection

from app.core.database import engine

Migration = tuple[int, str, Callable[[Connection], None]]


def _remove_viewer_role(connection: Connection) -> None:
    # Preserve any legacy account and its data, but prevent it from logging in.
    connection.execute(
        text(
            """
            UPDATE users
            SET role = 'TRADER', is_active = 0
            WHERE role IN ('viewer', 'VIEWER')
            """
        )
    )


def _add_trade_risk_metrics(connection: Connection) -> None:
    columns = {
        row[1]
        for row in connection.execute(text("PRAGMA table_info(trades)"))
    }
    additions = {
        "stop_loss_price": "FLOAT NOT NULL DEFAULT 0",
        "take_profit_price": "FLOAT NOT NULL DEFAULT 0",
        "risk_percent": "FLOAT NOT NULL DEFAULT 2",
        "account_equity_before": "FLOAT NOT NULL DEFAULT 0",
        "planned_risk_amount": "FLOAT NOT NULL DEFAULT 0",
        "r_multiple": "FLOAT NOT NULL DEFAULT 0",
        "planned_rr": "FLOAT NOT NULL DEFAULT 0",
        "account_return_percent": "FLOAT NOT NULL DEFAULT 0",
        "strategy_tag": "VARCHAR(64)",
        "exit_reason": "VARCHAR(32)",
    }
    for column, definition in additions.items():
        if column not in columns:
            connection.execute(
                text(f"ALTER TABLE trades ADD COLUMN {column} {definition}")
            )


def _add_trade_plan_execution_metrics(connection: Connection) -> None:
    columns = {
        row[1]
        for row in connection.execute(text("PRAGMA table_info(trades)"))
    }
    additions = {
        "planned_profit_amount": "FLOAT NOT NULL DEFAULT 0",
        "simulated_equity_before": "FLOAT NOT NULL DEFAULT 0",
        "simulated_risk_amount": "FLOAT NOT NULL DEFAULT 0",
        "simulated_profit_target": "FLOAT NOT NULL DEFAULT 0",
        "simulated_pnl": "FLOAT NOT NULL DEFAULT 0",
        "followed_plan": "BOOLEAN NOT NULL DEFAULT 1",
        "deviation_reason": "VARCHAR(32)",
        "deviation_note": "TEXT",
    }
    for column, definition in additions.items():
        if column not in columns:
            connection.execute(
                text(f"ALTER TABLE trades ADD COLUMN {column} {definition}")
            )


MIGRATIONS: tuple[Migration, ...] = (
    (1, "remove_viewer_role", _remove_viewer_role),
    (2, "add_trade_risk_metrics", _add_trade_risk_metrics),
    (3, "add_trade_plan_execution_metrics", _add_trade_plan_execution_metrics),
)


def run_migrations() -> None:
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version INTEGER PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    applied_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
        )
        applied = {
            row[0]
            for row in connection.execute(
                text("SELECT version FROM schema_migrations")
            )
        }
        for version, name, migrate in MIGRATIONS:
            if version in applied:
                continue
            migrate(connection)
            connection.execute(
                text(
                    """
                    INSERT INTO schema_migrations (version, name)
                    VALUES (:version, :name)
                    """
                ),
                {"version": version, "name": name},
            )
