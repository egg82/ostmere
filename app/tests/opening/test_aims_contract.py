"""Blind contract test (written from the contract, not the implementation): the content loader rejects content with no
aims, a first aim that has an `after`, a later aim without one, an `after` naming an unknown id, an `after` that neither
the start nor any outcome unlocks, and an aim longer than 40 characters. Each rejected file differs from a control that
loads by exactly that property; the shipped content, as served, keeps the same rules."""
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from ashfall_app.api.content_models import Content
from ashfall_app.main import create_app
from ashfall_app.opening.schema import OPENING, load_opening

TEXT = OPENING.read_text()
AIM_BLOCK = re.compile(r"\[\[aims\]\]\n(?:(?!\[)[^\n]*\n)*")
TEXT_ANCHOR = '"ui.rate.per_minute" = "{n}/min"'
TABLE_ANCHOR = "[[order_cards]]\n"

# the start unlocks card stand_up; a trigger's outcome unlocks feature mix (both in the shipped opening)
AT_START = '{ unlock_kind = "card", id = "stand_up" }'
AT_OUTCOME = '{ unlock_kind = "feature", id = "mix" }'
Aim = tuple[str, str, str | None]   # id, text, after


def aims_file(tmp_path: Path, aims: list[Aim], extra_features: str = "") -> Path:
    """The shipped opening with its aims replaced by `aims`; every other line is the shipped one."""
    body = AIM_BLOCK.sub("", TEXT)
    assert "[[aims]]" not in body, "the probe did not strip the shipped aims"
    assert body.count(TEXT_ANCHOR) == 1 and body.count(TABLE_ANCHOR) >= 1, "an anchor drifted"
    texts = "".join(f'"aimtest_{i}" = "{text}"\n' for i, (_, text, _) in enumerate(aims))
    blocks = "".join(
        f'[[aims]]\nid = "{aim}"\ntext_key = "aimtest_{i}"\n' + (f"after = {after}\n" if after else "") + "\n"
        for i, (aim, _, after) in enumerate(aims))
    body = body.replace(TEXT_ANCHOR, texts + TEXT_ANCHOR).replace(TABLE_ANCHOR, extra_features + blocks + TABLE_ANCHOR, 1)
    path = tmp_path / "opening.toml"
    path.write_text(body)
    return path


def loads(path: Path) -> None:
    load_opening(path, chapters=())


def rejects(path: Path) -> None:
    with pytest.raises(ValueError):
        loads(path)


CONTROL: list[Aim] = [("a_first", "Get warm", None), ("a_second", "Keep the fire", AT_OUTCOME), ("a_third", "Eat", AT_START)]


def test_a_control_with_aims_loads(tmp_path: Path):
    """The harness can pass: the same file shape with valid aims loads, so each rejection below is the rule's doing."""
    loads(aims_file(tmp_path, CONTROL))


def test_a_single_first_aim_loads(tmp_path: Path):
    loads(aims_file(tmp_path, CONTROL[:1]))


def test_content_with_no_aims_is_rejected(tmp_path: Path):
    rejects(aims_file(tmp_path, []))


def test_a_first_aim_with_an_after_is_rejected(tmp_path: Path):
    rejects(aims_file(tmp_path, [("a_first", "Get warm", AT_START), *CONTROL[1:]]))


def test_a_later_aim_without_an_after_is_rejected(tmp_path: Path):
    rejects(aims_file(tmp_path, [CONTROL[0], ("a_second", "Keep the fire", None)]))


def test_an_after_naming_an_unknown_id_is_rejected(tmp_path: Path):
    rejects(aims_file(tmp_path, [CONTROL[0], ("a_second", "Keep the fire", '{ unlock_kind = "card", id = "no_such_card" }')]))


ORPHAN = '[[features]]\nid = "aim_orphan"\n\n'


def test_a_feature_nothing_unlocks_loads_when_no_aim_waits_on_it(tmp_path: Path):
    """Control for the next test: the orphan itself is not what the loader objects to."""
    loads(aims_file(tmp_path, CONTROL, extra_features=ORPHAN))


def test_an_after_nothing_unlocks_is_rejected(tmp_path: Path):
    orphan = ORPHAN
    after = '{ unlock_kind = "feature", id = "aim_orphan" }'
    rejects(aims_file(tmp_path, [CONTROL[0], ("a_second", "Keep the fire", after)], extra_features=orphan))


def test_an_aim_of_forty_characters_loads_and_forty_one_is_rejected(tmp_path: Path):
    forty = "x" * 40
    loads(aims_file(tmp_path, [("a_first", forty, None)]))
    rejects(aims_file(tmp_path, [("a_first", forty + "x", None)]))


def test_a_later_aim_too_long_is_rejected_too(tmp_path: Path):
    rejects(aims_file(tmp_path, [CONTROL[0], ("a_second", "x" * 41, AT_OUTCOME)]))


def test_the_shipped_opening_with_its_chapters_loads():
    load_opening()


def test_the_shipped_content_as_served_obeys_the_rules():
    content = Content.model_validate(TestClient(create_app()).get("/api/content").json())
    infos = content.aim_infos
    text = {e.key: e.text for e in content.text_entries}
    assert infos and infos[0].after is None and all(i.after is not None for i in infos[1:])
    assert all(0 < len(text[i.text_key]) <= 40 for i in infos)
