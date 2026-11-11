"""Fixture rules for the offer-kind contract tests (engine DESIGN.txt, "OFFER KINDS").
Built from the engine's public types only, on top of town_world's world.

Four kinded offers and one unkinded: one, two and three carry the arrival kind with the roles welcome and turn_away,
two declaring its answers in the opposite order to one and three (a position match answers the wrong one); stranger
carries a second kind with the same role names; ask (town_world's own offer, yes and no) carries none. Each answer's
outcome writes its own line key, so which answer landed is readable from the step's lines as well as the unlock set."""
from ashfall_app.engine import (
    AnswerDef, AnswerId, AnswerKind, RoleId, LineKey, OfferDef, OfferId, KindId, Outcome, Rules, TriggerDef,
    TriggerId, Unlock, UnlockKind, AfterTime,
)
from town_world import town

ARRIVAL, STRANGER_KIND = KindId("arrival"), KindId("stranger")
WELCOME, TURN_AWAY = RoleId("welcome"), RoleId("turn_away")
ONE, TWO, THREE, STRANGER = OfferId("one"), OfferId("two"), OfferId("three"), OfferId("stranger")
ONE_W, ONE_T = AnswerId("one_w"), AnswerId("one_t")
TWO_W, TWO_T = AnswerId("two_w"), AnswerId("two_t")
THREE_W, THREE_T = AnswerId("three_w"), AnswerId("three_t")
STR_W, STR_T = AnswerId("str_w"), AnswerId("str_t")


def answer_def(a: AnswerId, role: RoleId | None) -> AnswerDef:
    return AnswerDef(a, Outcome(lines=(LineKey(f"{a}.said"),)), role=role)


def kinded(o: OfferId, kind: KindId | None, welcome: AnswerId, turn_away: AnswerId, swapped: bool = False) -> OfferDef:
    pair = (answer_def(welcome, WELCOME), answer_def(turn_away, TURN_AWAY))
    return OfferDef(o, pair[::-1] if swapped else pair, kind=kind)


OFFERS = (
    kinded(ONE, ARRIVAL, ONE_W, ONE_T),
    kinded(TWO, ARRIVAL, TWO_W, TWO_T, swapped=True),
    kinded(THREE, ARRIVAL, THREE_W, THREE_T),
    kinded(STRANGER, STRANGER_KIND, STR_W, STR_T),
)


def shows(**at: int) -> tuple[TriggerDef, ...]:
    """A trigger per offer id keyword, each unlocking that offer's OFFER at the given second (ask included)."""
    return tuple(TriggerDef(TriggerId(f"show_{o}"), AfterTime(t), Outcome(unlocks=(Unlock(UnlockKind.OFFER, OfferId(o)),)))
                 for o, t in at.items())


def world(**show_at: int) -> Rules:
    """The town world with the five offers; nothing is shown except as show_at says (seconds, by offer id)."""
    return town(show_at=None, offers=OFFERS, triggers=shows(**show_at))


def rule(kind: KindId = ARRIVAL, role: RoleId = WELCOME) -> AnswerKind:
    return AnswerKind(kind, role)

