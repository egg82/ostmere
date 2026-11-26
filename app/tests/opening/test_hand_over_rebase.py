"""A save already past day eighteen's joins, written before the hand-over to groups, gets the hand-over at its next load
(docs/decisions/people.md, "The mark: who keeps their own split"): the four hand-over triggers are true at the rebase, so
they fire there, once, with their lines. The save is typical's at day eighteen's end, written under the rules shipped
before the hand-over (fixtures/eighteen_typical_end_5bf8c553.txt.xz: its envelope's rules digest begins 5bf8c553), with
n8 to n12 joined, each on their own split."""
import lzma
from functools import cache
from pathlib import Path

from ashfall_app.engine import BP, CardShare, Save, Step, encode, rebase_logged
from ashfall_app.engine.rates import store_value
from ashfall_app.opening.convert import build_rules
from ashfall_app.opening.schema import Opening
from tests.shipped_ruleset import ShippedRuleset

SAVE = Path(__file__).parent / "fixtures" / "eighteen_typical_end_5bf8c553.txt.xz"
HANDED = ["n8", "n9", "n10", "n11", "n12"]
HAND_OVERS = ("t_choir_groups_beds", "t_choir_groups_road", "t_cutter_groups_beds", "t_cutter_groups_road")
LINES = {"l_choir_group_beds", "l_choir_group_road", "l_cutter_group_beds", "l_cutter_group_road"}


@cache
def text() -> str:
    return lzma.decompress(SAVE.read_bytes()).decode()


def own(save: Save) -> dict[str, bool]:
    return {str(x.lane): x.own_split for x in save.lanes}


def hand_over_lines(step: Step) -> list[str]:
    return [str(x.key) for x in step.lines if str(x.key) in LINES]


def test_without_the_hand_over_the_save_keeps_its_five_bars(shipped_opening: Opening):
    plain = shipped_opening.model_copy(update={"triggers": [t for t in shipped_opening.triggers if t.id not in HAND_OVERS]})
    loaded = rebase_logged(text(), build_rules(plain))
    assert all(own(loaded.save)[x] for x in HANDED) and not hand_over_lines(loaded)


def test_the_next_load_hands_the_five_to_the_field_crew_once_and_leaves_nothing_negative(shipped_ruleset: ShippedRuleset):
    rules = shipped_ruleset.rs.rules
    loaded = rebase_logged(text(), rules)
    marks = own(loaded.save)
    assert [x for x in HANDED if marks[x]] == [] and marks["n1"] and marks["n4"]
    assert sorted(hand_over_lines(loaded)) == ["l_choir_group_road", "l_cutter_group_beds"]   # typical's two answers
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
