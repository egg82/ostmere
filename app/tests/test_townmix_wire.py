"""The town's mix on the wire (api/CONTRACT.txt, "The town's mix"): the view's running_town_mix_id and town_mix_order,
the joined unlock category and the decisions' refusals, each a plain copy of the engine's, on one ruled lane whose
person joins at second 100."""
from dataclasses import replace

import pytest

from ashfall_app import engine as e
from ashfall_app.api import models as w
from ashfall_app.api.service import Game
from ashfall_app.saves.ruleset import ruleset
from tests.opening.test_townsfolk_loader import loaded

pytestmark = pytest.mark.usefixtures("townsfolk_opening")

Q = e.QUANTITY_SCALE
PERSON = e.LaneId("p1")
X, A, B, TOWN = e.StoreId("x"), e.CardId("a"), e.CardId("b"), e.MixId("town:main")
RULE = e.Order(e.AtLeast(e.CardCount(A), 15, 15), e.TapCard(B))
ALWAYS = e.AfterTime(0)


def old_rules() -> e.Rules:
    """One ruled lane, its card a uncapped and making x, b uncapped; no join."""
    return e.Rules(stores=(e.StoreDef(X, 10**6 * Q, 0),), skills=(e.SkillDef(e.SkillId("k")),), standing=(),
                   curve=e.PacingCurve((10**9 * Q,)), lanes=(e.LaneDef(PERSON, True),),
                   cards=(e.CardDef(A, 100, lane=PERSON, makes=(e.Flow(X, Q),)), e.CardDef(B, 50, lane=PERSON)))


def new_rules() -> e.Rules:
    """old_rules plus a trigger at second 100 whose outcome joins the lane."""
    r = replace(old_rules(), triggers=(e.TriggerDef(e.TriggerId("join"), e.AfterTime(100),
                                                    e.Outcome(joins=(e.Join(PERSON, TOWN),))),))
    e.validate_rules(r)
    return r


def saved_before_the_join() -> e.Save:
    """The person's always rule and the rule that is not, a tap of a in progress, at 500 s under old_rules."""
    r = old_rules()
    return e.advance(e.decide(e.new_save(r), r, 0, e.SetOrders((RULE, e.Order(ALWAYS, e.TapCard(A))))), r, 500)


def joined_save() -> e.Save:
    return e.rebase(e.encode(saved_before_the_join(), old_rules()), new_rules())


def game(rules: e.Rules) -> Game:
    """The townsfolk chapter's content over the fixture's rules: the wire reads only the rules and the save."""
    return Game(loaded(), replace(ruleset(loaded(), [], "test", 1), rules=rules))


def town_mix(*shares: tuple[str, int]) -> w.SaveMix:
    return w.SaveMix(mix=w.Mix(id=str(TOWN), components=[w.CardShare(card=c, share_bp=bp) for c, bp in shares]))


def decide(g: Game, save: e.Save, rules: e.Rules, decision: w.Decision) -> e.Save:
    return e.decide(save, rules, save.time, g.verb(decision))


def test_the_view_serves_the_town_mix_before_and_after_the_join():
    before_rules, rules = old_rules(), new_rules()
    before = game(before_rules).view(saved_before_the_join())
    assert (before.running_town_mix_id, before.town_mix_order) == (None, None)
    assert not [u for u in before.unlocked if u.category is w.UnlockKind.JOINED]
    save = joined_save()
    wire = game(rules).view(save)
    assert w.View.model_validate(wire.model_dump()) == wire
    assert wire.running_town_mix_id == str(TOWN)
    assert wire.orders[wire.town_mix_order or 0].then == w.SwitchMix(mix_id=str(TOWN))
    assert w.Unlock(category=w.UnlockKind.JOINED, id=PERSON) in wire.unlocked
    assert wire.running_mix_id != str(TOWN) and wire.active_mix_id != str(TOWN)   # the hands read hands mixes alone
    assert [(m.id, [c.card for c in m.components if isinstance(c, w.CardShare)]) for m in wire.mixes if m.id == str(TOWN)] == [(str(TOWN), ["a"])]


def test_a_town_mix_saved_over_the_wire_is_served_and_runs_at_once():
    rules, save = new_rules(), joined_save()
    g = game(rules)
    saved = decide(g, save, rules, town_mix(("a", 4000), ("b", 3000)))
    mix = next(m for m in g.view(saved).mixes if m.id == str(TOWN))
    assert [(c.card, c.share_bp) for c in mix.components if isinstance(c, w.CardShare)] == [("a", 4000), ("b", 3000)]
    assert g.view(saved).running_town_mix_id == str(TOWN)


@pytest.mark.parametrize("decision", [
    town_mix(("a", 6000), ("b", 5000)),                                                        # one person above 10000
    w.SaveMix(mix=w.Mix(id="town:mine", components=[w.CardShare(card="a", share_bp=100)])),   # a reserved id
    w.SwitchMix(mix_id=str(TOWN)),                                                          # set by rules
    w.SetQueue(entries=[w.QueueEntry(verb=w.SwitchMix(mix_id=str(TOWN)), until=w.AfterTime(at=5))]),   # the hands' plan
], ids=["over", "reserved", "switch", "queue"])
def test_each_refusal_is_invalid_and_writes_nothing(decision: w.Decision):
    rules, save = new_rules(), joined_save()
    with pytest.raises(e.InvalidVerbError):
        decide(game(rules), save, rules, decision)
    assert e.encode(save, rules) == e.encode(joined_save(), rules)


def test_set_orders_accepts_a_town_mix_as_the_towns_rule():
    rules, save = new_rules(), joined_save()
    order = w.Order(when=w.AfterTime(at=0), then=w.SwitchMix(mix_id=str(TOWN)))
    assert decide(game(rules), save, rules, w.SetOrders(orders=[order])).orders[0].then == e.SwitchMix(TOWN)
