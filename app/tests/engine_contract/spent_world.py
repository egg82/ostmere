"""Fixture rules and readers for the SPENT contract tests (engine DESIGN.txt, "SPENT", invariants 133-141). Built from the
engine's public names and the part's documented additions only; the additions are read through the helpers below, so
the one place that names a field the engine does not have yet is this file.

Every card runs 1 whole item a second at a full share on its one line, so at a share of s basis points a line moves a
store exactly 360 * s units a second (QUANTITY_SCALE 3_600_000 over BP 10_000): every expectation below is an exact
integer. EAT is the card that costs a pool (and makes y); R1, R2, R3 are plain makers of z, w, v. A pool is a store
nothing makes: p, p2, p3 and u are the pools the tests drain."""
from collections.abc import Callable, Sequence
from dataclasses import dataclass, replace

import pytest

from ashfall_app.engine import (
    BP, QUANTITY_SCALE as Q, ActionId, AfterTime, Amount, CardDef, CardId, CardShare, Explanation, Flow, FlowKind, Join,
    LaneDef, LaneId, Mix, MixId, Outcome, PacingCurve, RateRef, Rules, RunKind, Save, SaveMix, SkillDef, SkillId,
    StandingDef, StoreDef, StoreId, SwitchMix, TapCard, TriggerDef, TriggerId, Unlock, UnlockKind, advance, decide,
    explain, explain_work, new_save, per_hour, segment, validate_rules, view,
)
from ashfall_app.engine.viewparts import CardView

P, P2, P3, U, Y, Z, W, V = (StoreId(n) for n in ("p", "p2", "p3", "u", "y", "z", "w", "v"))
EAT, EAT2, R1, R2, R3, MK, MK2 = (CardId(n) for n in ("eat", "eat2", "r1", "r2", "r3", "mk", "mk2"))
LA, LB = LaneId("la"), LaneId("lb")
EATA, RA, RB = CardId("eata"), CardId("ra"), CardId("rb")
MIX, TM = MixId("m"), MixId("town:main")
BIG = 10**6 * Q
PS = per_hour(3600)
"""One whole item a second."""
UNITS_PER_BP = Q // BP
"""A full-speed 1-item-a-second line moves 360 units a second per basis point of share."""
STORES = (P, P2, P3, U, Y, Z, W, V)
PLAIN_MAKES = {R1: Z, R2: W, R3: V}


def kills(*mutants: int) -> Callable[[Callable[..., None]], Callable[..., None]]:
    """Marks the test as one that must go red for these rows of MUTANTS_spent.txt."""
    return pytest.mark.kills(*mutants)


def spent_kind() -> RunKind:
    """RunKind.SPENT, looked up by its documented value so a module that imports before item 1 still collects."""
    return RunKind("spent")


def gained_of(reading: object) -> tuple[tuple[CardId, int], ...]:
    """The (card, share_bp) pairs of an Explanation's or a CardView's `gained`, in the order given."""
    entries: tuple[object, ...] = getattr(reading, "gained") 
    return tuple((getattr(g, "card"), getattr(g, "share_bp")) for g in entries)


def spent_store_of(cv: CardView) -> StoreId | None:
    return getattr(cv, "spent_store") 


def eater(card: CardId = EAT, pool: StoreId = P, makes: StoreId = Y, **kw: object) -> CardDef:
    """A card costing `pool` at one item a second: it pauses when the pool is dry."""
    return replace(CardDef(card, 10, costs=(Flow(pool, PS),), makes=(Flow(makes, PS),)), **kw)


def maker(card: CardId, store: StoreId, rate: int = PS, **kw: object) -> CardDef:
    """A plain card making `store`: R1..R3 by default make z, w, v."""
    return replace(CardDef(card, 10, makes=(Flow(store, rate),)), **kw)


def plain(*cards: CardId) -> tuple[CardDef, ...]:
    return tuple(maker(c, PLAIN_MAKES[c]) for c in cards)


def world(*cards: CardDef, initial: dict[StoreId, int] | None = None, standing: tuple[StandingDef, ...] = (),
          triggers: tuple[TriggerDef, ...] = (), opening: tuple[Unlock, ...] | None = None,
          lanes: tuple[LaneDef, ...] = ()) -> Rules:
    """Rules over the eight stores (all at 0 unless `initial` says), checked by the engine's own validation."""
    start = initial or {}
    stores = tuple(StoreDef(s, BIG, start.get(s, 0)) for s in STORES)
    r = Rules(stores, (SkillDef(SkillId("k")),), standing, PacingCurve((10**15,)), lanes=lanes, cards=cards,
              triggers=triggers, opening=opening)
    validate_rules(r)
    return r


def pool_for(share_bp: int, seconds: int) -> int:
    """The pool a card at `share_bp` costing one item a second empties in exactly `seconds`."""
    return share_bp * UNITS_PER_BP * seconds


def refill(at: int, store: StoreId, items: int, tid: str = "refill") -> TriggerDef:
    """A trigger adding `items` whole items of `store` at second `at`: a season's turn filling a pool."""
    return TriggerDef(TriggerId(tid), AfterTime(at), Outcome(stores=(Amount(store, items * Q),)))


def unlocking(at: int, *unlocks: Unlock, tid: str = "unlock") -> TriggerDef:
    return TriggerDef(TriggerId(tid), AfterTime(at), Outcome(unlocks=unlocks))


def opening_without(cards: Sequence[CardDef], standing: Sequence[StandingDef] = (), *locked: str,
                    retired: Sequence[str] = ()) -> tuple[Unlock, ...]:
    """An opening unlocking every card and standing action except the ids in `locked`, plus RETIRED for `retired`."""
    cs = tuple(Unlock(UnlockKind.CARD, str(c.id)) for c in cards if str(c.id) not in locked)
    ss = tuple(Unlock(UnlockKind.ACTION, str(a.id)) for a in standing if str(a.id) not in locked)
    return cs + ss + tuple(Unlock(UnlockKind.RETIRED, c) for c in retired)


def mixed(r: Rules, shares: Sequence[tuple[CardId, int]], t: int = 0, mix: MixId = MIX, base: Save | None = None,
          ) -> Save:
    """`base` (a new save) advanced to t, then a running mix of these shares saved and switched to at t."""
    s = decide(base if base is not None else new_save(r), r, t, SaveMix(Mix(mix, tuple(CardShare(c, b) for c, b in shares))))
    return decide(s, r, t, SwitchMix(mix))


def standard(shares: Sequence[int] = (4000, 2500, 1500), *, t_empty: int | None = 100, triggers: tuple[TriggerDef, ...] = (),
             standing: tuple[StandingDef, ...] = (), extra: tuple[CardDef, ...] = ()) -> tuple[Rules, Save]:
    """EAT (shares[0]) costing pool p, then R1, R2, ... at their shares, as one running hands mix from 0. p holds
    exactly what EAT empties in `t_empty` seconds (None: p starts at 0, so EAT is dry from the first instant)."""
    initial = {} if t_empty is None else {P: pool_for(shares[0], t_empty)}
    receivers = (R1, R2, R3)[:len(shares) - 1]
    r = world(eater(), *plain(*receivers), *extra, initial=initial, triggers=triggers, standing=standing)
    return r, mixed(r, [(EAT, shares[0])] + list(zip(receivers, shares[1:])))


def share_of(s: Save, r: Rules, card: CardId, t: int) -> int:
    """The share_bp a card's one make line explains with at t: its effective share."""
    store = PLAIN_MAKES.get(card, Y)
    return explain(advance(s, r, t), r, RateRef(card, FlowKind.MAKE, store)).share_bp


def gains(s: Save, r: Rules, card: CardId, t: int) -> tuple[tuple[CardId, int], ...]:
    store = PLAIN_MAKES.get(card, Y)
    return gained_of(explain(advance(s, r, t), r, RateRef(card, FlowKind.MAKE, store)))


def rate(s: Save, r: Rules, store: StoreId, t: int) -> int:
    """The store's segment slope on the span after t (units a second)."""
    return segment(advance(s, r, t), r, store).rate


def card_view(s: Save, r: Rules, card: CardId, t: int) -> CardView:
    return next(cv for cv in view(advance(s, r, t), r).cards if cv.card == card)


def make_run(s: Save, r: Rules, card: CardId, t: int) -> RunKind:
    """The Run kind a card's make line explains with at t."""
    store = PLAIN_MAKES.get(card, Y)
    return explain(advance(s, r, t), r, RateRef(card, FlowKind.MAKE, store)).run.kind


def work_of(s: Save, r: Rules, card: CardId, t: int) -> Explanation:
    return explain_work(advance(s, r, t), r, card)


def town_rules(*cards: CardDef, initial: dict[StoreId, int] | None = None) -> Rules:
    """Two ruled lanes, la and lb, each joined at 0 into the town mix with the first card given for it."""
    firsts = {LA: EATA, LB: RB}
    joins = tuple(TriggerDef(TriggerId("j" + str(lane)), AfterTime(0), Outcome(joins=(Join(lane, TM, card),)))
                  for lane, card in firsts.items())
    return world(*cards, initial=initial, triggers=joins, lanes=(LaneDef(LA, True), LaneDef(LB, True)))


def town_cards() -> tuple[CardDef, ...]:
    """la: EATA (costs p, dry from 0) and RA (makes z); lb: RB (makes w)."""
    return (eater(EATA, P, lane=LA), maker(RA, Z, lane=LA), maker(RB, W, lane=LB))


@dataclass(frozen=True)
class Scenario:
    """A pool-shaped world where EAT is dry on `store` from the first instant of the mix; `spent` is what the part
    says that store is. `pre` is the card tapped at 0 (if any), `t0` is when the mix is saved."""

    rules: Rules
    store: StoreId
    spent: bool
    t0: int = 0
    pre: CardId | None = None


def begin(sc: Scenario) -> Save:
    """The scenario's save with EAT at 4000 and R1 at 2500 as the running mix from t0."""
    s = new_save(sc.rules)
    if sc.pre is not None:
        s = decide(s, sc.rules, 0, TapCard(sc.pre))
    return mixed(sc.rules, [(EAT, 4000), (R1, 2500)], sc.t0, base=s)


def _on(store: StoreId) -> CardDef:
    return eater(pool=store)


def scenarios() -> dict[str, Scenario]:
    """Every shape of invariant 133, each with EAT (dry on `store`) in a mix with R1: the makers that keep a store out
    of the spent set, and the ones that do not."""
    base = (_on(P),) + plain(R1)
    locked_mk = base + (maker(MK, P),)
    done = replace(CardDef(MK, 1, makes=(Flow(P, per_hour(1)),)), cap=1)
    late = TriggerDef(TriggerId("late"), AfterTime(10**6), Outcome(stores=(Amount(P, Q),)))
    src = StandingDef(ActionId("src"), makes=(Flow(P, per_hour(1)),))
    return {
        "no maker": Scenario(world(*base), P, True),
        "locked maker": Scenario(world(*locked_mk, opening=opening_without(locked_mk, (), "mk")), P, True),
        "retired maker": Scenario(world(*locked_mk, opening=opening_without(locked_mk, (), retired=("mk",))), P, True),
        "completed maker": Scenario(world(*base, done), P, True, t0=2, pre=MK),
        "trigger adds": Scenario(world(*base, triggers=(late,)), P, True),
        "standing maker": Scenario(world(*base, standing=(src,)), P, False),
        "unmixed card maker": Scenario(world(*base, maker(MK, P)), P, False),
    } | chains()


def chains() -> dict[str, Scenario]:
    """Makers that take from other stores: a store is spent when each of its makers is stuck on a spent empty store.
    EAT is dry on p2, whose makers take from p and p3."""
    cards = (_on(P2),) + plain(R1)
    mk_p2 = replace(maker(MK, P2), inputs=(Amount(P, Q),))
    ring_a, ring_b = replace(maker(MK, P2), inputs=(Amount(P3, Q),)), replace(maker(MK2, P3), inputs=(Amount(P2, Q),))
    two = replace(maker(MK, P2), inputs=(Amount(P, Q), Amount(P3, Q)))
    costing = replace(maker(MK, P2), costs=(Flow(P, PS),))
    from_p3 = replace(maker(MK, P2), inputs=(Amount(P3, Q),))
    drains = replace(maker(MK, P2), drains=(Amount(P, Q),))
    src3 = StandingDef(ActionId("src3"), makes=(Flow(P3, per_hour(1)),))
    return {
        "chain": Scenario(world(*cards, mk_p2), P2, True),
        "cycle": Scenario(world(*cards, ring_a, ring_b), P2, True),
        "one stuck input of two": Scenario(world(*cards, two, initial={P3: 100 * Q}), P2, True),
        "cost counts": Scenario(world(*cards, costing), P2, True),
        "input above zero": Scenario(world(*cards, mk_p2, initial={P: 100 * Q}), P2, False),
        "maker takes nothing": Scenario(world(*cards, maker(MK, P2)), P2, False),
        "input not spent": Scenario(world(*cards, from_p3, standing=(src3,)), P2, False),
        "drain is no take": Scenario(world(*cards, drains), P2, False),
    }
