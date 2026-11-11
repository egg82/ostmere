"""Hypothesis strategies for day two's contract properties: town worlds (town_world.town) whose answers, a second
offer and an installing trigger are drawn, and scenarios playing every day-two verb on them: answers good and bad,
taps of every lane (a ruled one refused), orders tapping any card or answering any pair, queues tapping the hands or
the rack or answering. No player SwitchMix or SaveMix after the opening mix, so invariant 57 holds of every save
played (DESIGN.txt, invariant 57: "decisions other than a player's SwitchMix and SaveMix")."""
from dataclasses import dataclass

from hypothesis import strategies as st
from hypothesis.strategies import DrawFn

from ashfall_app.engine import (
    AfterTime, AnswerId, AnswerOffer, AtLeast, AtMost, CardCount, Condition, OfferId, Order, OrderVerb,
    Outcome, QueueEntry, RuleInstall, Rules, Save, SetOrders, SetQueue, StoreValue, TapCard, TriggerDef, TriggerId,
    Unlock, UnlockKind, Unlocked, Verb, InvalidVerbError, LineKey, advance, decide, new_save,
)
from cards_world import Q
from town_world import (
    ASK, H, H2, HC, LATER, M, NO, NO_OUT, OTHER, R, SECOND, SOONER, T1, T2, TC, X, YES, YES_OUT, mixing, town,
)

GO = TriggerId("go")
TOWN_CARDS = (T1, T2, TC)
OUTCOMES = (
    YES_OUT, NO_OUT, Outcome(), Outcome(starts=(T2,)), Outcome(orders=(RuleInstall(T1), RuleInstall(T2, first=True))),
    Outcome(unlocks=(Unlock(UnlockKind.CARD, TC),), orders=(RuleInstall(TC, first=True),), queues=(HC,)),
    Outcome(orders=(RuleInstall(T1),), queues=(HC,), lines=(LineKey("both.said"),)),
)
PAIRS = (AnswerOffer(ASK, YES), AnswerOffer(ASK, NO), AnswerOffer(OTHER, LATER), AnswerOffer(OTHER, SOONER))
BAD_PAIRS = (AnswerOffer(ASK, LATER), AnswerOffer(OfferId("nope"), YES), AnswerOffer(ASK, AnswerId("maybe")))


@dataclass(frozen=True)
class TownScenario:
    rules: Rules
    steps: tuple[tuple[int, Verb], ...]
    """(seconds after the previous step, verb), applied with decide(); a refused verb only advances."""
    offsets: tuple[int, ...]


@st.composite
def town_rules_st(draw: DrawFn) -> Rules:
    yes, no = draw(st.sampled_from(OUTCOMES)), draw(st.sampled_from(OUTCOMES))
    show_at = draw(st.sampled_from([0, 50, 333, None]))
    other = SECOND if draw(st.booleans()) else None
    triggers: tuple[TriggerDef, ...] = ()
    if draw(st.booleans()):
        installs = tuple(RuleInstall(c, draw(st.booleans()))
                         for c in draw(st.lists(st.sampled_from(TOWN_CARDS), min_size=1, max_size=2, unique=True)))
        triggers += (TriggerDef(GO, AfterTime(draw(st.integers(0, 900))), Outcome(orders=installs)),)
    if other is not None and draw(st.booleans()):
        triggers += (TriggerDef(TriggerId("show_other"), AfterTime(draw(st.integers(0, 900))),
                                Outcome(unlocks=(Unlock(UnlockKind.OFFER, OTHER),))),)
    return town(gated=draw(st.booleans()), yes=yes, no=no, show_at=show_at, triggers=triggers,
                offers=() if other is None else (other,),
                max_firings=draw(st.sampled_from([1000, 1000, 3])))


@st.composite
def condition_st(draw: DrawFn) -> Condition:
    kind = draw(st.sampled_from(["after", "store", "count", "offer"]))
    if kind == "after":
        return AfterTime(draw(st.sampled_from([0, 0, 40, 400, 10**6])))
    if kind == "store":
        v = Q * draw(st.integers(0, 5))
        return AtLeast(StoreValue(X), v, v) if draw(st.booleans()) else AtMost(StoreValue(X), v, v + Q)
    if kind == "count":
        c = draw(st.sampled_from([H, HC, T1, TC, R]))
        n = draw(st.integers(0, 3))
        return AtLeast(CardCount(c), n, n) if draw(st.booleans()) else AtMost(CardCount(c), n, n)
    return AtLeast(Unlocked(Unlock(UnlockKind.OFFER, ASK)), 1, 1)


@st.composite
def order_verb_st(draw: DrawFn, r: Rules, queue: bool) -> OrderVerb:
    pairs = [p for p in PAIRS if any(o.id == p.offer for o in r.offers)]
    taps = [H, H2, HC, M, R] if queue else [H, H2, HC, M, R, T1, T2, TC]
    if draw(st.integers(0, 2)) == 0:
        return draw(st.sampled_from(pairs))
    card = draw(st.sampled_from(taps))
    return TapCard(card)


def no_player_always_rule(o: Order) -> bool:
    """The player's orders never hold a ruled lane's always rule, so every such rule in a save was installed."""
    return not (o.when == AfterTime(0) and isinstance(o.then, TapCard) and o.then.card in TOWN_CARDS)


@st.composite
def step_verb_st(draw: DrawFn, r: Rules) -> Verb:
    kind = draw(st.sampled_from(["answer", "answer", "bad", "tap", "tap", "orders", "queue"]))
    if kind == "answer":
        return draw(st.sampled_from(PAIRS))
    if kind == "bad":
        return draw(st.sampled_from(BAD_PAIRS))
    if kind == "tap":
        return TapCard(draw(st.sampled_from([H, H2, HC, R, T1, TC])))
    n = draw(st.integers(0, 3))
    if kind == "orders":
        orders = [Order(draw(condition_st()), draw(order_verb_st(r, False))) for _ in range(n)]
        return SetOrders(tuple(o for o in orders if no_player_always_rule(o)))
    return SetQueue(tuple(QueueEntry(draw(order_verb_st(r, True)), draw(condition_st())) for _ in range(n)))


@st.composite
def town_scenario_st(draw: DrawFn) -> TownScenario:
    r = draw(town_rules_st())
    steps: list[tuple[int, Verb]] = [(0, v) for v in mixing()] if draw(st.booleans()) else []
    for _ in range(draw(st.integers(1, 5))):
        steps.append((draw(st.one_of(st.integers(0, 3), st.integers(0, 600))), draw(step_verb_st(r))))
    offsets = tuple(draw(st.lists(st.integers(0, 3000), min_size=1, max_size=3)))
    return TownScenario(r, tuple(steps), offsets)


def try_decide(s: Save, r: Rules, t: int, verb: Verb) -> Save:
    """decide(), except that a verb the engine refuses leaves the save advanced to t."""
    try:
        return decide(s, r, t, verb)
    except InvalidVerbError:
        return advance(s, r, t)


def play(sc: TownScenario, rules: Rules | None = None) -> list[Save]:
    """The save after each step (from new_save), under `rules` (default the scenario's)."""
    r = sc.rules if rules is None else rules
    s = new_save(r)
    out = [s]
    for dt, verb in sc.steps:
        s = try_decide(s, r, s.time + dt, verb)
        out.append(s)
    return out

