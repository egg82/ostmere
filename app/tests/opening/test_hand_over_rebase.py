"""A save already past day eighteen's joins, written before the hand-over to groups, gets the hand-over at its next load
(docs/decisions/people.md, "The mark: who keeps their own split"): the four hand-over triggers and the two early
companions' are true at the rebase, so they fire there, once, with their lines. The save is typical's at day eighteen's
end, written under the rules shipped before the hand-over (fixtures/eighteen_typical_end_5bf8c553.txt.xz: its envelope's
rules digest begins 5bf8c553), with n8 to n12 joined, each on their own split, and one field crew."""
import lzma
from functools import cache
from pathlib import Path

from ashfall_app.engine import BP, CardShare, Rules, Save, Step, encode, rebase_logged
from ashfall_app.engine.groups import crews
from ashfall_app.engine.joins import is_joined
from ashfall_app.engine.rates import store_value
from ashfall_app.opening.convert import build_rules
from ashfall_app.opening.schema import Opening
from tests.shipped_ruleset import ShippedRuleset

SAVE = Path(__file__).parent / "fixtures" / "eighteen_typical_end_5bf8c553.txt.xz"
HANDED = ["n8", "n9", "n10", "n11", "n12"]
HAND_OVERS = ("t_choir_groups_beds", "t_choir_groups_road", "t_cutter_groups_beds", "t_cutter_groups_road")
PAIR = "t_pair_crews"
LINES = {"l_choir_group_beds", "l_choir_group_road", "l_cutter_group_beds", "l_cutter_group_road", "l_pair_crews"}
HEARTH = ["n4", "n6", "n8", "n10", "n11"]


@cache
def text() -> str:
    return lzma.decompress(SAVE.read_bytes()).decode()


def own(save: Save) -> dict[str, bool]:
    return {str(x.lane): x.own_split for x in save.lanes}


def hand_over_lines(step: Step) -> list[str]:
    return [str(x.key) for x in step.lines if str(x.key) in LINES]


def without(o: Opening, *triggers: str) -> Opening:
    assert set(triggers) <= {t.id for t in o.triggers}, triggers
    return o.model_copy(update={"triggers": [t for t in o.triggers if t.id not in triggers]})


def crew_shares(save: Save, rules: Rules, group: str) -> list[tuple[str, int]]:
    cards = {c.id: str(c.lane) for c in rules.cards}
    return [(str(c.card), c.share_bp) for m in save.mixes if str(m.id).startswith("town:")
            for c in m.components if isinstance(c, CardShare) and cards.get(c.card) == group]


def test_without_the_hand_over_the_save_keeps_its_five_bars(shipped_opening: Opening):
    plain = without(shipped_opening, *HAND_OVERS, PAIR)
    loaded = rebase_logged(text(), build_rules(plain))
    assert all(own(loaded.save)[x] for x in (*HANDED, "n2", "n4")) and not hand_over_lines(loaded)


def test_the_next_load_hands_the_five_to_the_field_crew_once_and_leaves_nothing_negative(shipped_ruleset: ShippedRuleset):
    rules = shipped_ruleset.rs.rules
    loaded = rebase_logged(text(), rules)
    marks = own(loaded.save)
    assert [x for x in (*HANDED, "n2", "n4") if marks[x]] == [] and marks["n1"] and marks["n3"]
    assert sorted(hand_over_lines(loaded)) == ["l_choir_group_road", "l_cutter_group_beds", "l_pair_crews"]   # typical's two answers, and the crews
    assert [str(s.store) for s in loaded.save.stores if store_value(loaded.save, s.store) < 0] == []
    cards = {c.id: c.lane for c in rules.cards}
    for mix in loaded.save.mixes:
        assert all(c.share_bp >= 0 for c in mix.components), mix.id
        if str(mix.id).startswith("town:"):
            by_lane: dict[str, int] = {}
            for c in (x for x in mix.components if isinstance(x, CardShare)):
                by_lane[str(cards[c.card])] = by_lane.get(str(cards[c.card]), 0) + c.share_bp
            assert max(by_lane.values()) <= BP, (mix.id, by_lane)
    again = rebase_logged(encode(loaded.save, rules), rules)
    assert hand_over_lines(again) == [] and own(again.save) == marks


def test_the_save_written_with_one_field_crew_loads_with_two_and_the_hearth_crew_foraging(shipped_ruleset: ShippedRuleset):
    rules = shipped_ruleset.rs.rules
    assert "g_hearth_pick" in text() and "g_hearth_pick" not in {str(c.id) for c in rules.cards}   # the control: an old hearth crew's card is gone
    loaded = rebase_logged(text(), rules)
    known = {c.id for c in rules.cards}
    groups = {str(x.id): str(x.group) for x in rules.lanes if x.group is not None}
    assert [x for x in HEARTH if groups[x] != "g_hearth"] == [] and groups["n7"] == "g_field" and not own(loaded.save)["n7"]
    assert [c.card for m in loaded.save.mixes for c in m.components if isinstance(c, CardShare) and c.card not in known] == []
    assert crew_shares(loaded.save, rules, "g_hearth") == [("g_hearth_forage", BP)]
    kept = [str(x.lane) for x in loaded.save.lanes if x.own_split and is_joined(loaded.save, rules, x.lane)]
    assert sorted(kept) == ["n1", "n3"] and sorted(crews(loaded.save, rules)) == ["g_field", "g_hearth"]   # the Town view's rows: four


def test_without_the_crews_trigger_the_two_companions_keep_their_bars_and_the_hearth_crew_has_no_forage(shipped_opening: Opening):
    """The control: this trigger is what takes n2 and n4 into the crews and starts the hearth crew foraging, so
    without it they keep a row each and the crew starts on whatever the day-eighteen hand-over gave it (this goes red)."""
    rules = build_rules(without(shipped_opening, PAIR))
    loaded = rebase_logged(text(), rules)
    assert own(loaded.save)["n2"] and own(loaded.save)["n4"]
    assert ("g_hearth_forage", BP) not in crew_shares(loaded.save, rules, "g_hearth")
