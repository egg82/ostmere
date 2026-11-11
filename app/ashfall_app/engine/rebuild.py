"""Segments from state: rebuild recomputes every rate at save.time; shift re-anchors segments without recomputing.

rebuild runs only at event instants and after decisions; between events shift is exact because rates are constant.
"""
from collections.abc import Callable
from dataclasses import dataclass, replace

from .cards import CardDef, CardState
from .counts import card_state, effective_cap, repeating, unit
from .gates import stack_inputs, store_cap
from .ids import ActionId, CardId, Runner, SkillId, StoreId
from .index import index
from .lumps import NO_TERMS, Terms, forgiven, lump_terms, motion, moving_lumps
from .memo import PartsMemo
from .modifiers import FlowKind, RateRef
from .motion import keep_segments, store_segment
from .phases import accrues, xp_ceiling
from .rates import Running, flow_net, keep_running, line, running, tapped_cards, work_line
from .rules import Rules, StoreDef
from .segments import Lump, LumpSegment, Segment, value_at
from .state import Save, SkillState, StoreState


@dataclass(frozen=True)
class _Rates:
    """The rates of a running set under the effective stack: each store's unclamped net over its flow lines (its lump
    lines move it by their cards' work), each skill's XP, and each running card's work speed."""

    flows: dict[StoreId, int]
    xp: dict[SkillId, int]
    work: dict[CardId, int]


_RATES: PartsMemo[_Rates] = PartsMemo(32)
"""Kept while the stack's inputs are the same objects and the chips and the running set are equal: about half of an
advance's rebuilds (a handler's after the instant's own, an instant that changed only values) run what the last one
ran, and an advance where a rule's mix comes and goes runs the few running sets of its cycle again and again."""


def rebuild(save: Save, rules: Rules) -> Save:
    """Every store, XP and card-work segment at the rates `running` gives now. A running card's work
    rises at its share's work speed (BP for a tap), limited only where it must stop: at its effective cap and, for a
    tap, at the next completion (TAP_DONE), unless the tap repeats (counts.repeating); a card not running keeps its
    work, rate 0."""
    now = running(save, rules)
    rates = _RATES.get(stack_inputs(save, rules), lambda: _rates(save, rules, now), (save.chips, now))
    values: dict[StoreId, int] = {}
    for st in save.stores:
        values.setdefault(st.store, st.segment.start_value)
    cards = _card_states(save, rules, rates.work)
    work = {cs.card: cs.work for cs in cards}
    rest = Segment(save.time, 0, 0)
    terms = lump_terms(save, rules)
    motions = {d.id: _store_motion(save, rules, d, values[d.id], rates.flows[d.id],
                                   terms.get(d.id, NO_TERMS), lambda c: work.get(c, rest))
               for d in rules.stores}
    stores = tuple(StoreState(d.id, _plain(motions[d.id])) for d in rules.stores)
    skills = tuple(SkillState(st.skill, _xp_segment(save, rules, st, rates.xp.get(st.skill, 0)), st.phase)
                   for st in save.skills)
    rebuilt = replace(save, stores=stores, skills=skills, cards=cards)
    keep_running(rebuilt, rules, now)
    keep_segments(rebuilt, rules, motions)
    return rebuilt


def _rates(save: Save, rules: Rules, now: Running) -> _Rates:
    """A line reads the save only through the effective stack, so these are a function of `now` and the stack."""
    flows = {d.id: flow_net(save, rules, now, d.id) for d in rules.stores}
    xp: dict[SkillId, int] = {}
    for r, s in now.shares.items():
        skill = _skill_of(rules, r)
        if skill is not None:
            xp[skill] = xp.get(skill, 0) + line(save, rules, RateRef(r, FlowKind.XP), s, now.runs[r]).per_hour
    work = {c.id: work_line(save, rules, c.id, now.shares[c.id], now.runs[c.id]).per_hour
            for c in rules.cards if c.id in now.shares}
    return _Rates(flows, xp, work)


def shift(save: Save, rules: Rules, t: int) -> Save:
    """Every segment re-anchored at t (stores, XP, card work); no rate changes."""
    motions = {st.store: _moved_motion(store_segment(save, rules, st.store), t) for st in save.stores}
    stores = tuple(StoreState(st.store, _plain(motions[st.store])) for st in save.stores)
    skills = tuple(SkillState(st.skill, _moved(st.xp, t), st.phase) for st in save.skills)
    cards = tuple(CardState(cs.card, _moved(cs.work, t), cs.raised) for cs in save.cards)
    shifted = replace(save, time=t, stores=stores, skills=skills, cards=cards)
    keep_segments(shifted, rules, motions)
    return shifted


def _moved_motion(seg: Segment, t: int) -> Segment:
    """A store's segment re-anchored at t, its cards' work with it: what store_segment gives for the shifted save."""
    moved = _moved(seg, t)
    if not isinstance(seg, LumpSegment):
        return moved
    lumps = tuple(Lump(w, k.num) for k in seg.lumps if (w := _moved(k.work, t)).rate > 0)
    return motion(moved, seg.flow, seg.den, lumps)


def _moved(seg: Segment, t: int) -> Segment:
    v = value_at(seg, t)
    if seg.limit is not None and v == seg.limit:
        return Segment(t, v, 0)
    return Segment(t, v, seg.rate, seg.limit)


def _store_motion(save: Save, rules: Rules, d: StoreDef, v: int, flow: int, terms: Terms,
                  work: Callable[[CardId], Segment]) -> Segment:
    """_store_segment of the store's `terms` moving under `work`; a store with no flow and no lump line is still, and so
    is one at 0 whose drains are forgiven (DESIGN.txt, "DRAINS")."""
    moving = moving_lumps(terms, work) if terms[1] else (terms[0], ())
    if (flow == 0 and not moving[1]) or (v == 0 and forgiven(rules, d.id, flow, terms, work)):
        return Segment(save.time, v, 0)
    return _store_segment(save, rules, d, v, flow, moving)


def _store_segment(save: Save, rules: Rules, d: StoreDef, v: int, flow: int,
                   moving: tuple[int, tuple[Lump, ...]]) -> Segment:
    """`v` is the store's value now; `flow`, its unclamped net over its flow lines;
    `moving`, the lumps moving it from now (lumps.moving_lumps). What store_segment gives; the save keeps its plain
    Segment, the slope rounded down."""
    cap = store_cap(save, rules, d.id)
    den, lumps = moving
    slope = flow * den + sum(k.num * k.work.rate for k in lumps)
    if slope > 0 and v >= cap:
        return Segment(save.time, v, 0)
    limit = _limit(v, slope, cap)
    return motion(Segment(save.time, v, slope // den, limit), flow, den, lumps)


def _plain(seg: Segment) -> Segment:
    """The four fields a save keeps of a store's segment (motion.store_segment)."""
    return seg if type(seg) is Segment else Segment(seg.start, seg.start_value, seg.rate, seg.limit)


def _limit(v: int, rate: int, cap: int) -> int | None:
    """The bound strictly beyond v in the direction of motion: 0 or the cap."""
    if rate > 0:
        return cap if cap > v else None
    if rate < 0:
        return 0 if v > 0 else None
    return None


def _xp_segment(save: Save, rules: Rules, st: SkillState, rate: int) -> Segment:
    """The skill's XP rising at `rate` up to its phase's ceiling (phases.xp_ceiling); standing still at the ceiling, at
    rate 0, and once accrual has stopped (phases.accrues)."""
    xp = st.xp.start_value
    cap = xp_ceiling(rules.curve, rules.prestige, st.phase.phase)
    if xp >= cap or rate == 0 or not accrues(rules.prestige, st.phase, save.time):
        return Segment(save.time, xp, 0)
    return Segment(save.time, xp, rate, cap)


def _skill_of(rules: Rules, runner: Runner) -> SkillId | None:
    ix = index(rules)
    card = ix.cards.get(CardId(runner))
    return card.skill if card is not None else ix.standing[ActionId(runner)].skill


def _card_states(save: Save, rules: Rules, speeds: dict[CardId, int]) -> tuple[CardState, ...]:
    """Each card's work at the speed it runs at now (`speeds`, a running card's); present only when it has work, a
    raise or a rate. A card with no state that does not run has none after, so only the others are visited, in rules
    order."""
    bounded = {c for c in tapped_cards(save, rules) if not repeating(save, rules, c)}
    ix = index(rules)
    visited = {cs.card for cs in save.cards if cs.card in ix.cards} | speeds.keys()
    found: list[CardState] = []
    for c in sorted((ix.cards[card] for card in visited), key=lambda c: ix.card_pos[c.id]):
        cs = card_state(save, c.id)
        raised = 0 if cs is None else cs.raised
        w = 0 if cs is None else cs.work.start_value
        speed = speeds.get(c.id)
        seg = Segment(save.time, w, 0) if speed is None else _work_segment(save, rules, c, w, c.id in bounded, speed)
        if seg.start_value != 0 or seg.rate != 0 or raised != 0:
            found.append(cs if cs is not None and cs.work == seg else CardState(c.id, seg, raised))
    return tuple(found)


def _work_segment(save: Save, rules: Rules, card: CardDef, w: int, bounded: bool, rate: int | None) -> Segment:
    """`w`, the card's work now; `rate`, its work speed, None when it is not running; `bounded`, a tap that stops at
    its next completion."""
    cap = effective_cap(save, rules, card.id)
    if (cap is not None and w // unit(card) >= cap) or rate is None or rate <= 0:
        return Segment(save.time, w, 0)
    bounds = [cap * unit(card)] if cap is not None else []
    if bounded:
        bounds.append((w // unit(card) + 1) * unit(card))
    return Segment(save.time, w, rate, min(bounds, default=None))
