"""Every card on a player's lane has a town twin or an only_player tag (docs/decisions/people.md, "Who can do which job";
rules/checks/people/player_checks.py). The cards with neither are held per chapter file in tests/held/player_only.json, and the
count only shrinks: `python -m tests.rules.checks.test_player_only --write` (from app/) lowers it once one is marked; never
run it to let a new one through."""
import sys
import tomllib
from pathlib import Path

import pytest

from ashfall_app.rules.entries.entries import CardEntry
from ashfall_app.rules.checks.people.player_checks import check_player_only, unmarked
from ashfall_app.rules.schema import CHAPTERS, IN_WRITING, OPENING, Opening, load_opening
from tests.held_ledger import Ledger, dump, load, problems, tally, total

APP = Path(__file__).resolve().parents[3]
HELD = APP / "tests/held/player_only.json"
FILES = (OPENING, *CHAPTERS, *IN_WRITING)


def full() -> Opening:
    return load_opening(chapters=(*CHAPTERS, *IN_WRITING))


def home() -> dict[str, str]:
    """Each hand-written card's id to the file that authors it."""
    out: dict[str, str] = {}
    for path in FILES:
        with path.open("rb") as f:
            for c in tomllib.load(f).get("cards", []):
                out[c["id"]] = str(path.relative_to(APP))
    return out


def ledger(o: Opening) -> Ledger:
    where = home()
    return tally([(where.get(c.id, "?"), "unmarked") for c in unmarked(o)])


@pytest.fixture(scope="module")
def content() -> Opening:
    return full()


def test_every_player_card_has_a_town_twin_or_a_reason(content: Opening):
    assert sum(1 for c in content.cards if c.only_player is not None) > 40, "almost no tags seen: the check is blind"
    assert sum(1 for c in content.cards if c.twin_of is not None) > 40, "almost no twins seen: the check is blind"
    found = problems(ledger(content), load(HELD), "give it a town twin (twin_of) or an only_player tag",
                     "python -m tests.rules.checks.test_player_only --write")
    assert not found, "\n".join(found)


def planted(o: Opening, card: CardEntry) -> Opening:
    return o.model_copy(update={"cards": [*o.cards, card]})


def test_a_player_card_with_neither_is_unmarked(content: Opening):
    card = CardEntry(id="plant", presentation="action", label_key="c_stew", work_s=10)
    assert [c.id for c in unmarked(planted(content, card))][-1] == "plant"


def test_a_twin_or_a_tag_marks_it(content: Opening):
    tagged = CardEntry(id="plant", presentation="action", label_key="c_stew", work_s=10, only_player="story")
    twin = CardEntry(id="n1_plant", lane="n1", presentation="action", label_key="c_stew", work_s=10, twin_of="plant")
    bare = tagged.model_copy(update={"only_player": None})
    assert "plant" not in {c.id for c in unmarked(planted(content, tagged))}
    assert "plant" not in {c.id for c in unmarked(planted(planted(content, bare), twin))}


@pytest.mark.parametrize(("card", "says"), [
    (CardEntry(id="plant", presentation="action", label_key="c_stew", work_s=10, twin_of="stew"), "not on a townsperson"),
    (CardEntry(id="plant", lane="n1", presentation="action", label_key="c_stew", work_s=10, twin_of="n1_stew"),
     "not a card on a player's lane"),
    (CardEntry(id="plant", lane="n1", presentation="action", label_key="c_stew", work_s=10, twin_of="nothing"),
     "not a card on a player's lane"),
    (CardEntry(id="plant", lane="n1", presentation="action", label_key="c_stew", work_s=10, only_player="story"),
     "only_player is set"),
])
def test_a_field_pointing_the_wrong_way_fails(content: Opening, card: CardEntry, says: str):
    with pytest.raises(ValueError, match=f"card plant: .*{says}"):
        check_player_only(planted(content, card))


def test_a_tagged_card_with_a_twin_fails(content: Opening):
    cards = [c.model_copy(update={"only_player": "story"}) if c.id == "stew" else c for c in content.cards]
    with pytest.raises(ValueError, match="card stew: only_player is set"):
        check_player_only(content.model_copy(update={"cards": cards}))


if __name__ == "__main__" and "--write" in sys.argv:
    led = ledger(full())
    HELD.write_text(dump(led))
    print(f"wrote {HELD}: {total(led)} held")
