"""The content file's entries, as Type Objects: each table an `opening.toml` or chapter file holds, validated on
load (schema.Opening and schema.Chapter are made of these)."""
from typing import Literal

from pydantic import Field, model_validator

from .entry_base import Entry
from .move_entries import CastEntry, JoinEntry, LeaveEntry, MarkEntry
from .site_entries import SiteEntry


class ItemAmount(Entry):
    store: str
    items: int = Field(ge=1)
    every: int = Field(default=1, ge=1)


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
    """items_per_hour items every `every_hours` hours, refused unless exact (engine design/, "FRACTIONS AT THE
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
    """The arrival queue's lines for one fight won, a pool the page draws from (api/contract/fights.txt, "FIGHTS"); empty:
    ui.fight.won. Words only: the engine never reads it."""
    lost_line_keys: list[str] = []
    """The same for one fight lost; empty: ui.fight.lost."""
    loss_pool: list[str] | None = None
    """With loss_notes, on_loss_key and loss_after, all or none: api/contract/loss-lines.txt, "LOSS LINES" (loss_checks.py)."""
    loss_notes: list[str] | None = None
    on_loss_key: str | None = None
    loss_after: str | None = None


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
    """Divides value and release alike, on a store only, refused unless exact (engine design/, "FRACTIONS AT
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


class WhereaboutsEntry(Entry):
    """Where an outcome puts a person, and what the scene shows of it (app/tests/test_scene_people.py): `layer` is the id of
    the scene layer that shows it, `no_scene` the reason nothing does. Exactly one; words only to the engine."""

    person: str
    layer: str | None = None
    no_scene: str | None = None

    @model_validator(mode="after")
    def _one_answer(self) -> "WhereaboutsEntry":
        if (self.layer is None) == (self.no_scene is None):
            raise ValueError("whereabouts: name exactly one of layer and no_scene")
        return self


class LineDoingsEntry(Entry):
    """The people a line shows doing something, for a line no outcome carries (a card's stage line, an offer's ask line): the
    same `doings` and `whereabouts` as an outcome's, authored under the line's key in `[line_doings]`."""

    doings: list[str]
    whereabouts: list[WhereaboutsEntry] = []
    clock: str | None = None
    """A moment clock (clocks.py) that starts when the line is told: from the card or offer whose `line_keys` hold it."""


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
    casts: list[CastEntry] = []
    """Only in a trigger's or an answer's outcome, one per role across the content (cast_checks.py)."""
    marks: list[MarkEntry] = []
    """Only in a trigger's or an answer's outcome (group_checks.py)."""
    doings: list[str] = []
    """People the lines show doing something besides joining or leaving: marked here, never read off the lines."""
    whereabouts: list[WhereaboutsEntry] = []
    """The scene's answer for each person the outcome joins, leaves or does something."""
    clock: str | None = None
    """A moment clock (clocks.py) that starts with this outcome, for the scene's window on it."""


class CardEntry(Entry):
    """One card (engine CardDef). cap: completions allowed, absent for no limit; a told step is a card with a cap of
    its step count and one line key per step. presentation dresses it on the page and changes no rule."""

    id: str
    lane: str = "hands"
    presentation: Literal["narrative", "action", "craft"]
    label_key: str
    upside_key: str | None = None
    upside_of: str | None = None
    """A runner, a standing action or a card, whose while_running entries the upside describes, served after the card's
    own changes: a recipe whose make that runner eats (api/contract/, {pct})."""
    variant_of: str | None = None
    """The card this one is a kind of (itself on the first): cards of one variant_of are one card on the Tasks page,
    with a kind picker (api/contract/, CardInfo.variant_of)."""
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
    stake: Literal["side", "speed", "reach"] | None = None
    """What a card that takes stores feeds: "side", a fight's side it holds an entry on while it runs (a later chapter
    may add the entry); "speed", a lane's speed it holds while it runs; "reach", a store its completions fill whose amount triggers read, each paying a modifier (its
    upside's figures are theirs). Required, with an upside_key, on a card that takes stores and gives nothing by itself
    (stake_checks.py)."""
    glows: bool = False
    """The one glow lands here the first time the card is ready while its lane is free: the opening's obvious next
    steps (docs/design/opening-screen/feedback.md, "Dots and the one glow"), said where the card is authored."""
    twin_of: str | None = None
    """On a townsperson's lane: the player's card this one is the town's version of (player_checks.py)."""
    only_player: Literal["alone", "story", "self", "fight", "magic", "station", "project"] | None = None
    """On a player's lane: why no townsperson has this card, as a tag (player_checks.py)."""
    site: SiteEntry | None = None
    """Where the scene shows this card's work done: a layer, or why there is none (site_checks.py, app/tests/test_scene_sites.py).
    A card and its `twin_of` name the same site."""


class TriggerEntry(Entry):
    id: str
    when: ConditionEntry
    outcome: OutcomeEntry
    season: bool = False
    """A season's turn: an `after_time` trigger the season checks read (season_checks.py). Words only to the engine."""
    requires: list[ConditionEntry] = []
    """Must also hold when `when` does, each on an unlock or a runner (engine TriggerDef.requires)."""
    line_only: bool = False
    """It exists to say its line once and gates nothing: lines only, and no condition names it (line_only_checks.py).
    The goals walk leaves it out. Words only to the engine."""
