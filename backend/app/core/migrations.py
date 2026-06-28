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


MIGRATIONS: tuple[Migration, ...] = (
    (1, "remove_viewer_role", _remove_viewer_role),
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
