"""Hypothesis strategies for the journal contract's properties: a generated history (save id, a few days of lines over a
small pool of subjects of every kind, and habits anywhere in their ranges), and `examples(n)` for a test that is costly
per example at the push profile."""
import os
from dataclasses import dataclass

from hypothesis import settings, strategies as st

from ashfall_app.saves.journal import Fade, Habits, Line, Press, Subject
from journal_world import beat, crowd, person, routine, shows, worry


def examples(n: int) -> settings:
    """`n` examples on the push profile; the loaded profile's count (the nightly `ci`) otherwise."""
    return settings(max_examples=n) if os.environ.get("HYPOTHESIS_PROFILE", "contract") == "contract" else settings()


@dataclass(frozen=True)
class History:
    save_id: int
    days: int
    lines: tuple[Line, ...]
    subjects: tuple[Subject, ...]
    habits: Habits


unit = st.floats(0.0, 1.0, allow_nan=False)


@st.composite
def habits(draw: st.DrawFn) -> Habits:
    start = draw(st.integers(1, 6))
    return Habits(
        routine=Fade(draw(st.sampled_from([0.0, 0.5, 1.0])), draw(unit)),
        worry=Press(draw(unit), draw(st.floats(0.0, 2.0))),
        crowd=Fade(draw(unit), draw(unit)),
        floor=draw(unit), halflife=draw(st.floats(0.5, 8.0)), beat_refresh=draw(st.floats(0.0, 1.5)),
        lines_start=start, lines_floor=draw(st.integers(1, start)), lines_halflife=draw(st.floats(0.5, 8.0)),
        busy_ratio=draw(st.floats(0.5, 4.0)),
        late_rate=draw(st.sampled_from([0.0, 0.5, 1.0])), misremember_rate=draw(st.sampled_from([0.0, 0.5, 1.0])),
        correct_after_days=draw(st.integers(1, 3)),
    )


@st.composite
def subjects(draw: st.DrawFn) -> tuple[Subject, ...]:
    """A few subjects of every kind, ids sorted so the pool's order is fixed; slots vary in size and presence."""
    small = st.integers(0, 3)
    pool = [
        beat("b0", repeat=draw(st.integers(0, 2)), late=draw(st.integers(0, 1))),
        beat("b1", repeat=draw(st.integers(0, 2)), away=draw(st.sampled_from([0, 0, 1, 2]))),
        person("p0", repeat=draw(st.integers(0, 2)), late=draw(st.integers(0, 1))),
        routine("r0", repeat=draw(small), late=draw(st.integers(0, 1)), misremember=draw(st.sampled_from([0, 2]))),
        routine("r1", repeat=draw(small), misremember=draw(st.sampled_from([0, 1]))),
        routine("r2", repeat=draw(small), late=draw(st.integers(0, 2)), away=draw(st.sampled_from([0, 0, 0, 1]))),
        worry("w0", repeat=draw(small), late=draw(st.integers(0, 1))),
        worry("w1", repeat=draw(small)),
        crowd("c0", bands=draw(st.sampled_from([((1, 2), (3, 2)), ((2, 3),), ((1, 1), (2, 2), (4, 3))]))),
    ]
    chosen = draw(st.lists(st.booleans(), min_size=len(pool), max_size=len(pool)))
    return tuple(s for s, keep in zip(pool, chosen) if keep) or (pool[3],)


@st.composite
def histories(draw: st.DrawFn, max_days: int = 10) -> History:
    subs = draw(subjects())
    days = draw(st.integers(2, max_days))
    lines: list[Line] = []
    for d in range(days):
        for s in subs:
            if s.kind == "crowd":
                for i in range(draw(st.integers(0, 4))):
                    lines.append(shows(s, d, f"{s.id}.who.{draw(st.integers(0, 5))}", second=i))
            elif draw(st.integers(0, 2)) > 0:
                lines.append(shows(s, d, f"{s.id}.line.{draw(st.integers(0, 2))}", second=draw(st.integers(0, 86399))))
    return History(draw(st.integers(0, 2**40)), days, tuple(draw(st.permutations(lines))), subs, draw(habits()))
