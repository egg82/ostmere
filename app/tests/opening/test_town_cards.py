"""Town cards (ashfall_app/opening/town.py): one definition expands to a card per lane at the merge. The rules digest
the lock records is the proof that moving week one's copies into entries changed structure only."""
from pathlib import Path

import pytest

from ashfall_app.engine import rules_digest
from ashfall_app.opening.convert import build_rules
from ashfall_app.opening.lock import load_lock
from ashfall_app.opening.schema import CHAPTERS, IN_WRITING, OPENING, Opening, load_opening, to_rules
from ashfall_app.opening.town import TownCardEntry, undeclared_lanes
from tests.opening.playthrough import opening

DAY_THREE = CHAPTERS[2]
GATHERED = ["forage", "gather", "cut", "scavenge"]


def planted(tmp_path: Path, old: str, new: str) -> Opening:
    """The shipped chapters with day three's text edited: exactly one occurrence of `old` becomes `new`."""
    text = DAY_THREE.read_text()
    assert text.count(old) == 1, f"anchor is not unique: {old!r}"
    path = tmp_path / DAY_THREE.name
    path.write_text(text.replace(old, new))
    return load_opening(OPENING, (*CHAPTERS[:2], path, *CHAPTERS[3:]))


def digest(o: Opening) -> str:
    return rules_digest(to_rules(o))


@pytest.fixture(scope="module")
def digests(tmp_path_factory: pytest.TempPathFactory) -> tuple[str, str, str]:
    """The digest of the chapters reloaded with an unedited copy of day three, of the cached shipped opening, and the
    lock's, computed once."""
    same = planted(tmp_path_factory.mktemp("town"), 'label_key = "c_woodcutting"', 'label_key = "c_woodcutting"')
    return digest(same), digest(opening()), load_lock().digest


def test_the_shipped_content_digest_is_the_lock_s(digests: tuple[str, str, str]):
    """The control for the dropped-lane test: the unedited chapters match the recorded digest, so a difference below
    is the edit's."""
    same, shipped, locked = digests
    assert same == shipped == locked


@pytest.fixture(scope="module")
def dropped_lane() -> tuple[Opening, Opening, str, str]:
    """The cached shipped opening, the same without n3's gather card, and the digests of the rules built from each
    without the checks, computed once."""
    o = opening()
    dropped = o.model_copy(update={"cards": [c for c in o.cards if c.id != "n3_gather"]})
    return o, dropped, rules_digest(build_rules(o)), rules_digest(build_rules(dropped))


def test_an_expansion_that_drops_a_lane_changes_the_digest(dropped_lane: tuple[Opening, Opening, str, str]):
    """The planted expansion loses n3's gather card. The loader would refuse the content (a trigger joins that card), so
    the rules are built without the checks: the digest alone has to see it."""
    o, dropped, shipped, without = dropped_lane
    assert len(dropped.cards) == len(o.cards) - 1
    assert shipped == load_lock().digest
    assert without != load_lock().digest


def test_an_expansion_that_collides_with_an_id_fails_the_loader_naming_it(tmp_path: Path):
    entry = '[[town_cards]]\nid = "{lane}_build_bay"\nlanes = ["n2"]\npresentation = "action"\nlabel_key = "c_forage"\nwork_s = 5\n'
    with pytest.raises(ValueError, match="duplicate id n2_build_bay"):
        planted(tmp_path, "[[town_cards]]\nid = \"{lane}_forage\"", entry + "\n[[town_cards]]\nid = \"{lane}_forage\"")


@pytest.fixture(scope="module")
def everything() -> Opening:
    """Every chapter, those in writing too, loaded once: a lane a shipped entry names may be declared in
    a chapter still in writing, and expands there."""
    return load_opening(chapters=(*CHAPTERS, *IN_WRITING))


def test_every_lane_a_town_card_names_is_declared(everything: Opening):
    o = everything
    assert o.town_cards
    assert undeclared_lanes(o.town_cards, {x.id for x in o.lanes}) == []
    assert undeclared_lanes(o.town_cards, set()) == ["n1", "n2", "n3", "n4", "n5", "n6", "n7"]


def test_a_lane_gets_its_cards_together_in_the_entries_order():
    ids = [c.id for c in load_opening().cards]
    at = ids.index("n2_build_bay")
    assert ids[at + 1:at + 6] == ["n2_stakes", *(f"n2_{g}" for g in GATHERED)]
    assert ids[ids.index("n3_build_bay") + 1:][:3] == ["n3_pick", "n3_forage", "n3_gather"]


@pytest.mark.parametrize("fields, why", [
    ({"id": "forage"}, "needs {lane}"),
    ({"id": "{lane}_forage", "lane": "n2"}, "`lane` is not set"),
])
def test_an_entry_is_refused_without_a_pattern_or_with_a_lane(fields: dict[str, object], why: str):
    base = {"presentation": "action", "label_key": "c_forage", "work_s": 5, "lanes": ["n2"]}
    with pytest.raises(ValueError, match=why.replace("{", r"\{").replace("}", r"\}")):
        TownCardEntry.model_validate({**base, **fields})
