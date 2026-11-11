"""The shipped opening with its journal taken out (the book's declaration, its pages and their notes' words), for the
journal fixture to declare its own book on: the loader allows [journal] once."""
import re
import tempfile
from functools import cache
from pathlib import Path

from ashfall_app.opening.schema import OPENING

START, STOP = "# ---------- the journal ----------\n", "# ---------- features ----------\n"


def strip_journal(text: str) -> str:
    assert text.count(START) == 1 and text.count(STOP) == 1, "the opening's journal block is marked"
    start, stop = text.index(START), text.index(STOP)
    block = text[start:stop]
    notes = re.findall(r'^\[\[notes\]\]\nid = "(\w+)"', block, re.M)
    assert "[journal]" in block and notes, "the block holds the book and a note"
    rest = text[:start] + text[stop:]
    for n in notes:
        rest, found = re.subn(rf"^{n} = .*\n", "", rest, flags=re.M)
        assert found == 1, f"one text entry for {n}"
    return rest


@cache
def bookless_opening() -> Path:
    path = Path(tempfile.mkdtemp(prefix="bookless-")) / OPENING.name
    path.write_text(strip_journal(OPENING.read_text()))
    return path
