"""A wall clock a test moves by hand (ashfall_app.clock.Clock)."""
from datetime import UTC, datetime, timedelta

T0 = datetime(2026, 10, 1, 12, tzinfo=UTC)


class FakeClock:
    def __init__(self, now: datetime = T0) -> None:
        self.now = now

    def __call__(self) -> datetime:
        return self.now

    def tick(self, seconds: float = 0, **delta: float) -> datetime:
        self.now += timedelta(seconds=seconds, **delta)
        return self.now
