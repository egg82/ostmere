"""A long absence counted: the instants and full schedules an advance resolves, read off the engine's own functions, so a
busy runner cannot hide them (tests/saves/test_long_absence.py, tests/weekone/test_weekone_long_absence.py)."""
from collections.abc import Callable

from ashfall_app.engine import Event, Rules, Save, advance, api, schedule
from ashfall_app.engine.handlers import Emit, ignore

DAY_S = 86_400


def advanced_counted(save: Save, rules: Rules, days: int) -> dict[str, int]:
    """`save` advanced `days` game days under `rules`, with how many instants it resolved and full schedules it built."""
    counts = {"instants": 0, "schedules": 0}
    events: Callable[[Save, Rules], list[Event]] = getattr(schedule, "_events")   # the full schedule's build
    resolve = api.resolve_instant

    def counted_events(s: Save, r: Rules) -> list[Event]:
        counts["schedules"] += 1
        return events(s, r)

    def counted_resolve(s: Save, r: Rules, arrivals: list[Event], must_evaluate: bool, emit: Emit = ignore) -> Save:
        counts["instants"] += 1
        return resolve(s, r, arrivals, must_evaluate, emit)

    setattr(schedule, "_events", counted_events)
    setattr(api, "resolve_instant", counted_resolve)
    try:
        advance(save, rules, save.time + days * DAY_S)
    finally:
        setattr(schedule, "_events", events)
        setattr(api, "resolve_instant", resolve)
    return counts
