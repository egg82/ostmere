"""Hypothesis strategies for the cards contract tests: random valid worlds of cards (capped and not, on HANDS and on a
rack, with flows, inputs, outcome stores, requires, raises and starts), standing actions, chips, triggers and an
opening, and scenarios that play every verb on them. Built from the engine's public types only; nothing here calls an
engine function while generating.

Every world passes "Validation of cards" (DESIGN.txt): a store appears once across a card's makes, costs, inputs and
outcome stores, requires are plain thresholds, an uncapped card's outcome is stores only with at most one line, a capped card has no lines or one per completion of its base cap, raises name capped
cards, and no HANDS completion starts a HANDS card. Mixes hold HANDS cards only."""
import os
from dataclasses import dataclass

from hypothesis import settings, strategies as st
from hypothesis.strategies import DrawFn

from ashfall_app.engine import (
    HANDS, AfterTime, Amount, AtLeast, AtMost, CapRaise, CardCount, CardDef, CardId, CardShare, ChipDef, ChipId,
    Condition, DeleteMix, Flow, LaneId, LaneSpeed, Line, LineKey, Mix, MixId, Modifier, ModifierKind, Order, Outcome,
    QueueEntry, RateRef, FlowKind, Rules, Running, Save, SaveMix, SetOrders, SetQueue, SkillLevel, SourceId,
    StandingDef, StoreDef, StoreId, StoreValue, SwitchMix, Target, TapCard, TriggerDef, TriggerId, Unlock, UnlockKind,
    Unlocked, Verb, WorkRef, ActionId, InvalidVerbError, advance, advance_logged, decide, decide_logged, new_save,
    next_event, validate_rules,
)
from cards_world import K, Q, RACK, rules as make_rules

Draw = DrawFn


def few(n: int):
    """Fewer examples for a heavy test on the default profile only; `ci`/`debug` keep their own (larger) count."""
    return settings(max_examples=n) if os.environ.get("HYPOTHESIS_PROFILE", "contract") == "contract" else settings()


S = [StoreId(f"s{i}") for i in range(3)]
CARDS = [CardId(f"c{i}") for i in range(4)]
ST = ActionId("st")
MIXES = [MixId(f"m{i}") for i in range(2)]

_rate = st.one_of(st.just(0), st.integers(1, 500), st.integers(1, 40_000))
_amount = st.one_of(st.integers(1, 1000), st.integers(1, 2 * Q))


@st.composite
def _sides(draw: Draw, stores: list[StoreId]) -> tuple[tuple[Flow, ...], tuple[Flow, ...], tuple[Amount, ...],
                                                        tuple[Amount, ...]]:
    """makes, costs, inputs, outcome stores: each store appears at most once across the four (validation)."""
    makes: list[Flow] = []
    costs: list[Flow] = []
    inputs: list[Amount] = []
    outs: list[Amount] = []
    for s in stores:
        role = draw(st.sampled_from(["none", "make", "cost", "input", "out"]))
        if role == "make":
            makes.append(Flow(s, draw(_rate)))
        if role == "cost":
            costs.append(Flow(s, draw(_rate)))
        if role == "input":
            inputs.append(Amount(s, draw(_amount)))
        if role == "out":
            outs.append(Amount(s, draw(_amount)))
    return tuple(makes), tuple(costs), tuple(inputs), tuple(outs)


@st.composite
def _condition(draw: Draw, stores: list[StoreDef], cards: list[CardId], band: bool) -> Condition:
    """A chip, trigger or requires condition, true at time 0 or not; band: a hysteresis band where bounds allow."""
    kinds = ["after", "level", "after0", "count"]
    kinds += ["least"] if any(s.initial < s.cap for s in stores) else []
    kinds += ["most"] if any(s.initial > 0 for s in stores) else []
    kind = draw(st.sampled_from(kinds))
    width = Q * draw(st.integers(1, 3)) if band else 0
    if kind == "after":
        return AfterTime(draw(st.integers(1, 20_000)))
    if kind == "after0":
        return AfterTime(0)
    if kind == "level":
        lv = draw(st.integers(2, 3))
        return AtLeast(SkillLevel(K), lv, lv if not band else lv - 1)
    if kind == "count":
        n = draw(st.integers(1, 3))
        return AtLeast(CardCount(draw(st.sampled_from(cards))), n, n)
    if kind == "least":
        s = draw(st.sampled_from([s for s in stores if s.initial < s.cap]))
        v = draw(st.integers(0, s.cap))
        return AtLeast(StoreValue(s.id), v, max(0, v - width))
    s = draw(st.sampled_from([s for s in stores if s.initial > 0]))
    v = draw(st.integers(0, s.cap - 1))
    return AtMost(StoreValue(s.id), v, min(s.cap, v + width))


@st.composite
def _modifier(draw: Draw, targets: list[Target], source: str) -> Modifier:
    target = draw(st.sampled_from(targets))
    if draw(st.booleans()):
        return Modifier(target, ModifierKind.ADD_BP, draw(st.integers(-6000, 6000)), SourceId(source))
    return Modifier(target, ModifierKind.MUL_BP, draw(st.integers(0, 30_000)), SourceId(source))


@dataclass(frozen=True)
class _Plan:
    """What the cards of one world are, decided before their outcomes (which name each other)."""

    ids: list[CardId]
    lane: dict[CardId, LaneId]
    cap: dict[CardId, int | None]


@st.composite
def _discrete_outcome(draw: Draw, plan: _Plan, me: CardId | None, lockable: list[Unlock], targets: list[Target],
                      source: str, line: str) -> Outcome:
    """An outcome's non-store parts. me None: a trigger's (it may start any card)."""
    unlocks = tuple(draw(st.lists(st.sampled_from(lockable), unique=True, max_size=2))) if lockable else ()
    mods = tuple(draw(st.lists(_modifier(targets, source), max_size=1)))
    # A raise points only at a later card: a card raising itself (or two raising each other) with a one-second work
    # would complete every second for the whole run, and the suite has a time budget.
    capped = [c for c in plan.ids if plan.cap[c] is not None and (me is None or plan.ids.index(c) > plan.ids.index(me))]
    raises = tuple(CapRaise(c, draw(st.integers(1, 2)))
                   for c in draw(st.lists(st.sampled_from(capped), unique=True, max_size=1))) if capped else ()
    startable = [c for c in plan.ids if me is None or not (plan.lane[me] == HANDS and plan.lane[c] == HANDS)]
    starts = tuple(draw(st.lists(st.sampled_from(startable), unique=True, max_size=1))) if startable else ()
    lines = (LineKey(line),) if draw(st.booleans()) else ()
    return Outcome((), unlocks, mods, raises, starts, lines)


def _card(draw: Draw, plan: _Plan, c: CardId, stores: list[StoreDef], lockable: list[Unlock],
          targets: list[Target]) -> CardDef:
    sids = [s.id for s in stores]
    makes, costs, inputs, outs = draw(_sides(sids))
    cap = plan.cap[c]
    xp = draw(st.one_of(st.just(0), st.integers(1, 40_000)))
    requires: tuple[Condition, ...] = ()
    if draw(st.integers(0, 3)) == 0:
        requires = (draw(_condition(stores, plan.ids, False)),)
    # Seconds-long work only where completions are bounded (a cap): an order re-tapping an uncapped one-second card
    # would make every second an instant, and the suite has a time budget.
    work_s = draw(st.sampled_from([1, 3, 7, 300, 900]) if cap is not None else st.integers(300, 1500))
    if cap is None:
        lines = (LineKey(f"{c}.tap"),) if draw(st.booleans()) else ()
        return CardDef(c, work_s, plan.lane[c], K, xp, makes, costs, inputs, requires, Outcome(stores=outs), None,
                       Outcome(), lines)
    disc = draw(_discrete_outcome(plan, c, lockable, targets, f"out.{c}", f"{c}.out"))
    fin = draw(_discrete_outcome(plan, c, lockable, targets, f"fin.{c}", f"{c}.fin"))
    lines = tuple(LineKey(f"{c}.{n}") for n in range(1, cap + 1)) if draw(st.booleans()) else ()
    outcome = Outcome(outs, disc.unlocks, disc.modifiers, disc.raises, disc.starts, disc.lines)
    return CardDef(c, work_s, plan.lane[c], K, xp, makes, costs, inputs, requires, outcome, cap, fin, lines)


@st.composite
def world_st(draw: Draw, max_firings: int | None = None) -> Rules:
    stores: list[StoreDef] = []
    for i in range(draw(st.integers(2, 3))):
        cap = Q * draw(st.integers(4, 20))
        stores.append(StoreDef(S[i], cap, draw(st.one_of(st.just(0), st.just(cap), st.integers(0, cap)))))
    sids = [s.id for s in stores]
    standing: list[StandingDef] = []
    if draw(st.booleans()):
        s = draw(st.sampled_from(sids))
        flow = Flow(s, draw(_rate))
        standing.append(StandingDef(ST, (flow,), ()) if draw(st.booleans()) else StandingDef(ST, (), (flow,)))
    lanes: list[LaneId] = [RACK] if draw(st.booleans()) else []
    ids = CARDS[:draw(st.integers(1, 4))]
    plan = _Plan(ids, {c: draw(st.sampled_from([HANDS, HANDS, *lanes])) for c in ids},
                 {c: draw(st.sampled_from([None, None, 1, 2, 3])) for c in ids})
    chip_ids = [ChipId(f"k{i}") for i in range(draw(st.integers(0, 1)))]
    gated = draw(st.booleans())
    lockable = ([Unlock(UnlockKind.CARD, c) for c in ids[1:]] + [Unlock(UnlockKind.CHIP, k) for k in chip_ids]
                + ([Unlock(UnlockKind.ACTION, ST)] if standing else [])) if gated else []
    targets: list[Target] = [*(WorkRef(c) for c in ids), LaneSpeed(HANDS), *(LaneSpeed(x) for x in lanes)]
    targets += [RateRef(c, FlowKind.XP) for c in ids]
    cards = [_card(draw, plan, c, stores, lockable, targets) for c in ids]
    chips = [ChipDef(k, draw(_condition(stores, ids, True)), tuple(draw(st.lists(_modifier(targets, k), max_size=2))),
                     LineKey(f"{k}.on") if draw(st.booleans()) else None,
                     LineKey(f"{k}.off") if draw(st.booleans()) else None) for k in chip_ids]
    triggers = [TriggerDef(TriggerId(f"t{i}"), draw(_condition(stores, ids, False)),
                           draw(_discrete_outcome(plan, None, lockable, targets, f"t{i}", f"t{i}.fired")))
                for i in range(draw(st.integers(0, 1)))]
    opening = None
    if gated:
        opening = ([Unlock(UnlockKind.STORE, s) for s in sids] + [Unlock(UnlockKind.SKILL, K)]
                   + [Unlock(UnlockKind.CARD, ids[0])])
        if lockable:
            opening += draw(st.lists(st.sampled_from(lockable), unique=True))
    steps = draw(st.lists(st.integers(1, 3 * Q), min_size=1, max_size=4))
    thresholds = tuple(sum(steps[: k + 1]) for k in range(len(steps)))
    mf = max_firings if max_firings is not None else draw(st.one_of(st.just(1000), st.integers(1, 4)))
    return make_rules(stores, cards=cards, standing=standing, lanes=lanes, chips=chips, triggers=triggers,
                      opening=opening, thresholds=thresholds, max_firings=mf)


def hands_cards(r: Rules) -> list[CardId]:
    return [c.id for c in r.cards if c.lane == HANDS]


@st.composite
def condition_st(draw: Draw, r: Rules) -> Condition:
    """Any condition an order may hold, over every subject kind."""
    kind = draw(st.sampled_from(["after", "store", "level", "count", "running", "unlocked"]))
    if kind == "after":
        return AfterTime(draw(st.integers(0, 20_000)))
    if kind == "store":
        s = draw(st.sampled_from(r.stores))
        subj: object = StoreValue(s.id)
        lo, top = 0, s.cap
    elif kind == "level":
        subj, lo, top = SkillLevel(K), 1, len(r.curve.thresholds) + 1
    elif kind == "count":
        subj, lo, top = CardCount(draw(st.sampled_from([c.id for c in r.cards]))), 0, 4
    elif kind == "running":
        subj, lo, top = Running(draw(st.sampled_from([c.id for c in r.cards]))), 0, 1
    else:
        subj, lo, top = Unlocked(Unlock(UnlockKind.CARD, draw(st.sampled_from([c.id for c in r.cards])))), 0, 1
    v = draw(st.integers(lo, top))
    if draw(st.booleans()):
        return AtLeast(subj, v, draw(st.integers(lo, v)))
    return AtMost(subj, v, draw(st.integers(v, top)))


@st.composite
def order_verb_st(draw: Draw, r: Rules) -> SwitchMix | TapCard:
    if draw(st.booleans()):
        return SwitchMix(draw(st.sampled_from(MIXES)))
    return TapCard(draw(st.sampled_from([c.id for c in r.cards])))  # a locked one is planning ahead


@st.composite
def mix_st(draw: Draw, r: Rules, mix: MixId) -> Mix:
    remaining = 10_000
    comps: list[CardShare] = []
    for c in draw(st.lists(st.sampled_from(hands_cards(r)), unique=True, max_size=3)) if hands_cards(r) else []:
        share = draw(st.integers(0, remaining))
        remaining -= share
        comps.append(CardShare(c, share))
    return Mix(mix, tuple(comps))


@st.composite
def verb_st(draw: Draw, r: Rules) -> Verb:
    kind = draw(st.sampled_from(["tap", "tap", "tap", "switch", "orders", "queue", "save", "delete"]))
    if kind == "tap":
        return TapCard(draw(st.sampled_from([c.id for c in r.cards])))
    if kind == "switch":
        return SwitchMix(draw(st.sampled_from(MIXES)))
    if kind == "save":
        return SaveMix(draw(mix_st(r, draw(st.sampled_from(MIXES)))))
    if kind == "delete":
        return DeleteMix(draw(st.sampled_from(MIXES)))
    n = draw(st.integers(0, 3))
    if kind == "orders":
        return SetOrders(tuple(Order(draw(condition_st(r)), draw(order_verb_st(r))) for _ in range(n)))
    return SetQueue(tuple(QueueEntry(draw(order_verb_st(r)), draw(condition_st(r))) for _ in range(n)))


@dataclass(frozen=True)
class Scenario:
    rules: Rules
    modifiers: tuple[Modifier, ...]
    steps: tuple[tuple[int, Verb], ...]
    """(seconds after the previous step, verb), applied with decide(); a refused verb only advances."""
    probe: Verb
    """One more verb, for decide-property tests (it may be refused)."""
    offsets: tuple[int, ...]
    """Extra time offsets (seconds after the final save) for sampling."""


def _time_scale(r: Rules) -> int:
    """How much shorter a world's runs are than the default: a tiny firing cap makes a re-tapping order an event every
    second (READY at T + 1), so such a world gets a tenth of the time. The suite has a time budget."""
    return 10 if r.max_firings_per_instant <= 4 else 1


def span(r: Rules, seconds: int) -> int:
    """A test's own stretch of time on top of a scenario's rules, shortened as the scenario's own steps are."""
    return seconds // _time_scale(r)


@st.composite
def scenario_st(draw: Draw, max_firings: int | None = None) -> Scenario:
    r = draw(world_st(max_firings))
    targets: list[Target] = [*(WorkRef(c.id) for c in r.cards), LaneSpeed(HANDS), *(LaneSpeed(x.id) for x in r.lanes)]
    mods = tuple(draw(st.lists(_modifier(targets, "save"), max_size=2)))
    steps: list[tuple[int, Verb]] = [(0, SaveMix(draw(mix_st(r, m)))) for m in MIXES]
    scale = _time_scale(r)
    steps.append((draw(st.integers(0, 2000 // scale)), SwitchMix(MIXES[0])))
    steps.append((draw(st.integers(0, 600 // scale)), TapCard(r.cards[0].id)))
    for _ in range(draw(st.integers(1, 5))):
        steps.append((draw(st.one_of(st.integers(0, 3), st.integers(0, 6000 // scale))), draw(verb_st(r))))
    offsets = tuple(draw(st.lists(st.integers(0, 12_000 // scale), min_size=1, max_size=3)))
    return Scenario(r, mods, tuple(steps), draw(verb_st(r)), offsets)


def try_decide(s: Save, r: Rules, t: int, verb: Verb) -> Save:
    """decide(), except that a verb the engine refuses (a busy lane, a locked or completed card, a mix that cannot be
    saved, switched to or deleted) leaves the save advanced to t."""
    try:
        return decide(s, r, t, verb)
    except InvalidVerbError:
        return advance(s, r, t)


def play(sc: Scenario) -> Save:
    validate_rules(sc.rules)
    s = new_save(sc.rules, sc.modifiers)
    for dt, verb in sc.steps:
        s = try_decide(s, sc.rules, s.time + dt, verb)
    return s


def play_logged(sc: Scenario) -> tuple[Save, list[Save], tuple[Line, ...]]:
    """play() through the logged entry points: the final save, the save after each step, and every line since time 0."""
    validate_rules(sc.rules)
    s = new_save(sc.rules, sc.modifiers)
    saves = [s]
    lines: tuple[Line, ...] = ()
    for dt, verb in sc.steps:
        t = s.time + dt
        try:
            step = decide_logged(s, sc.rules, t, verb)
        except InvalidVerbError:
            step = advance_logged(s, sc.rules, t)
        s = step.save
        lines += step.lines
        saves.append(s)
    return s, saves, lines


def timeline(save: Save, r: Rules, offsets: tuple[int, ...], events: int = 4) -> list[Save]:
    """Saves at the save's time, the next few event times and +/- 1 second, and the offsets: each carried forward
    from the previous one (invariant 1 makes that equal to advancing from `save`; test_cards_split checks it)."""
    ts = {save.time}
    s = save
    for _ in range(events):
        e = next_event(s, r)
        if e is None:
            break
        ts |= {e.time - 1, e.time, e.time + 1}
        s = advance(s, r, e.time)
    ts |= {save.time + o for o in offsets}
    out: list[Save] = []
    s = save
    for t in sorted(t for t in ts if t >= save.time):
        s = advance(s, r, t)
        out.append(s)
    return out


def rule_keys(r: Rules) -> set[str]:
    """Every line key the rules can emit (DESIGN.txt, "Lines"; CardDef.lines, outcomes, chips)."""
    found: set[str] = set()
    for c in r.cards:
        found |= set(c.lines) | set(c.outcome.lines) | set(c.finished.lines)
    for k in r.chips:
        found |= {x for x in (k.on_line, k.off_line) if x}
    for t in r.triggers:
        found |= set(t.outcome.lines)
    return found
