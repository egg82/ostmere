"""A role cast from per-lane counts (api/contract/casting.txt, "CASTING"): unit tests written beside the implementation.
The blind contract tests are written elsewhere, from the contract alone."""
from dataclasses import replace

import pytest

from ashfall_app.engine import (
    BP, AfterTime, AnswerDef, AnswerId, Cast, CastPick, CardDef, CardId, CardState, FeatureId, InvalidRulesError, Join,
    LaneDef, LaneId, Leave, MixId, OfferDef, OfferId, Outcome, PacingCurve, Rules, Save, Segment, TriggerDef, TriggerId,
    UnlockKind, advance, decode, encode, new_save, rebase, rules_digest, validate_rules,
)
from ashfall_app.engine.casts import cast_roles
from ashfall_app.engine.joins import joined
from ashfall_app.engine.leaves import left
from ashfall_app.engine.unlock_known import features

TOWN = MixId("town:main")
WORK = 100
P = [LaneId(f"p{i}") for i in range(1, 5)]
G = LaneId("grp")
"""p1 to p4 are people, declared in this order; grp is a group."""


def hunt(lane: LaneId) -> CardId:
    return CardId(f"hunt_{lane}")


def fish(lane: LaneId) -> CardId:
    return CardId(f"fish_{lane}")


def role(role_id: str = "scout", lanes: list[LaneId] | None = None, patterns: int = 2) -> Cast:
    """Every person is a pick, each counting hunt then fish (a pattern past two counts nothing)."""
    return Cast(role_id, tuple(CastPick(x, FeatureId(f"{role_id}_{x}"), (hunt(x), fish(x))[:patterns])
                               for x in (P if lanes is None else lanes)))


def world(*casts: Cast, joins: bool = True) -> Rules:
    cards = tuple(CardDef(c(x), WORK, lane=x) for x in (*P, G) for c in (hunt, fish))
    triggers = [TriggerDef(TriggerId("join"), AfterTime(0), Outcome(joins=tuple(Join(x, TOWN) for x in P)))] if joins else []
    triggers.append(TriggerDef(TriggerId("cast"), AfterTime(10), Outcome(casts=casts)))
    lanes = (*(LaneDef(x, True) for x in P), LaneDef(G, True, pooled=True))
    r = Rules(stores=(), skills=(), standing=(), curve=PacingCurve((10**9,)), lanes=lanes, cards=cards,
              triggers=tuple(triggers), opening=())
    validate_rules(r)
    return r


def planted(r: Rules, counts: dict[CardId, int]) -> Save:
    """A save at the moment the people have joined, with each card's completions as given."""
    s = advance(new_save(r), r, 1)
    states = tuple(CardState(c.id, Segment(s.time, counts[c.id] * WORK * BP, 0)) for c in r.cards if c.id in counts)
    return replace(s, cards=states)


def cast_of(s: Save, role_id: str = "scout") -> list[str]:
    return [u.id for u in s.unlocked if u.kind is UnlockKind.FEATURE and u.id.startswith(f"{role_id}_")]


def run(counts: dict[CardId, int], c: Cast | None = None) -> list[str]:
    r = world(c or role())
    return cast_of(cast_roles(planted(r, counts), r, (c or role(),)))


def test_the_lane_with_the_most_of_the_first_card_is_cast():
    assert run({hunt(P[0]): 2, hunt(P[1]): 5, hunt(P[2]): 3}) == ["scout_p2"]


def test_the_count_is_each_lanes_own_never_the_total_over_lanes_or_patterns():
    assert run({hunt(P[0]): 4, fish(P[0]): 4, hunt(P[1]): 5, fish(P[1]): 0, hunt(P[2]): 0, fish(P[2]): 9}) == ["scout_p2"]


def test_a_tie_goes_to_the_next_pattern_among_the_tied_only():
    # p1 and p2 tie on the first card; p3 has fewer of it but the most of the second, which only the tied are read for
    assert run({hunt(P[0]): 3, hunt(P[1]): 3, hunt(P[2]): 1, fish(P[0]): 1, fish(P[1]): 2, fish(P[2]): 9}) == ["scout_p2"]


def test_none_goes_to_the_next_pattern_over_everyone():
    assert run({fish(P[0]): 1, fish(P[2]): 4, fish(P[3]): 2}) == ["scout_p3"]


def test_a_tie_past_every_pattern_goes_to_the_earliest_declared_never_the_latest():
    assert run({hunt(P[1]): 2, hunt(P[3]): 2, fish(P[1]): 2, fish(P[3]): 2}) == ["scout_p2"]
    assert run({}) == ["scout_p1"]


def test_a_single_pattern_cast_with_a_tie_takes_the_earliest():
    assert run({hunt(P[2]): 2, hunt(P[3]): 2}, role(patterns=1)) == ["scout_p3"]


def test_a_group_with_the_highest_count_is_passed_over():
    r = world(role())
    s = planted(r, {hunt(G): 9, hunt(P[0]): 1})
    assert cast_of(cast_roles(s, r, (role(),))) == ["scout_p1"]
    with_group = Cast("scout", (CastPick(G, FeatureId("scout_grp"), (hunt(G), fish(G))), *role().picks))
    with pytest.raises(InvalidRulesError, match="not a declared ruled lane of a person"):
        validate_rules(replace(r, triggers=(TriggerDef(TriggerId("cast"), AfterTime(10), Outcome(casts=(with_group,))),)))


def test_only_people_who_are_present_are_eligible():
    r = world(role())
    s = planted(r, {hunt(P[0]): 9, hunt(P[1]): 5, hunt(P[2]): 1})
    assert cast_of(cast_roles(left(s, r, (Leave(P[0]),)), r, (role(),))) == ["scout_p2"]
    alone = world(role(), joins=False)
    s = joined(planted(alone, {hunt(P[0]): 9, hunt(P[2]): 1}), alone, (Join(P[2], TOWN),))
    assert cast_of(cast_roles(s, alone, (role(),))) == ["scout_p3"]


def test_nobody_eligible_casts_no_one():
    r = world(role(), joins=False)
    s = planted(r, {hunt(P[0]): 9})
    assert cast_roles(s, r, (role(),)) is s


def test_a_lane_holds_one_role_and_a_role_is_cast_once():
    first, second = role("scout"), role("guard")
    r = world(first, second)
    s = planted(r, {hunt(P[0]): 9, hunt(P[1]): 5})
    both = cast_roles(s, r, (first, second))
    assert cast_of(both, "scout") == ["scout_p1"] and cast_of(both, "guard") == ["guard_p2"]
    again = cast_roles(replace(planted(r, {hunt(P[2]): 99}), unlocked=both.unlocked), r, (first, second))
    assert again.unlocked == both.unlocked


def test_the_cast_does_not_move_when_counts_change_later():
    r = world(role())
    s = cast_roles(planted(r, {hunt(P[0]): 2, hunt(P[1]): 1}), r, (role(),))
    later = replace(s, cards=planted(r, {hunt(P[1]): 50}).cards)
    assert cast_roles(later, r, (role(),)) is later and cast_of(later) == ["scout_p1"]
    gone = left(later, r, (Leave(P[0]),))
    assert cast_of(gone) == ["scout_p1"]


def test_the_outcome_lands_it_at_its_instant_from_the_counts_then():
    r = world(role())
    s = planted(r, {hunt(P[1]): 4})
    assert cast_of(advance(s, r, 9)) == []
    assert cast_of(advance(s, r, 10)) == ["scout_p2"]


def test_a_cast_survives_a_rebase_and_a_late_one_casts_from_the_counts_then():
    r = world(role())
    s = advance(planted(r, {hunt(P[1]): 4}), r, 20)
    assert cast_of(s) == ["scout_p2"]
    assert cast_of(rebase(encode(s, r), r)) == ["scout_p2"]
    old = world(role(), joins=True)
    old = replace(old, triggers=old.triggers[:1])
    held = advance(planted(old, {hunt(P[3]): 7}), old, 20)
    assert cast_of(held) == []
    assert cast_of(rebase(encode(held, old), r)) == ["scout_p4"]


PLAIN_DIGEST = "ee2f4ee8cccde8383774b444f1ad7ab8b282819ad9d85395b890d2b01cde8c19"
"""The digest of world() with no cast, taken from the code before casts existed: rules with no cast keep it."""


def test_codec_and_digest():
    r = world(role())
    s = advance(planted(r, {hunt(P[1]): 4}), r, 20)
    assert decode(encode(s, r), r) == s
    assert rules_digest(world()) == PLAIN_DIGEST != rules_digest(r)


def test_the_features_are_known_to_the_rules():
    r = world(role())
    assert {f"scout_{x}" for x in P} <= features(r)


def test_validation():
    bad: dict[str, Rules] = {}
    r = world(role())
    cast_trigger = r.triggers[1]
    bad["has no lane"] = replace(r, triggers=(r.triggers[0], replace(cast_trigger, outcome=Outcome(casts=(Cast("scout", ()),)))))
    bad["not a declared ruled lane"] = replace(r, triggers=(r.triggers[0], replace(cast_trigger, outcome=Outcome(
        casts=(Cast("scout", (CastPick(LaneId("nowhere"), FeatureId("scout_x"), (hunt(P[0]),)),)),)))))
    bad["not on it"] = replace(r, triggers=(r.triggers[0], replace(cast_trigger, outcome=Outcome(
        casts=(Cast("scout", (CastPick(P[0], FeatureId("scout_p1"), (hunt(P[1]),)),)),)))))
    uneven = Cast("scout", (CastPick(P[0], FeatureId("scout_p1"), (hunt(P[0]),)), CastPick(P[1], FeatureId("scout_p2"), ())))
    bad["do not count the same patterns"] = replace(
        r, triggers=(r.triggers[0], replace(cast_trigger, outcome=Outcome(casts=(uneven,)))))
    bad["cast by two outcomes"] = replace(r, triggers=(*r.triggers, TriggerDef(TriggerId("again"), AfterTime(20), Outcome(casts=(role(),)))))
    bad["only a trigger's or an answer's"] = replace(r, cards=(replace(r.cards[0], cap=1, outcome=Outcome(casts=(role("x"),))), *r.cards[1:]))
    for message, rules in bad.items():
        with pytest.raises(InvalidRulesError, match=message):
            validate_rules(rules)
    offer = OfferDef(OfferId("o"), (AnswerDef(AnswerId("y"), Outcome(casts=(role("guard"),))), AnswerDef(AnswerId("n"))))
    validate_rules(replace(r, offers=(offer,)))
