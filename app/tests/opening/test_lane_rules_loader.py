"""The loader's `lane_rules` condition kind (docs/design/rule-taken-condition.md, contract statement 8): allowed only as
a trigger's `when` or an offer's `gate`, with `at_least`, no `release`, on a declared ruled lane. Each refusal is a
file built to break it from the townsfolk test chapter, beside a control that loads; the day-two chapter carries
`t_her_rule`."""
from pathlib import Path

import pytest

from ashfall_app.engine import AtLeast, LaneId, LaneRules
from ashfall_app.engine.index import index
from ashfall_app.opening.schema import Opening, merge_chapters, to_rules
from tests.opening.test_townsfolk_loader import shipped

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "townsfolk.toml"
TEXT = FIXTURE.read_text()

pytestmark = pytest.mark.usefixtures("townsfolk_opening")


def cond(lane: str = "t_helper", test: str = "at_least", extra: str = "") -> str:
    return f'{{ test = "{test}", subject_kind = "lane_rules", id = "{lane}", value = 1{extra} }}'


def trigger(when: str) -> str:
    return f'[[triggers]]\nid = "t_rule_seen"\nwhen = {when}\noutcome = {{ line_keys = ["t_l_rule"] }}\n\n[text]\n'


def edited(tmp_path: Path, *edits: tuple[str, str]) -> Path:
    text = TEXT
    for old, new in edits:
        assert text.count(old) == 1, f"anchor is not unique: {old!r}"
        text = text.replace(old, new)
    path = tmp_path / FIXTURE.name
    path.write_text(text)
    return path


def with_trigger(tmp_path: Path, when: str) -> Path:
    return edited(tmp_path, ("[text]\n", trigger(when)))


def load_with(path: Path) -> Opening:
    return merge_chapters(shipped(), (path,))


def test_a_trigger_on_a_ruled_lane_loads_as_lane_rules_at_least_one(tmp_path: Path):
    """Statement 8, control: `lane_rules` on a ruled lane, at_least 1, loads as a trigger on AtLeast(LaneRules(lane), 1)."""
    r = to_rules(load_with(with_trigger(tmp_path, cond())))
    when = next(t.when for t in r.triggers if t.id == "t_rule_seen")
    assert isinstance(when, AtLeast) and when.subject == LaneRules(LaneId("t_helper")) and when.value == 1


def test_an_offers_gate_may_be_lane_rules(tmp_path: Path):
    """Statement 8: an offer's gate may be lane_rules; the trigger the loader makes for the offer holds it."""
    gate = 'gate = { test = "at_least", subject_kind = "unlocked", unlock_kind = "feature", id = "t_named", value = 1 }'
    r = to_rules(load_with(edited(tmp_path, (gate, f"gate = {cond()}"))))
    when = next(t.when for t in r.triggers if t.id == "offer_t_ask")
    assert isinstance(when, AtLeast) and when.subject == LaneRules(LaneId("t_helper"))


@pytest.mark.parametrize("when", [
    cond(test="at_most"),
    cond(extra=", release = 0"),
    cond(lane="t_nope"),
    cond(lane="rack"),
])
def test_8_a_lane_rules_trigger_that_is_not_at_least_unreleased_on_a_ruled_lane_fails(tmp_path: Path, when: str):
    """Statement 8: lane_rules with at_most, with a release, on an unknown lane or on a declared unruled lane (the
    rack) fails the load."""
    with pytest.raises(ValueError):
        load_with(with_trigger(tmp_path, when))


STORE = '{ test = "at_most", subject_kind = "store", id = "damp_wood", value = 3, release = 5 }'
CARD_COUNT = '{ test = "at_least", subject_kind = "card_count", id = "t_help_rest", value = 1 }'
UNLOCKED = '{ test = "at_least", subject_kind = "unlocked", unlock_kind = "feature", id = "t_named", value = 1 }'
CHIP = ('[[chips]]\nid = "t_chip"\nlabel_key = "t_chip"\ntone = "cold"\nwhen = WHEN\ncost_key = "t_chip_cost"\n'
        'effects = [{ target = "lane", id = "hands", kind = "mul_bp", amount_bp = 8000, source = "t_chip" }]\n\n[text]\n')
CARD = 'label_key = "t_c_one_off"\nwork_s = 40\ncap = 1\n'
FAILED = 'failed_line_key = "t_l_rule"\n'
TRIGGER = 'outcome = { unlocks = [{ unlock_kind = "feature", id = "t_after" }] }\n'
TEXT_KEY = 't_c_one_off = "Look"'


def placed(where: str, c: str) -> tuple[tuple[str, str], ...]:
    """The fixture's edits putting condition `c` in a chip's when, a card's requires or a trigger's requires."""
    if where == "chip":
        return (("[text]\n", CHIP.replace("WHEN", c)), (TEXT_KEY, f'{TEXT_KEY}\nt_chip = "Chip"\nt_chip_cost = "costs"'))
    if where == "card":
        return ((CARD, f"{CARD}{FAILED}requires = [{c}]\n"),)
    return ((TRIGGER, f"{TRIGGER}requires = [{c}]\n"),)


ALLOWED = {"chip": STORE, "card": CARD_COUNT, "trigger": UNLOCKED}
"""For each place, a condition the place accepts: the control that the file otherwise loads."""


@pytest.mark.parametrize("where", sorted(ALLOWED))
def test_8_lane_rules_outside_a_triggers_when_and_an_offers_gate_fails(tmp_path: Path, where: str):
    """Statement 8: lane_rules in a chip's when, a card's requires or a trigger's requires fails the load, and the same
    edit holding an allowed condition loads."""
    load_with(edited(tmp_path, *placed(where, ALLOWED[where])))
    with pytest.raises(ValueError, match="lane_rules is only a trigger's when or an offer's gate"):
        load_with(edited(tmp_path, *placed(where, cond())))


def with_day_two() -> Opening:
    return shipped()


def test_8_day_twos_chapter_carries_t_her_rule():
    """Statement 8: the day-two chapter loads with t_her_rule, an AtLeast(LaneRules(n1), 1) on a ruled lane."""
    r = to_rules(with_day_two())
    when = next(t.when for t in r.triggers if t.id == "t_her_rule")
    assert isinstance(when, AtLeast) and when.subject == LaneRules(LaneId("n1")) and when.value == 1
    assert LaneId("n1") in index(r).ruled
