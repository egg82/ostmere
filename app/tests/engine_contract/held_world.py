"""Fixture rules and readers for the held-entries contract tests (engine DESIGN.txt, "ENTRIES HELD WHILE A CARD RUNS",
invariants 110-118). Built from the engine's public names only; the new ones (WhileRunning, CardDef.while_running,
View.held) are looked up when a fixture is built, never when a test module imports.

One side g (base BP) and one threat (base BP), a standing fight RAID on g (live odds: its loss_bp is the readout of
the stack), and guard cards on every layer:
  town (ruled lanes la, lb of town_mix_world): ga 4000, ga2 3000, gac (capped) 4000, gb 2000, glk 1000 (locked at
    the start where a test gives an opening);
  hands: gh 5000, gh2 (g 2000 and g2 1500), gcap (capped) 2500, greq (requires rq <= 2) 3000, gdry (costs food) 6000,
    build (queue's stage) 3500, stepg (glowing, capped) 1500; plain hands cards ph, step (glowing, capped).
With base BP and only adds on g, strength == BP + the sum of the adds, so the raise is read straight off it."""
from collections.abc import Callable
from typing import Any
from dataclasses import replace

import pytest

import ashfall_app.engine as eng
from ashfall_app.engine import (
    BP, QUANTITY_SCALE as Q, ActionId, Amount, AtMost, CardDef, CardId, CardShare, FightDef, Flow, Mix, Modifier,
    Rules, Save, SaveMix, SideDef, SideId, SideStrength, StandingDef, StoreDef, StoreId, StoreValue,
    SwitchMix, ThreatDef, ThreatId, TriggerDef, Unlock, UnlockKind, advance, decide, new_save, next_event, per_hour,
    strength, view,
)
from ashfall_app.engine.gates import effective_stack
from town_mix_world import LA, LB, PER_SECOND, TM, WORK, joiner, world as town_world

G, G2, WOLF = SideId("g"), SideId("g2"), ThreatId("wolf")
RAID, MKRQ, MKFOOD = ActionId("raid"), ActionId("mkrq"), ActionId("mkfood")
STASH, RLOST, FOUGHT, GRAIN, LOST, HURT, FOOD, RQ, HX, LOST2 = (
    StoreId(n) for n in ("stash", "rlost", "fought", "grain", "lost", "hurt", "food", "rq", "hx", "lost2"))
GA, GA2, GAC, GB, GLK = (CardId(n) for n in ("ga", "ga2", "gac", "gb", "glk"))
GH, GH2, GCAP, GREQ, GDRY, BUILD, STEPG, PH, STEP, HF, HFR = (
    CardId(n) for n in ("gh", "gh2", "gcap", "greq", "gdry", "build", "stepg", "ph", "step", "hf", "hfr"))
HM = eng.MixId("hm")
BIG = 10**6 * Q
HELD = "held:"


def kills(*mutants: int) -> Callable[[Callable[..., None]], Callable[..., None]]:
    """Marks the test as one that must go red for these rows of MUTANTS_held.txt (read by tools/mutate_suite.py)."""
    return pytest.mark.kills(*mutants)


def wr(side: SideId, amount_bp: int) -> Any:
    return getattr(eng, "WhileRunning")(side, amount_bp)  # a name item 2 adds: looked up here, not at import


def guard(card: str, work_s: int, *entries: tuple[SideId, int], **kw: Any) -> CardDef:
    return CardDef(CardId(card), work_s, while_running=tuple(wr(s, a) for s, a in entries), **kw)


def cards() -> tuple[CardDef, ...]:
    return (
        guard("ga", WORK, (G, 4000), lane=LA, makes=(Flow(HX, PER_SECOND),)), guard("ga2", WORK, (G, 3000), lane=LA),
        guard("gac", 20, (G, 4000), lane=LA, cap=1), guard("gb", WORK, (G, 2000), lane=LB),
        guard("glk", WORK, (G, 1000), lane=LA),
        guard("gh", 100, (G, 5000)), guard("gh2", 100, (G, 2000), (G2, 1500)), guard("gcap", 20, (G, 2500), cap=1),
        guard("greq", 100, (G, 3000), requires=(AtMost(StoreValue(RQ), 2 * Q, 2 * Q),)),
        guard("gdry", 100, (G, 6000), costs=(Flow(FOOD, per_hour(1)),)),
        guard("build", 1000, (G, 3500), cap=3), guard("stepg", 5, (G, 1500), cap=1, glows=True),
        CardDef(PH, 100), CardDef(STEP, 5, cap=1, glows=True),
        CardDef(HF, 100, fight=FightDef(G, WOLF, LOST, wounds=(Amount(HURT, 2 * Q),))),
    )


def ruled_fight() -> CardDef:
    """A fight card on g on the ruled lane lb (a repeating tap there reads the live stack): lost fights count in lost2."""
    return CardDef(HFR, WORK, lane=LB, fight=FightDef(G, WOLF, LOST2))


def standing(drain: StoreId) -> tuple[StandingDef, ...]:
    """RAID: two fights an hour, each lost one taking 3 of `drain`. mkrq counts rq up one a second (greq's requires
    holds until it passes 2); mkfood makes 2.5 food an hour."""
    return (StandingDef(RAID, makes=(Flow(GRAIN, per_hour(3)),),
                        fight=FightDef(G, WOLF, RLOST, FOUGHT, per_hour(2), (Amount(drain, 3 * Q),))),
            StandingDef(MKRQ, makes=(Flow(RQ, PER_SECOND),)), StandingDef(MKFOOD, makes=(Flow(FOOD, per_hour(5) // 2),)))


def world(triggers: tuple[TriggerDef, ...] = (), opening: tuple[Unlock, ...] | None = None, drain: StoreId = STASH,
          extra: tuple[CardDef, ...] = ()) -> Rules:
    r = town_world(triggers, cards() + extra, opening)
    stores = tuple(StoreDef(s, BIG, BIG if s == STASH else Q if s == FOOD else 0)
                   for s in (STASH, RLOST, FOUGHT, GRAIN, LOST, HURT, FOOD, RQ, HX, LOST2))
    return replace(r, stores=r.stores + stores, standing=standing(drain),
                   sides=(SideDef(G, BP), SideDef(G2, BP)), threats=(ThreatDef(WOLF, BP),))


def plain(r: Rules) -> Rules:
    """The same rules with no card holding anything: the twin that takes the entries by hand."""
    return replace(r, cards=tuple(replace(c, **{"while_running": ()}) for c in r.cards))


def opening_all(r: Rules, *locked: CardId) -> tuple[Unlock, ...]:
    return tuple(Unlock(UnlockKind.CARD, c.id) for c in r.cards if c.id not in locked) + tuple(
        Unlock(UnlockKind.ACTION, a.id) for a in r.standing)


def held_mods(s: Save, r: Rules) -> tuple[Modifier, ...]:
    return tuple(m for m in effective_stack(s, r) if m.source.startswith(HELD))


def held_of(s: Save, r: Rules, card: CardId) -> list[int]:
    """The amounts of the card's held entries on g, in stack order."""
    return [m.amount_bp for m in held_mods(s, r) if m.source == HELD + card and m.target == SideStrength(G)]


def raised(s: Save, r: Rules) -> int:
    return strength(s, r, SideStrength(G)) - BP


def loss(s: Save, r: Rules) -> int:
    """RAID's loss_bp now (a standing fight reads the live stack)."""
    return next(f.loss_bp for f in view(s, r).fights if f.runner == RAID)


def odds_loss(raise_bp: int) -> int:
    """The documented odds ceil(BP * T / (T + P)) with T = BP and g raised by raise_bp over its base BP."""
    return -(-BP * BP // (2 * BP + raise_bp))


def flat(a: int, h: int) -> int:
    return a * h // BP


def hands(r: Rules, *shares: tuple[CardId, int]) -> Save:
    """A new save running the hands' mix hm with these shares."""
    s = decide(new_save(r), r, 0, SaveMix(Mix(HM, tuple(CardShare(c, b) for c, b in shares))))
    return decide(s, r, 0, SwitchMix(HM))


def town(r: Rules, *shares: tuple[CardId, int], at: int = 0) -> Save:
    """A save whose la has joined (trigger ja) and whose town mix holds these shares; the rules must carry joiner ja."""
    s = advance(new_save(r), r, at)
    return decide(s, r, at, SaveMix(Mix(TM, tuple(CardShare(c, b) for c, b in shares))))


def ja(at: int = 0, card: CardId = GA) -> TriggerDef:
    return joiner("ja", LA, TM, card, at)


def jb(at: int = 0, card: CardId = GB) -> TriggerDef:
    return joiner("jb", LB, TM, card, at)


def first(s: Save, r: Rules, pred: Callable[[Save], bool], steps: int = 60) -> Save:
    """The save at the first event instant (from s on) where pred holds."""
    for _ in range(steps):
        if pred(s):
            return s
        ev = next_event(s, r)
        assert ev is not None, "no further event and pred never held"
        s = advance(s, r, ev.time)
    raise AssertionError("pred did not hold within the steps")


def run_of(s: Save, r: Rules, card: CardId) -> eng.RunKind:
    run = next(c.run for c in view(s, r).cards if c.card == card)
    assert run is not None
    return run


def paused(s: Save, runner: eng.Runner) -> bool:
    return any(p.runner == runner for p in s.pauses)
