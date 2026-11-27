"""A chapter's saved end is keyed by what its play reads (keys.py): a change to an earlier chapter re-keys every later one, a
change to a later chapter leaves every earlier key alone, and a change to what every chapter reads re-keys them all. The
tests change a copy of the files the keys read and compare keys, so a missed input is a key that stays equal."""
import dataclasses
import shutil
from collections.abc import Generator
from pathlib import Path

import pytest

from ashfall_app.rules.schema import CHAPTERS as CHAPTER_FILES
from tests.daythree.content import rules3
from tests.weektwo import keys
from tests.weektwo.routes import BEFORE, DAYS, SAVED

ORDER = keys.ORDER
COPIED = ("ashfall_app/engine", "ashfall_app/rules", "tests/dayone", "tests/daytwo", "tests/daythree", "tests/weekone",
          "tests/weektwo", "tools/chapter_saves.py")


@pytest.fixture
def tree(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Generator[Path, None, None]:
    """The files the keys read, copied; the keys are read from the copy, with SHAPE held fixed (its own test is below)."""
    app = tmp_path / "app"
    (tmp_path / "content").mkdir()
    shutil.copy(keys.APP.parent / keys.BEATS, tmp_path / keys.BEATS)
    for entry in COPIED:
        src = keys.APP / entry
        dst = app / entry
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "captured"))
        else:
            shutil.copy(src, dst)
    monkeypatch.setattr(keys, "APP", app)
    monkeypatch.setattr(keys, "shape_digest", lambda: "shape")
    keys.clear()
    yield tmp_path
    keys.clear()


def all_keys() -> dict[str, str]:
    keys.clear()
    return {c: keys.key(c) for c in ORDER}


def after_editing(tree: Path, entry: str) -> tuple[dict[str, str], dict[str, str]]:
    before = all_keys()
    path = tree / entry if entry.startswith("content") else tree / "app" / entry
    path.write_text(path.read_text() + "\n# edited\n")
    return before, all_keys()


def changed(before: dict[str, str], after: dict[str, str]) -> list[str]:
    assert before.keys() == after.keys() and len(before) == len(ORDER)
    return [c for c in ORDER if before[c] != after[c]]


@pytest.mark.parametrize("chapter", ORDER[1:])
def test_a_changed_chapter_file_re_keys_it_and_every_chapter_after_and_none_before(tree: Path, chapter: str):
    toml = f"ashfall_app/rules/days/{keys.DAY_FILES[chapter][0]}.toml"
    before, after = after_editing(tree, toml)
    assert changed(before, after) == list(ORDER[ORDER.index(chapter):])


def test_week_ones_chapter_files_and_players_re_key_everything(tree: Path):
    for entry in ("ashfall_app/rules/days/day_three.toml", "tests/dayone/player/player.py", "tests/weekone/routes.py"):
        before, after = after_editing(tree, entry)
        assert changed(before, after) == list(ORDER), entry


def test_a_chapters_moves_re_key_the_chapters_that_file_holds_and_those_after(tree: Path):
    before, after = after_editing(tree, "tests/weektwo/weekfour.py")
    assert changed(before, after) == list(ORDER[ORDER.index("twentytwo"):])
    before, after = after_editing(tree, "tests/weektwo/content.py")
    assert changed(before, after) == list(ORDER[1:])


@pytest.mark.parametrize("entry", ["ashfall_app/engine/api.py", "ashfall_app/rules/schema.py",
                                   "ashfall_app/rules/opening.toml", "ashfall_app/rules/prestige.toml",
                                   "tests/weektwo/routes.py", "tools/chapter_saves.py", "content/beats.yaml"])
def test_what_every_chapter_reads_re_keys_every_chapter(tree: Path, entry: str):
    before, after = after_editing(tree, entry)
    assert changed(before, after) == list(ORDER), entry


def test_a_changed_shape_re_keys_every_chapter(tree: Path, monkeypatch: pytest.MonkeyPatch):
    before = all_keys()
    monkeypatch.setattr(keys, "shape_digest", lambda: "another shape")
    assert changed(before, all_keys()) == list(ORDER)


def test_a_test_file_is_not_an_input(tree: Path):
    before, after = after_editing(tree, "tests/weektwo/test_weektwo_saved.py")
    assert changed(before, after) == []


def test_the_keys_name_every_file_that_makes_a_chapter_and_every_chapter_has_files():
    assert len(keys.shared_files()) > 100
    assert all(keys.own_files(c) and all(f.is_file() for f in keys.own_files(c)) for c in ORDER)
    named = {f"{name}.toml" for names in keys.DAY_FILES.values() for name in names} | {"prestige.toml", "phase_pays.toml"}
    assert named == {p.name for p in CHAPTER_FILES}, "a chapter file merged by schema.CHAPTERS that no chapter's key reads"


def test_the_chapters_the_keys_order_are_the_ones_the_plays_build_on():
    assert {c: keys.before(c) for c in ORDER[1:]} == BEFORE
    assert set(SAVED) <= set(ORDER) and set(DAYS) == set(ORDER[1:])
    for chapter, play in DAYS.items():
        assert play.__code__.co_filename.endswith(keys.MOVES[chapter]), chapter


def test_shape_ignores_a_changed_number_and_sees_an_added_id():
    rules = rules3()
    first = rules.stores[0]
    kept = dataclasses.replace(rules, stores=(dataclasses.replace(first, cap=first.cap + 1), *rules.stores[1:]))
    added = dataclasses.replace(rules, stores=(*rules.stores, dataclasses.replace(first, id="zz_probe")))
    assert keys.masked(rules) == keys.masked(kept)
    assert keys.masked(rules) != keys.masked(added)
    assert rules.stores[0] != kept.stores[0], "the control changed something"
