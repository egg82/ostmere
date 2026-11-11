"""Week two's routes: each week-one route (weekone/routes.py) played on from G2's visit through day eight to the visit B9
is seen in. The week-one play is copied, not replayed: up to G2 being seen both plays make the same moves, since day
eight's chapter starts at G2, so the copy re-enters G2's visit at the moment the week-one play left it and plays on with
day eight's moves (DayOnePlayer.play_on). The one difference from a play from the start: day eight's moves in G2's
visit wait until that moment (the week-one play leaves once nothing of its own is left to act on). Played once per
pytest session, in a fixture's setup (docs/engineering.md, "Fast from the start"). Day nine's play is day eight's copied
the same way at B9's visit and given day nine, day eleven's day nine's at B10's visit, and day twelve's day eleven's at B11's.
Day fifteen's is day twelve's copied at S4's visit and given day fifteen, the first of week three's.
Each chapter plays on from the saved end of the one before (ends.py) where the route's is saved and the saves are present, so a session plays each
chapter once and week one not at all; `played` is the same chain from the start, which the saved ends are written from."""
import copy
from functools import cache

from tests.daythree.chapter import Later
from tests.daytwo.player import DayTwoPlayer
from tests.weekone import content as w1
from tests.weekone.routes import week1
from tests.weektwo import content as w2
from tests.weektwo import ends

PUSH_ROUTES = ("typical", "sharp", "babysitter", "whenever")
NINE_PUSH_ROUTES = ("typical", "sharp", "whenever")
"""Day nine's plays on a push: the banded routes and the 2 AM test's (the babysitter's own play is the nightly run's)."""
ELEVEN_PUSH_ROUTES = NINE_PUSH_ROUTES
"""Day eleven's, the same."""
TWELVE_PUSH_ROUTES = NINE_PUSH_ROUTES
"""Day twelve's, the same."""
FIFTEEN_PUSH_ROUTES = NINE_PUSH_ROUTES
"""Day fifteen's, the same."""
REPORT_ROUTES = ("typical", "sharp", "evenings", "whenever", "babysitter")


def play_on(p: DayTwoPlayer, laters: tuple[Later, ...]) -> DayTwoPlayer:
    """A copy of `p` given `laters` and played on until the last one's stop beat's visit ends. `p` is untouched; the
    copy shares its rules object (the engine caches by its identity) and the saves, views and lines it has recorded,
    which are immutable values: copying them would cost most of the copy and change nothing."""
    kept = [p.rules, *p.lines, *p.decided, *(x for moment in p.history for x in moment)]
    q = copy.deepcopy(p, {id(x): x for x in kept})
    q.laters = laters
    q.play_on()
    return q


CHAPTERS = ("eight", "nine", "eleven", "twelve", "fifteen")
"""Week two's chapters and week three's first, in the order their plays build on each other."""
BEFORE = {"eight": "week1", "nine": "eight", "eleven": "nine", "twelve": "eleven", "fifteen": "twelve"}
SAVED = {"week1": PUSH_ROUTES, "eight": NINE_PUSH_ROUTES, "nine": ELEVEN_PUSH_ROUTES, "eleven": TWELVE_PUSH_ROUTES,
         "twelve": FIFTEEN_PUSH_ROUTES}
"""The routes whose end of each chapter is saved (ends.py): the ones the next chapter plays on a push, seed 0."""
DAYS = {"eight": w2.day_eight, "nine": w2.day_nine, "eleven": w2.day_eleven, "twelve": w2.day_twelve,
        "fifteen": w2.day_fifteen}


def laters(chapter: str, name: str) -> tuple[Later, ...]:
    """The chapters a play through `chapter` ("week1" or one of CHAPTERS) is given: week one's, then week two's to it."""
    own = CHAPTERS[:CHAPTERS.index(chapter) + 1] if chapter in CHAPTERS else ()
    return (*w1.chapters(), *(DAYS[c](name) for c in own))


@cache
def played(chapter: str, name: str, seed: int = 0) -> DayTwoPlayer:
    """A play through `chapter` from the start, reading no saved end: what tools/chapter_saves.py saves."""
    if chapter == "week1":
        return week1(name, seed)
    return play_on(played(BEFORE[chapter], name, seed), laters(chapter, name))


@cache
def saved_end(chapter: str, name: str) -> DayTwoPlayer:
    """The saved play through `chapter` on route `name`, seed 0 (ends.py); where none is saved, that play from the
    start."""
    return ends.load(chapter, name, laters(chapter, name)) if ends.available() else played(chapter, name)


def start(chapter: str, name: str, seed: int) -> DayTwoPlayer:
    """The play `chapter` plays on from: the saved end of the chapter before when the route's is saved, else that
    chapter played on from its own start (week one from the start)."""
    before = BEFORE[chapter]
    if seed == 0 and name in SAVED[before]:
        return saved_end(before, name)
    return week1(name, seed) if before == "week1" else from_saved(before, name, seed)


@cache
def from_saved(chapter: str, name: str, seed: int = 0) -> DayTwoPlayer:
    return play_on(start(chapter, name, seed), laters(chapter, name))


def week_one(name: str) -> DayTwoPlayer:
    """Week one's play on a saved route, read from its saved end (week one's job holds it to the play)."""
    return saved_end("week1", name)


def week2(name: str, seed: int = 0) -> DayTwoPlayer:
    """A play to G2's visit played on through day eight to B9's visit."""
    return from_saved("eight", name, seed)


def nine(name: str, seed: int = 0) -> DayTwoPlayer:
    """Day eight's play played on through day nine to B10's visit."""
    return from_saved("nine", name, seed)


def eleven(name: str, seed: int = 0) -> DayTwoPlayer:
    """Day nine's play played on through day eleven to B11's visit."""
    return from_saved("eleven", name, seed)


def twelve(name: str, seed: int = 0) -> DayTwoPlayer:
    """Day eleven's play played on through day twelve to S4's visit, week two's last."""
    return from_saved("twelve", name, seed)


def fifteen(name: str, seed: int = 0) -> DayTwoPlayer:
    """Day twelve's play played on through day fifteen to B14's visit, the edge of written content."""
    return from_saved("fifteen", name, seed)
