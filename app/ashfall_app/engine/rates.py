"""What runs now: each runner's share and Run (grey, pauses, waits, yield), and every line's
rate, a card's lump lines included (DESIGN.txt, "Rate form").

All of it is a function of the save's values at save.time and its discrete state, never of history.
"""
from collections.abc import Callable
from dataclasses import dataclass, field, replace
from fractions import Fraction

from .cards import LaneState
from .counts import is_completed, unit
from .gates import effective_stack, is_unlocked, stack_inputs
from .gone import stopped
from .ids import CardId, LaneId, Runner, StoreId
from .index import derived, index
from .lumps import base_of, has_lump, lump_amount, lump_lines
from .memo import PartsMemo, SaveMemo
from .mixes import SpentShare
from .modifiers import (
    Explanation, FlowKind, LaneSpeed, Modifier, ModifierKind, RateRef, Run, RunKind, WorkRef, modified_rate,
)
from .mixruns import mix_entries, mix_gains, town_entries
from .requires import first_unmet
from .rules import Rules, StandingDef
from .sides import costs, makes, touching
from .state import Save
from .unlocks import Unlock, UnlockKind
from .units import BP

FULL = Run(RunKind.FULL)


@dataclass(frozen=True)
class Running:
    """Effective shares and Runs of every runner in the running set: standing actions (BP), the running mix's cards
    (their flattened shares, Run YIELDED during a HANDS tap, GREYED while the mix is greyed, WAITING on requires), and
    each tapped card (BP, on its lane), in the order running-dry pauses read backwards: standing in rules order, then
    the hands (the mix in mix order, then a tapped card), then the other lanes in rules order; the running town mix's
    cards come after the hands' mix and before the taps. A card both mixed and
    tapped appears once, as its tap at BP: its mix share is yielded with the rest of the mix (DESIGN.txt, "One
    bar"). A mix card's share is its effective one, its saved share plus `gained`, what it receives from paused and
    spent cards (DESIGN.txt, "SPENT")."""

    shares: dict[Runner, int]
    runs: dict[Runner, Run]
    gained: dict[Runner, tuple[SpentShare, ...]] = field(default_factory=dict[Runner, tuple[SpentShare, ...]])


def store_value(save: Save, store: StoreId) -> int:
    return next(st.segment.start_value for st in save.stores if st.store == store)


def aimed_stack(save: Save, rules: Rules, ref: RateRef, run: Run) -> tuple[Modifier, ...]:
    """The save's modifiers then the shown chips', those aimed at `ref` or at the speed of the lane it runs on (a
    standing action has no lane), and, for a card's lump line, at its WorkRef; each retargeted at `ref` so the
    Explanation recomputes from its own fields. The speed entries are run.speed's when it holds them (_picked)."""
    ix = index(rules)
    lane = ix.runner_lane[ref.runner]
    card = ix.cards.get(CardId(ref.runner))
    speed: list[LaneSpeed | WorkRef] = []
    if lane is not None:
        speed.append(LaneSpeed(lane))
    if card is not None and has_lump(card, ref):
        speed.append(WorkRef(card.id))
    return tuple(replace(m, target=ref) for m in _picked(save, rules, [ref], speed, run))


def _picked(save: Save, rules: Rules, own: list[RateRef], speed: list[LaneSpeed | WorkRef], run: Run
            ) -> list[Modifier]:
    """The effective stack's entries aimed at `own` or `speed`, in the stack's own order; for a tap that kept its speed
    entries (run.speed), the live ones aimed at `own`, then the kept ones aimed at `speed`."""
    by = _by_target(save, rules)
    if run.speed is None:
        return [m for _, m in sorted((i, m) for aim in [*own, *speed] for i, m in by.get(aim, ()))]
    live = [m for _, m in sorted((i, m) for aim in own for i, m in by.get(aim, ()))]
    return live + [m for m in run.speed if m.target in speed]


_BY_TARGET: SaveMemo[dict[object, list[tuple[int, Modifier]]]] = SaveMemo()


def _by_target(save: Save, rules: Rules) -> dict[object, list[tuple[int, Modifier]]]:
    """The effective stack grouped by target, each entry with its place in the stack: one pass per save."""
    def build() -> dict[object, list[tuple[int, Modifier]]]:
        out: dict[object, list[tuple[int, Modifier]]] = {}
        for i, m in enumerate(effective_stack(save, rules)):
            out.setdefault(m.target, []).append((i, m))
        return out
    return _BY_TARGET.get(save, rules, build)


_LINES: PartsMemo[dict[tuple[RateRef | CardId, int, Run], Explanation]] = PartsMemo(8)
_MAX_LINES = 4096
"""Lines kept under one stack before they are dropped."""


def _kept_line(save: Save, rules: Rules, key: tuple[RateRef | CardId, int, Run],
               build: Callable[[], Explanation]) -> Explanation:
    """A line is a function of its ref, share and run and of the effective stack alone, so it is kept while the stack's
    inputs are the same objects, across saves, as the instants of an advance mostly leave them."""
    lines = _LINES.get(stack_inputs(save, rules), dict, save.chips)
    found = lines.get(key)
    if found is None:
        if len(lines) >= _MAX_LINES:
            lines.clear()
        found = lines[key] = build()
    return found


def line(save: Save, rules: Rules, ref: RateRef, share: int, run: Run) -> Explanation:
    return _kept_line(save, rules, (ref, share, run), lambda: _line(save, rules, ref, share, run))


def _line(save: Save, rules: Rules, ref: RateRef, share: int, run: Run) -> Explanation:
    base, den = base_of(rules, ref)
    return modified_rate(ref, base, share, aimed_stack(save, rules, ref, run), run, den)


def work_line(save: Save, rules: Rules, card: CardId, share: int, run: Run) -> Explanation:
    """Work units per second the card's bar fills at under `share` and `run`."""
    return _kept_line(save, rules, (card, share, run), lambda: _work_line(save, rules, card, share, run))


def _work_line(save: Save, rules: Rules, card: CardId, share: int, run: Run) -> Explanation:
    """modified_rate takes a RateRef, so the formula runs on a stand-in ref and the result is relabelled with the
    WorkRef and the entries retargeted at it."""
    lane = index(rules).cards[card].lane
    target = WorkRef(card)
    aimed = tuple(replace(m, target=target) for m in _picked(save, rules, [], [target, LaneSpeed(lane)], run))
    stand_in = RateRef(card, FlowKind.XP)
    e = modified_rate(stand_in, BP, share, tuple(replace(m, target=stand_in) for m in aimed), run)
    adds = tuple(m for m in aimed if m.kind is ModifierKind.ADD_BP)
    muls = tuple(m for m in aimed if m.kind is ModifierKind.MUL_BP)
    return replace(e, ref=target, adds=adds, muls=muls)


def work_speed(save: Save, rules: Rules, card: CardId, run: Run) -> Explanation:
    """Work units per second a card's bar fills at, tapped (share BP) or mixed (its share): base BP, the WorkRef and
    LaneSpeed entries aimed at it."""
    return work_line(save, rules, card, running(save, rules).shares.get(card, BP), run)


def contribution(save: Save, rules: Rules, runner: Runner, store: StoreId, share: int, run: Run) -> int:
    """What `runner` adds to `store` per hour (its make, or minus its cost) at this share and run."""
    if store in makes(rules, runner):
        return line(save, rules, RateRef(runner, FlowKind.MAKE, store), share, run).per_hour
    if store in costs(rules, runner):
        return -line(save, rules, RateRef(runner, FlowKind.COST, store), share, run).per_hour
    return 0


def flow_net(save: Save, rules: Rules, now: Running, store: StoreId) -> int:
    """The store's unclamped net over its flow lines: its lump lines move it by their cards' work (lumps.py)."""
    touch = derived(rules, "_flow_touch", _all_flow_touch).get(store, frozenset())
    return sum(contribution(save, rules, a, store, now.shares[a], now.runs[a]) for a in touch if a in now.shares)


def _all_flow_touch(rules: Rules) -> dict[StoreId, frozenset[Runner]]:
    """The runners whose flow lines move each store: those touching it but for its lump cards, which move it by work."""
    return {d.id: touching(rules, d.id) - {c.id for c, _ in lump_lines(rules, d.id)} for d in rules.stores}


def exact_contribution(save: Save, rules: Rules, runner: Runner, store: StoreId, share: int, run: Run) -> Fraction:
    """What `runner` adds to `store` per second, exactly: a flow's rate, or a lump's amount per completion times the
    card's work speed over its work per completion, the rate its card's work pays it at (DESIGN.txt, "Rate form")."""
    card = index(rules).cards.get(CardId(runner))
    ref = RateRef(runner, FlowKind.MAKE if store in makes(rules, runner) else FlowKind.COST, store)
    if card is None or not has_lump(card, ref):
        return Fraction(contribution(save, rules, runner, store, share, run))
    paid = lump_amount(save, rules, card, ref) * work_line(save, rules, card.id, share, run).per_hour
    return Fraction(paid if ref.kind is FlowKind.MAKE else -paid, unit(card))


def exact_net(save: Save, rules: Rules, now: Running, store: StoreId) -> Fraction:
    """The store's unclamped net per second, exactly: the sum of every running runner's exact contribution."""
    touch = touching(rules, store)   # a runner that neither makes nor costs it adds 0
    return sum((exact_contribution(save, rules, a, store, s, now.runs[a]) for a, s in now.shares.items()
                if a in touch), Fraction(0))


def lane_state(save: Save, lane: LaneId) -> LaneState:
    return next(ls for ls in save.lanes if ls.lane == lane)


def tapped_cards(save: Save, rules: Rules) -> tuple[CardId, ...]:
    """The cards a tap is running, in lane order (a completed card is done)."""
    return tuple(ls.card for ls in save.lanes if ls.card is not None and not is_completed(save, rules, ls.card))


_RUNNING: SaveMemo[Running] = SaveMemo(4)
"""A few saves, each built once: rebuild keeps its own for the save it returns (keep_running). Callers never change
what it returns."""


def running(save: Save, rules: Rules) -> Running:
    """Shares and Runs in the order running-dry pauses read them backwards (see Running)."""
    return _RUNNING.get(save, rules, lambda: _running(save, rules))


def keep_running(save: Save, rules: Rules, now: Running) -> None:
    """`now` is running(save): a rebuilt save has the values and the discrete state of the save it was built from,
    and running reads nothing else."""
    _RUNNING.put(save, rules, now)


_STANDING: PartsMemo[tuple[StandingDef, ...]] = PartsMemo()
"""The unlocked standing actions, kept while the rules and the save's unlock set are the same objects."""


def unlocked_standing(save: Save, rules: Rules) -> tuple[StandingDef, ...]:
    """The standing actions that run: unlocked, and not stopped by a leave (DESIGN.txt, "LEAVES")."""
    return _STANDING.get((rules, save.unlocked), lambda: _unlocked_standing(save, rules))


def _unlocked_standing(save: Save, rules: Rules) -> tuple[StandingDef, ...]:
    gone = stopped(save, rules)
    return tuple(a for a in rules.standing
                 if is_unlocked(save, rules, Unlock(UnlockKind.ACTION, a.id)) and a.id not in gone)


def _running(save: Save, rules: Rules) -> Running:
    shares: dict[Runner, int] = {}
    runs: dict[Runner, Run] = {}
    paused = {p.runner: p.store for p in save.pauses}
    tapped = tapped_cards(save, rules)
    for a in unlocked_standing(save, rules):
        shares[a.id] = BP
        runs[a.id] = Run(RunKind.PAUSED, 0, 1, paused[a.id]) if a.id in paused else FULL
    for card, share, run in (*mix_entries(save, rules), *town_entries(save, rules)):
        if card not in tapped:
            shares[card], runs[card] = share, run
    gains = mix_gains(save, rules)
    gained: dict[Runner, tuple[SpentShare, ...]] = {c: g for c, g in gains.items() if c not in tapped} if gains else {}
    for card in tapped:
        kept = lane_state(save, index(rules).cards[card].lane).speed
        shares[card], runs[card] = BP, _tap_run(save, rules, card, paused.get(card), kept)
    return Running(shares, runs, gained)


def _tap_run(save: Save, rules: Rules, card: CardId, paused_on: StoreId | None,
             speed: tuple[Modifier, ...] | None) -> Run:
    if paused_on is not None:
        return Run(RunKind.PAUSED, 0, 1, paused_on, speed=speed)
    unmet = first_unmet(save, rules, index(rules).cards[card])
    return Run(RunKind.FULL, speed=speed) if unmet is None else Run(RunKind.WAITING, 0, 1, None, unmet, speed=speed)
