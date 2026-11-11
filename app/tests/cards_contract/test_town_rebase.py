"""Rebase for day two (engine DESIGN.txt, part "TOWNSFOLK, INSTALLED RULES AND OFFERS": "Rebase", "Installs land
once"; invariant 60). IdKind gains OFFER and ANSWER. Step 3 renames Unlock(OFFER) and Unlock(ANSWERED) by OFFER,
Unlock(ANSWER) by ANSWER, and both ids of an AnswerOffer in orders and the queue; step 4 checks them against the
manifest's offers and raises RebaseError(ANSWER, id) for an answer the new rules put under another offer; step 6 is
where a new trigger already true installs its rule, reported by rebase_logged's rule changes."""
from collections.abc import Mapping
from dataclasses import fields, is_dataclass, replace
from typing import TypeGuard

import pytest

from ashfall_app.engine import (
    AfterTime, AnswerDef, AnswerId, AnswerOffer, IdKind, OfferDef, OfferId, Order, Outcome, QueueEntry, RebaseError,
    Rename, RuleChange, RuleInstall, Rules, Save, SetOrders, SetQueue, StoreDef, StoreId, TriggerDef, TriggerId,
    Unlock, UnlockKind, advance, decide, encode, rebase, rebase_logged, unlock_key, validate_rules,
)
from cards_world import Q
from town_world import (
    ASK, LATER, NEVER, NO, OTHER, SECOND, SOONER, T1, TOWN, YES, always, answer, running, started, town,
)

NAMES = {"ask": "ask2", "other": "other2", "yes": "yes2", "no": "no2", "later": "later2", "sooner": "sooner2"}
RENAMES = (Rename(IdKind.OFFER, "ask", "ask2"), Rename(IdKind.OFFER, "other", "other2"),
           Rename(IdKind.ANSWER, "yes", "yes2"), Rename(IdKind.ANSWER, "no", "no2"),
           Rename(IdKind.ANSWER, "later", "later2"), Rename(IdKind.ANSWER, "sooner", "sooner2"))


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


def sub_save(s: Save, ids: Mapping[str, str]) -> Save:
    """What a save says under renamed ids: every id replaced, the unlock set re-sorted (step 5)."""
    out = _sub(s, ids)
    assert isinstance(out, Save)
    return replace(out, unlocked=tuple(sorted(out.unlocked, key=unlock_key)))


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


def test_offer_and_answer_renames_reach_every_unlock_and_every_answer_offer():
    """Step 3: OFFER renames Unlock(OFFER) and Unlock(ANSWERED), ANSWER renames Unlock(ANSWER), and AnswerOffer's two ids
    are renamed in orders and the queue: the save under renamed rules is the save under the old ones, renamed."""
    r, s = world()
    text = encode(s, r)
    r2 = sub_rules(spare(r), NAMES)
    validate_rules(r2)
    got = rebase(text, r2, RENAMES)
    assert got == sub_save(rebase(text, spare(r), ()), NAMES)
    assert Unlock(UnlockKind.ANSWERED, "ask2") in got.unlocked and Unlock(UnlockKind.ANSWER, "yes2") in got.unlocked
    assert got.orders[-1].then == AnswerOffer(OfferId("other2"), AnswerId("later2"))
    assert got.queue[0].verb == AnswerOffer(OfferId("other2"), AnswerId("sooner2"))


def test_renames_of_one_kind_never_touch_the_other():
    """Each id is renamed by renames of its own kind: an ANSWER rename named like an offer leaves the offer alone, so
    the save's offer id, missing from the new rules, raises RebaseError(OFFER, ask)."""
    r, s = world()
    r2 = sub_rules(spare(r), {"ask": "ask2"})
    with pytest.raises(RebaseError) as raised:
        rebase(encode(s, r), r2, (Rename(IdKind.ANSWER, "ask", "ask2"),))
    assert (raised.value.kind, raised.value.id) == (IdKind.OFFER, "ask")
    assert rebase(encode(s, r), r2, (Rename(IdKind.OFFER, "ask", "ask2"),)).unlocked


def moved(yes_under_other: bool) -> Rules:
    """The world's rules with `yes` moved to `other` (ask keeps `no` and gains `maybe`), when asked."""
    r = spare(town(offers=(SECOND,)))
    if not yes_under_other:
        return r
    ask = OfferDef(ASK, (AnswerDef(NO, Outcome()), AnswerDef(AnswerId("maybe"), Outcome())))
    other = OfferDef(OTHER, (AnswerDef(LATER, Outcome()), AnswerDef(SOONER, Outcome()), AnswerDef(YES, Outcome())))
    return replace(r, offers=(ask, other))


def test_an_answer_moved_to_another_offer_raises_naming_it_as_the_save_had_it():
    """Step 4: an answer the save's manifest puts under one offer that, renamed, the new rules put under another
    raises RebaseError(ANSWER, id), the id as the save had it; the unmoved rules are the control."""
    r, s = world()
    text = encode(s, r)
    assert rebase(text, moved(False), ()) is not None
    with pytest.raises(RebaseError) as raised:
        rebase(text, moved(True), ())
    assert (raised.value.kind, raised.value.id) == (IdKind.ANSWER, "yes")
    renamed = sub_rules(moved(True), {"yes": "aye"})
    with pytest.raises(RebaseError) as raised:
        rebase(text, renamed, (Rename(IdKind.ANSWER, "yes", "aye"),))
    assert (raised.value.kind, raised.value.id) == (IdKind.ANSWER, "yes")


def test_a_gone_answer_raises_and_a_gone_offer_raises_for_it_or_its_answers():
    """Step 4, as for every declared id: `sooner` gone (other keeps two answers) raises RebaseError(ANSWER, sooner);
    `other` gone with its answers raises naming the offer or one of its answers (which is checked first is not
    stated)."""
    r, s = world()
    text = encode(s, r)
    fewer = OfferDef(OTHER, (AnswerDef(LATER, Outcome()), AnswerDef(AnswerId("new"), Outcome())))
    with pytest.raises(RebaseError) as raised:
        rebase(text, replace(spare(r), offers=(r.offers[0], fewer)), ())
    assert (raised.value.kind, raised.value.id) == (IdKind.ANSWER, "sooner")
    with pytest.raises(RebaseError) as raised:
        rebase(text, replace(spare(r), offers=r.offers[:1]), ())
    assert (raised.value.kind, raised.value.id) in {(IdKind.OFFER, "other"), (IdKind.ANSWER, "later"),
                                                     (IdKind.ANSWER, "sooner")}


GO = TriggerId("go")


def test_a_new_trigger_already_true_installs_its_rule_at_the_rebase_instant_and_logs_it():
    """Step 6: a save already past a moment that installs a rule gets it at the rebase instant, forward only, latch on;
    rebase_logged's Step carries that instant's rule changes, so the install is listed from the rebase; it acts there
    (the town was free)."""
    r = town()
    s = advance(started(r), r, 500)
    r2 = replace(r, triggers=r.triggers + (TriggerDef(GO, AfterTime(100), Outcome(orders=(RuleInstall(T1),))),))
    validate_rules(r2)
    step = rebase_logged(encode(s, r), r2, ())
    assert step.save == rebase(encode(s, r), r2, ())
    assert step.save.time == 500 and step.save.orders == (always(T1),) and step.save.latches == (True,)
    assert RuleChange(500, always(T1), True, None) in step.rule_changes
    assert running(step.save, TOWN) == T1


def test_a_removed_installed_rule_does_not_come_back_through_a_rebase():
    """Invariant 60: step 6 never re-fires a fired trigger, so after the player removed the rule a rebase under an
    allowed change (a new store) leaves it removed; so does one renaming the trigger."""
    r = replace(town(), triggers=town().triggers + (TriggerDef(GO, AfterTime(100), Outcome(orders=(RuleInstall(T1),))),))
    s = advance(started(r), r, 150)
    assert s.orders == (always(T1),)
    s = decide(s, r, 200, SetOrders(()))
    assert rebase(encode(s, r), spare(r), ()).orders == ()
    r2 = sub_rules(spare(r), {"go": "go2"})
    assert rebase(encode(s, r), r2, (Rename(IdKind.TRIGGER, "go", "go2"),)).orders == ()
