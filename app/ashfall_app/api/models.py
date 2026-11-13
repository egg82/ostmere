"""Wire models of the game API: one schema per resource, one type per field name, typed errors. The save endpoints'
own models (accounts, saves, their requests) are saves_models.py; the decisions and the shapes they share with the
view (requests, conditions, mixes, orders, the queue) are decision_models.py, re-exported here.

Method: contract-first API design (one schema per resource, one type per field name). The engine's types are stdlib dataclasses; these are their wire form, and
convert.py (stage 2) maps between them. Conventions binding here:
- Ids are strings; a field named after a kind (`store`, `action`, `card`, `lane`, `skill`, `chip`) is always that
  kind's id; `runner` is a standing action's or a card's id (they share one namespace). A field holding a whole
  object is named for the object (`mix: Mix`), an id of it `<kind>_id`.
- Times are integer engine seconds (`at`, `start`, `*_at`); quantities and rates are the engine's fixed-point
  integers, scaled by Scales (served once in Content), never floats.
- Text is never here: every `*_key` is a key into Content.text.
- A collection key names its item type: View.cards holds Card, Content.card_infos CardInfo;
  a condition's subject is `watched` (`subject` is a commit subject in main.py's Change).
- extra="forbid" on requests: a request is the page's own code, so an unknown field is a bug to see at once.
"""
from enum import StrEnum

from pydantic import BaseModel

from .decision_models import (
    Request as Request, Segment as Segment, StoreValue as StoreValue, SkillLevel as SkillLevel,
    CardCount as CardCount, UnlockKind as UnlockKind, Unlock as Unlock, Unlocked as Unlocked, Running as Running,
    Subject as Subject, AtLeast as AtLeast, AtMost as AtMost, AfterTime as AfterTime, Condition as Condition,
    CardShare as CardShare, SubMix as SubMix, Mix as Mix, SwitchMix as SwitchMix, TapCard as TapCard,
    OrderVerb as OrderVerb, Order as Order, QueueEntry as QueueEntry, SaveMix as SaveMix, DeleteMix as DeleteMix,
    SetOrders as SetOrders, SetQueue as SetQueue, AnswerOffer as AnswerOffer, AnswerKind as AnswerKind, Decision as Decision,
    Prestige as Prestige, UndoPick as UndoPick, MovePick as MovePick,
)
from .fight_models import Fight as Fight, Strength as Strength, StrengthEntry as StrengthEntry, StrengthKind as StrengthKind
from .need_models import Blocker as Blocker, Need as Need
from .offer_models import Offer as Offer, OfferAnswer as OfferAnswer
from .goal_models import Goal as Goal, GoalKind as GoalKind, GoalLimit as GoalLimit, GoalRow as GoalRow, RuleDry as RuleDry
from .repeat_models import RepeatedSwitch as RepeatedSwitch, RepeatedTap as RepeatedTap, Repeats as Repeats
from .rulerun_models import RuleRun as RuleRun
from .spent_models import SpentShare as SpentShare
from .phase_models import MenuNode as MenuNode, ParkedPick as ParkedPick, SkillPrestige as SkillPrestige
from .forecast_models import (
    ForecastLevel as ForecastLevel, ForecastFull as ForecastFull, ForecastEmpty as ForecastEmpty, Forecast as Forecast,
    ForecastAnswer as ForecastAnswer, ForecastTop as ForecastTop,
)


# ---------- the view (what the client draws) ----------

class RunKind(StrEnum):
    FULL = "full"
    PAUSED = "paused"
    YIELDED = "yielded"
    WAITING = "waiting"
    """A mix card whose requirement does not hold yet."""
    GREYED = "greyed"
    """A card of the running mix while the mix is greyed."""
    SPENT = "spent"
    """Its share runs nothing and its store will not refill by itself; the rest of its mix runs the share."""


class OrderState(StrEnum):
    """Where a rule stands now, so the page can say why one is off (CONTRACT.txt, "THE CLIENT MAY")."""

    ON = "on"
    """A mix rule whose mix runs (it is View.mix_order), or a task rule whose condition holds."""
    WAITING = "waiting"
    """Its condition does not hold now."""
    OUTRANKED = "outranked"
    """A mix rule whose condition holds while an earlier rule, View.mix_order, has the hands; a task rule whose
    condition holds while its card's lane runs an earlier rule's task (orders[LaneBar.order])."""
    PASSED_OVER = "passed_over"
    """It cannot act whatever its condition: its mix is greyed (in greyed_mix_ids), or its task is completed."""


class RunBy(StrEnum):
    """Who runs a card now: never both on the hands, since a tap yields the mix."""

    TAP = "tap"
    MIX = "mix"


class Contribution(BaseModel):
    runner: str
    per_hour: int
    """Signed: + makes, - costs, in rate units."""


class LedgerLine(BaseModel):
    store: str
    segment: Segment
    net_per_hour: int
    contributions: list[Contribution]
    empties_at: int | None
    fills_at: int | None
    falling: bool
    covered: bool
    """Some order or the queue head makes this store. A falling, uncovered line is the one to offer an order card."""
    starved: bool
    """The store has run dry while something waits on it (a card paused on it that is not spent, or a tap an order or
    the queue is waiting to make): a problem to draw red whether covered or not."""
    cap: int
    """What the store holds now: StoreInfo.cap as raised by any level that raises it."""


class SkillBar(BaseModel):
    skill: str
    xp: Segment
    level: int
    level_xp: int
    """XP at which `level` began (0 at level 1): the bar's left end."""
    next_level_xp: int | None
    """XP of the next level, the bar's right end; null at the last level (the bar is full)."""
    next_level_at: int | None
    prestige: SkillPrestige | None
    """Null when the content has no prestige; `level` is then the curve's, else the phase's shown level."""


class StandingBar(BaseModel):
    """An unlocked standing action, maker or consumer: full, or paused by a dry store."""

    action: str
    run: RunKind


class LaneBar(BaseModel):
    """Which card a lane is tapping, and when the tap ends. The bar is the card's own (Card.bar)."""

    lane: str
    running_card: str | None
    """null while the lane is free."""
    completes_at: int | None
    order: int | None
    """Index into orders of the rule whose task the lane runs now; null while free or no rule taps what it runs."""


class Card(BaseModel):
    """An unlocked card that is not completed: one entry of the card panel, the same whether tapped, mixed or idle.
    Tappable iff blocker is null and its lane's LaneBar has no running_card or cuts_in is true."""

    card: str
    completions: int
    cap: int | None
    """Completions allowed, raised caps included; null: no cap. Draw "completions of cap"."""
    bar: Segment
    """The card's one bar, whoever runs it: sample it and draw the remainder modulo bar_total."""
    bar_total: int
    by: RunBy | None
    """Who moves its work now: tap, or mix while its share runs; null: nobody (paused,
    waiting, greyed or yielded), the bar holds still."""
    completes_at: int | None
    """When a tap's bar next fills; null: not tapped (a share claims no landing: a rule may take the hands from the
    mix), or it will not by itself."""
    share_bp: int
    """Its share in the running mix (flattened) as the player set it; 0 when the running mix does not hold it. It runs
    at share_bp plus the sum of gained."""
    run: RunKind | None
    """How its mix share runs, whoever runs the card (yielded while it or another card is tapped); the longest-lasting
    of greyed, spent, paused, waiting, yielded when several apply; null when the running mix does not hold it."""
    blocker: Blocker | None
    """null means a tap now is ready; otherwise what a tap now fails on (a failed tap: CONTRACT.txt)."""
    tap_s: int | None
    """Seconds a tap started now takes; null when its speed is 0. Draw this, not
    CardInfo.work_s, which is the time at full speed."""
    needs: list[Need]
    """The stores a tap needs, inputs in CardInfo order then requirements."""
    cuts_in: bool
    """A tap now starts it although its lane is busy: a glowing step not yet done, while the hands run a task the queue
    or a rule starts again once it lands, or a cure for a chip shown now, while the hands run a task that is not one
    (CONTRACT.txt, "Cut-in")."""
    spent_store: str | None
    """The store a spent card is stopped on; null unless run is spent."""
    gained: list[SpentShare]
    """What each spent card of its mix on its lane gives it now, in mix order; empty when none (CONTRACT.txt, "SPENT")."""


class CompletedCard(BaseModel):
    """An unlocked card at its cap: the Completed tab. It returns to View.cards if a cap is raised."""

    card: str
    completions: int


class LogLine(BaseModel):
    at: int
    seq: int
    key: str
    card: str | None
    """The card whose completion, tap or failed tap wrote the line, however it was run (a tap, the mix, a rule);
    null for a chip's line, a trigger's and the opening's first lines."""


class View(BaseModel):
    at: int
    next_event_at: int | None
    """Sample until this time, then step again (null: nothing will happen by itself)."""
    ledger: list[LedgerLine]
    skills: list[SkillBar]
    standing: list[StandingBar]
    lanes: list[LaneBar]
    cards: list[Card]
    """The card panel, in CardInfo order."""
    completed: list[CompletedCard]
    """The Completed tab, in CardInfo order."""
    greyed_mix_ids: list[str]
    """Saved mixes holding a completed card: drawn grey, offered only edit and delete."""
    chips: list[str]
    chips_seen: list[str]
    """Every chip the save has shown, now included, in content order: a rule may watch any of them (CONTRACT.txt,
    "The condition editor")."""
    unlocked: list[Unlock]
    all_covered: bool
    """No ledger line falling uncovered and none starved (true at time 0). Live: not the end on its own."""
    ended_at: int | None
    """Game time the end happened (CONTRACT.txt, "The end"), or null. Once set it never clears."""
    mixes: list[Mix]
    active_mix_id: str | None
    """The player's own mix: what runs when no rule's or queue entry's mix does. Only the player's switch_mix sets it."""
    running_mix_id: str | None
    """The mix the hands run now: the first rule that is on with a mix that isn't greyed, else the controlling queue
    entry's mix when it is a switch_mix (CONTRACT.txt, "Goal stints"), else active_mix_id."""
    mix_order: int | None
    """Index into orders of the rule whose mix runs; null when the queue's or the player's own mix runs."""
    running_town_mix_id: str | None
    """The town mix running now: the first rule that is on with a switch_mix of a town mix that isn't greyed; null when
    none runs (CONTRACT.txt, "The town's mix"). running_mix_id reads hands mixes alone."""
    town_mix_order: int | None
    """Index into orders of the rule whose town mix runs; null when none does."""
    orders_on: list[bool]
    """orders_on[i]: orders[i]'s condition holds now."""
    order_states: list[OrderState]
    """order_states[i]: where orders[i] stands now."""
    order_dry: list[RuleDry | None]
    """order_dry[i]: a store rule whose mix is, or may be, short of an input (CONTRACT.txt, "Dry rules"); else null."""
    runs_out_at: int | None
    """When the running mix first runs a store it costs to empty: the earliest empties_at among falling ledger lines
    that a card of the flattened running mix costs. null: no running mix, or it runs indefinitely as set."""
    orders: list[Order]
    queue: list[QueueEntry]
    """The player's plan as it stands: edit it and send the whole list back (set_orders, set_queue replace)."""
    offers: list[Offer]
    """Every offer shown so far, in content order (CONTRACT.txt, "Offers")."""
    fights: list[Fight]
    """One per unlocked fight card, then standing fight, each in content order (CONTRACT.txt, "FIGHTS")."""
    goals: list[Goal]
    """What the next beat waits on, unmet: at most one step of work, then at most one clock (CONTRACT.txt, "Goals")."""
    goal_rows: list[GoalRow]
    """Each goal a mix can move, when it lands at the rates as set and what binds it (CONTRACT.txt, "Goal rows")."""


class Step(BaseModel):
    """A save as just written: what to draw, and the lines the game wrote since it was last written."""

    save_id: int
    decisions: int
    """The save's decisions so far: the next decision's `after`."""
    rules_digest: str
    build: str
    """The server's build (as /page-config.json's version): a page booted on another reloads itself at a quiet moment."""
    view: View
    lines: list[LogLine]
    failed_tap: str | None
    """The card, when this answers the player's tap of it and it was not ready: a failed tap, which took no time and
    changed nothing and emitted no line; the card's blocker in view is what stopped it."""
    repeats: Repeats
    """What the player keeps doing by hand, as of view.at (CONTRACT.txt, "Repeats")."""
    rule_runs: list[RuleRun]
    """What the rules did lately, the most recent change first (CONTRACT.txt, "Rule runs")."""
    catching_up_to: int | None
    """Set when this request's time ran out before the save reached now: the game time it was advancing to (view.at
    is short of it). Ask advance again at once until it is null (CONTRACT.txt, "Catching up")."""
