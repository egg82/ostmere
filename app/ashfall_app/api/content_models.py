"""Wire models of the game's static content, fetched once (GET /api/content): text, the stores, cards, chips, skills,
lanes, the Camp bar and the first mix. The conventions in models.py hold here."""
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel

from .fight_models import SideInfo as SideInfo, ThreatInfo as ThreatInfo
from .find_models import FindInfo as FindInfo
from .camp_models import CampInfo, CampLevel as CampLevel
from .journal_models import EntryInfo as EntryInfo, Hand as Hand, JournalInfo, NoteInfo as NoteInfo, Section as Section
from .line_models import LineInfo, PeopleInfo
from .models import Condition, OrderVerb, Unlock
from .need_models import SkillNeed as SkillNeed, StepNeed as StepNeed
from .offer_models import AnswerGain as AnswerGain, AnswerInfo as AnswerInfo, OfferInfo


class Scales(BaseModel):
    quantity_per_item: int
    rate_per_item_hour: int
    bp: int


class Limits(BaseModel):
    """What the page's editors stop at (CONTRACT.txt, "Request limits"): a request past one is a 422."""

    max_orders: int
    max_queue: int
    max_mixes: int


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


class CardInfo(BaseModel):
    card: str
    lane: str
    """"hands": tappable and mixable; another lane: tappable only."""
    presentation: CardPresentation
    label_key: str
    upside_key: str | None
    """CRAFT only: the one upside the card names; the cost is for the player to work out."""
    change_bp: list[int]
    """The modifiers of its outcome (at each completion, as a staged build's), of its finish and held while it runs (at
    its full share), as signed changes in basis points, as LevelPays.change_bp: the slots of upside_key."""
    work_s: int
    inputs: list[Amount]
    """Taken by each completion, paid as its work is done, tapped or mixed."""
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
    bonus_bp: int | None
    """Set on a store only standing actions take from, each holding a lane speed while it runs: that speed change, in
    basis points. Its ledger line is a bonus, never red, and says the bonus is off once dry (CONTRACT.txt, "Ledger")."""


class StandingInfo(BaseModel):
    """A standing action: runs by itself while unlocked, outside every mix and lane."""

    action: str
    label_key: str
    skill: str | None
    fight: FightInfo | None
    """Set on a threat that runs on its own (CONTRACT.txt, "FIGHTS")."""


class LevelPays(BaseModel):
    """What a level brings, shown before it lands: words (pays_key), "?" for a story unlock."""

    level: int
    pays_key: str
    change_bp: list[int]
    """The level's modifiers as signed changes in basis points (+1000 is +10%), each distinct value once, in the order
    authored; the {pct} and {pct_b} slots of pays_key. Empty for a level that pays a find."""


class NodeTarget(StrEnum):
    MAKE = "make"
    WORK = "work"
    CAP = "cap"


class NodeChange(BaseModel):
    """What a node's ranks change, as the content authors it: `make`, what runner `id` (a card or standing action)
    makes of `store`; `work`, card `id`'s work speed; `cap`, store `id`'s cap. The page names it by those ids' labels."""

    target: NodeTarget
    id: str
    store: str | None


class NodeInfo(BaseModel):
    """One node of `skill`'s prestige track (CONTRACT.txt, "PRESTIGE PHASES"); SkillPrestige.menu_nodes names it."""

    node: str
    skill: str
    label_key: str
    change: NodeChange


class SkillInfo(BaseModel):
    skill: str
    label_key: str
    levels: list[LevelPays]
    """The levels that bring something, in order: the row shows the first above its level."""


class FirstMix(BaseModel):
    """The first mix the page offers once `feature` is unlocked and no mix exists: `card_ids` at an even split, saved
    by the player's tap (CONTRACT.txt)."""

    feature: str
    card_ids: list[str]


class LaneLabel(BaseModel):
    after: Unlock
    label_key: str


class LaneInfo(BaseModel):
    """Every lane, "hands" included. Its label is the label_key of the last of later_labels whose `after`
    view.unlocked holds, else label_key (CONTRACT.txt, "A lane run by rules")."""

    lane: str
    label_key: str
    ruled: bool
    """A townsperson who works: the player's rules set its task, never their tap."""
    later_labels: list[LaneLabel]
    name_key: str | None
    """The person's name, filling every text's {<lane>} slot (CONTRACT.txt, "Text and numbers"); null: no name."""
    told: Literal["line", "mention"] | None
    """How a person's coming and going is written (CONTRACT.txt, "People"); null for a lane that is not a person."""


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
    off_line_key: str | None
    """The lines the chip writes as it turns on and off (a LogLine with card null and one of these keys is the chip's,
    whatever outcome also shows it)."""
    offered_after: Unlock | None
    """Drawn only once view.unlocked holds this (its cure is on screen), as an OrderCard's offered_after."""


class FeatureCard(BaseModel):
    title_key: str
    line_keys: list[str]
    button_key: str
    """Its one button, which puts the card away."""


class FeatureInfo(BaseModel):
    feature: str
    hint_key: str | None
    """A banner shown once when the feature unlocks."""
    label_key: str | None
    """A thing the player carries, shown with the chips once the feature unlocks."""
    feature_card: FeatureCard | None
    """A card shown once when the feature unlocks, after what came with it (CONTRACT.txt, "A feature's card")."""


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
    end_line_keys: list[str]
    """Lines the page appends to the log when the end happens (view.ended_at)."""
    line_infos: list[LineInfo]
    """Every text key a log line can carry (LogLine.key and end_line_keys), each once, with its kind and cause: the page
    sizes its story strip to the tallest it shows and sets each chronicle line by its kind, under its cause."""
    aim_infos: list[AimInfo]
    journal: JournalInfo | None
    """The book, its pages and their notes (CONTRACT.txt, "JOURNAL"); null until a chapter declares [journal]."""
    camp: CampInfo | None
    people: PeopleInfo | None
    """The bands a day's mention is worded from (CONTRACT.txt, "People"); null until a chapter declares [people]."""
    first_mix: FirstMix
    transfer_code_s: int
    """How long a transfer code works (TransferCode.expires_in_s), for the text that says so ({minutes})."""

