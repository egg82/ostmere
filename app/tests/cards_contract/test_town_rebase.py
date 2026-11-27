"""Rebase for day two (engine design/townsfolk.txt, part "TOWNSFOLK, INSTALLED RULES AND OFFERS": "Rebase", "Installs land
once"; invariant 60). IdKind gains OFFER and ANSWER. Step 3 drops an offer or answer the new rules lack (an answer
they put under another offer counts as gone) from the unlock set (OFFER, ANSWERED, ANSWER) and drops each order and
queue entry answering one; step 6 is where a new trigger already true installs its rule, reported by rebase_logged's
rule changes."""
from collections.abc import Mapping
from dataclasses import fields, is_dataclass, replace
from typing import TypeGuard


from ashfall_app.engine import (
    AfterTime, AnswerDef, AnswerId, AnswerOffer, IdKind, OfferDef, Order, Outcome, QueueEntry, RuleChange,
    RuleInstall, Rules, Save, SetOrders, SetQueue, StoreDef, StoreId, TriggerDef, TriggerId, Unlock, UnlockKind,
    advance, decide, encode, rebase, rebase_logged, validate_rules,
)
from cards_world import Q
from town_world import (
    ASK, LATER, NEVER, NO, OTHER, SECOND, SOONER, T1, TOWN, YES, always, answer, running, started, town,
)

NAMES = {"ask": "ask2", "other": "other2", "yes": "yes2", "no": "no2", "later": "later2", "sooner": "sooner2"}


def _is_tuple(v: object) -> TypeGuard[tuple[object, ...]]:
    return isinstance(v, tuple)


def _sub(v: object, ids: Mapping[str, str]) -> object:
    if isinstance(v, str):
        return ids.get(v, v)
    if _is_tuple(v):
        return tuple(_sub(x, ids) for x in v)
    if is_dataclass(v) and not isinstance(v, type):
        return replace(v, **{f.name: _sub(getattr(v, f.name), ids) for f in fields(v)})
    return v


def sub_rules(r: Rules, ids: Mapping[str, str]) -> Rules:
    """r with every id string in `ids` replaced (every id string in this world is distinct from every line key)."""
    out = _sub(r, ids)
    assert isinstance(out, Rules)
    return out


def spare(r: Rules) -> Rules:
    """Other rules (a new digest) with the same behaviour: one unused store added."""
    return replace(r, stores=r.stores + (StoreDef(StoreId("spare"), Q, 0),))


def world() -> tuple[Rules, Save]:
    """ask shown at 50 and answered yes at 60; other never shown, its answer in an order and in the queue."""
    r = town(offers=(SECOND,))
    s = started(r, SetOrders((Order(NEVER, AnswerOffer(OTHER, LATER)),)),
                SetQueue((QueueEntry(AnswerOffer(OTHER, SOONER), NEVER),)))
    return r, answer(advance(s, r, 60), r, 60, YES)


def test_idkind_gains_offer_and_answer():
    assert {IdKind.OFFER.name, IdKind.ANSWER.name} <= {k.name for k in IdKind}


def answered(s: Save) -> set[Unlock]:
    kinds = (UnlockKind.OFFER, UnlockKind.ANSWERED, UnlockKind.ANSWER)
    return {u for u in s.unlocked if u.kind in kinds}


def test_rules_that_rename_every_offer_and_answer_drop_each_from_the_save():
    """Step 3: every offer and answer id is gone from the new rules, so the save keeps no unlock of them and no order
    or queue entry answering them, and counts what it dropped."""
    r, s = world()
    r2 = sub_rules(spare(r), NAMES)
    validate_rules(r2)
    step = rebase_logged(encode(s, r), r2)
    assert answered(s) and any(isinstance(o.then, AnswerOffer) for o in s.orders) and s.queue   # control
    assert answered(step.save) == set() and step.save.queue == ()
    assert not any(isinstance(o.then, AnswerOffer) for o in step.save.orders)
    assert step.dropped == ((IdKind.OFFER, 2), (IdKind.ANSWER, 4))


def test_a_gone_offer_takes_only_its_own_unlocks():
    """ask renamed: ask's unlocks go, and its answer yes (now under ask2) with them; other's order and queue entry
    stay."""
    r, s = world()
    got = rebase(encode(s, r), sub_rules(spare(r), {"ask": "ask2"}))
    assert answered(got) == set()
    assert got.orders[-1].then == AnswerOffer(OTHER, LATER) and got.queue[0].verb == AnswerOffer(OTHER, SOONER)


def moved(yes_under_other: bool) -> Rules:
    """The world's rules with `yes` moved to `other` (ask keeps `no` and gains `maybe`), when asked."""
    r = spare(town(offers=(SECOND,)))
    if not yes_under_other:
        return r
    ask = OfferDef(ASK, (AnswerDef(NO, Outcome()), AnswerDef(AnswerId("maybe"), Outcome())))
    other = OfferDef(OTHER, (AnswerDef(LATER, Outcome()), AnswerDef(SOONER, Outcome()), AnswerDef(YES, Outcome())))
    return replace(r, offers=(ask, other))


def test_an_answer_moved_to_another_offer_is_dropped_and_its_old_offer_stays_answered():
    """Step 3: an answer the new rules put under another offer is gone; the unmoved rules are the control."""
    r, s = world()
    text = encode(s, r)
    assert Unlock(UnlockKind.ANSWER, YES) in rebase(text, moved(False)).unlocked
    got = rebase_logged(text, moved(True))
    assert Unlock(UnlockKind.ANSWER, YES) not in got.save.unlocked
    assert Unlock(UnlockKind.ANSWERED, ASK) in got.save.unlocked and got.dropped == ((IdKind.ANSWER, 1),)


def test_a_gone_answer_drops_what_answers_with_it_and_a_gone_offer_drops_all_of_its():
    """`sooner` gone (other keeps two answers): the queue entry answering it goes, the order answering `later` stays;
    `other` gone with its answers: both go."""
    r, s = world()
    text = encode(s, r)
    fewer = OfferDef(OTHER, (AnswerDef(LATER, Outcome()), AnswerDef(AnswerId("new"), Outcome())))
    got = rebase(text, replace(spare(r), offers=(r.offers[0], fewer)))
    assert got.queue == () and got.orders[-1].then == AnswerOffer(OTHER, LATER)
    gone = rebase(text, replace(spare(r), offers=r.offers[:1]))
    assert gone.queue == () and not any(isinstance(o.then, AnswerOffer) for o in gone.orders)


GO = TriggerId("go")


def test_a_new_trigger_already_true_installs_its_rule_at_the_rebase_instant_and_logs_it():
    """Step 6: a save already past a moment that installs a rule gets it at the rebase instant, forward only, latch on;
    rebase_logged's Step carries that instant's rule changes, so the install is listed from the rebase; it acts there
    (the town was free)."""
    r = town()
    s = advance(started(r), r, 500)
    r2 = replace(r, triggers=r.triggers + (TriggerDef(GO, AfterTime(100), Outcome(orders=(RuleInstall(T1),))),))
    validate_rules(r2)
    step = rebase_logged(encode(s, r), r2)
    assert step.save == rebase(encode(s, r), r2)
    assert step.save.time == 500 and step.save.orders == (always(T1),) and step.save.latches == (True,)
    assert RuleChange(500, always(T1), True, None) in step.rule_changes
    assert running(step.save, TOWN) == T1


def test_a_removed_installed_rule_does_not_come_back_through_a_rebase():
    """Invariant 60: step 6 never re-fires a fired trigger, so after the player removed the rule a rebase under a
    change that keeps the trigger (a new store) leaves it removed. A renamed trigger is a new one, so it fires and
    installs the rule again (the control)."""
    r = replace(town(), triggers=town().triggers + (TriggerDef(GO, AfterTime(100), Outcome(orders=(RuleInstall(T1),))),))
    s = advance(started(r), r, 150)
    assert s.orders == (always(T1),)
    s = decide(s, r, 200, SetOrders(()))
    assert rebase(encode(s, r), spare(r)).orders == ()
    r2 = sub_rules(spare(r), {"go": "go2"})
    assert rebase(encode(s, r), r2).orders == (always(T1),)
