"""Groups as data (engine design/groups.txt, "GROUPS (pooled lanes)"): the fields, their codec and digest absence at defaults,
and validation. Nothing runs differently yet: the running is the next slice's. Each refusal has the good case
(`world`) beside it."""
from dataclasses import replace

import pytest

from ashfall_app.engine import (
    QUANTITY_SCALE as Q, AfterTime, CardDef, CardId, Flow, InvalidRulesError, Join, LaneDef, LaneId,
    LaneState, Leave, Mark, MixId, Outcome, PacingCurve, RuleInstall, Rules, SkillDef, SkillId, StoreDef, StoreId, TriggerDef,
    TriggerId, decode, encode, new_save, rules_digest, validate_rules,
)
from ashfall_app.engine.codec import canonical, from_json, to_json

X = StoreId("x")
G, P1, P2 = LaneId("g"), LaneId("p1"), LaneId("p2")
GWORK, GCAP, A1, A2 = CardId("gwork"), CardId("gcap"), CardId("a1"), CardId("a2")
TOWN = MixId("town:main")
GO = TriggerId("go")


def world(outcome: Outcome | None = None, lanes: tuple[LaneDef, ...] | None = None,
          extra: tuple[CardDef, ...] = ()) -> Rules:
    """A pooled lane g with one uncapped card, p1 in group g, p2 with none, each person one card. `outcome` is a
    trigger's; the default hands p1 to the group and p2 to their own split."""
    if outcome is None:
        outcome = Outcome(joins=(Join(P1, TOWN, GWORK, own_split=False), Join(P2, TOWN, A2)))
    cards = (CardDef(GWORK, 100, lane=G, makes=(Flow(X, Q),)), CardDef(A1, 100, lane=P1, makes=(Flow(X, Q),)),
             CardDef(A2, 100, lane=P2, makes=(Flow(X, Q),)), *extra)
    r = Rules(stores=(StoreDef(X, 10**6 * Q, 0),), skills=(SkillDef(SkillId("s")),), standing=(),
              curve=PacingCurve((10**9 * Q,)),
              lanes=lanes or (LaneDef(G, True, pooled=True), LaneDef(P1, True, group=G), LaneDef(P2, True)),
              cards=cards, triggers=(TriggerDef(GO, AfterTime(10), outcome),))
    validate_rules(r)
    return r


def test_fields_at_their_defaults_stay_out_of_the_encoding():
    """The plain world's rules and save carry none of the new fields, so their text, and so their digest, is what they
    were before the fields existed."""
    plain = world(Outcome(joins=(Join(P1, TOWN, A1), Join(P2, TOWN, A2))),
                  lanes=(LaneDef(G, True), LaneDef(P1, True), LaneDef(P2, True)))
    text = encode(new_save(plain), plain)
    shown = text + canonical(to_json(plain))
    for name in ("pooled", "group", "own_split", "marks"):
        assert f'"{name}"' not in shown


def test_each_field_set_is_written_read_back_and_moves_the_digest():
    r = world()
    assert '"pooled":true' in canonical(to_json(r)) and '"own_split":false' in canonical(to_json(r))
    marked = Outcome(marks=(Mark(P1, False, GWORK),))
    assert from_json(to_json(marked)) == marked
    assert from_json(to_json(r.triggers[0].outcome)) == r.triggers[0].outcome
    save = replace(new_save(r), lanes=(LaneState(P1, own_split=False), LaneState(P2)))
    assert decode(encode(save, r), r) == save
    assert '"own_split":false' in encode(save, r)
    unpooled = world(Outcome(), lanes=(LaneDef(G, True), LaneDef(P1, True, group=None), LaneDef(P2, True)))
    assert rules_digest(unpooled) != rules_digest(world(Outcome()))


def test_the_good_world_validates():
    world(Outcome(marks=(Mark(P1, True, A1), Mark(P1, False))))


BAD_LANES = [
    ("a pooled lane that is not ruled", "a pooled lane is a ruled lane",
     (LaneDef(G, False, pooled=True), LaneDef(P1, True), LaneDef(P2, True))),
    ("a pooled lane with a group", "a pooled lane has no group",
     (LaneDef(G, True, pooled=True, group=G), LaneDef(P1, True, group=G), LaneDef(P2, True))),
    ("a group on an unruled lane", "only a ruled lane has a group",
     (LaneDef(G, True, pooled=True), LaneDef(P1, False, group=G), LaneDef(P2, True))),
    ("a group naming a lane that is not pooled", "is not a pooled lane",
     (LaneDef(G, True, pooled=True), LaneDef(P1, True, group=P2), LaneDef(P2, True))),
    ("a group naming nothing", "is not a pooled lane",
     (LaneDef(G, True, pooled=True), LaneDef(P1, True, group=LaneId("nowhere")), LaneDef(P2, True))),
]


@pytest.mark.parametrize(("lanes", "match"), [(lanes, match) for _, match, lanes in BAD_LANES],
                         ids=[name for name, _, _ in BAD_LANES])
def test_a_bad_lane_is_refused(lanes: tuple[LaneDef, ...], match: str):
    with pytest.raises(InvalidRulesError, match=match):
        world(lanes=lanes)


BAD_CARDS = [
    ("a capped card on a pooled lane", "no cap", CardDef(GCAP, 100, lane=G, cap=2)),
    ("an XP card on a pooled lane", "trains no skill",
     CardDef(GCAP, 100, lane=G, skill=SkillId("s"), xp_per_hour=Q)),
]


@pytest.mark.parametrize(("card", "match"), [(card, match) for _, match, card in BAD_CARDS],
                         ids=[name for name, _, _ in BAD_CARDS])
def test_a_pooled_lane_holds_uncapped_cards_with_no_xp(card: CardDef, match: str):
    with pytest.raises(InvalidRulesError, match=match):
        world(extra=(card,))


BAD_OUTCOMES = [
    ("a start of a pooled card", "a card on a pooled lane", Outcome(starts=(GWORK,))),
    ("an install of a pooled card", "a card on a pooled lane", Outcome(orders=(RuleInstall(GWORK),))),
    ("a join of a pooled lane", "a join is not valid", Outcome(joins=(Join(G, TOWN),))),
    ("a leave of a pooled lane", "never a person", Outcome(leaves=(Leave(G),))),
    ("an unmarked join with no group", "a join is not valid", Outcome(joins=(Join(P2, TOWN, own_split=False),))),
    ("an unmarked join with a card off the group", "a join is not valid",
     Outcome(joins=(Join(P1, TOWN, A1, own_split=False),))),
    ("a mark of an unknown lane", "not a declared person's lane", Outcome(marks=(Mark(LaneId("nowhere"), True),))),
    ("a mark of a pooled lane", "not a declared person's lane", Outcome(marks=(Mark(G, True),))),
    ("an unmarking with no group", "has no group", Outcome(marks=(Mark(P2, False),))),
    ("a mark card off the person's lane", "not an uncapped card", Outcome(marks=(Mark(P1, True, A2),))),
]


@pytest.mark.parametrize(("outcome", "match"), [(o, m) for _, m, o in BAD_OUTCOMES], ids=[n for n, _, _ in BAD_OUTCOMES])
def test_a_bad_outcome_is_refused(outcome: Outcome, match: str):
    with pytest.raises(InvalidRulesError, match=match):
        world(outcome)


def test_a_mark_outside_a_trigger_or_an_answer_is_refused():
    marked = Outcome(marks=(Mark(P1, True),))
    with pytest.raises(InvalidRulesError, match="only a trigger's or an answer's outcome marks"):
        world(extra=(CardDef(CardId("h"), 10, cap=1, outcome=marked),))
    world(marked)
