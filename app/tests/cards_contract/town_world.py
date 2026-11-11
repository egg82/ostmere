"""Plain builders for day two's contract tests (engine DESIGN.txt, part "TOWNSFOLK, INSTALLED RULES AND OFFERS"): a
town lane run by rules beside the hands and a rack, one offer with two answers, and the trigger that shows it. Built
from the engine's public types and entry points only; no Hypothesis here.

Every card takes 100 s a completion at full speed, so a tap started at t lands at t + 100."""
from dataclasses import replace

from ashfall_app.engine import (
    BP, AfterTime, CardShare, Mix, MixId, SaveMix, SwitchMix, AnswerDef, AnswerId, AnswerOffer, CardDef, CardId, Flow, LaneDef, LaneId, LineKey, OfferDef,
    OfferId, Order, Outcome, Rules, RuleInstall, Save, StoreDef, StoreId, TapCard, TriggerDef, TriggerId, Unlock,
    UnlockKind, Verb, decide, new_save, validate_rules,
)
from cards_world import K, Q, RACK, lane, rules as base_rules

X = StoreId("x")
TOWN = LaneId("town")
H, H2, HC, M = CardId("h"), CardId("h2"), CardId("hc"), CardId("m")
"""The hands' cards: h and h2 uncapped, hc capped at 3 (a queued one-off needs a cap), m uncapped and making one x
per 100 s of running (for a mix that moves a store rule)."""
MIX = MixId("mix")
T1, T2, TC = CardId("t1"), CardId("t2"), CardId("tc")
"""The town's cards: t1 and t2 uncapped (tasks), tc capped at 1 (a one-off)."""
R = CardId("r")
"""The rack's card: a declared lane that is not ruled."""
ASK = OfferId("ask")
YES, NO = AnswerId("yes"), AnswerId("no")
SHOW = TriggerId("show")
ALWAYS = AfterTime(0)
NEVER = AfterTime(10**9)
SHOW_AT = 50

YES_OUT = Outcome(unlocks=(Unlock(UnlockKind.CARD, TC),), lines=(LineKey("yes.said"),),
                  orders=(RuleInstall(TC, first=True),))
"""The town's one-off: unlock tc and install its always rule at the top."""
OTHER = OfferId("other")
LATER, SOONER = AnswerId("later"), AnswerId("sooner")
SECOND = OfferDef(OTHER, (AnswerDef(LATER, Outcome()), AnswerDef(SOONER, Outcome())))
"""A second offer, shown only by a test's own trigger, its answers doing nothing."""
NO_OUT = Outcome(lines=(LineKey("no.said"),), queues=(HC,))
"""The hands' one-off: hc queued at the front as a When ready entry."""


def always(card: CardId) -> Order:
    """A lane's always rule (DESIGN.txt, "Ruled lane"; api CONTRACT.txt, "A lane run by rules")."""
    return Order(ALWAYS, TapCard(card))


def town(*, ruled: bool = True, gated: bool = True, yes: Outcome = YES_OUT, no: Outcome = NO_OUT,
         show_at: int | None = SHOW_AT, triggers: tuple[TriggerDef, ...] = (), offers: tuple[OfferDef, ...] = (),
         cards: tuple[CardDef, ...] = (), max_firings: int = 1000) -> Rules:
    """The town world. gated: an opening holding every store, the skill and every card but tc, so the offer shows only
    when `show` fires at show_at (None: no such trigger); ungated (opening None) shows every offer from time 0.
    `triggers`, `offers` and `cards` are added after the world's own."""
    own = (CardDef(H, 100), CardDef(H2, 100), CardDef(HC, 100, cap=3), CardDef(M, 100, makes=(Flow(X, Q // 100),)),
           CardDef(T1, 100, lane=TOWN), CardDef(T2, 100, lane=TOWN), CardDef(TC, 100, lane=TOWN, cap=1),
           CardDef(R, 100, lane=RACK))
    shows = () if show_at is None else (TriggerDef(SHOW, AfterTime(show_at), Outcome(
        unlocks=(Unlock(UnlockKind.OFFER, ASK),), lines=(LineKey("ask.shown"),))),)
    all_cards = own + cards
    opening = None
    if gated:
        opening = [Unlock(UnlockKind.STORE, X), Unlock(UnlockKind.SKILL, K)]
        opening += [Unlock(UnlockKind.CARD, c.id) for c in all_cards if c.id != TC]
    r = base_rules([StoreDef(X, 100 * Q, 0)], cards=list(all_cards), triggers=list(shows + triggers),
                   opening=opening, max_firings=max_firings)
    r = replace(r, lanes=(LaneDef(TOWN, ruled=ruled), LaneDef(RACK)),
                offers=(OfferDef(ASK, (AnswerDef(YES, yes), AnswerDef(NO, no))),) + offers)
    validate_rules(r)
    return r


def unruled(r: Rules) -> Rules:
    """The same rules with every lane's `ruled` False (invariant 58's comparison)."""
    return replace(r, lanes=tuple(replace(d, ruled=False) for d in r.lanes))


def answered(s: Save, offer: OfferId) -> bool:
    return Unlock(UnlockKind.ANSWERED, offer) in s.unlocked


def given(s: Save, answer: AnswerId) -> bool:
    return Unlock(UnlockKind.ANSWER, answer) in s.unlocked


def shown(s: Save, offer: OfferId) -> bool:
    return Unlock(UnlockKind.OFFER, offer) in s.unlocked


def answer(s: Save, r: Rules, t: int, a: AnswerId = YES, offer: OfferId = ASK) -> Save:
    """The player's AnswerOffer at t."""
    return decide(s, r, t, AnswerOffer(offer, a))


def running(s: Save, lane_id: LaneId) -> CardId | None:
    return lane(s, lane_id).card


def mixing() -> tuple[Verb, Verb]:
    """Save the mix {m: 100%} and switch to it: x then rises by one Q every 100 s."""
    return SaveMix(Mix(MIX, (CardShare(M, BP),))), SwitchMix(MIX)


def started(r: Rules, *verbs: Verb) -> Save:
    """A new save with each verb decided at time 0."""
    s = new_save(r)
    for v in verbs:
        s = decide(s, r, 0, v)
    return s

