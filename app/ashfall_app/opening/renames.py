"""renames.toml: every id content has renamed since release, as `{kind, from, to}` entries (hand-edited).

The engine's rebase reads them (as engine Renames) to load a save made under older rules; the release lock reads them
to tell a rename from a removal (engine DESIGN.txt, "Renames", "Release lock"). Entries are never removed once
released: one table maps a save from any older release.
"""
import tomllib
from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator

from ..engine import IdKind, Rename
from .convert import note_trigger_id, offer_trigger_id
from .entries import Entry

RENAMES = Path(__file__).resolve().parent / "renames.toml"

type LockKind = Literal["store", "skill", "standing", "card", "lane", "chip", "trigger", "feature", "line", "offer",
                        "answer", "entry", "note", "node"]
"""The kinds of id the release lock holds: the engine's IdKinds a save can name, and `line`, a text key a log line
can carry."""


class RenameEntry(Entry):
    """A rename. A `line` entry with no `to` retires the text key: nothing shows it any more, and a stored line that
    carries it is dropped when a save opens."""

    kind: LockKind
    old: str = Field(alias="from")
    new: str | None = Field(default=None, alias="to")

    @model_validator(mode="after")
    def _only_a_line_is_retired(self) -> "RenameEntry":
        if self.new is None and self.kind != "line":
            raise ValueError(f"{self.kind} {self.old} has no `to`: only a line can be retired")
        return self


class RenamesFile(Entry):
    renames: list[RenameEntry] = []


def load_renames(path: Path = RENAMES) -> list[RenameEntry]:
    """The file's renames, each offer's followed by the rename of the trigger that shows it ("offer_" + old to
    "offer_" + new; a note's likewise with "note_"), which the loader makes and the file never names (engine DESIGN.txt, "Release lock" in part
    "TOWNSFOLK, INSTALLED RULES AND OFFERS")."""
    with path.open("rb") as f:
        entries = RenamesFile.model_validate(tomllib.load(f)).renames
    return [d for r in entries for d in (r, *_offer_trigger(r))]


def _offer_trigger(r: RenameEntry) -> tuple[RenameEntry, ...]:
    """The rename of the trigger the loader made for a renamed offer or note."""
    made = {"offer": offer_trigger_id, "note": note_trigger_id}.get(r.kind)
    if made is None or r.new is None:
        return ()
    return (RenameEntry.model_validate({"kind": "trigger", "from": made(r.old), "to": made(r.new)}),)


def engine_renames(entries: list[RenameEntry]) -> tuple[Rename, ...]:
    """The entries a save can name (every kind but `line`: lines are never stored on a save)."""
    return tuple(Rename(IdKind(r.kind), r.old, r.new) for r in entries if r.kind != "line" and r.new is not None)
