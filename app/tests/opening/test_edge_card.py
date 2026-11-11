"""The content's one end card (opening.toml's end_card) sits on the end_feature of the last shipped chapter and nowhere
else: content runs on past every earlier chapter, so shipping a chapter moves the card with no hand edit. A chapter in
IN_WRITING is not shipped; it takes the card once it moves into CHAPTERS."""
import tomllib
from pathlib import Path
from typing import Any, NamedTuple

import pytest

from ashfall_app.opening.schema import CHAPTERS, IN_WRITING, OPENING, load_opening


class Declared(NamedTuple):
    end: str | None
    features: list[str]


def with_end(path: Path) -> Declared:
    """The chapter file's declared end_feature and its feature ids."""
    with path.open("rb") as f:
        d: dict[str, Any] = tomllib.load(f)
    return Declared(d.get("end_feature"), [str(x["id"]) for x in d.get("features", [])])


def carriers(chapters: tuple[Path, ...]) -> list[str]:
    return [f.id for f in load_opening(OPENING, chapters).features if f.card is not None]


def last_end(chapters: tuple[Path, ...]) -> str:
    return [c.end for c in map(with_end, chapters) if c.end is not None][-1]


def test_one_feature_carries_the_card_the_last_shipped_chapters_end_feature():
    assert carriers(CHAPTERS) == [last_end(CHAPTERS)]


def test_a_chapter_moving_from_writing_into_shipped_takes_the_card_with_it():
    before = carriers(CHAPTERS)
    after = carriers((*CHAPTERS, *IN_WRITING))
    assert IN_WRITING and len(before) == 1 and len(after) == 1
    assert after == [last_end(IN_WRITING)] and after != before


def test_every_chapter_with_features_declares_an_end_feature_among_them():
    found = [with_end(p) for p in (*CHAPTERS, *IN_WRITING) if with_end(p).features]
    assert found, "no chapter with features found: the scan reads nothing"
    assert all(c.end in c.features for c in found)


def planted(tmp_path: Path, old: str, new: str) -> Path:
    day_one = CHAPTERS[0]
    text = day_one.read_text()
    assert text.count(old) == 1, "the plant's anchor is not in day_one.toml"
    path = tmp_path / "day_one.toml"
    path.write_text(text.replace(old, new))
    return path


def test_a_card_on_a_chapters_own_feature_fails_the_load(tmp_path: Path):
    path = planted(tmp_path, '[[features]]\nid = "n1"\n',
                   '[[features]]\nid = "n1"\ncard = { title_key = "end_title", line_keys = [], button_key = "end_button" }\n')
    with pytest.raises(ValueError, match="carries no card"):
        load_opening(OPENING, (path,))


def test_a_chapter_with_features_and_no_end_feature_fails_the_load(tmp_path: Path):
    path = planted(tmp_path, 'end_feature = "n1"\n', "")
    with pytest.raises(ValueError, match="end_feature None"):
        load_opening(OPENING, (path,))


def test_an_end_feature_that_is_not_the_chapters_fails_the_load(tmp_path: Path):
    path = planted(tmp_path, 'end_feature = "n1"\n', 'end_feature = "ghost"\n')
    with pytest.raises(ValueError, match="ghost"):
        load_opening(OPENING, (path,))
