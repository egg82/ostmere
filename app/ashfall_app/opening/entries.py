"""The content file's entries, as Type Objects: each table an `opening.toml` or chapter file holds, validated on
load (schema.Opening and schema.Chapter are made of these)."""
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Entry(BaseModel):
    """Content is our own file one directory away: an unknown field is a typo, so it fails the load."""

    model_config = ConfigDict(extra="forbid")


class ItemAmount(Entry):
    store: str
    items: int = Field(ge=1)
    every: int = Field(default=1, ge=1)


class StoreEntry(Entry):
    id: str
    label_key: str
    cap_items: int = Field(ge=1)
    initial_items: int = Field(default=0, ge=0)
    tally: bool = False
    """A count the game keeps and no card spends (arrivals): only an outcome adds to it, a gate reads it, and no card
    takes it as a cost or an input (tally_checks.py)."""
    hidden: bool = False
    """The engine's bookkeeping (a clock, a countdown) the player never sees: no ledger line, in no served figure
    (api/CONTRACT.txt, StoreInfo.hidden)."""


class LevelPaysEntry(Entry):
    """What a skill's level brings, shown on its row before it lands: words, pays_unknown for a story unlock. The payout itself
    is a trigger on the level (a find) or a requirement that reads it (a craft made ready)."""

    level: int = Field(ge=2)
    pays_key: str


class SkillEntry(Entry):
    id: str
    label_key: str
    levels: list[LevelPaysEntry] = []


class FlowEntry(Entry):
    """items_per_hour items every `every_hours` hours, refused unless exact (engine DESIGN.txt, "FRACTIONS AT THE
    LOADER")."""

    store: str
    items_per_hour: int = Field(ge=0)
    every_hours: int = Field(default=1, ge=1)


class WhileRunningEntry(Entry):
    """A side (engine WhileRunning) or a declared lane's speed (engine HeldSpeed) that a card or standing action raises by
    `amount_bp` while it runs, exactly one of the two named; the engine checks the side and the lane."""

    side: str | None = None
    lane: str | None = None
    amount_bp: int = Field(ge=1)

    @model_validator(mode="after")
    def _one_target(self) -> "WhileRunningEntry":
        if (self.side is None) == (self.lane is None):
            raise ValueError("while_running: name exactly one of side and lane")
        return self


class FightEntry(Entry):
    """A card's or standing action's fight (engine FightDef): `lost` is the tally store of lost fights, `fought` that of
    all fights (a standing fight only). fights_per_hour is a standing fight's rate in whole fights, required there and
    absent on a card. loses are taken, wounds added, per lost fight."""

    side: str
    threat: str
    lost: str
    fought: str | None = None
    fights_per_hour: int = Field(default=0, ge=0)
    loses: list[ItemAmount] = []
    wounds: list[ItemAmount] = []
    won_line_keys: list[str] = []
    """The arrival queue's lines for one fight won, a pool the page draws from (api/CONTRACT.txt, "FIGHTS"); empty:
    ui.fight.won. Words only: the engine never reads it."""
    lost_line_keys: list[str] = []
    """The same for one fight lost; empty: ui.fight.lost."""


class StandingEntry(Entry):
    """A standing action: runs by itself while unlocked (a fire burning, a body getting hungry)."""

    id: str
    label_key: str
    skill: str | None = None
    xp_per_hour: int = Field(default=0, ge=0)
    makes: list[FlowEntry] = []
    costs: list[FlowEntry] = []
    fight: FightEntry | None = None
    while_running: list[WhileRunningEntry] = []


class UnlockEntry(Entry):
    """offer: the offer is shown; answered: it has been answered, by either answer (its id the offer's); answer: this
    answer was given. Only an answer adds those two, only a join adds joined and only a leave adds left (their ids a
    lane's), so only gates and conditions name them."""

    unlock_kind: Literal["action", "card", "skill", "store", "chip", "feature", "retired", "offer", "answered", "answer", "joined",
                         "left", "entry", "note"]
    id: str
    replaced_by: str | None = None
    """On a `retired` unlock only: the card that takes the retired one's place, which the same outcome unlocks. The page
    teaches a mix still holding the retired card to swap it for this one."""


class LaneLabelEntry(Entry):
    """The lane row's label once `after` is unlocked (the last one held wins, as aims do)."""

    after: UnlockEntry
    label_key: str


class LaneEntry(Entry):
    """A lane besides the hands. ruled: a townsperson who works, whose task the player's rules set; its cards have no
    skill and no XP, and fill the camp store as hands cards do (engine DESIGN.txt, "Ruled lane")."""

    id: str
    label_key: str
    ruled: bool = False
    later_labels: list[LaneLabelEntry] = []
    name_key: str | None = None
    """The person's name, as a label writes it: the page fills a text's `{<lane id>}` slot with it (api/CONTRACT.txt,
    "Text and numbers")."""


class ConditionEntry(Entry):
    """One condition in the order vocabulary. subject_kind picks the subject; `id` names it (a store, skill, card,
    action, a ruled lane for "lane_rules", or for "unlocked" the unlock's id with unlock_kind). Thresholds in whole items for stores."""

    test: Literal["at_least", "at_most", "after_time"]
    subject_kind: Literal["store", "skill_level", "card_count", "unlocked", "running", "lane_rules"] | None = None
    id: str | None = None
    unlock_kind: Literal["action", "card", "skill", "store", "chip", "feature", "retired", "offer", "answered",
                         "answer", "left", "entry", "note"] | None = None
    value: int
    release: int | None = None
    """Defaults to value (a plain threshold)."""
    every: int = Field(default=1, ge=1)
    """Divides value and release alike, on a store only, refused unless exact (engine DESIGN.txt, "FRACTIONS AT
    THE LOADER")."""


class ModifierEntry(Entry):
    """target: "rate" (runner + flow + store), "work" (card), "lane" (lane), "cap" (a store's cap, raised only), or
    "side" or "threat" (a strength; a threat's only in a trigger's outcome). amount_bp as in the engine."""

    target: Literal["rate", "work", "lane", "cap", "side", "threat"]
    id: str
    flow: Literal["make", "cost", "xp"] | None = None
    store: str | None = None
    kind: Literal["add_bp", "mul_bp"]
    amount_bp: int
    source: str


class CapRaiseEntry(Entry):
    card: str
    by: int = Field(ge=1)


class InstallEntry(Entry):
    """A rule an outcome installs: the always rule tapping `tap_card`, a card on a ruled lane, at the top of the rules
    (first) or at their end (engine RuleInstall)."""

    tap_card: str
    first: bool = False


class JoinEntry(Entry):
    """A person joins the town (engine Join): the ruled lane `lane`'s person is present from now on, and the lane's
    always task becomes its share in the town mix `mix` (an id beginning "town:"). `card` is the share when the lane has
    no uncapped always rule. `counted`: a tally counted this person when they arrived, so the join adds none."""

    lane: str
    mix: str
    card: str | None = None
    counted: bool = False


class LeaveEntry(Entry):
    """A person leaves the town for good (engine Leave): the ruled lane `lane`'s person is gone, and each standing
    action in `stops` stops with them."""

    lane: str
    stops: list[str] = []


class OutcomeEntry(Entry):
    stores: list[ItemAmount] = []
    unlocks: list[UnlockEntry] = []
    modifiers: list[ModifierEntry] = []
    raises: list[CapRaiseEntry] = []
    starts: list[str] = []
    line_keys: list[str] = []
    found_line_key: str | None = None
    """One of `line_keys`, whose text holds the slot `{found}`: the whole items of this outcome's one store, the amount
    a find found. Only in a trigger's outcome."""
    orders: list[InstallEntry] = []
    """Only in a trigger's or an answer's outcome."""
    queues: list[str] = []
    """Hands cards with a cap, each put at the queue's front as a When ready entry; only in an answer's outcome."""
    joins: list[JoinEntry] = []
    """Only in a trigger's or an answer's outcome."""
    retire_orders: list[str] = []
    """Chores' cures whose orders go at a season's turn; only there (retire_checks.py)."""
    leaves: list[LeaveEntry] = []
    """Only in a trigger's or an answer's outcome, one per lane across the content (leave_checks.py)."""


class CardEntry(Entry):
    """One card (engine CardDef). cap: completions allowed, absent for no limit; a told step is a card with a cap of
    its step count and one line key per step. presentation dresses it on the page and changes no rule."""

    id: str
    lane: str = "hands"
    presentation: Literal["narrative", "action", "craft"]
    label_key: str
    upside_key: str | None = None
    upside_of: str | None = None
    """A standing action whose while_running entries the upside describes, served after the card's own changes: a
    recipe whose make that action eats (api/CONTRACT.txt, {pct})."""
    work_s: int = Field(ge=1)
    skill: str | None = None
    xp_per_hour: int = Field(default=0, ge=0)
    makes: list[FlowEntry] = []
    costs: list[FlowEntry] = []
    inputs: list[ItemAmount] = []
    drains: list[ItemAmount] = []
    """Takes of up to `items` per completion, forgiven at 0 (engine CardDef.drains)."""
    requires: list[ConditionEntry] = []
    outcome: OutcomeEntry = OutcomeEntry()
    cap: int | None = Field(default=None, ge=1)
    finished: OutcomeEntry = OutcomeEntry()
    line_keys: list[str] = []
    fight: FightEntry | None = None
    while_running: list[WhileRunningEntry] = []
    glows: bool = False
    """The one glow lands here the first time the card is ready while its lane is free: the opening's obvious next
    steps (docs/design/opening-screen.md, "Dots and the one glow"), said where the card is authored."""


class ChipEntry(Entry):
    id: str
    label_key: str
    tone: str
    when: ConditionEntry
    effects: list[ModifierEntry] = []
    cost_key: str | None = None
    """What `effects` cost the player, in two or three words drawn with the chip; set exactly when it has effects."""
    on_line_key: str | None = None
    off_line_key: str | None = None
    no_cure: bool = False
    """Shown with nothing the player can do about it, on purpose: the day-one gate that every chip shown has a cure
    (tests/dayone/cures.py) passes it over."""
    offered_after: UnlockEntry | None = None
    """Drawn on the page only once this is unlocked, as an order card's is offered: the chip's cure is on screen. The
    engine's latch is the same either way, so a chip with effects has none (its cost would run unseen); unlock such a
    chip with its cure instead."""


class TriggerEntry(Entry):
    id: str
    when: ConditionEntry
    outcome: OutcomeEntry
    season: bool = False
    """A season's turn: an `after_time` trigger the season checks read (season_checks.py). Words only to the engine."""
    requires: list[ConditionEntry] = []
    """Must also hold when `when` does, each on an unlock or a runner (engine TriggerDef.requires)."""


class OrderCardEntry(Entry):
    """The prefilled rule for a store's line: `when` an at_most on that store, offered under its falling line, or an
    at_least, offered under its full or rising line while the card it taps (one that takes that store) is idle; the
    page words it from ui text. then: a card to tap, or a mix to switch to."""

    store: str
    when: ConditionEntry
    tap_card: str | None = None
    switch_mix: str | None = None
    offered_after: UnlockEntry | None = None
    """Offered only once this is unlocked: the drain the order answers has begun (a line falling for a moment before
    then, a roast drawing roots, gets no order card)."""
    chip: str | None = None
    """The chip this card answers: offered in the hands strip while that chip shows, not under a ledger line, and
    `when` is that chip's own (the rule reads as the chip)."""
    after_end: bool = False
    """Offered only after the end, once its lines have been read: a step taught past the opening. Needs `chip`."""

