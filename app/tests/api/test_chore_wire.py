"""ChipInfo.chore on the wire (week-four-plan item 4), on tests/rules/fixtures/chorechip.toml merged onto the opening
alone: the season's chip is served as a chore, the opening's own chips are not, and the same chip stops being one once
a card that is no season's standing also makes its store."""
from pathlib import Path

from ashfall_app.api.service import Game
from ashfall_app.rules.schema import OPENING, Opening, load_opening
from ashfall_app.saves.ruleset import ruleset

FIXTURE = Path(__file__).resolve().parent.parent / "rules" / "fixtures" / "chorechip.toml"


def served(o: Opening) -> dict[str, bool]:
    return {c.chip: c.chore for c in Game(o, ruleset(o, "test", 1)).content().chip_infos}


def test_the_seasons_chip_is_served_as_a_chore_and_the_openings_are_not():
    chips = served(load_opening(OPENING, (FIXTURE,)))
    assert chips.pop("t_ashed") is True
    assert chips and not any(chips.values()), "the opening's chips are no season's chores"


def test_a_chip_whose_store_another_card_makes_is_no_chore(tmp_path: Path):
    old = 'inputs = [{ store = "t_film", items = 12 }]\n\n[[chips]]'
    text = FIXTURE.read_text()
    assert text.count(old) == 1
    path = tmp_path / FIXTURE.name
    path.write_text(text.replace(old, old.replace("[[chips]]", '[[cards]]\nid = "t_smear"\npresentation = "action"\n'
                                                   'label_key = "t_c_wash"\nupside_key = "t_up"\nwork_s = 60\n'
                                                   'makes = [{ store = "t_film", items_per_hour = 30 }]\n\n[[chips]]')))
    assert served(load_opening(OPENING, (path,)))["t_ashed"] is False
