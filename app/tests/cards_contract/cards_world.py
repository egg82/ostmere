"""Plain builders for the cards contract tests: ids, rules, a running mix, lookups, and a rich world holding every
kind of state a save can carry. No Hypothesis here, so the purity subprocess can import it cheaply. Built from the
engine's public types and entry points only (DESIGN.txt, part "CARDS")."""
from collections.abc import Sequence

from ashfall_app.engine import (
    BP, HANDS, QUANTITY_SCALE, AfterTime, Amount, AtLeast, AtMost, CapRaise, CardCount, CardDef, CardId, CardShare,
    CardView, ChipDef, ChipId, Explanation, Flow, FlowKind, InvalidVerbError, LaneDef, LaneId, LaneSpeed,
    LaneState, LedgerLine, LineKey, Mix, MixId, Modifier, ModifierKind, Order, Outcome, PacingCurve, QueueEntry,
    RateRef, Rules, Running, Save, SaveMix, Segment, SetOrders, SetQueue, SkillDef, SkillId, SkillLevel, SourceId,
    StandingDef, StoreDef, StoreId, StoreValue, SubMix, SwitchMix, TapCard, TriggerDef, TriggerId, Unlock, UnlockKind,
    Unlocked, WorkRef, ActionId, advance, decide, explain, new_save, segment, view, Line, Runner, Target, Verb,
)

Q = QUANTITY_SCALE
K = SkillId("k0")
RACK = LaneId("rack")


def ceil_div(a: int, b: int) -> int:
    return -((-a) // b)


def rules(stores: list[StoreDef], *, cards: list[CardDef] | None = None, standing: list[StandingDef] | None = None,
          lanes: list[LaneId] | None = None, chips: list[ChipDef] | None = None,
          triggers: list[TriggerDef] | None = None, opening: list[Unlock] | None = None,
          thresholds: tuple[int, ...] = (10**15,), max_firings: int = 1000,
          skills: tuple[SkillId, ...] = (K,)) -> Rules:
    return Rules(
        stores=tuple(stores), skills=tuple(SkillDef(k) for k in skills), standing=tuple(standing or []),
        curve=PacingCurve(thresholds), max_firings_per_instant=max_firings,
        lanes=tuple(LaneDef(lane) for lane in (lanes or [])), cards=tuple(cards or []),
        chips=tuple(chips or []), triggers=tuple(triggers or []),
        opening=None if opening is None else tuple(opening),
    )


def refill(*stores: StoreId) -> CardDef:
    """A card making each store that no test mixes or taps: a maker in play, so a card paused on one of them is PAUSED,
    not SPENT (engine DESIGN.txt, "SPENT")."""
    return CardDef(CardId("refill"), 100, makes=tuple(Flow(s, 1000) for s in stores))


def save_mix(save: Save, r: Rules, t: int, shares: dict[CardId, int], mix: str = "m0") -> Save:
    return decide(save, r, t, SaveMix(Mix(MixId(mix), tuple(CardShare(c, b) for c, b in shares.items()))))


def with_mix(save: Save, r: Rules, t: int, shares: dict[CardId, int], mix: str = "m0") -> Save:
    """Save a mix of direct shares under `mix` and switch to it at t."""
    return decide(save_mix(save, r, t, shares, mix), r, t, SwitchMix(MixId(mix)))


def tap(save: Save, r: Rules, t: int, card: CardId) -> Save:
    """The player's tap at t."""
    return decide(save, r, t, TapCard(card))


def val(save: Save, r: Rules, store: StoreId) -> int:
    return segment(save, r, store).start_value


def lane(save: Save, lane_id: LaneId) -> LaneState:
    found = [ls for ls in save.lanes if ls.lane == lane_id]
    assert len(found) == 1, (lane_id, save.lanes)
    return found[0]


def work(save: Save, card: CardId) -> Segment:
    """The card's work segment; an absent CardState is all zero (state.Save.cards)."""
    found = [c for c in save.cards if c.card == card]
    assert len(found) <= 1, save.cards
    return found[0].work if found else Segment(save.time, 0, 0)


def raised(save: Save, card: CardId) -> int:
    return next((c.raised for c in save.cards if c.card == card), 0)


def per_completion(r: Rules, card: CardId) -> int:
    return next(c.work_s for c in r.cards if c.id == card) * BP


def done(save: Save, r: Rules, card: CardId) -> int:
    """Completions read off the work segment, as DESIGN.txt defines them (work // (work_s * BP))."""
    return work(save, card).start_value // per_completion(r, card)


def keys(lines: Sequence[Line]) -> list[tuple[int, str]]:
    """(time, key) of each line, in the order given."""
    return [(ln.time, ln.key) for ln in lines]


def mul(target: Target, bp: int, source: str) -> Modifier:
    return Modifier(target, ModifierKind.MUL_BP, bp, SourceId(source))


def add(target: Target, bp: int, source: str) -> Modifier:
    return Modifier(target, ModifierKind.ADD_BP, bp, SourceId(source))


def make(save: Save, r: Rules, runner: Runner, store: StoreId) -> Explanation:
    return explain(save, r, RateRef(runner, FlowKind.MAKE, store))


def cost(save: Save, r: Rules, runner: Runner, store: StoreId) -> Explanation:
    return explain(save, r, RateRef(runner, FlowKind.COST, store))


def card_view(save: Save, r: Rules, card: CardId) -> CardView | None:
    found = [c for c in view(save, r).cards if c.card == card]
    assert len(found) <= 1
    return found[0] if found else None


def view_of(save: Save, r: Rules, card: CardId) -> CardView:
    """card_view for a card the test expects to be on the panel."""
    cv = card_view(save, r, card)
    assert cv is not None
    return cv


def running_mix(save: Save, r: Rules) -> MixId | None:
    """The mix the hands run now (DESIGN.txt, "Order mix"): an order's while it is latched, else save.active."""
    return view(save, r).running_mix


def ledger(save: Save, r: Rules, store: StoreId) -> LedgerLine:
    return next(ln for ln in view(save, r).ledger if ln.store == store)


def try_decide(s: Save, r: Rules, t: int, verb: Verb) -> Save:
    """decide(), except that a verb the engine refuses leaves the save advanced to t."""
    try:
        return decide(s, r, t, verb)
    except InvalidVerbError:
        return advance(s, r, t)


# ---- a rich world: every kind of state a save can hold, for the codec, purity and reading tests -----------------

X, Y, Z = StoreId("x"), StoreId("y"), StoreId("z")
KSTORE = StoreId("k0")
"""A store sharing its id string with skill k0: ids are unique per kind, so a codec must keep the kind."""
FIRE = ActionId("fire")
G, H, P, R2, Q2, RZ = CardId("g"), CardId("h"), CardId("p"), CardId("r"), CardId("q"), CardId("rz")
COLD = ChipId("cold")
T0 = TriggerId("t0")


def rich_rules() -> Rules:
    return rules(
        [StoreDef(X, 50 * Q, 10 * Q), StoreDef(Y, 50 * Q, 2 * Q), StoreDef(Z, 50 * Q, 0), StoreDef(KSTORE, 5 * Q, Q)],
        standing=[StandingDef(FIRE, costs=(Flow(Y, 300),))],
        cards=[
            CardDef(G, 600, skill=K, xp_per_hour=2000, makes=(Flow(X, 3000),), costs=(Flow(Y, 500),),
                    lines=(LineKey("g.tap"),)),
            CardDef(H, 900, skill=K, xp_per_hour=1000, inputs=(Amount(X, Q),), outcome=Outcome(stores=(Amount(Z, Q),))),
            CardDef(P, 400, inputs=(Amount(X, Q),), cap=3,
                    lines=(LineKey("p.1"), LineKey("p.2"), LineKey("p.3")),
                    outcome=Outcome(stores=(Amount(Z, Q),), unlocks=(Unlock(UnlockKind.CARD, Q2),),
                                    modifiers=(mul(WorkRef(R2), 15_000, "p.out"),), starts=(R2,),
                                    lines=(LineKey("p.done"),)),
                    finished=Outcome(lines=(LineKey("p.fin"),))),
            CardDef(R2, 1300, lane=RACK, outcome=Outcome(stores=(Amount(Y, Q),)), lines=(LineKey("r.done"),)),
            CardDef(Q2, 400, cap=1, requires=(AtLeast(SkillLevel(K), 2, 2),)),
            CardDef(RZ, 500, lane=RACK, cap=2, outcome=Outcome(raises=(CapRaise(P, 1),))),
        ],
        lanes=[RACK],
        chips=[ChipDef(COLD, AtLeast(StoreValue(Z), 2 * Q, Q), (mul(LaneSpeed(HANDS), 5000, "cold"),),
                       LineKey("cold.on"), LineKey("cold.off"))],
        triggers=[TriggerDef(T0, AtLeast(CardCount(P), 1, 1),
                             Outcome(unlocks=(Unlock(UnlockKind.CHIP, COLD),), lines=(LineKey("t0.fired"),)))],
        opening=[Unlock(UnlockKind.STORE, X), Unlock(UnlockKind.STORE, Y), Unlock(UnlockKind.STORE, Z),
                 Unlock(UnlockKind.STORE, KSTORE), Unlock(UnlockKind.SKILL, K), Unlock(UnlockKind.ACTION, FIRE),
                 Unlock(UnlockKind.CARD, G), Unlock(UnlockKind.CARD, H), Unlock(UnlockKind.CARD, P),
                 Unlock(UnlockKind.CARD, R2), Unlock(UnlockKind.CARD, RZ)],
        thresholds=(Q // 2, 2 * Q, 6 * Q),
        max_firings=50,
    )


def rich_orders() -> SetOrders:
    """Orders using every condition and subject kind and both order verbs."""
    return SetOrders((
        Order(AtLeast(StoreValue(KSTORE), 4 * Q, 3 * Q), SwitchMix(MixId("inner"))),
        Order(AtLeast(SkillLevel(K), 4, 4), TapCard(P)),
        Order(AtMost(CardCount(R2), 0, 0), TapCard(R2)),
        Order(AtLeast(Unlocked(Unlock(UnlockKind.CARD, Q2)), 1, 1), SwitchMix(MixId("inner"))),
        Order(AtMost(Running(R2), 0, 0), TapCard(R2)),
        Order(AfterTime(10**8), SwitchMix(MixId("outer"))),
    ))


def rich_saves() -> list[Save]:
    """A run through every kind of state: a nested mix, orders and queue of both verbs, a capped card part
    done, a rack tap mid-bar, a failed tap, completions, unlocks grown, a chip, a fired trigger, a raised cap,
    outcome modifiers."""
    r = rich_rules()
    s = new_save(r, (add(RateRef(G, FlowKind.MAKE, X), 1500, "tool"), mul(LaneSpeed(RACK), 12_000, "rack")))
    s = decide(s, r, 0, SaveMix(Mix(MixId("inner"), (CardShare(G, 6000), CardShare(H, 4000)))))
    s = decide(s, r, 0, SaveMix(Mix(MixId("outer"), (SubMix(MixId("inner"), 5000), CardShare(P, 2000)))))
    s = decide(s, r, 0, SwitchMix(MixId("outer")))
    s = decide(s, r, 10, rich_orders())
    s = decide(s, r, 10, SetQueue((QueueEntry(SwitchMix(MixId("inner")), AtLeast(StoreValue(Z), 3 * Q, 3 * Q)),
                                   QueueEntry(TapCard(RZ), AfterTime(10**8)))))
    out = [s]
    for t in (20, 300, 1000, 1500, 2500, 3000, 4000, 5000, 9000, 20_000):
        if t in (20, 1000, 3000, 5000):
            s = try_decide(s, r, t, TapCard(P))
        elif t == 2500:
            s = try_decide(s, r, t, TapCard(Q2))  # locked or unready: refused or a failed tap
        else:
            s = advance(s, r, t)
        out.append(s)
    return out
