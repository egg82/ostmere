"""`load_opening` once per distinct content set per test process (docs/engineering.md, "Fast from the start").

One load parses and checks every chapter (~1 s here, more on a CI runner), and 90-odd test files call it, so each
would otherwise pay it again and creep toward the per-test ceiling. The cache is keyed on the path, the chapters and
a digest of those files' bytes, so an edited file or a test's temp chapter is its own entry. A caller gets a deep copy,
never the cached object: the loaded model is mutable, and a test that edits its opening cannot reach another's.
Installed by tests/conftest.py; the shipped loader is untouched."""
import hashlib
import sys
from pathlib import Path

from ashfall_app.rules import schema
from ashfall_app.rules.schema import CHAPTERS, OPENING, Opening

real_load_opening = schema.load_opening
Key = tuple[Path, tuple[Path, ...], str]
_cache: dict[Key, Opening] = {}


def digest(path: Path, chapters: tuple[Path, ...]) -> str:
    h = hashlib.sha256()
    for p in (path, *chapters):
        h.update(p.read_bytes())
        h.update(b"\0")
    return h.hexdigest()


def cached_load_opening(path: Path = OPENING, chapters: tuple[Path, ...] = CHAPTERS) -> Opening:
    chapters = tuple(chapters)
    key = (path, chapters, digest(path, chapters))
    if key not in _cache:
        _cache[key] = real_load_opening(path, chapters)
    return _cache[key].model_copy(deep=True)


def install() -> None:
    """Every module that already imported `load_opening`, and the schema module itself, so a test file importing it
    later gets the cached one too."""
    for module in list(sys.modules.values()):
        try:
            held = vars(module).get("load_opening")
        except TypeError:
            continue
        if held is real_load_opening:
            setattr(module, "load_opening", cached_load_opening)
