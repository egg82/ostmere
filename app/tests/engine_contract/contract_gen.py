"""Strategies and helpers for the engine contract tests. Built from the engine's public types only; nothing here
calls an engine function while generating, so a generated value never depends on the implementation."""
import os
from dataclasses import dataclass
from fractions import Fraction

from hypothesis import settings, strategies as st
from hypothesis.strategies import DrawFn

from ashfall_app.engine import (
    BP, QUANTITY_SCALE, AfterTime, AtLeast, AtMost, CardDef, CardId, CardShare, Flow, FlowKind, Mix, MixId,
    Modifier, ModifierKind, Order, PacingCurve, QueueEntry, RateRef, Rules, SaveMix, SetOrders, SetQueue, SkillDef,
    SkillId, SkillLevel, SourceId, StoreDef, StoreId, StoreValue, SubMix, SwitchMix, Verb, Save,
    advance, decide, new_save, next_event,
)

Q = QUANTITY_SCALE


def few(n: int):
    """Fewer examples for a heavy test on the default profile only; `ci`/`debug` keep their own (larger) count."""
    return settings(max_examples=n) if os.environ.get("HYPOTHESIS_PROFILE", "contract") == "contract" else settings()


SK = SkillId("k0")


def store_id(i: int) -> StoreId:
    return StoreId(f"s{i}")


def card_id(i: int) -> CardId:
    return CardId(f"c{i}")


def mix_id(i: int) -> MixId:
    return MixId(f"m{i}")


def card(i: int, xp: int = 0, makes: tuple[Flow, ...] = (), costs: tuple[Flow, ...] = (), work_s: int = 60) -> CardDef:
    """Card c<i>: continuous lines only (no cap, inputs or outcome), on HANDS, training SK. The mix runs it at a share."""
    return CardDef(card_id(i), work_s, skill=SK, xp_per_hour=xp, makes=makes, costs=costs)


def make_rules(stores: list[StoreDef], cards: list[CardDef], thresholds: tuple[int, ...] = (10**15,),
               max_firings: int = 1000, skills: int = 1) -> Rules:
    return Rules(tuple(stores), tuple(SkillDef(SkillId(f"k{i}")) for i in range(skills)), (), PacingCurve(thresholds),
                 max_firings, cards=tuple(cards))


def flow_refs(rules: Rules) -> list[tuple[RateRef, int]]:
    """Every rate line in the rules with its base per_hour."""
    out: list[tuple[RateRef, int]] = []
    for c in rules.cards:
        out += [(RateRef(c.id, FlowKind.MAKE, f.store), f.per_hour) for f in c.makes]
        out += [(RateRef(c.id, FlowKind.COST, f.store), f.per_hour) for f in c.costs]
        out.append((RateRef(c.id, FlowKind.XP), c.xp_per_hour))
    return out


def exact_rate(base: int, share_bp: int, adds: list[int], muls: list[int], num: int, den: int) -> Fraction:
    """The documented formula, exactly."""
    top = base * share_bp * max(0, BP + sum(adds)) * num
    for m in muls:
        top *= m
    return Fraction(top, BP ** (2 + len(muls)) * den)


def floor_frac(x: Fraction) -> int:
    return x.numerator // x.denominator


def ceil_frac(x: Fraction) -> int:
    return -((-x.numerator) // x.denominator)


# ---- random valid rules -------------------------------------------------------------------------------------

_rate = st.one_of(st.just(0), st.integers(1, 500), st.integers(1, 20_000))


@st.composite
def rules_st(draw: DrawFn, max_firings: int | None = None) -> Rules:
    n_st = draw(st.integers(1, 3))
    n_cd = draw(st.integers(1, 4))
    stores: list[StoreDef] = []
    for i in range(n_st):
        cap = Q * draw(st.integers(1, 20))
        init = draw(st.one_of(st.just(0), st.just(cap), st.integers(0, cap)))
        stores.append(StoreDef(store_id(i), cap, init))
    cards: list[CardDef] = []
    for j in range(n_cd):
        makes: list[Flow] = []
        costs: list[Flow] = []
        for i in range(n_st):
            role = draw(st.sampled_from(["none", "make", "cost"]))
            if role != "none":
                (makes if role == "make" else costs).append(Flow(store_id(i), draw(_rate)))
        xp = draw(st.one_of(st.just(0), st.integers(1, 5000)))
        work_s = draw(st.one_of(st.just(60), st.integers(1, 100_000)))
        cards.append(card(j, xp, tuple(makes), tuple(costs), work_s))
    steps = draw(st.lists(st.integers(1, 3 * Q), min_size=1, max_size=4))
    thresholds = tuple(sum(steps[: k + 1]) for k in range(len(steps)))
    mf = max_firings if max_firings is not None else draw(
        st.one_of(st.just(1000), st.integers(1, 4)))
    return make_rules(stores, cards, thresholds, mf)


@st.composite
def modifiers_st(draw: DrawFn, rules: Rules) -> tuple[Modifier, ...]:
    refs = [r for r, _ in flow_refs(rules)]
    n = draw(st.integers(0, 4))
    out: list[Modifier] = []
    for k in range(n):
        ref = draw(st.sampled_from(refs))
        if draw(st.booleans()):
            out.append(Modifier(ref, ModifierKind.ADD_BP, draw(st.integers(-6000, 6000)), SourceId(f"src{k}")))
        else:
            out.append(Modifier(ref, ModifierKind.MUL_BP, draw(st.integers(0, 30_000)), SourceId(f"src{k}")))
    return tuple(out)


@st.composite
def mix_st(draw: DrawFn, rules: Rules, index: int) -> Mix:
    """Mix m<index>: direct cards, sub-mixes of earlier mixes only (no cycles)."""
    remaining = BP
    comps: list[CardShare | SubMix] = []
    chosen = draw(st.lists(st.sampled_from([c.id for c in rules.cards]), unique=True, max_size=4))
    for a in chosen:
        share = draw(st.integers(0, remaining))
        remaining -= share
        comps.append(CardShare(a, share))
    if index > 0 and draw(st.booleans()):
        share = draw(st.integers(0, remaining))
        comps.append(SubMix(mix_id(draw(st.integers(0, index - 1))), share))
    return Mix(mix_id(index), tuple(comps))


@st.composite
def condition_st(draw: DrawFn, rules: Rules) -> AtLeast | AtMost | AfterTime:
    kind = draw(st.sampled_from(["atleast", "atmost", "after"]))
    if kind == "after":
        return AfterTime(draw(st.integers(0, 60_000)))
    if draw(st.booleans()):
        s = draw(st.sampled_from(rules.stores))
        subj: StoreValue | SkillLevel = StoreValue(s.id)
        top = s.cap
        lo = 0
    else:
        subj = SkillLevel(SK)
        top = len(rules.curve.thresholds) + 1
        lo = 1
    v = draw(st.integers(lo, top))
    if kind == "atleast":
        return AtLeast(subj, v, draw(st.integers(lo, v)))
    return AtMost(subj, v, draw(st.integers(v, top)))


@st.composite
def verb_st(draw: DrawFn, rules: Rules, n_mixes: int) -> Verb:
    ids = [mix_id(i) for i in range(n_mixes)]
    kind = draw(st.sampled_from(["switch", "orders", "queue"]))
    if kind == "switch":
        return SwitchMix(draw(st.sampled_from(ids)))
    if kind == "orders":
        n = draw(st.integers(0, 3))
        return SetOrders(tuple(Order(draw(condition_st(rules)), SwitchMix(draw(st.sampled_from(ids)))) for _ in range(n)))
    n = draw(st.integers(0, 3))
    return SetQueue(tuple(QueueEntry(SwitchMix(draw(st.sampled_from(ids))), draw(condition_st(rules))) for _ in range(n)))


@dataclass(frozen=True)
class Scenario:
    rules: Rules
    modifiers: tuple[Modifier, ...]
    steps: tuple[tuple[int, Verb], ...]
    """(seconds after the previous step, verb), applied with decide()."""
    probe: Verb
    """One more valid verb, for decide-property tests."""
    offsets: tuple[int, ...]
    """Extra time offsets (seconds after the final save) for sampling."""


@st.composite
def scenario_st(draw: DrawFn, max_firings: int | None = None) -> Scenario:
    rules = draw(rules_st(max_firings))
    mods = draw(modifiers_st(rules))
    n_mix = draw(st.integers(1, 3))
    mixes = [draw(mix_st(rules, i)) for i in range(n_mix)]
    steps: list[tuple[int, Verb]] = [(0, SaveMix(m)) for m in mixes]
    steps.append((draw(st.integers(0, 3000)), SwitchMix(mix_id(0))))
    for _ in range(draw(st.integers(0, 4))):
        dt = draw(st.one_of(st.integers(0, 3), st.integers(0, 20_000)))
        steps.append((dt, draw(verb_st(rules, n_mix))))
    probe = draw(verb_st(rules, n_mix))
    offsets = tuple(draw(st.lists(st.integers(0, 60_000), min_size=1, max_size=3)))
    return Scenario(rules, mods, tuple(steps), probe, offsets)


def play(sc: Scenario) -> Save:
    """Run a scenario's verbs through decide() from new_save()."""
    s = new_save(sc.rules, sc.modifiers)
    for dt, verb in sc.steps:
        s = decide(s, sc.rules, s.time + dt, verb)
    return s


def probe_times(save: Save, rules: Rules, offsets: tuple[int, ...], events: int = 3) -> list[int]:
    """Sorted unique times >= save.time: the save's time, the next few event times and +/- 1 second, plus offsets."""
    ts = {save.time}
    s = save
    for _ in range(events):
        e = next_event(s, rules)
        if e is None:
            break
        ts |= {e.time - 1, e.time, e.time + 1}
        s = advance(s, rules, e.time)
    ts |= {save.time + o for o in offsets}
    return sorted(t for t in ts if t >= save.time)
