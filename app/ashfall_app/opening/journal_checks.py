"""The loader's checks on the journal (api/contract/journal.txt, "JOURNAL"), each naming ids and never text: an entry or note
needs the book, the book is a feature with a label, a runner has a fight, a note is on a page declared so far, a sketch
id is not a path, and every entry has a first note in its own chapter. A note's words and their digits are the text
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
            check_sketch(f"entry {e.id}", e.sketch)
        for r in e.runners:
            need(f"entry {e.id}", "runner with a fight", r, sorted(runners))
    entries = [e.id for e in o.entries]
    for n in o.notes:
        need(f"note {n.id}", "entry", n.entry, entries)
        if n.sketch is not None:
            check_sketch(f"note {n.id}", n.sketch)


def check_sketch(where: str, sketch: str) -> None:
    if SKETCH_ID.fullmatch(sketch) is None:
        fail(where, f"sketch {sketch!r} is not an id of [a-z0-9_]+ (it is a file name, not a path)")


def check_first_notes(entries: "list[JournalEntry]", notes: "list[NoteEntry]") -> None:
    """Each entry has a note in the same file: its first note is what writes the page."""
    named = {n.entry for n in notes}
    for e in entries:
        if e.id not in named:
            fail(f"entry {e.id}", "no note of its chapter names it, so nothing writes the page")
