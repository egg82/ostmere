"""The writer keeps a saved end under today's key and removes one under any other (tools/chapter_saves.py): a rewrite after a
change plays only the chapters whose key is new."""
from pathlib import Path

import pytest

from tests.weektwo import ends, keys
from tools import chapter_saves


def test_prune_removes_a_directory_no_chapter_keys_and_keeps_todays(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("ASHFALL_SAVES_ROOT", str(tmp_path))
    (tmp_path / ends.key("eight")).mkdir()
    (tmp_path / "0123456789abcdef").mkdir()
    (tmp_path / "stray.txt").write_text("not a directory")
    assert chapter_saves.prune(tmp_path) == ["0123456789abcdef"]
    assert sorted(p.name for p in tmp_path.iterdir()) == sorted([ends.key("eight"), "stray.txt"])


def test_a_file_under_todays_key_is_present_and_one_under_another_key_is_not(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("ASHFALL_SAVES_ROOT", str(tmp_path))
    here = ends.player_path("nine", "typical")
    assert not chapter_saves.present(here)
    chapter_saves.put(here, b"x")
    assert chapter_saves.present(here)
    other = tmp_path / "0123456789abcdef" / here.name
    other.parent.mkdir()
    other.write_bytes(b"x")
    assert here.parent.name == ends.key("nine") and not chapter_saves.present(ends.player_path("eleven", "typical"))


def test_each_part_names_chapters_and_together_the_parts_name_every_chapter():
    named = {c for part in chapter_saves.ALL for c in chapter_saves.chapters_of(frozenset({part}))}
    assert named == set(keys.ORDER) and chapter_saves.chapters_of(frozenset()) == []
