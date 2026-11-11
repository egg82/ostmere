"""The aims' load check (opening/aims.py): an aim from the start, each later one from an unlock something really gives,
every one a line short enough for a phone. Each failure is a file built to break it; the control loads."""
from pathlib import Path

import pytest

from ashfall_app.opening.aims import AIM_MAX_CHARS
from ashfall_app.opening.schema import OPENING, load_opening
from tests.opening.test_opening_loader import broken

FIRST = '''[[aims]]
id = "aim_fire"
text_key = "aim_fire"
'''
SECOND_AFTER = 'text_key = "aim_alive"\nafter = { unlock_kind = "action", id = "fire" }\n'


def test_the_shipped_aims_load_in_order_and_the_first_takes_no_after():
    aims = load_opening().aims
    assert len(aims) >= 2 and aims[0].after is None and all(a.after is not None for a in aims[1:])


@pytest.mark.parametrize("old,new,match", [
    (FIRST, FIRST + 'after = { unlock_kind = "action", id = "fire" }\n', "the first aim holds from the start"),
    (SECOND_AFTER, 'text_key = "aim_alive"\n', "only the first aim takes no after"),
    (SECOND_AFTER, 'text_key = "aim_alive"\nafter = { unlock_kind = "card", id = "woodcutting_2" }\n', "unknown card"),
    (SECOND_AFTER, 'text_key = "aim_alive"\nafter = { unlock_kind = "feature", id = "fireback" }\n', None),
    ('aim_fire = "you\'re freezing. a fire, before dark."', f'aim_fire = "{"x" * (AIM_MAX_CHARS + 1)}"', "over 40 characters"),
])
def test_a_broken_aim_fails_the_load(tmp_path: Path, old: str, new: str, match: str | None):
    path = broken(tmp_path, old, new)
    if match is None:   # the control: an after that some outcome gives loads
        assert load_opening(path).aims[1].after is not None
        return
    with pytest.raises(ValueError, match=match):
        load_opening(path)


def test_an_after_nothing_unlocks_fails_the_load(tmp_path: Path):
    """A known id no outcome or start gives (nothing retires the first card): the aim before it would never end."""
    path = broken(tmp_path, SECOND_AFTER, 'text_key = "aim_alive"\nafter = { unlock_kind = "retired", id = "stand_up" }\n')
    with pytest.raises(ValueError, match="nothing unlocks retired stand_up"):
        load_opening(path)


def test_no_aims_fails_the_load(tmp_path: Path):
    head, sep, words = OPENING.read_text().partition("[text]")
    start, mark, _rest = head.partition("# ---------- aims ----------")
    tail = head[head.index("# ---------- order cards ----------"):]
    assert mark and start.count("[[aims]]") == 0
    path = tmp_path / "opening.toml"
    path.write_text(start + tail + sep + words)
    with pytest.raises(ValueError, match="aims"):
        load_opening(path)
