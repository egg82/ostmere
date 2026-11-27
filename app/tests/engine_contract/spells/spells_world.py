"""Fixtures and a model for the chain contract tests (engine/design/spells.txt, "SPELLS"; api/contract/spells.txt), built
from those two parts and the engine's public names alone.

One side and one wolf threat of `members` members; a standing fight RAID on it, `PER_HR` fights an hour, with the fought,
lost and chained tallies; a hands card SPELL, `work_s` seconds a completion, whose ChainDef names RAID. `model_links` is
the contract's arithmetic written out: due from the tallies, reach from the base and its entries, the firing room."""
from collections.abc import Sequence
from dataclasses import replace
from math import prod

import pytest

from ashfall_app.engine import (
    BP, HANDS, QUANTITY_SCALE as Q, ActionId, AfterTime, CardDef, CardId, CardShare, ChainDef, ChainReach, FightDef,
    LaneDef, LaneId, Line, LineKey, Mix, MixId, Modifier, ModifierKind, Order, PacingCurve, Rules, Save, SaveMix,
    SetOrders, SideDef, SideId, SkillDef, SkillId, SourceId, StandingDef, StoreDef, StoreId, SwitchMix, TapCard,
    ThreatDef, ThreatId, TriggerDef, advance_logged, decide, decide_logged, new_save, per_hour, value,
)

HAND, WOLF = SideId("hand"), ThreatId("wolf")
RAID, SPELL, SPELL2, PLAIN = ActionId("raid"), CardId("spell"), CardId("spell2"), CardId("plain")
FOUGHT, RLOST, CHAINED = (StoreId(n) for n in ("fought", "rlost", "chained"))
BIG = 10**6 * Q
PER_HR = 60                                  # a fight a minute: floor(fought / Q) at second t is t // 60
LANE = LaneId("L")
MIX = MixId("mx")
K = SkillId("k")
LINK_KEYS = tuple(LineKey(f"link{i}") for i in (1, 2, 3))
OWN, TAP = LineKey("own"), LineKey("tap")


def kills(*rows: int) -> pytest.MarkDecorator:
    """Marks the test as one that must go red for these rows of MUTANTS.txt."""
    return pytest.mark.kills(*rows)


def spell(work_s: int = 10, reach: int = 2, lines: tuple[LineKey, ...] = LINK_KEYS[:1], *, card_id: CardId = SPELL,
          runner: ActionId = RAID, lane: LaneId = HANDS, cap: int | None = None, own: tuple[LineKey, ...] = ()) -> CardDef:
    return CardDef(card_id, work_s, lane=lane, cap=cap, lines=own, chain=ChainDef(runner, reach, lines))


def raid(chained: StoreId | None = CHAINED, *, per: int = PER_HR) -> StandingDef:
    return StandingDef(RAID, fight=FightDef(HAND, WOLF, RLOST, FOUGHT, per_hour(per), chained=chained))


def world(m: int = 3, reach: int = 2, lines: tuple[LineKey, ...] = LINK_KEYS[:1], *, work_s: int = 10, per: int = PER_HR,
          cap: int | None = None, own: tuple[LineKey, ...] = (), fought_cap: int = BIG, side: int = 3,
          max_firings: int = 1000, cards: tuple[CardDef, ...] | None = None, triggers: tuple[TriggerDef, ...] = (),
          lanes: tuple[LaneDef, ...] = (), standing: tuple[StandingDef, ...] | None = None) -> Rules:
    stores = (StoreDef(FOUGHT, fought_cap), StoreDef(RLOST, BIG), StoreDef(CHAINED, BIG))
    cs = cards if cards is not None else (spell(work_s, reach, lines, cap=cap, own=own),)
    return Rules(stores, (SkillDef(K),), standing if standing is not None else (raid(per=per),), PacingCurve((10**15,)),
                 max_firings_per_instant=max_firings, lanes=lanes, cards=cs, triggers=triggers,
                 sides=(SideDef(HAND, side),), threats=(ThreatDef(WOLF, 6, members=m),))


def twin(r: Rules) -> Rules:
    """The same rules with every chain taken off its card: the flow alone."""
    return replace(r, cards=tuple(replace(c, chain=None) for c in r.cards))


def fought(r: Rules, t: int, s: Save | None = None) -> int:
    """Whole fights the flow has fought by t (the tally floored, as the contract's F), read off the chain-free twin."""
    w = twin(r)
    return value(new_save(w) if s is None else s, w, FOUGHT, t) // Q


def reach_of(base: int, mods: tuple[Modifier, ...] = ()) -> int:
    adds = sum(x.amount_bp for x in mods if x.kind is ModifierKind.ADD_BP)
    muls = [x.amount_bp for x in mods if x.kind is ModifierKind.MUL_BP]
    return base * max(0, BP + adds) * prod(muls) // BP ** (1 + len(muls))


def due_of(m: int, f: int, c: int, fighting: bool = True) -> int:
    return m - ((f + c) % m) if fighting else 0


def chained(r: Rules, s: Save, t: int | None = None) -> int:
    return value(s, r, CHAINED, s.time if t is None else t) // Q


def tap_at(r: Rules, s: Save, t: int, card: CardId = SPELL) -> tuple[Save, list[Line]]:
    """Advance to t, tap the card there, and run on to its completion (work_s on): the save and every line on the way."""
    step = decide_logged(s, r, t, TapCard(card))
    work = next(c.work_s for c in r.cards if c.id == card)
    end = advance_logged(step.save, r, t + work)
    return end.save, [*step.lines, *end.lines]


def play(r: Rules, taps: tuple[int, ...], *, mods: tuple[Modifier, ...] = ()) -> tuple[Save, list[Line]]:
    """Tap the first card at each time (spaced beyond its work), collecting the lines."""
    s, lines = new_save(r, mods), list[Line]()
    for t in taps:
        s, got = tap_at(r, s, t)
        lines += got
    return s, lines


def links(lines: Sequence[Line], card: CardId = SPELL, keys: tuple[LineKey, ...] = LINK_KEYS) -> list[Line]:
    return [x for x in lines if x.card == card and x.key in keys]


def link_times(lines: Sequence[Line]) -> list[int]:
    return [x.time for x in links(lines)]


def model_links(r: Rules, completions: tuple[int, ...], reach: int, m: int) -> list[tuple[int, int]]:
    """(completion time, links) at each completion, from the contract: min(due, reach, room), C the links so far."""
    out: list[tuple[int, int]] = []
    c = 0
    for at in completions:
        k = min(due_of(m, fought(r, at), c), reach, max(0, r.max_firings_per_instant - 1))
        out.append((at, k))
        c += k
    return [x for x in out if x[1]]


def per_instant(lines: Sequence[Line], card: CardId = SPELL, keys: tuple[LineKey, ...] = LINK_KEYS) -> list[tuple[int, int]]:
    """(time, links) for each instant that carries any."""
    times = sorted({x.time for x in links(lines, card, keys)})
    return [(t, sum(1 for x in links(lines, card, keys) if x.time == t)) for t in times]


def mixed(r: Rules, shares: dict[CardId, int], at: int = 0) -> Save:
    s = new_save(r)
    s = decide_logged(s, r, at, SaveMix(Mix(MIX, tuple(CardShare(c, bp) for c, bp in shares.items())))).save
    return decide_logged(s, r, at, SwitchMix(MIX)).save


def ruled(r: Rules, card: CardId = SPELL) -> Save:
    """The card repeated on a ruled side lane by an always rule."""
    return decide(new_save(r), r, 0, SetOrders((Order(AfterTime(0), TapCard(card)),)))


def entry(card: CardId, kind: ModifierKind, bp: int, source: str = "pay") -> Modifier:
    return Modifier(ChainReach(card), kind, bp, SourceId(source))
