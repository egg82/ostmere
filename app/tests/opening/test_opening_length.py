"""The opening played to its end moment in simulated time by the scripted newcomer-ish player (playthrough.py). It knows
each next step, so it is a lower bound on a real player's pace (docs/decisions.md): the run reaches the end, the
first mix is the player's own, the edge greys it, and the end waits for both crafts and the roast."""

import pytest

from ashfall_app.engine import (
    BP, CardId, CardShare, FlowKind, Mix, MixId, RateRef, Run, RunKind, SaveMix, SetOrders, SwitchMix, TapCard, Unlock,
    UnlockKind, advance, decide, modified_rate, units, view,
)
from tests.opening.playthrough import CRAFTS, Player, even, opening, opening_rules
from tests.opening.routes import plays

pytestmark = pytest.mark.playthrough


@pytest.fixture
def finished(typical: Player) -> Player:
    """The typical route (routes.py), under this file's old name for it."""
    return typical


def first(p: Player, line: str) -> int:
    return next(ln.time for ln in p.lines if ln.key == line)


@pytest.mark.parametrize("a_route", plays(), indirect=True)
def test_a_newcomerish_player_reaches_the_end(a_route: Player):
    """Reactions of seconds, one tap per decision: the route reaches the end moment. When it does is the readout's
    (report.py), never a threshold."""
    assert a_route.end_at is not None


def test_the_end_moment_comes_after_both_crafts_and_the_roast(finished: Player):
    assert finished.has(UnlockKind.FEATURE, opening().end_feature)
    assert all(finished.completed(c) for c in (*CRAFTS, "roast_roots"))
    keys: list[str] = [ln.key for ln in finished.lines]
    assert keys.index("l_fire_takes") < keys.index("l_knap_2") < keys.index("l_stool")
    assert finished.end_at is not None and finished.end_at >= first(finished, "l_settled")


@pytest.mark.parametrize("player", ["finished", "by_hand"])
def test_the_end_lines_come_after_a_quiet_stretch_not_on_the_last_step(player: str, request: pytest.FixtureRequest):
    """The last settling step's lines are read on their own: the evening runs before the end feature unlocks, and no
    story step lands in it (a clock line may)."""
    p: Player = request.getfixturevalue(player)
    settled = first(p, "l_settled")
    assert p.end_at is not None and p.end_at >= settled + 40
    clock = {"l_hungry", "l_tired"}
    assert [ln.key for ln in p.lines if settled < ln.time <= p.end_at and ln.key not in clock] == []


def test_the_roots_order_comes_with_hunger_as_its_own_step_before_the_end(by_hand: Player):
    """Eating starts at hunger, so the roots line is red with its order card then, not at the end: the hands' rule is
    offered and set before the last of the three steps, and the end comes after them."""
    shown = {n.thing: n.at for n in by_hand.news}   # when the player sees it: a tap holding the hands delays it
    assert first(by_hand, "l_hungry") <= shown["action:eating"] == shown["order_card:roots"] < first(by_hand, "l_settled")
    roots = [t for t, _, v in by_hand.decisions
             if isinstance(v, SetOrders) and any(o.then == TapCard(CardId("forage")) for o in v.orders)]
    assert roots and by_hand.end_at is not None
    assert roots[0] < first(by_hand, "l_settled") <= by_hand.end_at


def test_the_first_mix_is_made_by_the_player_from_the_offer(finished: Player):
    """Offered once the spot is cleared (the mix feature), made by one decision: both hand jobs at an even split."""
    saves = [(t, v) for t, _, v in finished.decisions if isinstance(v, SaveMix)]
    t, mix = saves[0]
    assert t >= first(finished, "l_clear_2")
    assert [(c.card, c.share_bp) for c in mix.mix.components if isinstance(c, CardShare)] == \
        [(c, BP // 2) for c in opening().first_mix.cards]
    assert any(isinstance(v, SwitchMix) and when == t for when, _, v in finished.decisions)
    assert Player(opening_rules()).save.mixes == ()


def test_the_edge_retires_gathering_greys_the_mix_and_the_editor_puts_woodcutting_in(finished: Player):
    p = finished.at(lambda q: q.completed("knap_edge"))
    v = p.view()
    assert p.has(UnlockKind.RETIRED, "gather_wood") and "gather_wood" in {c.card for c in v.completed}
    assert p.save.active in v.greyed_mixes
    assert {"woodcutting", *CRAFTS} <= {c.card for c in v.cards}
    edit = next(v for _, _, v in finished.decisions
                if isinstance(v, SaveMix) and any(c.card == "woodcutting" for c in v.mix.components
                                                  if isinstance(c, CardShare)))
    assert "gather_wood" not in {c.card for c in edit.mix.components if isinstance(c, CardShare)}
    assert finished.view().greyed_mixes == ()


def test_a_card_lists_what_its_next_completion_needs_and_how_much_there_is(typical: Player):
    """Ring the spot, shown unready, lists its stones short; strike lists its dry wood, flint and nail; the crafts
    show their stores before they can be built."""
    p = typical.at(lambda q: q.card("ring_it") is not None)
    ring = p.card("ring_it")
    assert ring is not None and [(n.store, n.quantity) for n in ring.needs] == [("stones", units(5))]
    assert ring.needs[0].segment.start_value < units(5) and ring.blocker is not None
    strike = p.card("strike_fire")
    assert strike is not None and [n.store for n in strike.needs] == ["dry_wood", "flint", "nails"]
    p = typical.at(lambda q: q.card("build_fireback") is not None)
    fireback = p.card("build_fireback")
    assert fireback is not None and [(n.store, n.quantity) for n in fireback.needs] == \
        [("dry_wood", units(3)), ("stones", units(4))]


def test_camp_levels_pay_their_bonus_to_the_wall_and_the_stores(typical: Player):
    """Camp 1: the wall takes 5 at a time instead of 3, shown as the card's need, and a batch dries 5. Camp 2: the
    stores hold half again (12 to 18, roots 8 to 12), on the ledger's caps. Each lands as a modifier sourced by its
    level; the opening never reaches the level past them (its own held marker, which day one fills in)."""
    camp = opening().camp
    assert camp is not None
    p = typical.at(lambda q: q.card("lay_to_dry") is not None)
    lay_card = p.card("lay_to_dry")
    assert lay_card is not None and [(n.store, n.quantity) for n in lay_card.needs] == [("damp_wood", units(3))]
    assert [(lv.pays_from, lv.pays_to) for lv in camp.levels[:2]] == [(3, 5), (12, 18)]   # the markers' numbers
    assert lay_card.needs[0].quantity == units(camp.levels[0].pays_from or 0)
    p = typical.at(lambda q: "camp_1" in {m.source for m in q.save.modifiers})
    lay_to_dry = p.card("lay_to_dry")
    assert lay_to_dry is not None
    need = lay_to_dry.needs[0].quantity
    assert units(5) - units(1) // 1000 <= need <= units(5), need   # five, a hair under (no exact factor for 5/3)
    assert camp.levels[0].pays_to == 5
    caps: dict[str, int] = {ln.store: ln.cap for ln in p.view().ledger}
    assert caps["damp_wood"] == units(camp.levels[1].pays_from or 0)
    lay = next(c for c in p.rules.cards if c.id == "lay_to_dry")
    ref = RateRef(lay.id, FlowKind.MAKE, lay.outcome.stores[0].store)
    own = tuple(m for m in p.save.modifiers if m.target == ref)
    assert modified_rate(ref, lay.outcome.stores[0].quantity, BP, own, Run(RunKind.FULL)).per_hour >= units(5)
    p = typical.at(lambda q: "camp_2" in {m.source for m in q.save.modifiers})
    caps: dict[str, int] = {ln.store: ln.cap for ln in p.view().ledger}
    assert [caps.get(s) for s in ("damp_wood", "dry_wood", "stones", "roots")] == [units(18), units(18), units(18), units(12)]
    assert caps["damp_wood"] == units(camp.levels[1].pays_to or 0)
    p = typical
    assert Unlock(UnlockKind.STORE, camp.store) in p.save.unlocked
    assert p.items(camp.store) < camp.levels[2].at_items   # the opening ends before the level past its own two


def test_rest_at_a_quarter_of_a_mix_answers_tiredness_within_two_minutes(by_hand: Player):
    """Tiredness is felt (the chip and half-speed hands come by the clock), but a quarter share of rest in a shared mix
    answers it within about two minutes of play. The mix yields to every tap, and a newcomer's hands tap about half
    the time, so that is a minute of mix time (rest at 1080/h took 85 s here and over six minutes in a real run)."""
    p = by_hand.at(lambda q: "tired" in q.view().chips and q.card("rest") is not None)
    t = p.save.time
    others = [c for c in ("scavenge", "woodcutting", "gather_wood", "forage") if p.card(c) is not None][:3]
    shares = even(["rest", *others])
    s = decide(p.save, p.rules, t, SaveMix(Mix(MixId("tired"), shares)))
    s = decide(s, p.rules, t, SwitchMix(MixId("tired")))
    assert "tired" in view(s, p.rules).chips and shares[0].share_bp <= BP // 4 + 1
    cleared = next((dt for dt in range(5, 600, 5) if "tired" not in view(advance(s, p.rules, t + dt), p.rules).chips), None)
    assert cleared is not None and 20 <= cleared <= 60, cleared
