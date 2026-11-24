"""The journal on the wire (CONTRACT.txt, "JOURNAL"): what the content says of the book, its pages and their notes, and
the daily journal's written days. Whether a page or note is written is view.unlocked's, and a page's numbers are
View.fights'. Re-exported from content_models.py and, the days, models.py."""
from enum import StrEnum

from pydantic import BaseModel


class Hand(StrEnum):
    """How a note is written; each is a style the page owns, so a new one is page work as well as content."""

    INK = "ink"
    PENCIL = "pencil"


class Section(StrEnum):
    """The part of the book an entry's page is in, each behind its own bookmark; within one, pages run in writing order.
    The days pages are not entries: they are the written days (JournalDay)."""

    CREATURES = "creatures"
    """The things fought, with their numbers."""
    PLACES = "places"
    """Places, events and expeditions."""


class NoteInfo(BaseModel):
    """A note on a page, in content order. Its words are the text entry of the same id."""

    note: str
    hand: Hand
    """Resolved: the note's own, else its entry's."""
    sketch: str | None
    """A small drawing beside the note, /assets/journal/<sketch>.png; null for none."""


class EntryInfo(BaseModel):
    """A page: a thing known, in content order. Written when view.unlocked holds `entry`."""

    entry: str
    section: Section
    sketch: str | None
    """The page's drawing, /assets/journal/<sketch>.png; null for a page laid out as text alone."""
    runners: list[str]
    """The fight cards and standing fights whose numbers the page shows, in this order; empty for none."""
    notes: list[NoteInfo]
    """In content order, a later chapter's notes after the earlier ones'."""


class JournalInfo(BaseModel):
    """The book the player carries. Null in Content until a chapter declares it."""

    feature: str
    """A feature with a label_key: the Journal button's word."""
    entries: list[EntryInfo]


class Mark(StrEnum):
    """A kind of mark a written day leaves on its page (docs/design/journal.md, "Marks on the page"); each is art the page
    owns, so a new one is page work as well as content."""

    BLOOD = "blood"
    SOOT = "soot"
    WATER = "water"
    MUD = "mud"
    SMUDGE = "smudge"


class Slot(StrEnum):
    """The occasion a day's note was written for (docs/design/journal.md, "The content's side")."""

    FIRST = "first"
    REPEAT = "repeat"
    CATCHUP = "catchup"
    MENTION = "mention"
    LATE = "late"
    MISREMEMBER = "misremember"
    CORRECTION = "correction"
    LOSS = "loss"
    FOLD = "fold"


class DayNote(BaseModel):
    """A note on a written day, in page order. Its words are the text entry `key`."""

    subject: str
    """The journal subject it is about (the content's)."""
    slot: Slot
    key: str
    hand: Hand
    """Resolved: the slot's own, else ink."""
    sketch: str | None
    """A small drawing beside the note, /assets/journal/<sketch>.png; null for none."""
    count: int | None
    """On a fold note, the lost fights it folds (at least 1), drawn beside its words; null on every other (LOSS LINES)."""


class JournalDay(BaseModel):
    """A game day the daily journal wrote: game seconds [day * 86400, (day + 1) * 86400). A later copy of a day still being
    written begins with this one's notes and marks."""

    day: int
    day_notes: list[DayNote]
    """At least one, in page order."""
    marks: list[Mark]
    """The marks the day leaves on its page, each kind at most once, in the order drawn; empty for none."""
