"""One fixed history touching every habit (musts, fading routine, a worry, a crowd, an away gap, late additions,
misremembering), for tests that need a realistic span rather than one rule: determinism across processes and the
isolation statements. Rates sit mid-range so rolls decide things both ways."""
from dataclasses import replace

from ashfall_app.saves.journal import ComposedDay, Fade, Habits, Line, Press, Subject
from journal_world import PLAIN, beat, compose_span, crowd, person, routine, shows, worry

SAVE_ID = 9041
DAYS = 12

HABITS: Habits = replace(
    PLAIN, routine=Fade(0.9, 0.6), worry=Press(0.4, 0.5), crowd=Fade(0.8, 0.7), floor=0.3, halflife=4.0,
    beat_refresh=0.5, lines_start=4, lines_floor=1, lines_halflife=5.0, busy_ratio=1.5,
    late_rate=0.5, misremember_rate=0.5, correct_after_days=2,
)


def subjects() -> tuple[Subject, ...]:
    return (
        beat("arrival", repeat=2, late=1), beat("storm", away=2), person("smith", repeat=1, late=1),
        routine("kettle", repeat=3, late=2, misremember=1), routine("wood", repeat=2), routine("snares", repeat=1),
        worry("hunger", repeat=2, late=1), crowd("strangers"),
    )


def lines() -> tuple[Line, ...]:
    arrival, storm, smith, kettle, wood, snares, hunger, strangers = subjects()
    out = [shows(arrival, 0), shows(arrival, 5), shows(smith, 2), shows(storm, 7)]
    out += [shows(kettle, d, "kettle.cracked" if d >= 6 else None, second=60 * d) for d in range(DAYS) if d % 3]
    out += [shows(wood, d, second=7) for d in range(DAYS)]
    out += [shows(snares, d, second=99) for d in (1, 2, 4, 8, 9)]
    out += [shows(hunger, d, second=3) for d in (3, 4, 5, 6, 10)]
    out += [shows(strangers, d, f"who.{i}", second=i) for d in range(DAYS) for i in range(d % 5)]
    return tuple(out)


def composed() -> tuple[ComposedDay, ...]:
    return compose_span(SAVE_ID, DAYS, lines(), subjects(), HABITS)
