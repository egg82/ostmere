"""A browser's reminder requests as the page sends them, and a look at the stored rows."""
from datetime import datetime
from typing import Any

from sqlalchemy import Engine

from ashfall_app.db.engine import Database
from tests.game_client import GameClient

PUSH = "https://fcm.googleapis.com/fcm/send/"
WINDOW = {"after_hours": 24, "send_from_hour": 9, "send_until_hour": 21}


def on(endpoint: str = PUSH + "one", window: dict[str, Any] | None = WINDOW, tz: str = "Europe/Paris") -> dict[str, Any]:
    return {"endpoint": endpoint, "p256dh": "BPk-key_1", "auth": "auth_1", "tz": tz, "window": window}


def engine_of(game: GameClient) -> Engine:
    database: Database = game.app.state.db
    return database.engine


def rows(game: GameClient) -> list[dict[str, Any]]:
    with engine_of(game).connect() as c:
        found = c.exec_driver_sql(
            "SELECT account_id, endpoint, p256dh, tz, after_hours, send_from_hour, send_until_hour, visited_at "
            "FROM reminder_devices ORDER BY id")
        keys = list(found.keys())
        return [dict(zip(keys, r, strict=True)) for r in found]


def visited(game: GameClient) -> datetime:
    found = rows(game)
    assert len(found) == 1, found
    at: datetime = found[0]["visited_at"]
    return at
