"""The shipped content (the opening and its chapters) with a test edit applied to every file before the merge, so a
change like a store's rename runs through each file that names it."""
import tomllib
from collections.abc import Callable
from pathlib import Path

from ashfall_app.opening.chapters import merge
from ashfall_app.opening.checks import check_opening
from ashfall_app.opening.schema import CHAPTERS, OPENING, Chapter, Opening

type Edit = Callable[[str], str]


def same(part: str) -> str:
    return part


def _parsed(path: Path, data: Edit, text: Edit) -> dict[str, object]:
    head, sep, words = path.read_text().partition("[text]")
    return tomllib.loads(data(head) + sep + text(words))


def edited(data: Edit = same, text: Edit = same) -> Opening:
    """Each file's data (above its [text] table) through `data` and its text through `text`, merged and checked."""
    o = Opening.model_validate(_parsed(OPENING, data, text))
    for chapter in CHAPTERS:
        o = merge(o, Chapter.model_validate(_parsed(chapter, data, text)))
    check_opening(o)
    return o


def roots_renamed(part: str) -> str:
    """The store `roots` renamed `tubers` in a file's data (its text keys stay)."""
    return part.replace('"roots"', '"tubers"')
