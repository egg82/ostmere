"""The one wall clock (docs/engineering.md, "One injectable clock"): what time it is, as an aware UTC datetime. The app
passes `system` to what it builds; tests pass their own. Never `now()` in SQL."""

from collections.abc import Callable
from datetime import UTC, datetime

type Clock = Callable[[], datetime]


def system() -> datetime:
    return datetime.now(UTC)
