"""A second magic skill opening on its first card (week-three-plan item 10), on fixtures/secondskill.toml merged after the
shipped chapters with a level marker and its paying trigger per level added here. The skill arrives with a trigger's outcome
and its first card is a hands card that cures a chip; the per-skill checks (tests/opening/test_level_pays.py,
tests/dayone/growth.py) read the new row without any change to them, and two order cards on one chip load."""
import tempfile
from pathlib import Path

import pytest

from ashfall_app.engine import Rules, UnlockKind
from ashfall_app.opening.schema import Opening, merge_chapters, to_rules
from tests.dayone.growth import runaway
from tests.opening.test_level_pays import mixed_skills, top_level, unmarked_levels, unpaid_markers

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "secondskill.toml"
LORE = "t_lore"


def rows(top: int, skip: int | None = None, unpaid: int | None = None) -> str:
    """A marker for each level 2..top except `skip`, and a trigger paying each except `unpaid`'s."""
    marked = [n for n in range(2, top + 1) if n != skip]
    levels = ", ".join(f'{{ level = {n}, pays_key = "t_pays_lore" }}' for n in marked)
    out = [f'[[skills]]\nid = "{LORE}"\nlabel_key = "t_k_lore"\nlevels = [{levels}]\n']
    out += [f'[[triggers]]\nid = "t_lore_{n}"\nwhen = {{ test = "at_least", subject_kind = "skill_level", id = "{LORE}", value = {n} }}\n'
            'outcome = { line_keys = ["t_pays_lore"] }\n' for n in marked if n != unpaid]
    return "\n".join(out)


def loaded(shipped: Opening, skip: int | None = None, unpaid: int | None = None, old: str = "", new: str = "") -> tuple[Opening, Rules]:
    top = top_level(to_rules(shipped))
    text = FIXTURE.read_text().replace(old, new, 1) if old else FIXTURE.read_text()
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / FIXTURE.name
        path.write_text(text.replace("\n[text]\n", "\n" + rows(top, skip, unpaid) + "\n[text]\n", 1))
        o = merge_chapters(shipped, (path,))
    return o, to_rules(o)


@pytest.fixture(scope="module")
def variants(shipped_opening: Opening) -> dict[str, tuple[Opening, Rules]]:
    """Each variant is merged once onto the session's shipped opening, in setup."""
    return {"": loaded(shipped_opening), "skip": loaded(shipped_opening, skip=7), "unpaid": loaded(shipped_opening, unpaid=7)}


@pytest.fixture(scope="module")
def refused(shipped_opening: Opening) -> str:
    """The loader's refusal of an order card naming a card that is not there."""
    try:
        loaded(shipped_opening, old='tap_card = "t_charm"', new='tap_card = "t_missing"')
    except ValueError as e:
        return str(e)
    return ""


def test_the_skill_arrives_with_an_outcome_and_its_first_card(variants: dict[str, tuple[Opening, Rules]]):
    _, rules = variants[""]
    arrives = next(t for t in rules.triggers if t.id == "t_lore_arrives")
    assert {(u.kind, str(u.id)) for u in arrives.outcome.unlocks} == {(UnlockKind.SKILL, LORE), (UnlockKind.CARD, "t_charm")}


def test_the_skill_checks_cover_the_new_row_and_pass(variants: dict[str, tuple[Opening, Rules]]):
    o, rules = variants[""]
    assert LORE in mixed_skills(rules), "the check reads the new skill: a hands card trains it"
    assert unpaid_markers(o, rules) == [] and unmarked_levels(o, rules) == [] and runaway(rules) == []


def test_a_level_left_blank_before_the_top_is_found(variants: dict[str, tuple[Opening, Rules]]):
    assert unmarked_levels(*variants["skip"]) == [f"{LORE} 7"]


def test_a_marker_nothing_pays_is_found(variants: dict[str, tuple[Opening, Rules]]):
    assert unpaid_markers(*variants["unpaid"]) == [f"{LORE} 7 (t_pays_lore)"]


def test_two_order_cards_on_one_chip_load(variants: dict[str, tuple[Opening, Rules]]):
    o, _ = variants[""]
    assert [c.tap_card for c in o.order_cards if c.chip == "t_cold"] == ["t_stoke", "t_charm"]


def test_an_order_card_for_a_card_that_is_not_there_fails_the_loader_naming_the_chapter(refused: str):
    assert "t_missing" in refused and refused.endswith(f" (in {FIXTURE.name})")
