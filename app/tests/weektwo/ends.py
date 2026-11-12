"""The saved ends week two's chapters play on from (written by tools/chapter_saves.py and nothing else, into a directory
named by key(), outside the source tree; CI builds and caches it, tools/saves_cache.py): each
push route's player at the end of week one and of days eight, nine and eleven, pickled, and typical's save at each of
those chapters' ends written under the rules without the chapters after it (rebased.py), as encoded text.

Where no saved end is present, the plays start from the start (`available`); ASHFALL_REQUIRE_SAVED=1, which CI sets,
makes a missing or stale one a failure instead. A saved end is stale when today's content or code plays it differently.
Three checks say so, each failing with the command that rewrites them (REWRITE):
- the manifest's rules digest is today's (fast, before any play);
- a chapter played on from the saved end before it ends where its own saved end says (test_weektwo_saved.py, and
  tests/weekone_saved for week one's ends, compared with the plays week one's job exports): the chain is checked link by
  link, each link at the cost of the chapter it plays;
- a saved rebased save decodes only under the rules it was written under (the envelope's rules digest), and its
  stamped inputs (rebased.inputs: the replayed decisions, the engine's source and the replay's) are today's."""
import hashlib
import io
import json
import lzma
import os
import pickle
import random
from dataclasses import dataclass
from functools import cache
from pathlib import Path

from ashfall_app.engine import Rules, rules_digest
from tests.daythree.chapter import Later
from tests.daythree.content import rules3
from tests.daytwo.player import DayTwoPlayer

APP = Path(__file__).resolve().parents[2]
PLAY_CODE = ("tests/dayone", "tests/daytwo", "tests/daythree", "tests/weekone", "tests/weektwo", "tools/chapter_saves.py")
"""What plays besides the engine and the rules: the players, policies and chapters' moves, and the writer."""
REWRITE = "PYTHONPATH=. python tools/chapter_saves.py --write   # from app/"
REQUIRE = "ASHFALL_REQUIRE_SAVED"
CONFIG = frozenset({"laters"})
"""A player's attributes that are code, not play: saved by reference and set from today's code at load, so not
compared (a chapter's own moves are closures, equal only to themselves)."""


def engine_digest() -> str:
    """A hex sha256 of the engine's source (it imports nothing but itself)."""
    code = hashlib.sha256()
    for f in sorted((APP / "ashfall_app" / "engine").rglob("*.py")):
        code.update(f.name.encode() + b"\0" + f.read_bytes())
    return code.hexdigest()


def play_digest() -> str:
    """A hex sha256 of PLAY_CODE's source, tests excluded: a test file reads a play, it does not make one."""
    code = hashlib.sha256()
    for entry in PLAY_CODE:
        found = [APP / entry] if entry.endswith(".py") else sorted((APP / entry).rglob("*.py"))
        for f in found:
            if not (f.name.startswith("test_") or f.name == "conftest.py"):
                code.update(str(f.relative_to(APP)).encode() + b"\0" + f.read_bytes())
    return code.hexdigest()


@cache
def key() -> str:
    """The inputs the saved ends depend on, as 16 hex: today's rules (the manifest's stamp), the engine and the play
    code. Equal keys, equal bytes (the writer runs under one hash seed), so the saves are cached under it."""
    parts = (rules_digest(rules3()), engine_digest(), play_digest())
    return hashlib.sha256("\n".join(parts).encode()).hexdigest()[:16]


def root() -> Path:
    return Path(os.environ.get("ASHFALL_SAVES_ROOT") or Path.home() / ".cache" / "ashfall" / "chapter-saves")


def golden() -> Path:
    """The directory holding today's saved ends."""
    return root() / key()


def manifest() -> Path:
    return golden() / "manifest.json"


def available() -> bool:
    """Whether today's saved ends are present and stamped with today's rules. When not, False, so a caller plays from
    the start; under REQUIRE, an AssertionError instead."""
    if not manifest().exists():
        found, why = False, f"no saved ends in {golden()}"
    elif manifest_rules() != rules_digest(rules3()):
        found, why = False, f"the saved ends in {golden()} were written under other rules"
    else:
        found, why = True, ""
    if not found and os.environ.get(REQUIRE):
        raise AssertionError(f"{why}: {REWRITE}")
    return found


def player_path(chapter: str, name: str) -> Path:
    return golden() / f"{chapter}-{name}.pickle.xz"


def rebased_path(chapter: str) -> Path:
    return golden() / f"rebased-{chapter}.json"


Span = tuple[str, int, int | None]
"""(chapter, first heavy step, the one after the last or None for all the rest): a slice of verdicts.heavy_steps."""
READINGS: dict[str, tuple[Span, ...]] = {
    "readings-early": (("eight", 0, None), ("nine", 0, None), ("eleven", 0, None)),
    "readings-twelve-a": (("twelve", 0, 3), ("twelve", 8, None)),
    "readings-twelve-b": (("twelve", 3, 5),),
    "readings-twelve-c": (("twelve", 5, 6),),
    "readings-twelve-d": (("twelve", 6, 7),),
    "readings-twelve-e": (("twelve", 7, 8),),
    "readings-fifteen-a": (("fifteen", 0, 12),),
    "readings-fifteen-b": (("fifteen", 12, 13),),
    "readings-fifteen-c": (("fifteen", 13, None),),
}
"""The typical route's heavy-step readings (verdicts.decided_in) saved beside the ends, in parts CI writes in jobs of
their own: no reading needs another, and day twelve's take minutes each. Each chapter's spans run from 0 with no gap and
the last open, so a step added by content is read by its chapter's last span."""


def readings_path(chapter: str, start: int) -> Path:
    return golden() / f"readings-{chapter}-{start}.json"


def saved_readings(chapter: str) -> dict[tuple[str, int], bool]:
    """Every saved reading of `chapter`'s heavy steps, by (visit label, step index)."""
    found: dict[tuple[str, int], bool] = {}
    for f in sorted(golden().glob(f"readings-{chapter}-*.json")):
        for label, i, decides in json.loads(f.read_text())["readings"]:
            found[str(label), int(i)] = bool(decides)
    return found


def readings_json(found: dict[tuple[str, int], bool]) -> str:
    return json.dumps({"readings": [[label, i, decides] for (label, i), decides in found.items()]}, indent=1) + "\n"


class _Out(pickle.Pickler):
    def __init__(self, f: io.BytesIO, p: DayTwoPlayer) -> None:
        super().__init__(f, protocol=5)
        self.rules, self.laters = p.rules, p.laters

    def persistent_id(self, obj: object) -> str | None:
        return "rules" if obj is self.rules else "laters" if obj is self.laters else None


class _In(pickle.Unpickler):
    def __init__(self, f: io.BytesIO, laters: tuple[Later, ...]) -> None:
        super().__init__(f)
        self.laters = laters

    def persistent_load(self, pid: object) -> object:
        if pid == "rules":
            return rules3()
        if pid == "laters":
            return self.laters
        raise pickle.UnpicklingError(f"unknown reference {pid!r}")


def dump(p: DayTwoPlayer) -> bytes:
    """The player pickled with its rules and chapters by reference, compressed."""
    assert p.rules is rules3(), "a saved end plays on today's content"
    f = io.BytesIO()
    _Out(f, p).dump(p)
    return lzma.compress(f.getvalue(), preset=6)


def load_from(path: Path, laters: tuple[Later, ...]) -> DayTwoPlayer:
    """The player pickled at `path`, on today's rules and given `laters` (today's chapters)."""
    p = _In(io.BytesIO(lzma.decompress(path.read_bytes())), laters).load()
    assert isinstance(p, DayTwoPlayer)
    return p


def load(chapter: str, name: str, laters: tuple[Later, ...]) -> DayTwoPlayer:
    """The saved player at `chapter`'s end on route `name`, on today's rules and given `laters` (today's chapters)."""
    return load_from(player_path(chapter, name), laters)


def exported_path(name: str) -> Path:
    """Where week one's job leaves route `name`'s play (tests/weekone/test_weekone_export.py), for the job that holds the
    saved week one to it (tests/weekone_saved). Under the key, so a play of other code is never read."""
    base = Path(os.environ.get("ASHFALL_WEEKONE_PLAYS") or Path.home() / ".cache" / "ashfall" / "week-one-plays")
    return base / key() / f"week1-{name}.pickle.xz"


def differs(a: DayTwoPlayer, b: DayTwoPlayer, skip: frozenset[str] = frozenset()) -> list[str]:
    """The attributes, by name, on which two players' plays differ: every attribute but CONFIG and `skip`, a random
    generator by its state (it draws the play's later glances)."""
    va, vb = vars(a), vars(b)
    out = sorted((set(va) ^ set(vb)) - CONFIG)
    for k in sorted((set(va) & set(vb)) - CONFIG - skip):
        x, y = va[k], vb[k]
        same = x.getstate() == y.getstate() if isinstance(x, random.Random) else x == y
        if not same:
            out.append(k)
    return out


@dataclass(frozen=True)
class SavedRebased:
    inputs: str
    """rebased.inputs of the replay that wrote it."""
    text: str
    """The save as encode() wrote it under the rules without the chapters after its own."""


def rebased_text(chapter: str) -> SavedRebased:
    found = json.loads(rebased_path(chapter).read_text())
    return SavedRebased(str(found["inputs"]), str(found["text"]))


def rebased_json(saved: SavedRebased) -> str:
    return json.dumps({"inputs": saved.inputs, "text": saved.text}, indent=1) + "\n"


def manifest_json(rules: Rules) -> str:
    return json.dumps({"rules": rules_digest(rules), "rewrite": REWRITE}, indent=1) + "\n"


def manifest_rules() -> str:
    return str(json.loads(manifest().read_text())["rules"])
