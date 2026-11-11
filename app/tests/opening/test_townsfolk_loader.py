"""The loader's day-two entries on a test chapter (fixtures/townsfolk.toml) merged after the shipped ones: a ruled lane
with later labels, its cards filling the camp store, and each rule failing on a file built to break it (engine
DESIGN.txt, part "TOWNSFOLK, INSTALLED RULES AND OFFERS", "Content")."""
from functools import cache
from pathlib import Path

import pytest

from ashfall_app import main
from ashfall_app.engine import AtLeast, CardId, LaneId, LaneRules, RuleInstall, StoreId, Unlock, UnlockKind
from ashfall_app.engine.index import index
from ashfall_app.opening.schema import Opening, merge_chapters, to_rules

pytestmark = pytest.mark.usefixtures("townsfolk_opening")
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "townsfolk.toml"
TEXT = FIXTURE.read_text()


def shipped() -> Opening:
    """The session's shipped opening: conftest's autouse patch makes `checked_opening` return it."""
    return main.checked_opening()


@cache
def loaded() -> Opening:
    return merge_chapters(shipped(), (FIXTURE,))


def broken(tmp_path: Path, old: str, new: str) -> Path:
    assert TEXT.count(old) == 1, f"anchor is not unique: {old!r}"
    path = tmp_path / FIXTURE.name
    path.write_text(TEXT.replace(old, new))
    return path


def load_with(path: Path) -> Opening:
    return merge_chapters(shipped(), (path,))


def test_a_ruled_lane_loads_ruled_and_its_cards_fill_the_camp():
    o = loaded()
    r = to_rules(o)
    assert LaneId("t_helper") in index(r).ruled
    camp = o.camp
    assert camp is not None
    gather = index(r).cards[CardId("t_help_gather")]
    assert any(f.store == StoreId(camp.store) for f in gather.makes)
    assert gather.skill is None and gather.xp_per_hour == 0


def test_the_control_loads(tmp_path: Path):
    load_with(broken(tmp_path, 't_c_help_rest = "Rest"', 't_c_help_rest = "Sit"'))


@pytest.mark.parametrize("old, new, match", [
    ('label_key = "t_c_help_rest"\n', 'label_key = "t_c_help_rest"\nskill = "scavenging"\n', "trains no skill"),
    ('label_key = "t_c_help_rest"\n', 'label_key = "t_c_help_rest"\nxp_per_hour = 5\n', "trains no skill"),
    ('label_key = "t_l_helper_named" }', 'label_key = "t_l_missing" }', "t_l_missing"),
    ('id = "t_named" }, label_key', 'id = "t_unknown" }, label_key', "t_unknown"),
])
def test_a_broken_ruled_lane_fails_the_load(tmp_path: Path, old: str, new: str, match: str):
    with pytest.raises(ValueError, match=match):
        load_with(broken(tmp_path, old, new))


def test_the_arrival_installs_the_lanes_always_rule():
    r = to_rules(loaded())
    arrive = next(t for t in r.triggers if t.id == "t_helper_arrives")
    assert arrive.outcome.orders == (RuleInstall(CardId("t_help_gather")),)


INSTALL = 'orders = [{ tap_card = "t_help_gather" }]\n'


@pytest.mark.parametrize("old, new, match", [
    (INSTALL, 'orders = [{ tap_card = "gather_wood" }]\n', "not on a ruled lane"),
    (INSTALL, 'queues = ["take_stock"]\n', "only an answer's outcome queues"),
    ('work_s = 30\n', f'work_s = 30\ncap = 1\n[cards.outcome]\n{INSTALL}', "only a trigger's or an answer's"),
])
def test_an_install_where_none_may_be_fails_the_load(tmp_path: Path, old: str, new: str, match: str):
    with pytest.raises(ValueError, match=match):
        load_with(broken(tmp_path, old, new))


def test_an_offer_loads_with_the_trigger_that_shows_it():
    r = to_rules(loaded())
    show = next(t for t in r.triggers if t.id == "offer_t_ask")
    assert show.outcome.unlocks == (Unlock(UnlockKind.OFFER, "t_ask"),) and show.outcome.lines == ("t_l_asked",)
    offer = next(o for o in r.offers if o.id == "t_ask")
    assert [a.id for a in offer.answers] == ["t_yes", "t_no"]
    assert offer.answers[0].outcome.orders == (RuleInstall(CardId("t_help_fetch"), first=True),)
    assert offer.answers[1].outcome.queues == (CardId("t_one_off"),)


@pytest.mark.parametrize("old, new, match", [
    ('[[offers.answers]]\nid = "t_no"', '[[offers.answers]]\nid = "t_yes"', "duplicate id t_yes"),
    ('queues = ["t_one_off"]', 'queues = ["t_help_rest"]', "a queued one-off is a hands card with a cap"),
    ('outcome = { unlocks = [{ unlock_kind = "feature", id = "t_after" }] }',
     'outcome = { unlocks = [{ unlock_kind = "answered", id = "t_ask" }] }', "only an answer adds"),
    ('unlock_kind = "answered", id = "t_ask"', 'unlock_kind = "answered", id = "t_nope"', "unknown answered t_nope"),
    ('cost_key = "t_a_no_cost"', 'cost_key = "t_a_missing"', "t_a_missing"),
    ('id = "t_answered"', 'id = "offer_t_ask"', "duplicate id offer_t_ask"),
])
def test_a_broken_offer_fails_the_load(tmp_path: Path, old: str, new: str, match: str):
    with pytest.raises(ValueError, match=match):
        load_with(broken(tmp_path, old, new))


def test_an_offer_with_one_answer_fails_the_load(tmp_path: Path):
    start = TEXT.index('[[offers.answers]]\nid = "t_no"')
    end = TEXT.index("[[triggers]]\nid = \"t_answered\"")
    path = tmp_path / FIXTURE.name
    path.write_text(TEXT[:start] + TEXT[end:])
    with pytest.raises(ValueError, match="at least 2"):
        load_with(path)


def test_a_trigger_reads_the_rules_set_on_a_ruled_lane():
    trigger = next(t for t in to_rules(loaded()).triggers if t.id == "t_rule_set")
    assert trigger.when == AtLeast(LaneRules(LaneId("t_helper")), 1, 1)


LANE_RULES = 'subject_kind = "lane_rules", id = "t_helper", value = 1'


@pytest.mark.parametrize("old, new, match", [
    ('test = "at_least", ' + LANE_RULES, 'test = "at_most", ' + LANE_RULES, "takes at_least and no release"),
    (LANE_RULES, LANE_RULES + ", release = 0", "takes at_least and no release"),
    (LANE_RULES, LANE_RULES.replace("t_helper", "t_nobody"), "unknown ruled lane t_nobody"),
    (LANE_RULES, LANE_RULES.replace("t_helper", "gather_wood"), "unknown ruled lane gather_wood"),
    ('{ test = "at_least", subject_kind = "unlocked", unlock_kind = "answered", id = "t_ask", value = 1 }\noutcome',
     '{ test = "at_least", subject_kind = "unlocked", unlock_kind = "answered", id = "t_ask", value = 1 }\n'
     'requires = [{ test = "at_least", ' + LANE_RULES + ' }]\noutcome', "only a trigger's when or an offer's gate"),
])
def test_a_misplaced_or_malformed_lane_rules_condition_fails_the_load(tmp_path: Path, old: str, new: str, match: str):
    with pytest.raises(ValueError, match=match):
        load_with(broken(tmp_path, old, new))
