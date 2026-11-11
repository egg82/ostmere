"""The loader's checks on the journal (api/CONTRACT.txt, "JOURNAL"), each naming ids and never text: an entry or note
needs the book, the book is a feature with a label, a runner has a fight, a note is on a page declared so far, a sketch
id is not a path, a days note names its beat and no other note does, and every entry has a first note in its own
chapter. A note's words and their digits are the text
checks'. Raises ValueError naming the entry."""
import re
from typing import TYPE_CHECKING

from .fight_refs import fights
from .refs import fail, need, outcomes

if TYPE_CHECKING:
    from .journal_entries import JournalEntry, NoteEntry
    from .schema import Opening

SKETCH_ID = re.compile(r"[a-z0-9_]+")
"""A sketch id is the file's name in /assets/journal/, so it holds no path."""
BEAT_ID = re.compile(r"[A-Za-z0-9-]+")
"""A beat's id as content/beats.yaml writes it (B5, O-book)."""


def check_journal(o: "Opening") -> None:
    """The book is declared before the first entry, is a feature with a label_key, and every entry and note is sound; and
    nothing authored unlocks an entry or a note: only the note triggers the loader makes do."""
    for where, unlocks in [("start", o.start), *((w, out.unlocks) for w, out in outcomes(o))]:
        if any(u.unlock_kind in ("entry", "note") for u in unlocks):
            fail(where, "only a note's trigger, which the loader makes, adds an entry or note unlock")
    if o.journal is None:
        for where, _ in (*((f"entry {e.id}", e) for e in o.entries), *((f"note {n.id}", n) for n in o.notes)):
            fail(where, "no chapter so far declares [journal]")
        return
    feature = next((f for f in o.features if f.id == o.journal.feature), None)
    if feature is None or feature.label_key is None:
        fail("journal", f"feature {o.journal.feature} is unknown or has no label_key: the book needs a word")
    runners = {where.split(" ", 1)[1] for where, _ in fights(o)}
    for e in o.entries:
        if e.sketch is not None:
            _check_sketch(f"entry {e.id}", e.sketch)
        for r in e.runners:
            need(f"entry {e.id}", "runner with a fight", r, sorted(runners))
    sections = {e.id: e.section for e in o.entries}
    for n in o.notes:
        need(f"note {n.id}", "entry", n.entry, list(sections))
        if n.sketch is not None:
            _check_sketch(f"note {n.id}", n.sketch)
        _check_beat(n, sections[n.entry])


def _check_beat(n: "NoteEntry", section: str) -> None:
    """A days note names the beat it retells; no other note names one."""
    if section != "days":
        if n.beat is not None:
            fail(f"note {n.id}", f"names beat {n.beat}, but only a days page's note retells a beat")
    elif n.beat is None:
        fail(f"note {n.id}", "is on a days page and names no beat")
    elif BEAT_ID.fullmatch(n.beat) is None:
        fail(f"note {n.id}", f"beat {n.beat!r} is not a beat id of [A-Za-z0-9-]+")


def _check_sketch(where: str, sketch: str) -> None:
    if SKETCH_ID.fullmatch(sketch) is None:
        fail(where, f"sketch {sketch!r} is not an id of [a-z0-9_]+ (it is a file name, not a path)")


def check_first_notes(entries: "list[JournalEntry]", notes: "list[NoteEntry]") -> None:
    """Each entry has a note in the same file: its first note is what writes the page."""
    named = {n.entry for n in notes}
    for e in entries:
        if e.id not in named:
            fail(f"entry {e.id}", "no note of its chapter names it, so nothing writes the page")
