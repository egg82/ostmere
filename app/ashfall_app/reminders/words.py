"""What a notification says: never how long the player has been away, what finished, or anything else about the game.
Each kind has a small pool (`lines.json` for the absence reminder, `hands_free_lines.json` for the hands-free notice); a
line is picked by a hash of the account and the moment it is for, so the job needs no counter and a device is sent the
same line however often it is asked."""

import hashlib
import json
from datetime import datetime
from functools import cache
from pathlib import Path

TITLE = "Ostmere"


@cache
def lines(name: str = "lines.json") -> list[str]:
    found: list[str] = json.loads(Path(__file__).with_name(name).read_text(encoding="utf-8"))
    return found


def _picked(pool: list[str], seed: str) -> dict[str, str]:
    """The message the service worker shows: a title, a line, and where a tap goes."""
    pick = int.from_bytes(hashlib.sha256(seed.encode()).digest()[:8]) % len(pool)
    return {"title": TITLE, "body": pool[pick], "url": "/"}


def payload(account_id: int, visited_at: datetime) -> dict[str, str]:
    """The absence reminder for the visit `visited_at`."""
    return _picked(lines(), f"{account_id}|{visited_at.isoformat()}")


def notice_payload(account_id: int, free_at: int) -> dict[str, str]:
    """The hands-free notice for the instant `free_at` (game seconds)."""
    return _picked(lines("hands_free_lines.json"), f"{account_id}|hands|{free_at}")
