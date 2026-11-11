"""The read model's parts: ledger lines, bars and cards, as view.view builds them. Semantics: DESIGN.txt, "Read model"
and part "CARDS", "Card panel".
"""
from dataclasses import dataclass, field
from enum import Enum

from .cards import Blocker
from .ids import ActionId, AnswerId, CardId, LaneId, NodeId, OfferId, Runner, SkillId, StoreId
from .mixes import SpentShare
from .modifiers import Modifier, RunKind
from .segments import Segment
from .state import ParkedRank


@dataclass(frozen=True)
class Contribution:
    """One running runner's signed part of a store's net rate (rate units per hour): + makes, - costs. A card's
    contribution sums its flow and its lump line on that store (they are one RateRef)."""

    runner: Runner
    per_hour: int


@dataclass(frozen=True)
class LedgerLine:
    """One unlocked store (DESIGN.txt, "Read model"). net_per_hour: the sum of contributions, unclamped (overflow at a
    cap shows). falling: the segment's rate < 0. empties_at: reach_time(segment, 0) when falling or at 0, else None.
    fills_at: reach_time(segment, cap) when rising or at the cap, else None. covered: some standing order's verb
    (latched or not) or the queue head's makes this store, following Outcome.starts; a dead verb covers nothing. starved: the store has run dry
    while something waits on it (work.starved; DESIGN.txt, "Starved line"), shown as a problem whether covered or
    not. cap: what the store holds now, StoreDef.cap under its StoreCap modifiers (DESIGN.txt, "Store caps")."""

    store: StoreId
    segment: Segment
    net_per_hour: int
    contributions: tuple[Contribution, ...]
    empties_at: int | None
    fills_at: int | None
    falling: bool
    covered: bool
    starved: bool
    cap: int


@dataclass(frozen=True)
class MenuNode:
    """One node the skill's next pick may go into (prestige.menu): its ranks taken of `ranks`, and its target's value
    now and with one more rank, each read at a full share and a FULL run (a make in rate units per hour, a card's work
    in work units per second, a store's cap in quantity units)."""

    node: NodeId
    ranks_taken: int
    ranks: int
    before_value: int
    after_value: int


@dataclass(frozen=True)
class SkillPhase:
    """A skill's prestige phase as its row shows it (DESIGN.txt, "PRESTIGE PHASES"), all at save.time: its phase,
    level_counted (what a SkillLevel condition reads), at_top (phases.at_top), waiting_levels (the levels a click now
    would land, phases.waiting_levels), the menu in track order, undo_open (prestige.undo_open), mastered
    (prestige.mastered), pick_owed (prestige.pick_owed), topped_at (PhaseState.topped_at), the nodes its picks hold
    (`picked`, in click order, each of which MovePick may move) and the ranks parked on their new nodes."""

    phase: int
    level_counted: int
    at_top: bool
    waiting_levels: int
    menu: tuple[MenuNode, ...]
    undo_open: bool
    mastered: bool
    pick_owed: bool
    topped_at: int | None
    picked: tuple[NodeId, ...] = ()
    parked: tuple[ParkedRank, ...] = ()


@dataclass(frozen=True)
class SkillBar:
    skill: SkillId
    xp: Segment
    level: int
    """The shown level (phases.level_shown): under prestige it counts from 1 in each phase and stops at its top."""
    level_xp: int
    """XP at which `level` began (0 at level 1; the phase's start plus the curve's under prestige): the bar's left
    end."""
    next_level_xp: int | None
    """XP of the next level, the bar's right end; None at the last level or at the phase's top."""
    next_level_at: int | None
    prestige: SkillPhase | None = field(default=None, repr=False)
    """None with rules.prestige None. Left out of the repr, so the recorded fingerprints stay those of a game with no
    prestige."""


@dataclass(frozen=True)
class StandingBar:
    """An unlocked standing action and how it runs (FULL, or PAUSED by a dry store)."""

    action: ActionId
    run: RunKind


@dataclass(frozen=True)
class LaneBar:
    """Which card a lane is tapping (None: free), and when the tap ends. The bar itself is the card's (CardView).
    order: the index of the rule whose task the lane runs now (plan.lane_order), None while free or no rule taps it."""

    lane: LaneId
    card: CardId | None
    completes_at: int | None
    order: int | None = None


class RunBy(Enum):
    """Who is running a card now. On HANDS a tap yields the mix, so it is never both (DESIGN.txt, "One bar")."""

    TAP = "tap"
    MIX = "mix"


@dataclass(frozen=True)
class Need:
    """A store the card needs: quantity is the most of what one whole completion takes of it (under its modifiers, the
    same however far the bar has run) and any AtLeast requirement on that store's value; segment is how much there is
    now, the store's own segment (locked or not). A half-done card's tap needs only the rest of its input: whether a tap
    is ready is the blocker's to say, never the need's."""

    store: StoreId
    quantity: int
    segment: Segment


@dataclass(frozen=True)
class CardView:
    """An unlocked card that is not completed: one panel entry, the same whether it is tapped, mixed, both or neither.

    One bar: `bar` sampled and taken modulo bar_total is the card's progress toward its next completion, whoever runs
    it: the card's cumulative work (bar_total work_s * BP). by: who moves its work now: TAP, MIX while its mix share
    runs at a non-zero fraction,
    else None (paused, waiting, greyed or yielded; the bar holds still). completes_at: when a tap's bar next
    fills, or None (not tapped, or it will not by itself; a share claims no landing, since a rule that takes the hands
    yields the mix). share_bp and run: its share in the flattened running mix and
    that share's state whoever runs the card (a card tapped while mixed reads YIELDED; explain() gives its tap FULL);
    when several apply, the longest-lasting: GREYED, SPENT, PAUSED, WAITING, YIELDED. 0 and None when the running
    mix does not hold it. share_bp is the saved share; the card runs at it plus the sum of `gained`. completions and cap (effective; None: no cap) read "3 of 5". blocker None means a tap now is
    ready, and otherwise is what a failed tap now would fail on; it ignores the lane. cuts_in: a tap now starts it
    although its lane is busy (decisions.cuts_in). tap_s: seconds a tap started now
    takes (the rest of the current completion); None when the speed is 0. needs: what one completion needs, inputs,
    then drains (1 unit), then requires, one entry per store at the larger quantity."""

    card: CardId
    completions: int
    cap: int | None
    bar: Segment
    bar_total: int
    by: RunBy | None
    completes_at: int | None
    share_bp: int
    run: RunKind | None
    blocker: Blocker | None
    tap_s: int | None
    needs: tuple[Need, ...]
    cuts_in: bool
    spent_store: StoreId | None = field(default=None, repr=False)
    """The store a SPENT card is stopped on; None unless run is SPENT (DESIGN.txt, "SPENT")."""
    gained: tuple[SpentShare, ...] = field(default=(), repr=False)
    """What each paused or spent card of its mix on its lane gives it now, as explain()'s `gained`; () when none. Left
    out of the repr with spent_store, so the recorded fingerprints stay those of a game with no spent card."""


@dataclass(frozen=True)
class HeldView:
    """A card or standing action whose while_running entries are held now: its share (of its lane's time; BP for a
    standing action) and the entries as the stack holds them, each sourced "held:" + the runner (DESIGN.txt, "ENTRIES
    HELD WHILE A CARD RUNS", "HELD SPEED"). `card` is the runner's id: cards and standing actions share one namespace."""

    card: Runner
    share_bp: int
    entries: tuple[Modifier, ...]


@dataclass(frozen=True)
class CompletedCard:
    """An unlocked card at its cap: the Completed tab. Never tappable or mixable until a cap raise returns it."""

    card: CardId
    completions: int


@dataclass(frozen=True)
class AnswerView:
    """One answer of a shown offer: the card it sets running (offerstate.answer_card, None for none) and takes_s, the
    seconds one completion of that card would take on its lane started now at a full share (tap_seconds' formula, for a
    locked card too), None without a card or at speed 0."""

    answer: AnswerId
    card: CardId | None
    takes_s: int | None


@dataclass(frozen=True)
class OfferView:
    """A shown offer: `answer` the one given, None while it is open; its answers in the offer's order."""

    offer: OfferId
    answer: AnswerId | None
    answers: tuple[AnswerView, ...]
