"""The content file's journal (api/CONTRACT.txt, "JOURNAL"): the book, its pages and the notes written on them, as Type
Objects. Beside entries.py, whose shapes they reuse."""
from typing import Literal

from .entries import ConditionEntry, Entry

type Hand = Literal["ink", "pencil"]
"""How a note is written. Closed: each hand is a style the page owns, so a new one is page work as well as content."""

type Section = Literal["days", "creatures", "places"]
"""The part of the book a page is in, each behind its own bookmark. Closed: a new one is page work as well as
content."""


class JournalDecl(Entry):
    """`[journal]`: the book the player carries, a feature with a label_key. Declared once, in the chapter holding the
    first entry or an earlier one."""

    feature: str


class JournalEntry(Entry):
    """One page: a thing known. Its words are its notes; `sketch` is /assets/journal/<sketch>.png, and `runners` are the
    fight cards and standing fights whose learned numbers the page shows, in this order. Within a section, pages are
    declared in the order they are written."""

    id: str
    section: Section
    sketch: str | None = None
    """None for a page laid out as text alone."""
    hand: Hand
    """How the page's notes are written where a note names no hand."""
    runners: list[str]


class NoteEntry(Entry):
    """One note on a page, written when `gate` and every `requires` hold (a trigger the loader makes, "note_" + id). Its
    words are the text entry of the same id. The page's first note also unlocks the page."""

    id: str
    entry: str
    gate: ConditionEntry
    requires: list[ConditionEntry] = []
    hand: Hand | None = None
    sketch: str | None = None
    """A small drawing beside the note."""
    beat: str | None = None
    """On a days page, required: the spine beat (content/beats.yaml) the note retells, written at its landing."""
