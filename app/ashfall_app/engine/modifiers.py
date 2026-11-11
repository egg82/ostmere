"""What changes a rate, and why a rate is the number it is.

One rate is one line of one runner (a standing action or a card): a make, a cost, or its XP (a RateRef). Its value:

    exact = base * share_bp * max(0, BP + sum(add_bp)) * prod(mul_bp) * run.num
            / (base_den * BP ** (2 + len(muls)) * run.den)

base / base_den is the line's rate at a 100% share: a flow's per_hour over 1, or a card's lump per completion over its
work_s, whoever runs it (DESIGN.txt, "Rate form").

rounded once, down for makes and XP and up for costs, so rounding never favours the player and a non-zero cost never
rounds to free. Additive entries sum first (two +10% are +20%); multiplicative entries then multiply in (they model
separate sources that compound). The sum is floored at 0 so a rate never changes sign.
"""
from dataclasses import dataclass
from enum import Enum
from math import prod

from .ids import CardId, LaneId, Runner, SideId, SourceId, StoreId, ThreatId
from .mixes import SpentShare
from .units import BP, ceil_div


class FlowKind(Enum):
    MAKE = "make"
    COST = "cost"
    XP = "xp"


@dataclass(frozen=True)
class RateRef:
    """One rate: a runner's make or cost of `store`, or its XP (store is None exactly when kind is XP). A card's make
    covers its make flows and its outcome stores, its cost its cost flows and its inputs (one store, one side:
    validation), so one ref names each line the ledger shows."""

    runner: Runner
    kind: FlowKind
    store: StoreId | None = None


@dataclass(frozen=True)
class WorkRef:
    """A card's work speed: how fast its one bar fills, tapped or mixed, and so how fast its lump lines run
    (DESIGN.txt, "Work", "Rate form"). Not a store's rate."""

    card: CardId


@dataclass(frozen=True)
class LaneSpeed:
    """Every line on `lane` at once: each make, cost and XP of what runs there, and each card's work. "Tired halves
    bar speed" is one MUL_BP entry aimed here (DESIGN.txt, "Speed")."""

    lane: LaneId


@dataclass(frozen=True)
class StoreCap:
    """How much a store holds (DESIGN.txt, "Store caps"): its StoreDef.cap under the entries aimed here, rounded down.
    Only raises (validation), so no store ever holds more than its cap. Not a rate: modified_rate never reads it."""

    store: StoreId


@dataclass(frozen=True)
class SideStrength:
    """How strong a side is (DESIGN.txt, "FIGHTS"): SideDef.base under the entries aimed here, as for a StoreCap,
    rounded down. Anything may aim here, a chip may lower it. Not a rate: modified_rate never reads it."""

    side: SideId


@dataclass(frozen=True)
class ThreatStrength:
    """How strong a threat is: ThreatDef.base under the entries aimed here, as for a StoreCap, rounded down. Only a
    trigger's outcome aims here, and only to raise it (validation): threats ramp by region and time, never by the
    player's defences. Not a rate."""

    threat: ThreatId


type Target = RateRef | WorkRef | LaneSpeed | StoreCap | SideStrength | ThreatStrength


class ModifierKind(Enum):
    ADD_BP = "add_bp"
    """amount_bp is added to the percentage (may be negative): 1_500 is +15%."""
    MUL_BP = "mul_bp"
    """amount_bp is a factor in basis points (>= 0): 15_000 is x1.5, 5_000 is x0.5."""


@dataclass(frozen=True)
class Modifier:
    """One entry in a rate's stack, carrying where it came from."""

    target: Target
    kind: ModifierKind
    amount_bp: int
    source: SourceId


def lowers_cap(m: Modifier) -> bool:
    """An entry aimed at a StoreCap that would lower it: add_bp below 0, mul_bp below BP (DESIGN.txt, "Store caps")."""
    return isinstance(m.target, StoreCap) and m.amount_bp < (BP if m.kind is ModifierKind.MUL_BP else 0)


def lowers_threat(m: Modifier) -> bool:
    """An entry aimed at a ThreatStrength that would lower it: add_bp below 0, mul_bp below BP."""
    return isinstance(m.target, ThreatStrength) and m.amount_bp < (BP if m.kind is ModifierKind.MUL_BP else 0)


class RunKind(Enum):
    FULL = "full"
    PAUSED = "paused"
    """Stopped because `store` ran dry; resumes when the store refills (api.py, 'Running dry')."""
    YIELDED = "yielded"
    """A mix card while the hands run a tap: 0/1, its share kept and shown (DESIGN.txt, "Lanes")."""
    WAITING = "waiting"
    """A mix card whose requires do not all hold: 0/1, `condition_index` names the first unmet one; it runs again the
    instant they hold (DESIGN.txt, "Requires in the mix")."""
    GREYED = "greyed"
    """Every card of the active mix while it holds a completed card: 0/1 (DESIGN.txt, "Greyed mix")."""
    SPENT = "spent"
    """A running mix's card paused on `store`, a store nothing in play can make again: 0/1, its share yielded to the
    rest of its mix on its lane (DESIGN.txt, "SPENT")."""


@dataclass(frozen=True)
class Run:
    """How much of its share a runner is running: FULL is 1/1, PAUSED, SPENT, YIELDED, WAITING and GREYED 0/1,
    0 <= num <= den. store: the store a PAUSED or SPENT run is about. condition_index: a WAITING card's first unmet
    requires, by index in CardDef.requires. speed: a HANDS tap's speed entries kept from its start (LaneState.speed),
    read in place of the live stack's LaneSpeed and WorkRef entries; None reads the live stack."""

    kind: RunKind
    num: int = 1
    den: int = 1
    store: StoreId | None = None
    condition_index: int | None = None
    speed: tuple[Modifier, ...] | None = None


@dataclass(frozen=True)
class Explanation:
    """Why a rate is this number: every input of the formula above, so a reader can recompute per_hour exactly.

    adds and muls keep the save's modifier order and hold every entry that applies, LaneSpeed ones included, each
    retargeted at `ref` with its source kept, so the formula recomputes per_hour from these fields alone. per_hour is
    the rounded result in rate units (work units per second for a WorkRef, rounded down).
    """

    ref: RateRef | WorkRef
    base_per_hour: int
    base_den: int
    """1 for a flow; a card's work_s for a lump line (base_per_hour is then the lump's quantity per completion)."""
    share_bp: int
    adds: tuple[Modifier, ...]
    muls: tuple[Modifier, ...]
    run: Run
    per_hour: int
    gained: tuple[SpentShare, ...] = ()
    """The paused and spent cards whose shares this line's card receives, each with its part: share_bp is the saved share plus
    their sum (DESIGN.txt, "SPENT", "Explain"). Empty for every other line."""


def modified_rate(
    ref: RateRef, base_per_hour: int, share_bp: int, stack: tuple[Modifier, ...], run: Run, base_den: int = 1
) -> Explanation:
    """Apply the formula in this module's docstring. Entries in `stack` whose target is not `ref` are ignored."""
    aimed = [m for m in stack if m.target == ref]
    adds = tuple(m for m in aimed if m.kind is ModifierKind.ADD_BP)
    muls = tuple(m for m in aimed if m.kind is ModifierKind.MUL_BP)
    add_factor = max(0, BP + sum(m.amount_bp for m in adds))
    num = base_per_hour * share_bp * add_factor * prod(m.amount_bp for m in muls) * run.num
    den = base_den * BP ** (2 + len(muls)) * run.den
    per_hour = ceil_div(num, den) if ref.kind is FlowKind.COST else num // den
    return Explanation(ref, base_per_hour, base_den, share_bp, adds, muls, run, per_hour)
