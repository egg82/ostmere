"""Fixture rules for the retired-chores contract tests (engine DESIGN.txt, "Installed rule" / "Retired chores",
invariants 142-147), built from the engine's public names and the stated interface only; Outcome.retire_orders is
reached through `turn`, at call time, so a module that tests it collects before it exists.

The hands run c1 and c2 (35 s each, both making m); the ruled lane lr runs r1 and r2 (40 s each). Five orders stand:
oa taps c1 and oc taps r1 (the chore cures, which the turn names), ob taps c2 and od taps r2 (same lanes and the same
store, which it does not), oe switches to a saved hands mix. The turn is at TURN: oa has c1 running since 80 (due
115) and oc has r1 running since 81 (due 121), so both are mid-task at the turn."""
import re
from pathlib import Path
from typing import Any

import pytest

from ashfall_app.engine import (
    BP, QUANTITY_SCALE as Q, ActionId, AfterTime, AtLeast, CardCount, CardDef, CardId, CardShare, Flow, LaneDef, LaneId,
    Mix, MixId, Order, Outcome, PacingCurve, QueueEntry, Rules, Save, SaveMix, SetOrders, SetQueue, SkillDef, SkillId,
    StandingDef, StoreDef, StoreId, StoreValue, SwitchMix, TapCard, TriggerDef, TriggerId, decide, new_save, per_hour,
    validate_rules,
)
from leaves_world import outcome
from ashfall_app.opening.schema import OPENING, load_opening, to_rules

M, T0 = StoreId("m"), StoreId("t0")
C1, C2, R1, R2 = CardId("c1"), CardId("c2"), CardId("r1"), CardId("r2")
LR = LaneId("lr")
MX = MixId("mx")
TURN = 100
BIG = 10**6 * Q
PER_SECOND = per_hour(3600)

OA = Order(AfterTime(10), TapCard(C1))
OB = Order(AfterTime(10), TapCard(C2))
OC = Order(AtLeast(StoreValue(T0), Q, Q), TapCard(R1))
OD = Order(AfterTime(10), TapCard(R2))
OE = Order(AfterTime(5), SwitchMix(MX))
OF = Order(AfterTime(10**6), TapCard(C2))
"""A kept order whose latch is off at the turn, behind removed ones: a latch that slid to the wrong order shows."""
ORDERS = (OA, OB, OC, OD, OE, OF)
NAMED = (C1, R1)
QUEUED = QueueEntry(TapCard(C1), AtLeast(CardCount(C1), 100, 100))
"""A hands queue entry tapping a named cure: the turn leaves the queue alone."""


def turn(named: tuple[CardId, ...] = NAMED) -> Outcome:
    return outcome(retire_orders=named)


def rules(at: int | None = TURN, outcome: Any = None) -> Rules:
    """The world; at None there is no turn at all (the control), else a trigger at `at` with this outcome (default: the
    turn naming c1 and r1)."""
    trig = () if at is None else (TriggerDef(TriggerId("turn"), AfterTime(at), turn() if outcome is None else outcome),)
    r = Rules(stores=tuple(StoreDef(s, BIG) for s in (M, T0)), skills=(SkillDef(SkillId("k")),),
              standing=(StandingDef(ActionId("tick"), makes=(Flow(T0, PER_SECOND),)),), curve=PacingCurve((10**15,)),
              lanes=(LaneDef(LR, True),),
              cards=(CardDef(C1, 35, makes=(Flow(M, PER_SECOND),)), CardDef(C2, 35, makes=(Flow(M, PER_SECOND),)),
                     CardDef(R1, 40, lane=LR), CardDef(R2, 40, lane=LR)), triggers=trig)
    validate_rules(r)
    return r


def scene(r: Rules) -> Save:
    """At 0: the five orders, a saved hands mix for oe, one queue entry on c1."""
    s = decide(new_save(r), r, 0, SaveMix(Mix(MX, (CardShare(C2, BP),))))
    return decide(decide(s, r, 0, SetOrders(ORDERS)), r, 0, SetQueue((QUEUED,)))


# ---- the loader's chapter (fixtures/chores_chapter.toml, merged onto the opening alone) --------------------------------

CHAPTER = Path(__file__).resolve().parent / "fixtures" / "chores_chapter.toml"
DEFAULTS = {"SEASON": "true", "CLOSE": "line_keys = []", "EXTRA": "", "OTHER": ""}


def render(tmp_path: Path, **slots: str) -> Path:
    """The chapter with each @SLOT@ filled (its default is the plain shape that loads), written under tmp_path."""
    unknown = set(slots) - set(DEFAULTS)
    assert not unknown, unknown
    text = CHAPTER.read_text()
    for name, default in DEFAULTS.items():
        text = text.replace(f"@{name}@", slots.get(name, default))
    assert not re.search(r"@[A-Z_]+@", text)
    path = tmp_path / CHAPTER.name
    path.write_text(text)
    return path


def loaded(tmp_path: Path, **slots: str) -> Rules:
    return to_rules(load_opening(OPENING, (render(tmp_path, **slots),)))


def close_outcome(r: Rules) -> Any:
    return next(t for t in r.triggers if t.id == "t_close").outcome


def refused(tmp_path: Path, entry: str, **slots: str) -> None:
    """The plain chapter loads (a control), and this edit of it raises ValueError with `entry` in its message."""
    loaded(tmp_path)
    with pytest.raises(ValueError, match=entry):
        loaded(tmp_path, **slots)
