"""The journal on the wire (CONTRACT.txt, "JOURNAL"): what the content says of the book, its pages and their notes. Whether
a page or note is written is view.unlocked's, and a page's numbers are View.fights'. Re-exported from content_models.py."""
from enum import StrEnum

from pydantic import BaseModel


class Hand(StrEnum):
    """How a note is written; each is a style the page owns, so a new one is page work as well as content."""

    INK = "ink"
    PENCIL = "pencil"


class Section(StrEnum):
    """The part of the book a page is in, each behind its own bookmark; within one, pages run in writing order."""

    DAYS = "days"
    """The daily journal: the story's bigger beats, retold."""
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
