"""Pending triggers (DESIGN.txt, "Pending triggers"): every unfired trigger whose requires hold or are each an unlock an
unfired trigger gives, with when it fires under the segments now; a require on an unlock waits for its giver; a time
shown comes true by itself; a fired trigger, and one waiting on a require no trigger gives, is not listed."""
from ashfall_app.engine import (
    AfterTime, AtLeast, CardCount, CardDef, CardId, FeatureId, Flow, Outcome, Rules, StandingDef, StoreDef, StoreId,
    Running, StoreValue, TriggerDef, TriggerId, Unlock, UnlockKind, Unlocked, ActionId, advance, new_save, pending,
    validate_rules,
)
from cards_world import Q, rules

C = StoreId("clock")
G = CardId("g")
F, H = FeatureId("f"), FeatureId("h")


def _feature(f: FeatureId) -> Outcome:
    return Outcome(unlocks=(Unlock(UnlockKind.FEATURE, f),))


def _needs(f: FeatureId) -> tuple[AtLeast, ...]:
    return (AtLeast(Unlocked(Unlock(UnlockKind.FEATURE, f)), 1, 1),)


def world() -> Rules:
    """A clock fills an item an hour. t_a at two items gives f; t_b at one item also needs f; t_c needs g running,
    which no trigger gives; t_d waits on two completions of g, which nothing runs."""
    r = rules([StoreDef(C, 100 * Q)], standing=[StandingDef(ActionId("tick"), makes=(Flow(C, 1000),))],
              cards=[CardDef(G, 100)],
              triggers=[
                  TriggerDef(TriggerId("t_a"), AtLeast(StoreValue(C), 2 * Q, 2 * Q), _feature(F)),
                  TriggerDef(TriggerId("t_b"), AtLeast(StoreValue(C), Q, Q), _feature(H), _needs(F)),
                  TriggerDef(TriggerId("t_c"), AfterTime(10), _feature(H), (AtLeast(Running(G), 1, 1),)),
                  TriggerDef(TriggerId("t_d"), AtLeast(CardCount(G), 2, 2), _feature(H)),
              ], opening=[Unlock(UnlockKind.STORE, C), Unlock(UnlockKind.CARD, G), Unlock(UnlockKind.ACTION, ActionId("tick"))])
    validate_rules(r)
    return r


def test_each_pending_trigger_with_when_it_fires():
    r = world()
    got = {str(p.trigger): (p.at, p.held) for p in pending(new_save(r), r)}
    assert got == {"t_a": (7200, True), "t_b": (7200, False), "t_d": (None, True)}


def test_the_time_comes_true_by_itself():
    r = world()
    s = new_save(r)
    before, at = advance(s, r, 7199), advance(s, r, 7200)
    assert {p.trigger for p in pending(before, r)} >= {"t_a", "t_b"}
    assert {p.trigger for p in pending(at, r)} == {"t_d"}


def test_a_require_already_met_waits_on_nothing_but_the_condition():
    """Once f is given, t_b's own condition (an item, already held) is all it waits on: it fires at once, so it is
    listed no more."""
    r = world()
    s = advance(new_save(r), r, 3600)
    got = {str(p.trigger): (p.at, p.held) for p in pending(s, r)}
    assert got["t_b"] == (7200, False) and got["t_a"] == (7200, True)


def test_only_restricts_what_is_listed():
    r = world()
    assert [p.trigger for p in pending(new_save(r), r, {"t_b"})] == ["t_b"]
