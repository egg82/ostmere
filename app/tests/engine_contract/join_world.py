"""A world with a ruled lane for the rebase tests of the town's mix (engine DESIGN.txt, "THE TOWN'S MIX", "Rebase"): the
release before the join's rules, and the release that adds a trigger whose outcome joins the lane."""
from dataclasses import replace

from ashfall_app.engine import (
    AfterTime, AtLeast, CardCount, CardDef, CardId, Flow, Join, LaneDef, LaneId, Leave, MixId, Order, Outcome, PacingCurve,
    Rules, Save, SetOrders, SkillDef, SkillId, StoreDef, StoreId, TapCard, TriggerDef, TriggerId, advance,
    decide, encode, new_save, rebase, validate_rules,
)
from contract_gen import Q

X = StoreId("x")
PERSON = LaneId("p1")
A, B = CardId("a"), CardId("b")
TOWN = MixId("town:main")
ALWAYS = AfterTime(0)
RULE = Order(AtLeast(CardCount(A), 15, 15), TapCard(B))
"""The first person's rule that is not an always rule: it must survive the join."""
JOIN_TRIGGER = TriggerId("join")


def old_rules() -> Rules:
    """One ruled lane, its card a uncapped and making x, b uncapped; no join anywhere."""
    return Rules(stores=(StoreDef(X, 10**6 * Q, 0),), skills=(SkillDef(SkillId("k")),), standing=(),
                 curve=PacingCurve((10**9 * Q,)), lanes=(LaneDef(PERSON, True),),
                 cards=(CardDef(A, 100, lane=PERSON, makes=(Flow(X, Q),)), CardDef(B, 50, lane=PERSON)))


def new_rules(at: int = 100) -> Rules:
    """old_rules plus a trigger at `at` seconds whose outcome joins the lane."""
    r = replace(old_rules(), triggers=(TriggerDef(JOIN_TRIGGER, AfterTime(at), Outcome(joins=(Join(PERSON, TOWN),))),))
    validate_rules(r)
    return r


def saved_before_the_join(t: int = 500) -> Save:
    """A save under old_rules at t: the person's always rule and the rule that is not, a tap of a in progress."""
    r = old_rules()
    s = decide(new_save(r), r, 0, SetOrders((RULE, Order(ALWAYS, TapCard(A)))))
    return advance(s, r, t)


def joined_save() -> Save:
    """The save before the join, rebased under the rules that join."""
    return rebase(encode(saved_before_the_join(), old_rules()), new_rules())


def left_save() -> Save:
    """The joined save run on under rules whose later trigger has the person leave (engine DESIGN.txt, "LEAVES")."""
    r = new_rules()
    gone = replace(r, triggers=(*r.triggers, TriggerDef(TriggerId("leave"), AfterTime(600), Outcome(leaves=(Leave(PERSON),)))))
    validate_rules(gone)
    return advance(rebase(encode(joined_save(), r), gone), gone, 700)
