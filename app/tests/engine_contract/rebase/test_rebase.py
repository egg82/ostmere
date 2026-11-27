"""Invariants 47 to 56: a save crossing releases (design/saves-across-releases.txt, part "SAVES ACROSS RELEASES"). The new rules are
generated rules transformed the way content changes them: ids added, renamed (so the old id is gone), work_s changed,
a card moved to another lane, caps raised, declarations reordered.

The renaming helper (`sub`) replaces id strings by value, and the dropping oracle (`named`) reads id strings by value,
so every world here keeps its id strings distinct across kinds, line keys and mix names; the one test about kinds
sharing a string checks its fields by hand."""
import json
from collections.abc import Mapping
from dataclasses import dataclass, fields, is_dataclass, replace
from functools import cache
from typing import cast

import pytest
from hypothesis import given, strategies as st
from hypothesis.strategies import DrawFn

import ashfall_app.engine as engine
from ashfall_app.engine.savefile.codec import to_json
from ashfall_app.engine import (
    BP, FORMAT, HANDS, OLDEST_FORMAT, UPGRADES, ActionId, AfterTime, Amount, AnswerDef, AnswerId, AnswerOffer, AtLeast,
    AtMost, CapRaise, CardCount, OfferDef, OfferId,
    CardDef, CardId, CardShare, ChipDef, ChipId, EntryId, FeatureId, Flow, FlowKind, IdKind,
    InvalidVerbError, LaneDef, LaneState, LaneId, LaneSpeed, LineKey, Mix, MixId, Modifier, ModifierKind, NoteId, Order,
    Outcome,
    PacingCurve, QueueEntry, RateRef, Rules, Running, Save, SaveMix, SetOrders, SetQueue,
    SkillDef, SkillId, SkillLevel, SourceId, StandingDef, StateFormatError, StoreCap, StoreDef, StoreId, StoreValue,
    SubMix, SwitchMix, TapCard, TriggerDef, TriggerId, Unlock, UnlockKind, Unlocked, WorkRef, advance, decide, decode,
    encode, new_save, rebase, rebase_logged, unlock_key, validate_rules,
)
from contract_gen import Q, Scenario, few, play, scenario_st
from join_world import joined_save, left_save

type Json = None | bool | int | str | list[Json] | dict[str, Json]


# ---- the renaming oracle and readers --------------------------------------------------------------------------

def _sub(v: object, ids: Mapping[str, str]) -> object:
    if isinstance(v, str):
        return ids.get(v, v)
    if isinstance(v, tuple):
        return tuple(_sub(x, ids) for x in cast(tuple[object, ...], v))  # cast -- isinstance leaves tuple[Unknown, ...]
    if is_dataclass(v) and not isinstance(v, type):
        return replace(v, **{f.name: _sub(getattr(v, f.name), ids) for f in fields(v)})
    return v


def sub[T](v: T, ids: Mapping[str, str]) -> T:
    """v with every id string in `ids` replaced (rules or save alike); enums, numbers and other strings kept."""
    return cast(T, _sub(v, ids))  # cast -- _sub returns the shape it was given, which a TypeVar cannot say


def named(v: object) -> set[str]:
    """Every id string a part of a save names, as the codec writes it: class tags and a modifier's source (a label)
    left out."""
    return _names(to_json(v))


def _names(v: Json) -> set[str]:
    if isinstance(v, str):
        return {v}
    if isinstance(v, list):
        return {x for item in v for x in _names(item)}
    if isinstance(v, dict):
        return {x for k, item in v.items() if k not in ("@", "source") for x in _names(item)}
    return set()


def kept_orders(s: Save, gone: frozenset[str]) -> tuple[Order, ...]:
    """Step 3's orders, by value: an order whose conditions name a gone id goes, an action naming one is taken out of
    its list, and an order with no action left goes."""
    out: list[Order] = []
    for o in s.orders:
        if named((o.when, o.unless)) & gone:
            continue
        actions = [a for a in (o.then, *o.or_else) if not named(a) & gone]
        if actions:
            out.append(replace(o, then=actions[0], or_else=tuple(actions[1:])))
    return tuple(out)


def store_value(s: Save, store: str) -> int:
    found = [x.segment.start_value for x in s.stores if x.store == store]
    assert len(found) == 1, (store, s.stores)
    return found[0]


def xp_of(s: Save, skill: str) -> int:
    found = [x.xp.start_value for x in s.skills if x.skill == skill]
    assert len(found) == 1, (skill, s.skills)
    return found[0]


def work_of(s: Save, card: str) -> int:
    """A card's work; an absent CardState is all zero."""
    return next((c.work.start_value for c in s.cards if c.card == card), 0)


def raised_of(s: Save, card: str) -> int:
    return next((c.raised for c in s.cards if c.card == card), 0)


def work_s_of(r: Rules, card: str) -> int:
    return next(c.work_s for c in r.cards if c.id == card)


def done(s: Save, r: Rules, card: str) -> int:
    return work_of(s, card) // (work_s_of(r, card) * BP)


def chip_latch(s: Save, r: Rules, chip: str) -> bool:
    return s.chips[[c.id for c in r.chips].index(ChipId(chip))]


def fired(s: Save, r: Rules, trigger: str) -> bool:
    return s.fired[[t.id for t in r.triggers].index(TriggerId(trigger))]


def lane_of(s: Save, lane: str) -> LaneState:
    found = [x for x in s.lanes if x.lane == lane]
    assert len(found) == 1, (lane, s.lanes)
    return found[0]


def rescaled(work: int, w_old: int, w_new: int) -> int:
    """engine/design/ step 5: c = work // (W * BP), rem = work % (W * BP), to c * W' * BP + rem * W' // W."""
    c, rem = divmod(work, w_old * BP)
    return c * w_new * BP + rem * w_new // w_old


def assert_canonical(s: Save, r: Rules) -> None:
    """Step 5's canonical save under the new rules (invariant 9, plus chips, fired and lanes by the new rules)."""
    assert [x.store for x in s.stores] == [d.id for d in r.stores]
    assert [x.skill for x in s.skills] == [d.id for d in r.skills]
    assert [x.lane for x in s.lanes] == [HANDS] + [d.id for d in r.lanes]
    assert len(s.chips) == len(r.chips) and len(s.fired) == len(r.triggers)
    order = {x: i for i, x in enumerate([a.id for a in r.standing] + [c.id for c in r.cards])}
    assert [order[p.runner] for p in s.pauses] == sorted(order[p.runner] for p in s.pauses)
    by_card = {c.id: i for i, c in enumerate(r.cards)}
    assert [by_card[c.card] for c in s.cards] == sorted(by_card[c.card] for c in s.cards)
    assert list(s.unlocked) == sorted(s.unlocked, key=unlock_key)
    assert len(s.latches) == len(s.orders)
    for x in s.stores:
        assert x.segment.start == s.time
    for c in s.cards:
        assert c.work.start == s.time


def assert_nothing_taken(s: Save, r: Rules, s2: Save, r2: Rules, gone: frozenset[str]) -> None:
    """Invariant 49 for every id both rules declare; each gone id named nowhere in s2 (step 3)."""
    assert s2.time == s.time
    for x in s.stores:
        if x.store not in gone:
            assert store_value(s2, x.store) >= x.segment.start_value, x.store
    for k in s.skills:
        if k.skill not in gone:
            assert xp_of(s2, k.skill) >= k.xp.start_value, k.skill
    for c in r.cards:
        if c.id not in gone:
            assert done(s2, r2, c.id) == done(s, r, c.id), c.id
            assert raised_of(s2, c.id) == raised_of(s, c.id), c.id
    assert {u for u in s.unlocked if u.id not in gone} <= set(s2.unlocked)
    for t in r.triggers:
        if fired(s, r, t.id) and t.id not in gone:
            assert fired(s2, r2, t.id), t.id
    assert s2.ended_at == s.ended_at
    assert s2.mixes == tuple(replace(m, components=tuple(c for c in m.components if not named(c) & gone))
                             for m in s.mixes)
    assert s2.orders == kept_orders(s, gone)
    kept = tuple(m for m in s.modifiers if not named(m) & gone)
    assert s2.modifiers[: len(kept)] == kept
    assert not named((s2.orders, s2.queue, s2.mixes, s2.pauses, s2.lanes, s2.modifiers, s2.unlocked)) & gone


# ---- envelope helpers ------------------------------------------------------------------------------------------

def as_obj(v: Json) -> dict[str, Json]:
    assert isinstance(v, dict), f"not a JSON object: {v!r}"
    return v


def as_list(v: Json) -> list[Json]:
    assert isinstance(v, list), f"not a JSON array: {v!r}"
    return v


def envelope(text: str) -> dict[str, Json]:
    loaded: Json = json.loads(text)
    return as_obj(loaded)


def canonical(value: Json) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def strings(v: Json) -> set[str]:
    if isinstance(v, str):
        return {v}
    if isinstance(v, list):
        return {x for item in v for x in strings(item)}
    if isinstance(v, dict):
        return {x for item in v.values() for x in strings(item)}
    return set()


def tagged(v: Json) -> bool:
    if isinstance(v, list):
        return any(tagged(x) for x in v)
    if isinstance(v, dict):
        return "@" in v or any(tagged(x) for x in v.values())
    return False


# ---- generated worlds: an allowed release over contract_gen rules -----------------------------------------------

@dataclass(frozen=True)
class Release:
    rules: Rules
    ids: dict[str, str]
    """Old id string -> new id string, for every id renamed (any kind): the old ones are gone."""
    new_store: StoreDef
    new_skill: SkillId
    new_card: CardId


@st.composite
def release_st(draw: DrawFn, r: Rules, sources: tuple[str, ...], tag: str) -> Release:
    """A content change: rename some stores, cards and skills (the old ids gone) and some sources; change some work_s;
    raise some caps; add a store, a skill and a card; append a curve level; reorder the stores and the cards. The
    generated ids (s0, c0, k0, src0) are distinct strings across kinds, so `sub` is exact."""
    ids: dict[str, str] = {}
    groups: list[list[str]] = [[d.id for d in r.stores], [c.id for c in r.cards], [k.id for k in r.skills], list(sources)]
    for names in groups:
        for old in names:
            if draw(st.booleans()):
                ids[old] = f"{old}_{tag}"
    r2 = sub(r, ids)
    cards = [replace(c, work_s=draw(st.integers(1, 100_000))) if draw(st.booleans()) else c for c in r2.cards]
    stores = [replace(d, cap=d.cap + Q * draw(st.integers(0, 5))) for d in r2.stores]
    new_store = StoreDef(StoreId(f"sn_{tag}"), 5 * Q, draw(st.integers(0, 5 * Q)))
    stores.insert(draw(st.integers(0, len(stores))), new_store)
    new_card = CardDef(CardId(f"cn_{tag}"), draw(st.integers(1, 1000)))
    cards.insert(draw(st.integers(0, len(cards))), new_card)
    new_skill = SkillId(f"kn_{tag}")
    th = r2.curve.thresholds
    out = replace(
        r2, stores=tuple(draw(st.permutations(stores))), cards=tuple(draw(st.permutations(cards))),
        skills=r2.skills + (SkillDef(new_skill),), curve=PacingCurve(th + (th[-1] + draw(st.integers(1, Q)),)),
    )
    return Release(out, ids, new_store, new_skill, new_card.id)


def gone_of(rel: Release, sources: tuple[str, ...] = ()) -> frozenset[str]:
    """The ids the release renamed, its sources left out (a source is a label: never dropped)."""
    return frozenset(rel.ids) - set(sources)


def sources_of(s: Save) -> tuple[str, ...]:
    return tuple(dict.fromkeys(m.source for m in s.modifiers))


@st.composite
def world_st(draw: DrawFn) -> tuple[Scenario, Save, Release]:
    """A played contract_gen scenario, advanced a little past its last verb, and one release over its rules."""
    sc = draw(scenario_st())
    s = play(sc)
    s = advance(s, sc.rules, s.time + sc.offsets[0])
    return sc, s, draw(release_st(sc.rules, sources_of(s), "a"))


# ---- a rich world: every kind of id a save can name ------------------------------------------------------------

X, Y, Z = StoreId("x"), StoreId("y"), StoreId("z")
EMBER = StoreId("ember")
K = SkillId("k0")
FIRE = ActionId("fire")
RACK = LaneId("rack")
G, H, P, R, QC, RZ, W = (CardId(c) for c in ("g", "h", "p", "r", "q", "rz", "w"))
COLD = ChipId("cold")
T0, T1, T2 = TriggerId("t0"), TriggerId("t1"), TriggerId("t2")
JOURNAL, LEDGER = FeatureId("journal"), FeatureId("ledger")
PAGE, NOTE = EntryId("page"), NoteId("note1")
OF1, AN1, AN2 = OfferId("offer1"), AnswerId("ans1"), AnswerId("ans2")
INNER, OUTER = MixId("inner"), MixId("outer")


def mod(target: RateRef | WorkRef | LaneSpeed | StoreCap, kind: ModifierKind, bp: int, source: str) -> Modifier:
    return Modifier(target, kind, bp, SourceId(source))


def rich_rules() -> Rules:
    """Standing action (dry on ember from the start, so a Pause names it), two lanes, capped and uncapped cards, a
    chip, three triggers (one retiring a card, one showing an offer), an offer, features, an opening. Every id string is
    distinct from every other id, line key and mix name."""
    return Rules(
        stores=(StoreDef(X, 50 * Q, 10 * Q), StoreDef(Y, 50 * Q, 2 * Q), StoreDef(Z, 50 * Q, 0),
                StoreDef(EMBER, 5 * Q, 0)),
        skills=(SkillDef(K),),
        standing=(StandingDef(FIRE, costs=(Flow(Y, 300), Flow(EMBER, 100))),),
        curve=PacingCurve((Q // 2, 2 * Q, 6 * Q)),
        max_firings_per_instant=50,
        lanes=(LaneDef(RACK),),
        cards=(
            CardDef(G, 600, skill=K, xp_per_hour=2000, makes=(Flow(X, 3000),), costs=(Flow(Y, 500),),
                    lines=(LineKey("g.tap"),)),
            CardDef(H, 900, skill=K, xp_per_hour=1000, inputs=(Amount(X, Q),), outcome=Outcome(stores=(Amount(Z, Q),))),
            CardDef(P, 400, inputs=(Amount(X, Q),), cap=3, lines=(LineKey("p.1"), LineKey("p.2"), LineKey("p.3")),
                    outcome=Outcome(stores=(Amount(Z, Q),),
                                    unlocks=(Unlock(UnlockKind.CARD, QC), Unlock(UnlockKind.FEATURE, JOURNAL),
                                             Unlock(UnlockKind.ENTRY, PAGE), Unlock(UnlockKind.NOTE, NOTE)),
                                    modifiers=(mod(WorkRef(R), ModifierKind.MUL_BP, 15_000, "p.out"),), starts=(R,),
                                    lines=(LineKey("p.done"),)),
                    finished=Outcome(lines=(LineKey("p.fin"),))),
            CardDef(R, 1300, lane=RACK, outcome=Outcome(stores=(Amount(Y, Q),)), lines=(LineKey("r.done"),)),
            CardDef(QC, 400, cap=1, requires=(AtLeast(SkillLevel(K), 2, 2),)),
            CardDef(RZ, 500, lane=RACK, cap=2, outcome=Outcome(raises=(CapRaise(P, 1),))),
            CardDef(W, 600, skill=K, xp_per_hour=500, lines=(LineKey("w.done"),)),
        ),
        chips=(ChipDef(COLD, AtLeast(StoreValue(Z), 2 * Q, Q),
                       (mod(LaneSpeed(HANDS), ModifierKind.MUL_BP, 5000, "cold"),),
                       LineKey("cold.on"), (LineKey("cold.off"),)),),
        triggers=(
            TriggerDef(T0, AtLeast(CardCount(P), 1, 1),
                       Outcome(unlocks=(Unlock(UnlockKind.CHIP, COLD),), lines=(LineKey("t0.fired"),))),
            TriggerDef(T1, AtLeast(Unlocked(Unlock(UnlockKind.FEATURE, JOURNAL)), 1, 1),
                       Outcome(stores=(Amount(Y, Q),), unlocks=(Unlock(UnlockKind.RETIRED, QC),),
                               lines=(LineKey("t1.fired"),))),
            TriggerDef(T2, AfterTime(200), Outcome(unlocks=(Unlock(UnlockKind.OFFER, OF1),), lines=(LineKey("t2.fired"),))),
        ),
        offers=(OfferDef(OF1, (AnswerDef(AN1, Outcome(lines=(LineKey("ans1.given"),))), AnswerDef(AN2))),),
        opening=(Unlock(UnlockKind.STORE, X), Unlock(UnlockKind.STORE, Y), Unlock(UnlockKind.STORE, Z),
                 Unlock(UnlockKind.SKILL, K), Unlock(UnlockKind.ACTION, FIRE), Unlock(UnlockKind.FEATURE, LEDGER),
                 Unlock(UnlockKind.CARD, G), Unlock(UnlockKind.CARD, H), Unlock(UnlockKind.CARD, P),
                 Unlock(UnlockKind.CARD, R), Unlock(UnlockKind.CARD, RZ), Unlock(UnlockKind.CARD, W)),
    )


def rich_orders() -> SetOrders:
    """Every condition subject kind (a standing runner and a feature unlock included) and both order verbs."""
    return SetOrders((
        Order(AtLeast(StoreValue(Y), 40 * Q, 30 * Q), SwitchMix(INNER)),
        Order(AtLeast(SkillLevel(K), 4, 4), TapCard(P)),
        Order(AtMost(CardCount(R), 0, 0), TapCard(R)),
        Order(AtLeast(Unlocked(Unlock(UnlockKind.FEATURE, LEDGER)), 1, 1), TapCard(RZ)),
        Order(AtMost(Running(FIRE), 0, 0), TapCard(R)),
        Order(AtLeast(Unlocked(Unlock(UnlockKind.CARD, QC)), 1, 1), SwitchMix(INNER)),
        Order(AfterTime(10**8), SwitchMix(OUTER)),
    ))


def try_decide(s: Save, r: Rules, t: int, verb: TapCard) -> Save:
    try:
        return decide(s, r, t, verb)
    except InvalidVerbError:
        return advance(s, r, t)


@cache
def rich_saves() -> tuple[Save, ...]:
    """A run through every kind of state: nested mix, orders and a queue, taps on both lanes, a capped
    card part done and raised, a fired trigger, a chip, feature, card and retired unlocks, an offer shown and answered,
    outcome modifiers."""
    r = rich_rules()
    s = new_save(r, (mod(RateRef(G, FlowKind.MAKE, X), ModifierKind.ADD_BP, 1500, "tool"),
                     mod(LaneSpeed(RACK), ModifierKind.MUL_BP, 12_000, "rackmod"),
                     mod(StoreCap(Z), ModifierKind.ADD_BP, 2000, "shelf"),
                     mod(RateRef(FIRE, FlowKind.COST, Y), ModifierKind.MUL_BP, 9000, "damp")))
    s = decide(s, r, 0, SaveMix(Mix(INNER, (CardShare(G, 6000), CardShare(H, 4000)))))
    s = decide(s, r, 0, SaveMix(Mix(OUTER, (SubMix(INNER, 5000), CardShare(P, 2000)))))
    s = decide(s, r, 0, SwitchMix(OUTER))
    s = decide(s, r, 10, rich_orders())
    s = decide(s, r, 10, SetQueue((QueueEntry(SwitchMix(INNER), AtLeast(StoreValue(Z), 3 * Q, 3 * Q)),
                                   QueueEntry(TapCard(RZ), AfterTime(10**8)))))
    out = [s]
    for t in (20, 300, 1000, 1500, 3000, 5000, 9000):
        s = try_decide(s, r, t, TapCard(P)) if t in (20, 1000, 3000) else advance(s, r, t)
        s = decide(s, r, t, AnswerOffer(OF1, AN1)) if t == 1500 else s
        out.append(s)
    return tuple(out)


RICH_IDS: dict[str, tuple[IdKind | None, str]] = {
    "x": (IdKind.STORE, "x_v2"), "ember": (IdKind.STORE, "ember_v2"), "y": (IdKind.STORE, "y_v2"),
    "z": (IdKind.STORE, "z_v2"),
    "k0": (IdKind.SKILL, "k0_v2"), "fire": (IdKind.STANDING, "fire_v2"), "rack": (IdKind.LANE, "rack_v2"),
    "g": (IdKind.CARD, "g_v2"), "h": (IdKind.CARD, "h_v2"), "p": (IdKind.CARD, "p_v2"), "r": (IdKind.CARD, "r_v2"),
    "q": (IdKind.CARD, "q_v2"), "rz": (IdKind.CARD, "rz_v2"), "w": (IdKind.CARD, "w_v2"),
    "cold": (IdKind.CHIP, "cold_v2"), "t0": (IdKind.TRIGGER, "t0_v2"), "t1": (IdKind.TRIGGER, "t1_v2"),
    "t2": (IdKind.TRIGGER, "t2_v2"), "offer1": (IdKind.OFFER, "offer1_v2"), "ans1": (IdKind.ANSWER, "ans1_v2"),
    "ans2": (IdKind.ANSWER, "ans2_v2"),
    "journal": (IdKind.FEATURE, "journal_v2"), "ledger": (IdKind.FEATURE, "ledger_v2"),
    "page": (None, "page_v2"), "note1": (None, "note1_v2"),
    "tool": (None, "tool_v2"), "rackmod": (None, "rackmod_v2"), "shelf": (None, "shelf_v2"), "damp": (None, "damp_v2"),
    "p.out": (None, "p.out_v2"),
}
"""Every id of the rich world, its kind and a new name (the chip's effect source is its id, so renaming the chip in the
rules renames that source with it, as validation requires). None: a kind no manifest declares (a journal page or note,
a modifier's source), never dropped."""
DECLARED = {old: kind for old, (kind, _) in RICH_IDS.items() if kind is not None}

SPARE = StoreDef(StoreId("spare"), Q, 0)


def plus_spare(r: Rules) -> Rules:
    """r with one unused store added: other rules (a new digest), the same behaviour."""
    return replace(r, stores=r.stores + (SPARE,))


# ---- 47, 48: identity and idempotence --------------------------------------------------------------------------

@few(10)
@given(w=world_st())
def test_rebase_under_the_same_rules_is_the_save(w: tuple[Scenario, Save, Release]):
    """Invariant 47: rebase(encode(s, r), r) == s, with no lines and nothing dropped."""
    sc, s, _ = w
    text = encode(s, sc.rules)
    assert rebase(text, sc.rules) == s
    step = rebase_logged(text, sc.rules)
    assert step.save == s and step.lines == () and step.dropped == ()


@few(10)
@given(w=world_st())
def test_rebasing_twice_is_rebasing_once(w: tuple[Scenario, Save, Release]):
    """Invariant 48: for s2 = rebase(x, r2), rebase(encode(s2, r2), r2) == s2."""
    sc, s, rel = w
    s2 = rebase(encode(s, sc.rules), rel.rules)
    assert rebase(encode(s2, rel.rules), rel.rules) == s2


def test_identity_on_a_rich_save():
    """Invariant 47 over every kind of state (chips, fired, lanes, unlocks, raised caps)."""
    r = rich_rules()
    for s in rich_saves():
        assert rebase(encode(s, r), r) == s


# ---- 49, 50, 51: a content change over generated worlds ---------------------------------------------------------

@few(15)
@given(w=world_st())
def test_a_change_takes_back_nothing_earned_under_a_kept_id(w: tuple[Scenario, Save, Release]):
    """Invariant 49 under renames (the old ids dropped), retuned work_s, raised caps, added ids, an appended level and
    reordered stores and cards; the result is canonical under the new rules (step 4)."""
    sc, s, rel = w
    validate_rules(rel.rules)
    s2 = rebase(encode(s, sc.rules), rel.rules)
    assert_canonical(s2, rel.rules)
    assert_nothing_taken(s, sc.rules, s2, rel.rules, gone_of(rel, sources_of(s)))


@few(15)
@given(w=world_st())
def test_new_stores_and_skills_start_at_their_defaults(w: tuple[Scenario, Save, Release]):
    """Invariant 50: a new store holds its initial value, a new skill XP 0, a new card no work (no outcome lands at a
    contract_gen world's rebase instant)."""
    sc, s, rel = w
    s2 = rebase(encode(s, sc.rules), rel.rules)
    assert store_value(s2, rel.new_store.id) == rel.new_store.initial
    assert xp_of(s2, rel.new_skill) == 0
    assert work_of(s2, rel.new_card) == 0


@few(15)
@given(w=world_st())
def test_a_work_s_change_keeps_completions_and_rescales_the_bar(w: tuple[Scenario, Save, Release]):
    """Invariant 51: work c * W' * BP + rem * W' // W, so CardCount is unchanged; unchanged work_s keeps the work; a
    renamed card is a new one, with no work."""
    sc, s, rel = w
    s2 = rebase(encode(s, sc.rules), rel.rules)
    for c in sc.rules.cards:
        new = rel.ids.get(c.id, c.id)
        expect = 0 if c.id in rel.ids else rescaled(work_of(s, c.id), c.work_s, work_s_of(rel.rules, new))
        assert work_of(s2, new) == expect, (c.id, c.work_s, work_s_of(rel.rules, new))


@few(10)
@given(w=world_st())
def test_a_raised_store_cap_keeps_every_value(w: tuple[Scenario, Save, Release]):
    """Step 4: each kept store at its value (only a lowered cap could clamp, and this change raises them); a renamed
    one is a new store, at its initial value."""
    sc, s, rel = w
    s2 = rebase(encode(s, sc.rules), rel.rules)
    initial: dict[str, int] = {d.id: d.initial for d in rel.rules.stores}
    for x in s.stores:
        new = rel.ids.get(x.store, x.store)
        assert store_value(s2, new) == (initial[new] if x.store in rel.ids else x.segment.start_value)


# ---- 54: composition across skipped releases -------------------------------------------------------------------

@few(10)
@given(data=st.data())
def test_a_save_skipping_a_change_rebases_straight_to_the_latest(data: st.DataObject):
    """Invariant 54: rebase(encode(s, r), r3) succeeds as rebasing through r2 does, and 49 holds between s and both
    results for every id all three rules declare. The two results need not be equal (engine/design/ 54)."""
    sc, s, rel1 = data.draw(world_st())
    s_mid = rebase(encode(s, sc.rules), rel1.rules)
    rel2 = data.draw(release_st(rel1.rules, sources_of(s_mid), "b"))
    gone = gone_of(rel1, sources_of(s)) | gone_of(rel2, sources_of(s_mid))
    through = rebase(encode(s_mid, rel1.rules), rel2.rules)
    direct = rebase(encode(s, sc.rules), rel2.rules)
    assert_canonical(direct, rel2.rules)
    assert_nothing_taken(s, sc.rules, direct, rel2.rules, gone)
    assert_nothing_taken(s, sc.rules, through, rel2.rules, gone)


# ---- 53: ids the new rules lack are dropped --------------------------------------------------------------------

@few(10)
@given(data=st.data())
def test_a_declared_id_the_new_rules_lack_is_dropped_and_counted(data: st.DataObject):
    """Invariant 53 over generated worlds: a store, card or skill gone from the new rules is named nowhere in the
    result, and rebase_logged counts it under its kind."""
    sc, s, _ = data.draw(world_st())
    r = sc.rules
    kind, old = data.draw(st.sampled_from(
        [(IdKind.STORE, str(d.id)) for d in r.stores] + [(IdKind.CARD, str(c.id)) for c in r.cards]
        + [(IdKind.SKILL, str(k.id)) for k in r.skills]))
    r2 = sub(r, {old: f"{old}_gone"})
    step = rebase_logged(encode(s, r), r2)
    assert step.dropped == ((kind, 1),)
    assert_nothing_taken(s, r, step.save, r2, frozenset({old}))


@pytest.mark.parametrize("old", sorted(DECLARED))
def test_every_declared_kind_is_dropped_when_its_id_is_gone(old: str):
    """Invariant 53 for every kind the manifest declares (store, skill, standing, lane, card, chip, trigger, feature,
    offer, answer), on a save that holds every kind of state: named nowhere after, counted, and the save runs on."""
    r = rich_rules()
    s = rich_saves()[-1]
    r2 = sub(r, {old: f"{old}_gone"})
    step = rebase_logged(encode(s, r), r2)
    moved = ((IdKind.ANSWER, 2),) if old == "offer1" else ()   # its answers now stand under offer1_gone: gone too
    assert step.dropped == ((DECLARED[old], 1), *moved)
    assert not named((step.save.orders, step.save.queue, step.save.mixes, step.save.pauses, step.save.lanes,
                      step.save.modifiers, step.save.unlocked)) & {old}
    advance(step.save, r2, step.save.time + 3600)


def test_a_source_is_a_label_and_is_never_dropped():
    """Step 3: a modifier's source is a label: gone from the rules, it stays on the save's modifiers as it is."""
    r = rich_rules()
    s = rich_saves()[-1]
    s2 = rebase(encode(s, r), sub(plus_spare(r), {"p.out": "p.out_gone"}))
    assert [m.source for m in s2.modifiers[: len(s.modifiers)]] == [m.source for m in s.modifiers]


# ---- step 3: drops applied everywhere, by kind -------------------------------------------------------------------

def test_the_rich_world_holds_every_kind_of_state():
    """The fixture check: the saves below do hold what the drop tests claim to cover."""
    saves = rich_saves()
    kinds = {u.kind for s in saves for u in s.unlocked} | {u.kind for s in (joined_save(), left_save()) for u in s.unlocked}
    assert kinds == set(UnlockKind)   # the rich world has no ruled lane: the join fixtures supply JOINED and LEFT
    assert any(any(s.fired) for s in saves) and any(any(s.chips) for s in saves)
    assert any(lane_of(s, RACK).card is not None for s in saves)
    assert any(raised_of(s, P) > 0 for s in saves) and any(s.pauses for s in saves)
    assert any(m.source == "p.out" for s in saves for m in s.modifiers)


def test_rules_lacking_every_id_drop_it_everywhere_in_the_save():
    """Step 3: every id of every kind gone (stores, skills, standing, cards, lanes, chips, triggers, features, offers,
    answers) is named nowhere in the result: not in pauses, lanes, mixes (CardShare), orders' conditions and verbs, the
    queue, the unlock set or modifiers' targets; stores, skills, chips and fired are the new rules'. Mix ids are the
    player's and stay. Each kind is counted."""
    r = plus_spare(rich_rules())
    ids = {old: new for old, (_, new) in RICH_IDS.items()}
    r2 = sub(r, ids)
    validate_rules(r2)
    counts: dict[IdKind, int] = {}
    for kind in DECLARED.values():
        counts[kind] = counts.get(kind, 0) + 1
    for s in rich_saves()[1:]:
        step = rebase_logged(encode(s, rich_rules()), r2)
        assert not named((step.save.orders, step.save.queue, step.save.mixes, step.save.pauses, step.save.lanes,
                          step.save.modifiers, step.save.unlocked)) & set(DECLARED)
        assert [m.id for m in step.save.mixes] == [m.id for m in s.mixes]
        assert dict(step.dropped) == counts
        assert_canonical(step.save, r2)


def test_a_gone_store_leaves_a_card_of_the_same_id_alone():
    """Step 3 reads each id by its kind: a store and a card sharing the id string `dup`; the store gone takes the
    modifier aimed at its rate (RateRef's store), never the card (CardShare, CardState)."""
    dup = "dup"
    r = Rules((StoreDef(StoreId(dup), 10 * Q),), (SkillDef(K),), (), PacingCurve((Q,)),
              cards=(CardDef(CardId(dup), 60, makes=(Flow(StoreId(dup), 1000),)),))
    ref = RateRef(CardId(dup), FlowKind.MAKE, StoreId(dup))
    s = new_save(r, (mod(ref, ModifierKind.ADD_BP, 100, dup),))
    s = decide(s, r, 0, SaveMix(Mix(MixId("m0"), (CardShare(CardId(dup), BP),))))
    s = decide(s, r, 0, SwitchMix(MixId("m0")))
    s = advance(s, r, 30)
    r2 = replace(r, stores=(StoreDef(StoreId("dup_s"), 10 * Q),),
                 cards=(CardDef(CardId(dup), 60, makes=(Flow(StoreId("dup_s"), 1000),)),))
    step = rebase_logged(encode(s, r), r2)
    s2 = step.save
    assert [x.store for x in s2.stores] == ["dup_s"] and step.dropped == ((IdKind.STORE, 1),)
    assert work_of(s2, dup) == work_of(s, dup) > 0
    assert s2.mixes == s.mixes
    assert s2.modifiers == ()


def standing_world() -> tuple[Rules, Save]:
    r = Rules((StoreDef(X, 10 * Q, 5 * Q),), (SkillDef(K),), (StandingDef(FIRE, costs=(Flow(X, 100),)),),
              PacingCurve((Q,)), opening=(Unlock(UnlockKind.ACTION, FIRE), Unlock(UnlockKind.STORE, X)))
    s = new_save(r, (mod(RateRef(FIRE, FlowKind.COST, X), ModifierKind.MUL_BP, 9000, "damp"),))
    s = decide(s, r, 5, SetOrders((Order(AtMost(Running(FIRE), 0, 0), TapCard(CardId("ghost"))),)))
    return r, s


def test_a_gone_standing_action_takes_what_names_it():
    """Step 3: a standing action gone takes the modifier aimed at its rate, the order watching it run and its ACTION
    unlock; under rules that keep it (the control) each stays."""
    r, s = standing_world()
    kept = rebase(encode(s, r), plus_spare(r))
    assert kept.modifiers == s.modifiers and kept.orders == s.orders and kept.unlocked == s.unlocked
    step = rebase_logged(encode(s, r), sub(plus_spare(r), {"fire": "fire_v2"}))
    assert step.save.modifiers == () and step.save.orders == ()
    assert Unlock(UnlockKind.ACTION, FIRE) not in step.save.unlocked and step.dropped == ((IdKind.STANDING, 1),)


def test_an_id_the_manifest_does_not_declare_passes_through():
    """Step 3: an order or queue entry naming a card no rules have keeps it as it is, while another card goes."""
    r = Rules((StoreDef(X, 10 * Q),), (SkillDef(K),), (), PacingCurve((Q,)), cards=(CardDef(W, 60),))
    ghost = TapCard(CardId("ghost"))
    s = new_save(r)
    s = decide(s, r, 0, SetOrders((Order(AfterTime(10**9), ghost),)))
    s = decide(s, r, 0, SetQueue((QueueEntry(ghost, AfterTime(10**9)),)))
    s2 = rebase(encode(s, r), sub(r, {"w": "w_v2"}))
    assert s2.orders == s.orders and s2.queue == s.queue


# ---- 50 and step 6: new content appears, earned content stays ----------------------------------------------------

SALT, ASH = StoreId("salt"), StoreId("ash")
WARM, CHILL = ChipId("warm"), ChipId("chill")
T8, T9 = TriggerId("t8"), TriggerId("t9")


def with_new_content(r: Rules) -> Rules:
    """New stores, a skill, chips and triggers, the new chips and triggers declared first so every old position moves:
    t9 and warm already true (t9 lands ash and unlocks warm), t8 and chill never true."""
    always = AtLeast(StoreValue(X), 0, 0)
    never = AtLeast(StoreValue(SALT), 10 * Q, 10 * Q)
    return replace(
        r,
        stores=(StoreDef(SALT, 10 * Q, 3 * Q), StoreDef(ASH, 10 * Q, 0)) + r.stores,
        skills=(SkillDef(SkillId("k9")),) + r.skills,
        chips=(ChipDef(WARM, always, on_line=LineKey("warm.on")), ChipDef(CHILL, never)) + r.chips,
        triggers=(TriggerDef(T8, never, Outcome(lines=(LineKey("t8.fired"),))),
                  TriggerDef(T9, always, Outcome(stores=(Amount(ASH, Q),), unlocks=(Unlock(UnlockKind.CHIP, WARM),),
                                                 lines=(LineKey("t9.fired"),)))) + r.triggers,
    )


@pytest.mark.parametrize("i", [1, 4, 7])
def test_new_content_starts_at_defaults_and_what_is_already_true_lands_once_at_the_saves_time(i: int):
    """Invariant 50 and step 6: a new store at its initial value unless an outcome at the rebase instant adds to it
    (salt 3, ash 0 + 1), a new skill at XP 0, a new trigger already true fired with its outcome landed once and its
    line emitted, a new chip already true latched and its on line after the outcome that unlocked it, the false ones
    unlatched and unfired; old chips and triggers keep their state by id though every position moved."""
    r = rich_rules()
    s = rich_saves()[i]
    r2 = with_new_content(r)
    validate_rules(r2)
    step = rebase_logged(encode(s, r), r2)
    s2 = step.save
    assert store_value(s2, SALT) == 3 * Q and store_value(s2, ASH) == Q
    assert xp_of(s2, "k9") == 0
    assert fired(s2, r2, T9) and not fired(s2, r2, T8)
    assert chip_latch(s2, r2, WARM) and not chip_latch(s2, r2, CHILL)
    assert Unlock(UnlockKind.CHIP, WARM) in s2.unlocked
    for t in (T0, T1):
        assert fired(s2, r2, t) == fired(s, r, t)
    assert chip_latch(s2, r2, COLD) == chip_latch(s, r, COLD)
    keys: list[str] = [ln.key for ln in step.lines]
    assert keys.count("t9.fired") == 1 and keys.count("warm.on") == 1
    assert keys.index("t9.fired") < keys.index("warm.on")
    assert "t8.fired" not in keys and "t0.fired" not in keys and "t1.fired" not in keys


def test_a_fired_trigger_stays_fired_through_a_retune_and_a_renamed_one_is_new():
    """Step 6: t1, fired in the save and given another condition that holds, is fired in the result, its outcome (one
    y, a retirement) does not land again and its line is not emitted. Renamed, it is a trigger the save never fired:
    it fires at the rebase instant and its line is emitted (the old id is dropped)."""
    r = rich_rules()
    s = next(x for x in rich_saves() if fired(x, r, T1))
    retuned = replace(r.triggers[1], when=AtLeast(StoreValue(X), 0, 0))
    r2 = replace(r, triggers=(retuned, r.triggers[0], *r.triggers[2:]))
    step = rebase_logged(encode(s, r), r2)
    assert fired(step.save, r2, T1) and fired(step.save, r2, T0) == fired(s, r, T0)
    assert store_value(step.save, Y) == store_value(s, Y)
    assert "t1.fired" not in [ln.key for ln in step.lines]
    r3 = replace(r2, triggers=(replace(retuned, id=TriggerId("t1_v2")), *r2.triggers[1:]))
    renamed = rebase_logged(encode(s, r), r3)
    assert fired(renamed.save, r3, "t1_v2") and "t1.fired" in [ln.key for ln in renamed.lines]


# ---- 51, 52: work_s and lanes, by example ----------------------------------------------------------------------

def mixed_world(seconds: int) -> tuple[Rules, Save]:
    """Card w (work_s 600, 3 XP/h) alone in the running mix at 100% for `seconds`."""
    r = Rules((StoreDef(X, 10 * Q),), (SkillDef(K),), (), PacingCurve((Q, 10 * Q)),
              cards=(CardDef(W, 600, skill=K, xp_per_hour=3000),))
    s = decide(new_save(r), r, 0, SaveMix(Mix(MixId("m0"), (CardShare(W, BP),))))
    s = decide(s, r, 0, SwitchMix(MixId("m0")))
    return r, advance(s, r, seconds)


@pytest.mark.parametrize(("w_new", "expect"), [(600, 9_010_000), (7, 105_116), (1000, 15_016_666), (1, 15_016)])
def test_a_work_s_change_rescales_a_part_done_bar(w_new: int, expect: int):
    """Invariant 51 by hand: 901 s at full speed is work 9_010_000 = 1 completion of 600 s and 3_010_000 over; under
    W' the work is W' * BP + 3_010_000 * W' // 600, rounded down, and the count stays 1."""
    r, s = mixed_world(901)
    assert work_of(s, W) == 9_010_000
    r2 = replace(r, cards=(replace(r.cards[0], work_s=w_new),))
    s2 = rebase(encode(s, r), plus_spare(r2))
    assert work_of(s2, W) == expect
    assert done(s2, r2, W) == 1


def lanes_world() -> Rules:
    """Card w ready on HANDS, lane rack."""
    return Rules((StoreDef(X, 10 * Q),), (SkillDef(K),), (), PacingCurve((Q,)), lanes=(LaneDef(RACK),),
                 cards=(CardDef(W, 600, lines=(LineKey("w.done"),)),))


def test_a_card_moved_to_another_lane_frees_its_lane_and_keeps_its_work():
    """Invariant 52 and step 5: HANDS holding w's tap when the new rules put that card on the rack is free in the
    result, as an interrupt: the work is kept, nothing lands, and the rack does not take it."""
    r = lanes_world()
    s = decide(new_save(r), r, 0, TapCard(W))
    s = advance(s, r, 250)
    assert lane_of(s, HANDS).card == W
    r2 = replace(r, cards=tuple(replace(c, lane=RACK) if c.id == W else c for c in r.cards))
    step = rebase_logged(encode(s, r), r2)
    assert lane_of(step.save, HANDS).card is None and lane_of(step.save, RACK).card is None
    assert work_of(step.save, W) == work_of(s, W)
    assert step.lines == ()


def test_a_lane_keeps_its_tap_when_its_card_stays():
    """The control for 52: the same tap under rules that only add a store keeps HANDS busy with w."""
    r = lanes_world()
    s = advance(decide(new_save(r), r, 0, TapCard(W)), r, 250)
    s2 = rebase(encode(s, r), plus_spare(r))
    assert lane_of(s2, HANDS).card == W and work_of(s2, W) == work_of(s, W)


# ---- step 5: clamping (reachable only by changes the lock forbids) ------------------------------------------------

def test_a_value_above_a_lowered_cap_is_clamped_under_the_saves_stack():
    """Step 5: a store above its lowered cap is clamped to the cap under the save's stack; a StoreCap entry that
    doubles the cap keeps the value."""
    r = Rules((StoreDef(X, 10 * Q, 8 * Q),), (SkillDef(K),), (), PacingCurve((Q,)))
    lowered = replace(r, stores=(StoreDef(X, 5 * Q, 0),))
    assert store_value(rebase(encode(new_save(r), r), lowered), X) == 5 * Q
    doubled = new_save(r, (mod(StoreCap(X), ModifierKind.MUL_BP, 2 * BP, "shelf"),))
    assert store_value(rebase(encode(doubled, r), lowered), X) == 8 * Q


def test_xp_is_kept_up_to_the_last_threshold():
    """Step 5: XP kept up to the new curve's last threshold (3 XP over a curve ending at 2 reads 2; an appended
    level keeps all 3)."""
    r, s = mixed_world(3600)
    assert xp_of(s, K) == 3 * Q
    assert xp_of(rebase(encode(s, r), replace(r, curve=PacingCurve((Q, 2 * Q)))), K) == 2 * Q
    assert xp_of(rebase(encode(s, r), replace(r, curve=PacingCurve((Q, 10 * Q, 20 * Q)))), K) == 3 * Q


# ---- 55: logged ------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("i", [0, 3, 7])
def test_rebase_logged_is_rebase_with_lines_at_the_saves_time(i: int):
    """Invariant 55: rebase_logged(x, r2, R).save == rebase(x, r2, R); every line at the save's time, seq from 0."""
    r = rich_rules()
    s = rich_saves()[i]
    r2 = with_new_content(r)
    text = encode(s, r)
    step = rebase_logged(text, r2)
    assert step.save == rebase(text, r2)
    assert step.lines and all(ln.time == s.time for ln in step.lines)
    assert [ln.seq for ln in step.lines] == list(range(len(step.lines)))


# ---- 56 and the envelope: formats, the manifest, the loose decode -----------------------------------------------

def test_the_engine_exports_the_rebase_surface():
    """Rebase: rebase, rebase_logged, IdKind, UPGRADES and OLDEST_FORMAT are exported; IdKind has the ten kinds a
    manifest declares."""
    for name in ("rebase", "rebase_logged", "IdKind", "UPGRADES", "OLDEST_FORMAT"):
        assert name in engine.__all__, name
    assert {k.name for k in IdKind} == {
        "STORE", "SKILL", "STANDING", "CARD", "LANE", "CHIP", "TRIGGER", "FEATURE", "OFFER", "ANSWER"}


def test_upgrades_cover_every_format_a_rebase_reads():
    """Invariant 56: UPGRADES has an entry for every format from OLDEST_FORMAT below FORMAT; FORMAT 4 is the first
    with a manifest, and FORMAT 3 is never rebased."""
    assert 4 <= OLDEST_FORMAT <= FORMAT
    assert set(range(OLDEST_FORMAT, FORMAT)) <= set(UPGRADES)


def test_encode_writes_the_manifest_beside_format_and_digest():
    """Manifest: the envelope is exactly format, rules, manifest and save; the manifest is plain untagged JSON, a
    function of the rules alone, and names every id the rules declare (feature vocabulary included)."""
    r = rich_rules()
    saves = rich_saves()
    envs = [envelope(encode(s, r)) for s in (saves[0], saves[-1])]
    for env in envs:
        assert set(env) == {"format", "rules", "manifest", "save"}
        assert env["format"] == FORMAT
        assert not tagged(env["manifest"])
    assert envs[0]["manifest"] == envs[1]["manifest"]
    assert set(DECLARED) <= strings(envs[0]["manifest"])


def reformat(text: str, edit: str) -> str:
    env = envelope(text)
    if edit == "format below oldest":
        env["format"] = OLDEST_FORMAT - 1
    elif edit == "format 3":
        env["format"] = 3
    elif edit == "format above current":
        env["format"] = FORMAT + 1
    elif edit == "extra envelope key":
        env["extra"] = 1
    elif edit == "no manifest":
        del env["manifest"]
    elif edit == "a chip latch short":
        save = as_obj(env["save"])
        save["chips"] = as_list(save["chips"])[:-1]
    elif edit == "a fired flag extra":
        save = as_obj(env["save"])
        save["fired"] = as_list(save["fired"]) + [False]
    elif edit == "whitespace":
        return text.replace(",", ", ", 1)
    elif edit == "truncated":
        return text[:-1]
    return canonical(env)


LENGTH_EDITS = ["a chip latch short", "a fired flag extra"]
"""Step 2 checks these on the loose decode only: under the same rules the result is decode(text, rules), which accepts
the encoding of any Save (Codec)."""
EDITS = ["format below oldest", "format 3", "format above current", "extra envelope key", "no manifest",
         "a chip latch short", "a fired flag extra", "whitespace", "truncated"]


@pytest.mark.parametrize("edit", EDITS)
def test_a_text_that_is_not_some_envelopes_canonical_text_raises_state_format_error(edit: str):
    """Invariant 56 and step 2: another format outside [OLDEST_FORMAT, FORMAT], an envelope not exactly format, rules,
    manifest and save, chips or fired not as long as the manifest's, or a text not canonical raises StateFormatError,
    under new rules and (but for the lengths) under the same ones. The unedited text is the control."""
    r = rich_rules()
    s = rich_saves()[-1]
    text = encode(s, r)
    r2 = plus_spare(r)
    assert rebase(text, r2) is not None
    bad = reformat(text, edit)
    assert bad != text
    for target in (r2,) if edit in LENGTH_EDITS else (r, r2):
        with pytest.raises(StateFormatError):
            rebase(bad, target)
        with pytest.raises(StateFormatError):
            rebase_logged(bad, target)


def test_the_digest_is_not_checked_by_the_loose_decode():
    """Step 2: the digest is not checked: a text with another digest rebases exactly as the original does."""
    r = rich_rules()
    s = rich_saves()[4]
    text = encode(s, r)
    env = envelope(text)
    env["rules"] = "0" * 64
    r2 = plus_spare(r)
    assert rebase(canonical(env), r2) == rebase(text, r2)


def test_decode_still_refuses_a_save_from_other_rules():
    """Codec: decode refuses a rules change; rebase is the one way a save crosses rules."""
    r = rich_rules()
    s = rich_saves()[-1]
    with pytest.raises(StateFormatError):
        decode(encode(s, r), plus_spare(r))
    assert decode(encode(s, r), r) == s
