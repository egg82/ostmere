"""tests/content_cache.py: one load per content set, and no test's edits reach another's opening."""
from pathlib import Path

import pytest

from ashfall_app.rules import schema
from ashfall_app.rules.schema import CHAPTERS, OPENING, Opening
from tests import content_cache


@pytest.fixture
def loads(monkeypatch: pytest.MonkeyPatch) -> list[tuple[Path, tuple[Path, ...]]]:
    """Each call the cache passes through to the real loader; the cache starts empty and is restored after."""
    calls: list[tuple[Path, tuple[Path, ...]]] = []
    real = content_cache.real_load_opening

    def counting(path: Path = OPENING, chapters: tuple[Path, ...] = CHAPTERS) -> Opening:
        calls.append((path, chapters))
        return real(path, chapters)

    monkeypatch.setattr(content_cache, "real_load_opening", counting)
    monkeypatch.setattr(content_cache, "_cache", {})
    return calls


def test_the_installed_loader_is_the_cache() -> None:
    assert schema.load_opening is content_cache.cached_load_opening


def test_one_content_set_is_loaded_once(loads: list[tuple[Path, tuple[Path, ...]]]) -> None:
    content_cache.cached_load_opening(OPENING, ())
    content_cache.cached_load_opening(OPENING, ())
    content_cache.cached_load_opening(path=OPENING, chapters=())
    assert len(loads) == 1


def test_another_chapter_set_is_another_load(loads: list[tuple[Path, tuple[Path, ...]]]) -> None:
    content_cache.cached_load_opening(OPENING, ())
    content_cache.cached_load_opening(OPENING, CHAPTERS[:1])
    assert len(loads) == 2


def test_an_edited_file_is_another_load(loads: list[tuple[Path, tuple[Path, ...]]], tmp_path: Path) -> None:
    chapter = tmp_path / "chapter.toml"
    chapter.write_bytes(CHAPTERS[0].read_bytes())
    content_cache.cached_load_opening(OPENING, (chapter,))
    chapter.write_bytes(chapter.read_bytes() + b"\n# edited\n")
    content_cache.cached_load_opening(OPENING, (chapter,))
    assert len(loads) == 2


def test_a_test_that_edits_its_opening_changes_nobody_elses(loads: list[tuple[Path, tuple[Path, ...]]]) -> None:
    """Load, edit every list the loaded model holds, load again: the digest of the second is the first's."""
    first = content_cache.cached_load_opening(OPENING, ())
    before = first.model_dump_json()
    for name in type(first).model_fields:
        value = getattr(first, name)
        if isinstance(value, list):
            value.clear()
    first.version = 1
    second = content_cache.cached_load_opening(OPENING, ())
    assert second is not first
    assert second.model_dump_json() == before
    assert len(loads) == 1
