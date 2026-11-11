"""Offer kinds (engine DESIGN.txt, part "OFFER KINDS", invariants 98-107): an AnswerKind order answers the first open
offer of its kind by role, every offer of the kind it can, as each shows."""
import json
from collections.abc import Callable
from dataclasses import replace

import pytest

from ashfall_app.engine import (
    QUANTITY_SCALE as Q, AfterTime, AnswerDef, AnswerId, AnswerKind, AnswerOffer, CardDef, CardId, InvalidRulesError,
    InvalidVerbError, KindId, LineKey, OfferDef, OfferId, Order, OrderState, Outcome, PacingCurve, QueueEntry,
    RebaseError, RoleId, Rules, Save, SetOrders, SetQueue, SkillDef, SkillId, StoreDef, StoreId, TriggerDef, TriggerId,
    Unlock, UnlockKind, advance, advance_logged, decide, decide_logged, decode, encode, new_save, rebase, rules_digest,
    validate_rules, view,
)
from ashfall_app.engine.codec import to_json, verb_from_json, verb_to_json

ASK, OTHER = KindId("ask"), KindId("other")
YES, NO = RoleId("yes"), RoleId("no")
RULE = Order(AfterTime(0), AnswerKind(ASK, YES))


def offer(name: str, kind: KindId | None, reverse: bool = False) -> OfferDef:
    """Answers `<name>_yes` and `<name>_no` (listed no first when `reverse`), each writing a line of its own id."""
    answers = [AnswerDef(AnswerId(f"{name}_{r}"), Outcome(lines=(LineKey(f"{name}_{r}"),)),
                         None if kind is None else RoleId(r)) for r in ("yes", "no")]
    return OfferDef(OfferId(name), tuple(reversed(answers) if reverse else answers), kind)


def unroled(o: OfferDef) -> OfferDef:
    return replace(o, answers=tuple(replace(a, role=None) for a in o.answers))


def unkinded(o: OfferDef) -> OfferDef:
    return replace(unroled(o), kind=None)


def half_roled(o: OfferDef) -> OfferDef:
    return replace(o, answers=(replace(o.answers[0], role=None), o.answers[1]))


def kindless(o: OfferDef) -> OfferDef:
    return replace(o, kind=None)


def shared_role(o: OfferDef) -> OfferDef:
    return replace(o, answers=tuple(replace(a, role=YES) for a in o.answers))


def odd_role(o: OfferDef) -> OfferDef:
    return replace(o, answers=(replace(o.answers[0], role=RoleId("maybe")), o.answers[1]))


def other_kind(o: OfferDef) -> OfferDef:
    return replace(o, kind=OTHER)


def renamed_roles(o: OfferDef) -> OfferDef:
    return replace(o, answers=tuple(replace(a, role=RoleId("z" + str(a.role))) for a in o.answers))


def world(shows: dict[str, int], offers: tuple[OfferDef, ...] | None = None, firings: int = 1000) -> Rules:
    """Offers a1, a2 (answers listed no first), a3 of kind ask, x of kind other, u unkinded, each shown at its time."""
    made = offers or (offer("a1", ASK), offer("a2", ASK, True), offer("a3", ASK), offer("x", OTHER), offer("u", None))
    triggers = tuple(TriggerDef(TriggerId(f"show_{o}"), AfterTime(t), Outcome(unlocks=(Unlock(UnlockKind.OFFER, OfferId(o)),)))
                     for o, t in shows.items())
    r = Rules(stores=(StoreDef(StoreId("s"), 100 * Q, 0),), skills=(SkillDef(SkillId("k")),), standing=(),
              curve=PacingCurve((10**9 * Q,)), cards=(CardDef(CardId("h"), 10),), triggers=triggers, offers=made,
              opening=(Unlock(UnlockKind.CARD, CardId("h")),), max_firings_per_instant=firings)
    validate_rules(r)
    return r


def given(s: Save) -> set[str]:
    return {u.id for u in s.unlocked if u.kind is UnlockKind.ANSWER}


def ruled(r: Rules, at: int = 0) -> Save:
    return decide(new_save(r), r, at, SetOrders((RULE,)))


def test_two_open_offers_are_answered_at_one_instant_by_role_whatever_their_answer_order():
    r = world({"a1": 10, "a2": 10, "a3": 10, "x": 10, "u": 10})
    s = decide(advance(new_save(r), r, 20), r, 20, SetOrders((RULE,)))
    assert given(s) == {"a1_yes", "a2_yes", "a3_yes"}   # x is another kind, u has none
    assert Unlock(UnlockKind.ANSWERED, OfferId("x")) not in s.unlocked


def test_the_first_open_offer_in_rules_order_is_answered_first_whatever_showed_first():
    r = world({"a3": 5, "a1": 10, "a2": 10})
    step = decide_logged(advance(new_save(r), r, 20), r, 20, SetOrders((RULE,)))
    assert [ln.key for ln in step.lines] == ["a1_yes", "a2_yes", "a3_yes"]


def test_a_later_offer_is_answered_at_the_instant_it_shows_and_equals_the_player_answering_each():
    r = world({"a1": 10, "a2": 80})
    by_rule = advance_logged(decide(advance(new_save(r), r, 60), r, 60, SetOrders((RULE,))), r, 100)
    first = decide(advance(new_save(r), r, 60), r, 60, AnswerOffer(OfferId("a1"), AnswerId("a1_yes")))
    by_hand = decide_logged(advance(first, r, 80), r, 80, AnswerOffer(OfferId("a2"), AnswerId("a2_yes")))
    assert [ln.key for ln in by_rule.lines] == ["a2_yes"] and [ln.time for ln in by_rule.lines] == [80]
    a, b = by_rule.save, advance(by_hand.save, r, 100)
    for part in ("stores", "cards", "lanes", "unlocked", "modifiers", "fired"):
        assert getattr(a, part) == getattr(b, part), part
    assert a.orders == (RULE,) and b.orders == ()


def test_the_rule_is_never_dead_and_answers_each_offer_of_the_kind_as_it_shows():
    r = world({"a1": 10, "a2": 50, "a3": 90})
    s = ruled(r)
    assert view(s, r).order_states == (OrderState.ON,)
    for t, answered in ((10, {"a1_yes"}), (60, {"a1_yes", "a2_yes"}), (100, {"a1_yes", "a2_yes", "a3_yes"})):
        s = advance(s, r, t)
        assert given(s) == answered and view(s, r).order_states == (OrderState.ON,) and s.orders == (RULE,)


def test_it_answers_no_offer_not_shown_none_answered_and_none_of_another_kind():
    r = world({"a1": 100, "x": 10, "u": 10})
    s = advance(ruled(r), r, 50)
    assert given(s) == set()                                       # a1 not shown yet; x and u are not of the kind
    answered = decide(advance(new_save(r), r, 100), r, 100, AnswerOffer(OfferId("a1"), AnswerId("a1_no")))
    assert given(decide(answered, r, 100, SetOrders((RULE,)))) == {"a1_no"}   # an answered offer is left alone


def test_an_unshown_offer_earlier_in_rules_order_does_not_hold_back_a_shown_later_one():
    r = world({"a2": 10, "a1": 100})
    assert given(advance(ruled(r), r, 50)) == {"a2_yes"}


def test_a_rule_for_the_other_role_gives_the_other_answer():
    r = world({"a1": 10, "a2": 10})
    s = decide(advance(new_save(r), r, 20), r, 20, SetOrders((Order(AfterTime(0), AnswerKind(ASK, NO)),)))
    assert given(s) == {"a1_no", "a2_no"}


def test_the_firing_cap_suspends_the_answers_and_a_ready_at_the_next_second_goes_on():
    r = world({"a1": 10, "a2": 11, "a3": 12}, firings=2)
    s = decide(advance(new_save(r), r, 20), r, 20, SetOrders((RULE,)))
    assert given(s) == {"a1_yes", "a2_yes"}
    assert given(advance(s, r, 21)) == {"a1_yes", "a2_yes", "a3_yes"}


def test_the_player_cannot_decide_an_answer_by_kind_nor_queue_one():
    r = world({"a1": 10})
    s = advance(new_save(r), r, 20)
    with pytest.raises(InvalidVerbError):
        decide(s, r, 20, AnswerKind(ASK, YES))
    with pytest.raises(InvalidVerbError):
        decide(s, r, 20, SetQueue((QueueEntry(AnswerKind(ASK, YES), AfterTime(10**9)),)))
    assert given(s) == set()


@pytest.mark.parametrize("verb", [AnswerKind(KindId("nope"), YES), AnswerKind(ASK, RoleId("maybe"))],
                         ids=["unknown kind", "role the kind lacks"])
def test_a_rule_naming_no_declared_kind_and_role_is_refused(verb: AnswerKind):
    r = world({})
    with pytest.raises(InvalidVerbError):
        decide(new_save(r), r, 0, SetOrders((Order(AfterTime(0), verb),)))


def test_a_declared_kind_and_role_is_accepted_with_no_offer_open():
    r = world({"a1": 100})
    assert ruled(r).orders == (RULE,)


PLANTS = [(unroled, "needs a role"), (half_roled, "needs a role"), (kindless, "has no kind"), (shared_role, "share a role"),
          (odd_role, "differ")]


@pytest.mark.parametrize("change,message", PLANTS, ids=["no roles", "one role missing", "no kind", "shared role", "different roles"])
def test_planted_offers_fail_validation_each_for_its_own_reason(change: Callable[[OfferDef], OfferDef], message: str):
    """Against a second, sound offer of the kind for the role sets, and alone for the offer's own rules."""
    with pytest.raises(InvalidRulesError, match=message):
        world({}, (offer("a1", ASK), change(offer("a2", ASK))))
    if change is not odd_role:
        with pytest.raises(InvalidRulesError, match=message):
            world({}, (change(offer("a1", ASK)),))


def test_a_kind_with_one_offer_is_valid():
    assert world({}, (offer("a1", ASK),)).offers[0].kind == ASK


def test_the_codec_round_trips_kinds_and_writes_them_into_the_manifest():
    r = world({"a1": 10})
    s = advance(ruled(r), r, 20)
    text = encode(s, r)
    assert decode(text, r) == s
    manifest = {o["id"]: o for o in json.loads(text)["manifest"]["offers"]}
    assert manifest["a2"] == {"id": "a2", "answers": ["a2_no", "a2_yes"], "kind": "ask", "roles": ["no", "yes"]}
    assert manifest["u"] == {"id": "u", "answers": ["u_yes", "u_no"]}


def test_rules_with_no_kind_keep_their_digest_and_text():
    kinded = world({})
    plain = world({}, tuple(unkinded(o) for o in kinded.offers))
    text = encode(new_save(plain), plain)
    assert '"role"' not in text and '"roles"' not in text and '"kind":"ask"' not in text
    assert all(set(o) == {"id", "answers"} for o in json.loads(text)["manifest"]["offers"])
    assert rules_digest(plain) != rules_digest(kinded)


def test_an_unkinded_offer_is_encoded_as_it_was_before_kinds():
    """The rules digest reads this encoding, so rules that use no kind keep theirs."""
    plain = world({}).offers[4]
    assert plain.kind is None
    encoded = to_json(plain)
    assert isinstance(encoded, dict) and set(encoded) == {"@", "id", "answers"}
    answers = encoded["answers"]
    assert isinstance(answers, list) and all(isinstance(a, dict) and set(a) == {"@", "id", "outcome"} for a in answers)
    kinded = to_json(world({}).offers[0])
    assert isinstance(kinded, dict) and set(kinded) == {"@", "id", "answers", "kind"}


def test_an_answer_by_kind_verb_round_trips():
    verb = SetOrders((RULE,))
    assert verb_from_json(verb_to_json(verb)) == verb


def test_a_save_rebases_into_rules_that_give_an_offer_a_kind_and_keeps_its_rule():
    plain = world({"a1": 10}, tuple(unkinded(o) for o in world({}).offers))
    old = encode(advance(new_save(plain), plain, 20), plain)
    now = world({"a1": 10})
    s = decide(rebase(old, now), now, 20, SetOrders((RULE,)))
    assert given(s) == {"a1_yes"}


@pytest.mark.parametrize("change", [other_kind, renamed_roles], ids=["kind changed", "roles changed"])
def test_a_save_cannot_rebase_into_rules_that_change_a_kind_or_a_role_it_was_written_with(
        change: Callable[[OfferDef], OfferDef]):
    old_rules = world({"a1": 10}, (offer("a1", ASK),))
    old = encode(new_save(old_rules), old_rules)
    changed = world({"a1": 10}, (change(offer("a1", ASK)),))
    with pytest.raises(RebaseError):
        rebase(old, changed)
