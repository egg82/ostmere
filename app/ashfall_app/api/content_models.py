"""Wire models of the game's static content, fetched once (GET /api/content): text, the stores, cards, chips, skills,
lanes, the Camp bar and the first mix. The conventions in models.py hold here."""
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel

from .fight_models import SideInfo as SideInfo, ThreatInfo as ThreatInfo
from .feature_models import FeatureCard as FeatureCard, FeatureInfo
from .find_models import FindInfo as FindInfo
from .camp_models import CampInfo, CampLevel as CampLevel
from .journal_models import EntryInfo as EntryInfo, Hand as Hand, JournalInfo, NoteInfo as NoteInfo, Section as Section
from .lane_models import LaneInfo, LaneLabel as LaneLabel
from .line_models import LineInfo, PeopleInfo
from .map_models import PlaceInfo, Stamp as Stamp
from .models import Condition, OrderVerb, Unlock
from .need_models import SkillNeed as SkillNeed, StepNeed as StepNeed
from .skill_models import LevelPays as LevelPays, NodeChange as NodeChange, NodeInfo, NodeTarget as NodeTarget, SkillInfo
from .offer_models import AnswerGain as AnswerGain, AnswerInfo as AnswerInfo, KindRole as KindRole, OfferInfo, OfferKindInfo as OfferKindInfo


class Scales(BaseModel):
    quantity_per_item: int
    rate_per_item_hour: int
    bp: int


class Limits(BaseModel):
    """What the page's editors stop at (CONTRACT.txt, "Request limits"): a request past one is a 422."""

    max_orders: int
    max_queue: int
    max_mixes: int
    max_unless: int
    """Guards a rule may hold (Order.unless)."""
    max_or_else: int
    """Fallbacks a rule may hold after its first action (Order.or_else)."""
    reserved_mix_prefix: str
    """A new mix id beginning so is the game's: save_mix of one is a 422 (CONTRACT.txt, "The town's mix")."""


class TextEntry(BaseModel):
    key: str
    text: str


class CardPresentation(StrEnum):
    """How the page dresses a card; one mechanic under all three (CONTRACT.txt, "Cards")."""

    NARRATIVE = "narrative"
    """A told step (a cap of a few completions, each with its line)."""
    ACTION = "action"
    """Work done again and again (gathering)."""
    CRAFT = "craft"
    """A recipe, shown with its upside."""


class Amount(BaseModel):
    store: str
    quantity: int


class FightInfo(BaseModel):
    """The odds a fight card or standing action runs under (CONTRACT.txt, "FIGHTS"): the strengths' ids, and what one lost
    fight costs. The strengths themselves are View.fights."""

    side: str
    threat: str
    loses: list[Amount]
    """Taken from a store per lost fight."""
    wounds: list[Amount]
    """Added to a store per lost fight."""
    won_line_keys: list[str]
    """The arrival queue's pool for one fight won; empty: ui.fight.won."""
    lost_line_keys: list[str]
    """The pool for one fight lost; empty: ui.fight.lost."""
    loss_pool: list[str] | None
    """With loss_notes and on_loss_key: set on a card that tells its losses from its own pools, else null (LOSS LINES)."""
    loss_notes: list[str] | None
    on_loss_key: str | None


class ReachInfo(BaseModel):
    """What a card with the stake reach fills: its face draws the store against the next stop (CONTRACT.txt, "Cards")."""

    store: str
    stops: list[int]
    """Each reach's threshold on the store, in quantity units, in trigger order (ascending)."""


class KeptInfo(BaseModel):
    """One entry a card holds while it runs (CONTRACT.txt, {pct}): on a side's strength or a lane's speed, never both."""

    side: str | None
    lane: str | None
    amount_bp: int
    """At the card's full share; the View's fight entries are what applies, at the runner's share."""
    slot: int
    """The position in CardInfo.change_bp this entry's amount fills (two entries of one amount fill one slot)."""


class CardInfo(BaseModel):
    card: str
    lane: str
    """"hands": tappable and mixable; another lane: tappable only."""
    presentation: CardPresentation
    label_key: str
    upside_key: str | None
    """CRAFT only: the one upside the card names; the cost is for the player to work out."""
    variant_of: str | None
    """The card this one is a kind of: cards of one variant_of are drawn as one card on the Tasks page, with a picker
    of the kinds unlocked (CONTRACT.txt, "Cards"); null: a card of its own."""
    change_bp: list[int]
    """The modifiers of its outcome (at each completion, as a staged build's), of its finish and held while it runs (at
    its full share), then those its reach pays (triggers on the store it fills), as signed changes in basis points, as
    LevelPays.change_bp: the slots of upside_key."""
    kept: list[KeptInfo]
    """The card's own while_running entries, in content order: the slots of change_bp that scale with the runner's share
    (amount_bp * share // Scales.bp, as the engine rounds it). The standing action named as upside_of is not here: it runs
    at the full share."""
    work_s: int
    inputs: list[Amount]
    """Taken by each completion, paid as its work is done, tapped or mixed."""
    makes: list[str]
    """The stores its completions land or its flows fill, in content order: what a rule doing it is about first."""
    takes: list[str]
    """The stores its inputs, costs and drains take from, in content order."""
    reach: ReachInfo | None
    """Set on a card with the stake reach: the store its completions fill and the amounts at which its triggers pay. The
    face draws the store's amount and the next stop, since a rising line is not in the ledger until it is full."""
    skill_needs: list[SkillNeed]
    """The skill levels its requirements ask for, in requirement order."""
    step_needs: list[StepNeed]
    """The other cards' completions its requirements ask for, in requirement order."""
    glows: bool
    """The one glow lands on it the first time it is ready while its lane is free (CONTRACT.txt)."""
    fight: FightInfo | None
    """Set on a fight card (CONTRACT.txt, "FIGHTS")."""
    replaced_by: str | None
    """The card that takes this one's place once it retires, when the content names one: a greyed mix is fixed by the swap."""


class StoreInfo(BaseModel):
    store: str
    label_key: str
    cap: int
    """The cap a new game starts with; LedgerLine.cap is the cap now."""
    made_by: list[str]
    """The cards that make it, in card order: by what a completion lands or a make flow, or by training the skill
    whose level pays it, or by the completion a find waits on."""
    hidden: bool
    """The engine's bookkeeping (a clock, a countdown), never seen: no ledger line, in no served figure (AnswerInfo.gains)."""
    tally: bool
    """A count the game keeps (arrivals): no ledger line, but a card's need on it is drawn as have/need."""
    clock: Literal["dawn", "day", "evening", "night"] | None
    """The part of the story's day this clock counts through: a condition on it reads as that time (ui.when.*), never as
    an amount (CONTRACT.txt, "Cards", "Line causes")."""
    bonus_bp: int | None
    """Set on a store only eaters take from (standing actions, or a station's cards that take and make nothing), each
    holding a lane speed while it runs: that speed change, in basis points. Its ledger line is a bonus, never red, and
    says the bonus is off once dry (CONTRACT.txt, "Ledger")."""
    group_key: str | None
    """The label of the one ledger row this store shares with the stores of the same key, which opens on a tap to show
    each (CONTRACT.txt, "Ledger"); null: a row of its own."""


class StandingInfo(BaseModel):
    """A standing action: runs by itself while unlocked, outside every mix and lane."""

    action: str
    label_key: str
    skill: str | None
    fight: FightInfo | None
    """Set on a threat that runs on its own (CONTRACT.txt, "FIGHTS")."""


class FirstMix(BaseModel):
    """The first mix the page offers once `feature` is unlocked and no mix exists: `card_ids` at an even split, saved
    by the player's tap (CONTRACT.txt)."""

    feature: str
    card_ids: list[str]


class ChipInfo(BaseModel):
    chip: str
    label_key: str
    tone: str
    """A style token (e.g. "cold"), resolved by the page's stylesheet."""
    when: Condition
    """When the chip shows. A rule whose `when` equals it is worded as the chip (ui.rule.chip, ui.hands.while_chip),
    never by its numbers."""
    cost_key: str | None
    """What the chip costs while it shows, a few words drawn with it; null for a chip that changes nothing."""
    change_bp: list[int]
    """The chip's effects as signed changes in basis points, as LevelPays.change_bp: the slots of cost_key."""
    on_line_key: str | None
    off_line_keys: list[str]
    """The lines the chip writes as it turns on (once a save) and off (one of off_line_keys each time, in turn); a
    LogLine with card null and one of these keys is the chip's, whatever outcome also shows it."""
    offered_after: Unlock | None
    """Drawn only once view.unlocked holds this (its cure is on screen), as an OrderCard's offered_after."""
    chore: bool
    """A season's chore: every maker of the store it watches is a standing action a season's turn opens. One with no
    order card arrives with the hint dot alone, and its rule is the player's to write (docs/decisions/clock.md, "Each
    season brings its own chores")."""


class AimInfo(BaseModel):
    """What a stretch of play is for: one line at the band's top, in content order (CONTRACT.txt, "The client may")."""

    aim: str
    text_key: str
    after: Unlock | None
    """Set from when view.unlocked holds this; null only on the first aim, set from the start. The page shows the last
    aim whose `after` holds."""


class OrderCard(BaseModel):
    """The prefilled rule offered when a store's line is falling and uncovered: `when` is an at_most on `store`, which
    the page words from ui text (CONTRACT.txt, "Text and numbers"); `then` taps a card."""

    store: str
    when: Condition
    then: OrderVerb
    offered_after: Unlock | None
    """Offered only once view.unlocked holds this: the drain the order answers has begun."""
    chip: str | None
    """The chip this card answers (its `when` is that chip's): offered in the hands strip while the chip shows, never
    under a ledger line (CONTRACT.txt)."""
    after_end: bool
    """Offered only once view.ended_at is set and the end lines have been read."""


class Content(BaseModel):
    rules_digest: str
    scales: Scales
    limits: Limits
    text_entries: list[TextEntry]
    side_infos: list[SideInfo]
    threat_infos: list[ThreatInfo]
    find_infos: list[FindInfo]
    store_infos: list[StoreInfo]
    standing_infos: list[StandingInfo]
    card_infos: list[CardInfo]
    chip_infos: list[ChipInfo]
    feature_infos: list[FeatureInfo]
    order_cards: list[OrderCard]
    skill_infos: list[SkillInfo]
    node_infos: list[NodeInfo]
    """Every node of every skill's track, in track order; empty when the content has no prestige."""
    lane_infos: list[LaneInfo]
    offer_infos: list[OfferInfo]
    """Every offer, in content order (CONTRACT.txt, "Offers")."""
    offer_kinds: list[OfferKindInfo]
    """Every kind of offer with its role labels, in content order."""
    end_line_keys: list[str]
    """Lines the page appends to the log when the end happens (view.ended_at)."""
    line_infos: list[LineInfo]
    """Every text key a log line can carry (LogLine.key and end_line_keys), each once, with its kind and cause: the page
    sizes its story strip to the tallest it shows and sets each chronicle line by its kind, under its cause."""
    aim_infos: list[AimInfo]
    journal: JournalInfo | None
    """The book, its pages and their notes (CONTRACT.txt, "JOURNAL"); null until a chapter declares [journal]."""
    places: list[PlaceInfo]
    """Every place on the world map, in content order (CONTRACT.txt, "MAP"); empty when no chapter declares one."""
    camp: CampInfo | None
    people: PeopleInfo | None
    """The bands a day's mention is worded from (CONTRACT.txt, "People"); null until a chapter declares [people]."""
    first_mix: FirstMix
    town_later_labels: list[LaneLabel]
    """The town's name once `after` is unlocked: the label_key of the last whose `after` view.unlocked holds, else
    ui.town.title (CONTRACT.txt, "The town's mix")."""
    game_mix_ids: list[str]
    """The mix ids the game makes (the town's mixes its joins make): the game's own, worded by ui.town.title and changed
    in the town's editor. Every other saved mix is the player's (CONTRACT.txt, "The town's mix")."""
    transfer_code_s: int
    """How long a transfer code works (TransferCode.expires_in_s), for the text that says so ({minutes})."""

