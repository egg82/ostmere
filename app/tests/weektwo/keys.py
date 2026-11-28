"""The key each chapter's saved end is stored under (ends.py): a hash of what that chapter's play reads, so a change to
one chapter re-keys it and the chapters after it, and leaves the ones before it on the keys they had.

key(c) = hash(SHARED, own(c), key(the chapter before c)). SHARED is what every chapter's play reads: the engine, the
opening's loader and shared data, the code that plays every chapter, and SHAPE (below). own(c) is what only c's play
adds: its chapter file (a day's toml) and its moves (the file its play code lives in); week one's own is its tomls and the
players' code. Chaining the key before makes a later chapter's key cover every earlier chapter's inputs.

SHAPE is the rules with every number masked, ids and structure kept. A save is a state shaped by the rules it was played
under, and loads only under rules of the same shape (a store a later chapter adds is a KeyError in an earlier save), so a
change that adds, removes or renames anything declared re-keys every chapter, while one that only changes a number in a
later chapter's file leaves the earlier ends alone. A saved end is read under today's rules, so a later chapter's numbers
reach an earlier play only where a later chapter's content shows inside an earlier span; the nightly run, which plays
every chapter from the start, is where that is checked."""
import hashlib
from dataclasses import fields, is_dataclass
from enum import Enum
from functools import cache
from pathlib import Path
from typing import Any

ORDER = ("week1", "eight", "nine", "eleven", "twelve", "fifteen", "sixteen", "eighteen", "nineteen", "twentytwo",
         "twentythree", "twentyfive", "twentyseven", "twentynine", "thirty", "thirtyone")
"""Every chapter with a saved end, in the order their plays build on each other ("week1" is week one's)."""
APP = Path(__file__).resolve().parents[2]
OPENING = "ashfall_app/rules"
DAYS = "days"
BEATS = "content/beats.yaml"
"""The one story file the plays read (the pace and the level gates); the rest of content/ is read by tests that play nothing."""
WEEK_ONE_CODE = ("tests/dayone", "tests/daytwo", "tests/daythree", "tests/weekone")
WEEK_FIVE_CODE = "tests/weekfive"
"""The week-five policies every week-five chapter's moves read (tests/weektwo/weekfive.py)."""
MOVES = {c: "tests/weektwo/content.py" for c in ORDER[1:ORDER.index("twentytwo")]} | \
        {c: "tests/weektwo/weekfour.py" for c in ORDER[ORDER.index("twentytwo"):ORDER.index("twentynine")]} | \
        {c: "tests/weektwo/weekfive.py" for c in ORDER[ORDER.index("twentynine"):]}
"""The file each chapter's moves live in (tests/weektwo/routes.py DAYS)."""
DAY_FILES = {"week1": ("day_one", "day_two", "day_three", "day_four", "day_five", "b7", "day_six"),
             "eight": ("day_eight",), "nine": ("day_nine",), "eleven": ("day_eleven",), "twelve": ("day_twelve",),
             "fifteen": ("day_fifteen",), "sixteen": ("day_sixteen",), "eighteen": ("day_eighteen",),
             "nineteen": ("day_nineteen",), "twentytwo": ("day_twenty_two",), "twentythree": ("day_twenty_three",),
             "twentyfive": ("day_twenty_five",), "twentyseven": ("day_twenty_seven",),
             "twentynine": ("day_twenty_nine",), "thirty": ("day_thirty",),
             "thirtyone": ("day_thirty_one",)}
"""Each chapter's toml files in the opening (schema.CHAPTERS)."""


def code_files(entry: str) -> list[Path]:
    """The play code under `entry` (a file or a directory), tests excluded: a test file reads a play, it does not make one."""
    found = [APP / entry] if entry.endswith(".py") else sorted((APP / entry).rglob("*.py"))
    return [f for f in found if not (f.name.startswith("test_") or f.name == "conftest.py")]


def digest(files: list[Path]) -> str:
    h = hashlib.sha256()
    for f in files:
        h.update(str(f.relative_to(APP.parent)).encode() + b"\0" + f.read_bytes())
    return h.hexdigest()


def listed(items: Any) -> list[Any]:
    return list(items)


def masked(obj: Any) -> Any:
    """`obj` as nested lists with every number and flag replaced by its type's name: the rules' structure and ids."""
    if isinstance(obj, (bool, int, float)):
        return type(obj).__name__
    if isinstance(obj, Enum):
        return obj.name
    if is_dataclass(obj) and not isinstance(obj, type):
        return [type(obj).__name__, [[f.name, masked(getattr(obj, f.name))] for f in fields(obj)]]
    if isinstance(obj, dict):
        return sorted(([repr(k), masked(v)] for k, v in listed(obj.items())), key=repr)
    if isinstance(obj, (set, frozenset, tuple, list)):
        found = [masked(x) for x in listed(obj)]
        return found if isinstance(obj, (tuple, list)) else sorted(found, key=repr)
    return obj if obj is None or isinstance(obj, str) else repr(obj)


@cache
def shape_digest() -> str:
    from tests.daythree.content import rules3
    return hashlib.sha256(repr(masked(rules3())).encode()).hexdigest()


def shared_files() -> list[Path]:
    own = {f"{APP / OPENING / DAYS / name}.toml" for names in DAY_FILES.values() for name in names}
    opening = sorted(f for f in (APP / OPENING).rglob("*") if f.suffix in (".py", ".toml") and str(f) not in own)
    moves = {APP / m for m in set(MOVES.values())}
    weektwo = [f for f in code_files("tests/weektwo") if f not in moves]
    return [*sorted((APP / "ashfall_app/engine").rglob("*.py")), *opening, *weektwo, *code_files(WEEK_FIVE_CODE),
            *code_files("tools/chapter_saves.py"),
            APP.parent / BEATS]


@cache
def shared() -> str:
    return hashlib.sha256((digest(shared_files()) + shape_digest()).encode()).hexdigest()


def own_files(chapter: str) -> list[Path]:
    toml = [APP / OPENING / DAYS / f"{name}.toml" for name in DAY_FILES[chapter]]
    if chapter == "week1":
        return [*toml, *(f for entry in WEEK_ONE_CODE for f in code_files(entry))]
    return [*toml, APP / MOVES[chapter]]


@cache
def own(chapter: str) -> str:
    """What only `chapter`'s play adds to the shared inputs: its files' hash."""
    return digest(own_files(chapter))


def before(chapter: str) -> str | None:
    i = ORDER.index(chapter)
    return ORDER[i - 1] if i else None


@cache
def key(chapter: str) -> str:
    """16 hex: the inputs `chapter`'s saved end depends on, those of every chapter before it included."""
    back = before(chapter)
    parts = (shared(), own(chapter), key(back) if back else "")
    return hashlib.sha256("\n".join(parts).encode()).hexdigest()[:16]


CACHED = (shape_digest, shared, own, key)


def clear() -> None:
    """Forget what was hashed (a test that changes a file)."""
    for f in CACHED:
        f.cache_clear()


if __name__ == "__main__":
    import json
    print(json.dumps({"shared": shared(), "own": {c: own(c) for c in ORDER}, "key": {c: key(c) for c in ORDER}}))
