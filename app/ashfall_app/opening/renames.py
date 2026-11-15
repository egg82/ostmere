"""renames.toml: every id content has renamed since release, as `{kind, from, to}` entries (hand-edited).

The engine's rebase reads them (as engine Renames) to load a save made under older rules; the release lock reads them
to tell a rename from a removal (engine DESIGN.txt, "Renames", "Release lock"). Entries are never removed once
released: one table maps a save from any older release.
"""
import tomllib
from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator

from ..engine import IdKind, Rename, Retired, TriggerId
from .convert import note_trigger_id, offer_trigger_id
from .entries import Entry

RENAMES = Path(__file__).resolve().parent / "renames.toml"

type LockKind = Literal["store", "skill", "standing", "card", "lane", "chip", "trigger", "feature", "line", "offer",
                        "answer", "entry", "note", "node", "subject", "slot_key"]
"""The kinds of id the release lock holds: the engine's IdKinds a save can name, and the content's own: `line`, a text
key a log line can carry, and the journal's `subject` ids and `slot_key`s (text keys its slots write), which a stored
day names."""
LOCAL_KINDS: tuple[LockKind, ...] = ("line", "subject", "slot_key")
"""The kinds no save's engine state names, so the engine's rebase never sees their renames."""


RETIRABLE = frozenset({"line", "note", "entry"})
"""The kinds an entry with no `to` may retire: ids no rule depends on once they are gone."""


class RenameEntry(Entry):
    """A rename. An entry with no `to` retires the id: a `line`'s text key is shown nowhere any more and a stored line
    that carries it is dropped when a save opens; a journal `note` or `entry` is written nowhere any more, and a save
    keeps the unlock it had (a retired note retires the trigger the loader made for it too)."""

    kind: LockKind
    old: str = Field(alias="from")
    new: str | None = Field(default=None, alias="to")

    @model_validator(mode="after")
    def _only_some_are_retired(self) -> "RenameEntry":
        if self.new is None and self.kind not in RETIRABLE:
            raise ValueError(f"{self.kind} {self.old} has no `to`: only a line, a note or an entry can be retired")
        return self


class RenamesFile(Entry):
    renames: list[RenameEntry] = []


def load_renames(path: Path = RENAMES) -> list[RenameEntry]:
    """The file's renames and retirements, each with what it does to the triggers the loader makes (with_made)."""
    with path.open("rb") as f:
        return with_made(RenamesFile.model_validate(tomllib.load(f)).renames)


def with_made(entries: list[RenameEntry]) -> list[RenameEntry]:
    """Each entry, an offer's followed by the rename of the trigger that shows it ("offer_" + old to "offer_" + new; a
    note's likewise with "note_", and a retired note by the retirement of its trigger), which the loader makes and the
    file never names (engine DESIGN.txt, "Release lock" in part "TOWNSFOLK, INSTALLED RULES AND OFFERS")."""
    return [d for r in entries for d in (r, *_made_trigger(r))]


def _made_trigger(r: RenameEntry) -> tuple[RenameEntry, ...]:
    """The rename of the trigger the loader made for a renamed offer or note, or the retirement of a retired note's."""
    made = {"offer": offer_trigger_id, "note": note_trigger_id}.get(r.kind)
    if made is None:
        return ()
    if r.new is None:   # a retired note: a trigger is retired only this way, past the file's check
        return (RenameEntry.model_construct(kind="trigger", old=made(r.old), new=None),)
    return (RenameEntry.model_validate({"kind": "trigger", "from": made(r.old), "to": made(r.new)}),)


def engine_renames(entries: list[RenameEntry]) -> tuple[Rename | Retired, ...]:
    """The entries the engine's rebase reads (every kind but LOCAL_KINDS): renames, and the retired triggers (a retired
    note or entry needs nothing of the engine: a save's unlock of it stays as it is)."""
    return tuple(Rename(IdKind(r.kind), r.old, r.new) if r.new is not None else Retired(TriggerId(r.old))
                 for r in entries if r.kind not in LOCAL_KINDS and (r.new is not None or r.kind == "trigger"))
