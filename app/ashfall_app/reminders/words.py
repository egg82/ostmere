"""What a reminder says: an invitation, never how long they have been away or anything about the game. A small pool in
`lines.json`; a line is picked by a hash of the account and the visit, so the job needs no counter and a device is
sent the same line however often it is asked."""

import hashlib
import json
from datetime import datetime
from functools import cache
from pathlib import Path

TITLE = "Ostmere"


@cache
def lines() -> list[str]:
    found: list[str] = json.loads(Path(__file__).with_name("lines.json").read_text(encoding="utf-8"))
    return found


def payload(account_id: int, visited_at: datetime) -> dict[str, str]:
    """The message the service worker shows: a title, a line, and where a tap goes."""
    pool = lines()
    pick = int.from_bytes(hashlib.sha256(f"{account_id}|{visited_at.isoformat()}".encode()).digest()[:8]) % len(pool)
    return {"title": TITLE, "body": pool[pick], "url": "/"}
