"""Random small worlds with town lanes, a leave and stopped standings, read through advance against an oracle written
from engine DESIGN.txt: SPENT (invariants 133, 134, every paused card a giver) and LEAVES (a stopped standing is no maker, a left lane's cards
are out of play, a town mix the leave empties never takes the hands). A seeded slice: each chunk is a fixed range of
seeds, so a failure names its seed."""
import random

import pytest

from ashfall_app.engine import (
    QUANTITY_SCALE as Q, ActionId, AfterTime, Amount, CardDef, CardId, CardShare, Flow, FlowKind, InvalidRulesError,
    InvalidVerbError, Join, LaneDef, LaneId, Leave, Mix, MixId, Order, Outcome, PacingCurve, RateRef, Rules, RunKind,
    Save, SaveMix, SetOrders, SkillDef, SkillId, StandingDef, StoreDef, StoreId, StoreState, SwitchMix, TriggerDef,
    TriggerId, advance, decide, explain, new_save, per_hour, validate_rules,
)
from ashfall_app.engine.counts import is_completed
from ashfall_app.engine.gone import left_lanes, stopped
from ashfall_app.engine.plan import running_mix_id, running_town_mix_id
from ashfall_app.engine.spent import spent_stores

HANDS, LA, LB = LaneId("hands"), LaneId("la"), LaneId("lb")
M, TOWN = MixId("m"), MixId("town:main")
CHUNK, CHUNKS = 25, 8

type Shares = list[tuple[CardId, int]]


def _flow(rng: random.Random, stores: list[StoreId], rates: list[int]) -> tuple[StoreId, tuple[Flow, ...]]:
    """A store made, and a cost on another store or none."""
    made = rng.choice(stores)
    cost = rng.choice([None, *(x for x in stores if x != made)])
    return made, () if cost is None else (Flow(cost, per_hour(rng.choice(rates))),)


def _world(rng: random.Random) -> Rules:
    stores = [StoreId(f"s{i}") for i in range(rng.randint(3, 5))]
    standing: list[StandingDef] = []
    for i in range(rng.randint(0, 2)):
        made, costs = _flow(rng, stores, [1, 60, 3600])
        standing.append(StandingDef(ActionId(f"a{i}"), makes=(Flow(made, per_hour(rng.choice([1, 60, 3600]))),),
                                    costs=costs))
    cards: list[CardDef] = []
    for i in range(rng.randint(2, 5)):
        lane = rng.choice([HANDS, HANDS, LA, LB, LB])
        made, costs = _flow(rng, stores, [360, 3600, 7200])
        cards.append(CardDef(CardId(f"c{i}"), rng.choice([5, 10]), lane=lane, makes=(Flow(made, per_hour(3600)),),
                             costs=costs))
    triggers = [TriggerDef(TriggerId(f"j{lane}"), AfterTime(0), Outcome(joins=(Join(lane, TOWN, first.id),)))
                for lane in (LA, LB) if (first := next((c for c in cards if c.lane == lane), None)) is not None]
    if rng.random() < 0.6:
        stops = tuple(a.id for a in standing if rng.random() < 0.6)
        triggers.append(TriggerDef(TriggerId("go"), AfterTime(rng.randint(0, 60)), Outcome(leaves=(Leave(LA, stops),))))
    if rng.random() < 0.5:
        triggers.append(TriggerDef(TriggerId("refill"), AfterTime(rng.randint(10, 200)),
                                   Outcome(stores=(Amount(rng.choice(stores), rng.randint(1, 20) * Q),))))
    initial = {s: rng.choice([0, 0, rng.randint(1, 50) * Q]) for s in stores}
    r = Rules(tuple(StoreDef(s, 10**6 * Q, initial[s]) for s in stores), (SkillDef(SkillId("k")),), tuple(standing),
              PacingCurve((10**15,)), lanes=(LaneDef(LA, True), LaneDef(LB, True)), cards=tuple(cards),
              triggers=tuple(triggers))
    validate_rules(r)
    return r


def _value(st: StoreState, t: int) -> int:
    sg = st.segment
    v = sg.start_value + sg.rate * (t - sg.start)
    if sg.limit is None or sg.rate == 0:
        return v
    return min(v, sg.limit) if sg.rate > 0 else max(v, sg.limit)


def _oracle(s: Save, r: Rules) -> set[StoreId]:
    """Invariant 133 from the save: the largest set whose every maker in play takes from an empty store of the set."""
    gone, stop = left_lanes(s), stopped(s, r)
    empty = {st.store for st in s.stores if _value(st, s.time) == 0}
    makers: dict[StoreId, list[set[StoreId]]] = {}
    for a in r.standing:
        if a.id not in stop:
            for f in a.makes:
                makers.setdefault(f.store, []).append({c.store for c in a.costs})
    for c in r.cards:
        if c.lane not in gone and not is_completed(s, r, c.id):
            for x in {f.store for f in c.makes} | {a.store for a in c.outcome.stores}:
                makers.setdefault(x, []).append({f.store for f in c.costs} | {a.store for a in c.inputs})
    spent = {d.id for d in r.stores}
    changed = True
    while changed:
        blocked = spent & empty
        drop = {x for x in spent if any(not (takes & blocked) for takes in makers.get(x, ()))}
        spent -= drop
        changed = bool(drop)
    return spent


def _yields(a: Save, r: Rules, t: int, shares: Shares, want: set[StoreId]) -> list[str]:
    """Invariant 134 on one lane's shares: every card holding a Pause gives, SPENT when its store is spent and PAUSED
    otherwise, and the rest gain in proportion to their saved shares."""
    paused = {p.runner: p.store for p in a.pauses}
    givers = {c for c, _ in shares if c in paused}
    rsum = sum(b for c, b in shares if c not in givers)
    probs: list[str] = []
    for c, b in shares:
        made = next(x for x in r.cards if x.id == c).makes[0].store
        e = explain(a, r, RateRef(c, FlowKind.MAKE, made))
        kind = (RunKind.SPENT if paused[c] in want else RunKind.PAUSED) if c in givers else None
        if kind is not None and e.run.kind is not kind:
            probs.append(f"t={t} {c} run {e.run.kind.value}, want {kind.value}")
        gain = sum(bk * b // rsum for k, bk in shares if k in givers) if rsum else 0
        if c not in givers and e.share_bp != b + gain:
            probs.append(f"t={t} {c} share {e.share_bp}, want {b + gain}")
    return probs


def _planned(rng: random.Random, r: Rules) -> tuple[Save, Shares, Shares] | None:
    """The player's mix m of every hands card, and the town mix of every town card under the town's always rule."""
    hands = [(c.id, rng.choice([1000, 2500, 4000])) for c in r.cards if c.lane == HANDS]
    town = [(c.id, rng.choice([2000, 5000])) for c in r.cards if c.lane in (LA, LB)]
    if not hands or not town:
        return None
    try:
        s = decide(new_save(r), r, 0, SaveMix(Mix(M, tuple(CardShare(c, b) for c, b in hands))))
        s = decide(s, r, 0, SwitchMix(M))
        s = decide(s, r, 0, SaveMix(Mix(TOWN, tuple(CardShare(c, b) for c, b in town))))
        s = decide(s, r, 0, SetOrders((Order(AfterTime(0), SwitchMix(TOWN)),)))
    except InvalidVerbError:
        return None   # hands shares past 100%
    return s, hands, town


def _problems(seed: int) -> list[str]:
    rng = random.Random(seed)
    try:
        r = _world(rng)
    except InvalidRulesError:
        return []
    planned = _planned(rng, r)
    if planned is None:
        return []
    s, hands, town = planned
    probs: list[str] = []
    for t in sorted(rng.sample(range(1, 400), 6)):
        a = advance(s, r, t)
        want = _oracle(a, r)
        if set(spent_stores(a, r)) != want:
            probs.append(f"t={t} spent {sorted(spent_stores(a, r))}, want {sorted(want)}")
        if running_mix_id(a, r) != M:
            probs.append(f"t={t} the hands run {running_mix_id(a, r)}, want {M}")
            continue
        groups = [hands]
        if running_town_mix_id(a, r) == TOWN:
            lane_of = {c.id: c.lane for c in r.cards}
            groups += [g for lane in (LA, LB) if lane not in left_lanes(a)
                       if (g := [(c, b) for c, b in town if lane_of[c] == lane])]
        for g in groups:
            probs += _yields(a, r, t, g, want)
    return probs


@pytest.mark.parametrize("chunk", range(CHUNKS))
def test_spent_and_leaves_agree_with_the_oracle_on_random_town_worlds(chunk: int):
    bad = {seed: p[:3] for seed in range(chunk * CHUNK, (chunk + 1) * CHUNK) if (p := _problems(seed))}
    assert bad == {}
