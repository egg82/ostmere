"""Cards: one Type Object for every kind of work the player does, tapped by hand or run by the mix.

A one-off, a building stage or a recipe is a card with a completion cap; gathering by hand and gathering all afternoon
are the same card (docs/systems.md, "Cards"). Semantics: DESIGN.txt, part "CARDS". What cards do to a save: work.py.
"""
from dataclasses import dataclass

from .ids import HANDS, ActionId, CardId, LaneId, LineKey, MixId, SideId, SkillId, StoreId, ThreatId
from .modifiers import Modifier
from .orders import Condition
from .flows import Flow
from .segments import Segment
from .unlocks import Unlock


@dataclass(frozen=True)
class Amount:
    """A lump quantity of one store (quantity units, > 0)."""

    store: StoreId
    quantity: int


@dataclass(frozen=True)
class FightDef:
    """The Component that makes a card or a standing action a fight: work with odds on it (DESIGN.txt, "FIGHTS").

    side and threat name the strengths whose ratio is the odds. lost: the tally store, one unit per lost fight.
    fought: the tally of all fights (a standing fight only; a card counts its completions). per_hour: a standing fight's
    fights per hour in rate units (RATE_SCALE per fight per hour), > 0 there and 0 on a card, whose rate is its
    completions. loses: per lost fight, taken from a store. wounds: per lost fight, added to a store."""

    side: SideId
    threat: ThreatId
    lost: StoreId
    fought: StoreId | None = None
    per_hour: int = 0
    loses: tuple["Amount", ...] = ()
    wounds: tuple["Amount", ...] = ()


@dataclass(frozen=True)
class WhileRunning:
    """An ADD_BP entry on SideStrength(side) that the card holds while it runs, at the card's share of its lane's time
    (DESIGN.txt, "ENTRIES HELD WHILE A CARD RUNS"). Its source is HELD_PREFIX + the card's id; amount_bp >= 1."""

    side: SideId
    amount_bp: int


@dataclass(frozen=True)
class HeldSpeed:
    """An ADD_BP entry on LaneSpeed(lane) that a runner holds while it runs, at its held share (DESIGN.txt, "HELD
    SPEED"). lane is a declared lane, never HANDS, whose lines keep no speed; amount_bp >= 1."""

    lane: LaneId
    amount_bp: int


type Held = WhileRunning | HeldSpeed
"""One entry of a runner's while_running."""

HELD_PREFIX = "held:"
"""Every held entry's source starts with it, followed by its runner's id; content may not use such a source."""


@dataclass(frozen=True)
class CapRaise:
    """Raise `card`'s completion cap by `by` (> 0). The card must have a cap (validation). A completed card whose cap
    rises leaves the Completed set, and a mix greyed by it is live again (DESIGN.txt, "Caps")."""

    card: CardId
    by: int


@dataclass(frozen=True)
class RuleInstall:
    """Install a ruled lane's always rule, Order(AfterTime(0), TapCard(card)): at the top of the orders (first) or
    at their end, unless an equal order is already set (DESIGN.txt, "Installed rule")."""

    card: CardId
    first: bool = False


@dataclass(frozen=True)
class Join:
    """A person joins the town: `lane`'s person is present from now on, and the lane's always task becomes its share
    in the town mix `mix` (an id beginning "town:"). `card` is the share when the lane has no uncapped always rule
    (DESIGN.txt, "THE TOWN'S MIX", "Join")."""

    lane: LaneId
    mix: MixId
    card: CardId | None = None


@dataclass(frozen=True)
class Leave:
    """A person leaves the town for good: `lane`'s person is gone from now on, the lane's cards go out of play, the
    orders tapping them and their shares in every saved mix are removed, and each standing action in `stops` stops
    (DESIGN.txt, "LEAVES")."""

    lane: LaneId
    stops: tuple[ActionId, ...] = ()


@dataclass(frozen=True)
class Outcome:
    """What lands at once when a completion, a trigger or an answer applies it, in this order: stores, unlocks,
    modifiers, raises, retire_orders, leaves, orders, joins, queues, starts, then lines (the parts from retire_orders to queues
    land in the middle; they come last in the class so the earlier fields keep their positions).

    stores: added, clamped at cap, overflow lost. unlocks: joined to the unlock set. modifiers: appended to the save's
    stack for good. raises: cap raises. orders: rules installed (only in a trigger's or an answer's outcome:
    validation). joins: people joining the town (only in a trigger's or an answer's outcome: validation). queues: hands one-offs put at the queue's front as When ready entries (only in an answer's outcome).
    retire_orders: every order tapping one of these cards is removed, whoever set it (only in a trigger's outcome:
    validation; DESIGN.txt, "Retired chores"). leaves: people leaving the town (only in a trigger's or an answer's
    outcome, one per lane across the rules: validation).
    starts: each tapped as an order would (TapCard; never a HANDS card from a HANDS landing: validation). lines:
    emitted after the completion's own line. Orders and the queue evaluate after it.
    """

    stores: tuple[Amount, ...] = ()
    unlocks: tuple[Unlock, ...] = ()
    modifiers: tuple[Modifier, ...] = ()
    raises: tuple[CapRaise, ...] = ()
    starts: tuple[CardId, ...] = ()
    lines: tuple[LineKey, ...] = ()
    orders: tuple[RuleInstall, ...] = ()
    queues: tuple[CardId, ...] = ()
    joins: tuple[Join, ...] = ()
    retire_orders: tuple[CardId, ...] = ()
    leaves: tuple[Leave, ...] = ()


@dataclass(frozen=True)
class CardDef:
    """A Type Object for one card. Its instance state is CardState: one cumulative work segment, so one bar.

    Work: work_s seconds per completion at full speed (>= 1); a completion is the card's work crossing a multiple of
    work_s * BP. Whoever runs the card advances that same work: a tap at a full share, or the mix at the card's share.
    On HANDS a tap yields the mix, so at most one of them runs a card at any instant (DESIGN.txt, "One bar"). A tap
    runs the card to its next completion, continuing any work the mix left. Only HANDS cards and, once their person has joined, uncapped cards on a ruled lane go in a mix.

    While the card runs, its lines run at the running share: makes and costs per hour at a 100% share and xp_per_hour
    into `skill` (skill None: xp_per_hour 0), per hour of running; `inputs` and `outcome.stores`, A per completion, as
    lines of A / work_s per second at full speed, scaled by the card's work speed too (DESIGN.txt, "Rate form"). So a
    completion's inputs are paid as its work is done, by whoever does it, and never twice. Each store appears at most
    once across makes, costs, inputs and outcome stores (validation).

    Completion events: a completion is an event (COMPLETION) when it has a discrete effect: always for a card with a
    cap, never for one without (its outcome is stores only, which ran as rates; CardCount is solved off the work
    segment). At a COMPLETION the outcome's non-store parts and the completion's line land; at the cap, `finished`
    lands too and the card is completed (DESIGN.txt, "Completions", "Caps").

    requires: plain thresholds (release == value, no Running subject: validation) that hold at a tap's start and while
    the card runs; one false stops it (WAITING in the mix; a tap ends, interrupted). cap: completions allowed, None for no limit. finished: lands at the completion that reaches the cap
    (after `outcome`); needs a cap; a raise and a later reach land it again.

    lines: with a cap, empty or one key per completion number up to the base cap (completion n emits lines[n - 1];
    completions past the base cap emit the last), however the card was run; without a cap, empty or one key, emitted
    when a tap ends at a completion. failed_line: emitted at the instant of a failed tap (TapCard).
    """

    id: CardId
    work_s: int
    lane: LaneId = HANDS
    skill: SkillId | None = None
    xp_per_hour: int = 0
    makes: tuple[Flow, ...] = ()
    costs: tuple[Flow, ...] = ()
    inputs: tuple[Amount, ...] = ()
    requires: tuple[Condition, ...] = ()
    outcome: Outcome = Outcome()
    cap: int | None = None
    finished: Outcome = Outcome()
    lines: tuple[LineKey, ...] = ()
    failed_line: LineKey | None = None
    fight: FightDef | None = None
    glows: bool = False
    """A step the page points at with its one glow: until its first completion, the player's tap of it cuts in on the
    hands while they run a task the queue or an order would start again (decisions.cuts_in)."""
    while_running: tuple[Held, ...] = ()
    """Sides and lane speeds this card raises while it runs (the codec leaves the field out while empty)."""
    drains: tuple[Amount, ...] = ()
    """Takes of up to `quantity` per completion, paid as inputs are and forgiven at 0: they never pause the card, and a
    tap needs each store above 0 (DESIGN.txt, "DRAINS"; the codec leaves the field out while empty)."""


@dataclass(frozen=True)
class CardState:
    """One card's state, present iff its work's value, its work's rate or its raise is non-zero (Save.cards, rules
    order).

    work: the card's cumulative work in work units (BP per second at full speed), a segment like a store's, advanced
    by a tap or a mix share, never both at once. completions = work.start_value // (work_s * BP); the bar is the
    remainder. Its limit is the effective cap's work, or for a tap the next completion; COMPLETION events between are
    solved, not limits, so no completion loses a partial second (DESIGN.txt, "Completions"). raised: the sum of
    CapRaise.by applied; effective cap = cap + raised (DESIGN.txt, "Caps").
    """

    card: CardId
    work: Segment
    raised: int = 0


@dataclass(frozen=True)
class LaneState:
    """What one lane is doing. A free lane is card None. A tap holds `card` and no timer of its own: its progress is
    the card's work, and it ends at the card's next completion (TAP_DONE). speed: a tap on HANDS keeps the effective
    stack's entries aimed at LaneSpeed(HANDS) or at its card's WorkRef as they stood at its start, and runs at them
    to its end (DESIGN.txt, "Speed"); None on any other lane, and for a tap a format 7 save began, which reads the
    live stack."""

    lane: LaneId
    card: CardId | None = None
    speed: tuple[Modifier, ...] | None = None


@dataclass(frozen=True)
class Blocker:
    """The first unmet precondition of a tap now, as a condition the engine solves: an input whose store holds less
    than the rest of the current completion's input (AtLeast(StoreValue(store), q, q), q rounded up as costs are),
    in declaration order, then requires, then a Pause on the card (AtLeast(StoreValue(pause store), resume_at,
    resume_at)). A busy lane and a completed card are never blockers (the LaneBar and the Completed set show those).
    ready_at: when the card is ready, the latest of the times each of its unmet preconditions first holds under the
    current segments, counting nothing an order, the queue or the player might do; None when one never holds."""

    condition: Condition
    ready_at: int | None
