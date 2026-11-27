"""The journal's subjects (docs/design/journal.md, "The content's side"): what the `days` pages write about, as Type
Objects. A subject is an instance of a kind carrying its slots, the text keys each occasion is written from; the kinds'
habit numbers are `[journal_habits]` (setting_entries.py). Checked by subject_checks.py."""
from typing import Literal

from pydantic import Field

from .entries import Entry
from .journal_entries import Hand
from ..people import BandEntry, Way

type SubjectKind = Literal["beat", "person", "routine", "worry", "crowd"]
"""Closed: each kind is a habit the composer owns, so a new one is code as well as content."""

type SourceKind = Literal["trigger", "card", "lane", "mentions"]

type SubjectMark = Literal["blood", "soot", "water", "mud"]
"""The page marks a subject can cause (docs/design/journal.md, "Marks on the page"); a smudge comes from a catch-up."""


class SourceEntry(Entry):
    """The cause whose lines feed a subject: a trigger's or a card's lines (`id`), a `line` person's coming or going
    (`id` the lane, and `way`), or the mention lines of one way (`way` alone)."""

    source_kind: SourceKind
    id: str | None = None
    way: Way | None = None


class SlotEntry(Entry):
    """The lines for one occasion, in the journal's voice; several take turns. A hand and a sketch as a note has."""

    keys: list[str] = Field(min_length=1)
    hand: Hand | None = None
    sketch: str | None = None


class SubjectEntry(Entry):
    """One thing the journal writes about. Which slots a kind needs: subject_checks.py."""

    id: str
    kind: SubjectKind
    source: SourceEntry
    away_days: int = Field(default=0, ge=0)
    """Days not written from this subject's day on: an away gap."""
    first: SlotEntry | None = None
    repeat: SlotEntry | None = None
    catchup: SlotEntry | None = None
    mention: list[BandEntry] = []
    """A crowd's lines, one band per how many came or went, as `[people]` words them."""
    late: SlotEntry | None = None
    misremember: SlotEntry | None = None
    correction: SlotEntry | None = None
    mark: SubjectMark | None = None
    """The mark a day that writes this subject may carry on its page."""
