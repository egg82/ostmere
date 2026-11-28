"""The opening's content file, as Type Objects: what `opening.toml` beside this module holds, validated on load.

The file is public (the first fifteen minutes only) and is the one home of the opening's data: the engine's Rules,
the game API's static Content and the text table all come from it (docs/engineering.md, "A value the server and
the page both need lives in one data file"). TOML, so loading needs only the stdlib (tomllib). Not in `content/` at the
repo root, whose story material is never shipped; this directory is shipped.

Authoring units are whole items and seconds; to_rules() converts to the engine's fixed point. A fraction is written
as `items` per `every` completions, and must divide exactly into quantity units (validated, never rounded).
Every `*_key` must be a key of `text`, and `text` holds the fixed `ui.*` keys the page needs (validated).
"""
import tomllib
from pathlib import Path
from typing import Literal, NoReturn

from ..engine import Rules, validate_rules
from .chapters import merge
from .entries.fight_entries import SideEntry, ThreatEntry
from .entries.journal_entries import JournalDecl, JournalEntry, NoteEntry
from .entries.map_entries import PlaceEntry
from .entries.offer_entries import OfferEntry, OfferKindEntry
from .expand.phase_pays import PhasePaysEntry
from .prestige import NodeEntry, PrestigeEntry
from .expand.town import TownCardEntry
from .expand.workings import WorkingEntry
from .people import PeopleEntry
from .expand.expansions import with_expansions
from .entries.close_call_entries import CloseCallEntry
from .checks.run import check_content, check_opening, check_structure
from .line_kinds import LineKind
from .checks.world.journal_checks import check_first_notes
from .expand.convert import build_rules
from .entries.camp_entries import CampEntry, CampLevelEntry
from .entries.chip_entries import ChipEntry
from .entries.setting_entries import FirstMixEntry, JournalHabitsEntry, RepeatOffersEntry
from .entries.subject_entries import SubjectEntry
from .entries.entries import (
    CardEntry, Entry, LevelPaysEntry, LineDoingsEntry, SkillEntry, StandingEntry, TriggerEntry,
    UnlockEntry, WhileRunningEntry,
)
from .entries.lane_entries import LaneEntry, LaneLabelEntry
from .entries.order_entries import OrderCardEntry
from .entries.store_entries import StoreEntry
from .entries.feature_entries import AimEntry, FeatureCardEntry, FeatureEntry

# Re-exported (`X as X`): the content files' paths are imported from here.
from .chapter_files import (
    OPENING as OPENING, DAY_ONE as DAY_ONE, DAY_TWO as DAY_TWO, DAY_THREE as DAY_THREE, DAY_FOUR as DAY_FOUR,
    DAY_FIVE as DAY_FIVE, B7 as B7, DAY_SIX as DAY_SIX, DAY_EIGHT as DAY_EIGHT, DAY_NINE as DAY_NINE,
    DAY_ELEVEN as DAY_ELEVEN, DAY_TWELVE as DAY_TWELVE, DAY_FIFTEEN as DAY_FIFTEEN, DAY_SIXTEEN as DAY_SIXTEEN,
    DAY_EIGHTEEN as DAY_EIGHTEEN, DAY_NINETEEN as DAY_NINETEEN, DAY_TWENTY_TWO as DAY_TWENTY_TWO,
    DAY_TWENTY_THREE as DAY_TWENTY_THREE, DAY_TWENTY_FIVE as DAY_TWENTY_FIVE, DAY_TWENTY_SEVEN as DAY_TWENTY_SEVEN,
    DAY_TWENTY_NINE as DAY_TWENTY_NINE, DAY_THIRTY as DAY_THIRTY, DAY_THIRTY_ONE as DAY_THIRTY_ONE,
    DAY_THIRTY_THREE as DAY_THIRTY_THREE,
    PRESTIGE as PRESTIGE, PHASE_PAYS as PHASE_PAYS, CHAPTERS as CHAPTERS, IN_WRITING as IN_WRITING,
    UNWRITTEN as UNWRITTEN,
)


class Opening(Entry):
    version: Literal[1]
    end_card: FeatureCardEntry | None = None
    """The one out-of-fiction card for the edge of the written content: merge_chapters puts it on the last shipped
    chapter's end_feature, so a chapter's features carry no card of their own."""
    stores: list[StoreEntry]
    skills: list[SkillEntry]
    standing: list[StandingEntry] = []
    sides: list[SideEntry] = []
    threats: list[ThreatEntry] = []
    hands_label_key: str
    """The label of the HANDS lane, which is never declared in `lanes`."""
    lanes: list[LaneEntry] = []
    town_later_labels: list[LaneLabelEntry] = []
    """The town's shown name once `after` is unlocked (the last one held wins), else `ui.town.title`: a chapter's."""
    cards: list[CardEntry]
    town_cards: list[TownCardEntry] = []
    """Only what chapters.merge carries; the opening's own file holds none (load_opening refuses it)."""
    chips: list[ChipEntry] = []
    triggers: list[TriggerEntry] = []
    features: list[FeatureEntry] = []
    order_cards: list[OrderCardEntry] = []
    offers: list[OfferEntry] = []
    offer_kinds: list[OfferKindEntry] = []
    journal: JournalDecl | None = None
    entries: list[JournalEntry] = []
    notes: list[NoteEntry] = []
    subjects: list[SubjectEntry] = []
    """What the journal's days are written about (subject_entries.py)."""
    places: list[PlaceEntry] = []
    start: list[UnlockEntry]
    """The unlock set a new save starts with (Rules.opening)."""
    camp: CampEntry | None = None
    prestige: PrestigeEntry | None = None
    people: PeopleEntry | None = None
    close_calls: list[CloseCallEntry] = []
    nodes: list[NodeEntry] = []
    phase_pays: list[PhasePaysEntry] = []
    """Only what chapters.merge carries, each entry kept so a later chapter's ranks expand their phases."""
    first_mix: FirstMixEntry
    repeat_offers: RepeatOffersEntry
    journal_habits: JournalHabitsEntry
    end_line_keys: list[str] = []
    """Lines the page appends at the end moment (api/contract/the-end.txt, "The end"): no engine event marks it."""
    end_feature: str
    """The feature the end is (api/contract/the-end.txt, "The end"): some trigger unlocks it, a milestone the page states as a
    goal before it is met."""
    start_line_keys: list[str] = []
    """Lines shown before the first decision (the new game's lines)."""
    aims: list[AimEntry]
    """What each stretch of play is for, in order; the first holds from the start."""
    curve_items: list[int]
    """The pacing curve's XP thresholds, in whole items of XP."""
    text: dict[str, str]
    """Every line and label, by key. Input only: the API serves it as a list of TextEntry."""
    line_kinds: dict[str, LineKind]
    """The kind of each log line in this file's `text`, by key (line_kinds.py)."""
    line_doings: dict[str, LineDoingsEntry] = {}
    """The people a line shows doing something, by the line's key, for a line no outcome carries (line_kinds.check_line_doings)."""
    beat_lines: dict[str, list[str]] = {}
    """A story beat's id (content/beats.yaml) to the key of its first line, one per way it can be told."""


class SkillLevelsEntry(Entry):
    """Levels of a skill an earlier file declares: a level it already lists is restated (a pays_unknown marker now paying a
    find), the rest are added."""

    skill: str
    levels: list[LevelPaysEntry]


class Chapter(Entry):
    """A later stretch of content in its own file, merged onto the opening by chapters.merge: new ids only, and the
    opening's markers past its end (a held Camp level, a pays_unknown level row) filled in. Its own file because the opening's
    is the first-hour material the owner reads: the file boundary is the spoiler boundary (CLAUDE.md)."""

    version: Literal[1]
    stores: list[StoreEntry] = []
    skills: list[SkillEntry] = []
    skill_levels: list[SkillLevelsEntry] = []
    standing: list[StandingEntry] = []
    sides: list[SideEntry] = []
    threats: list[ThreatEntry] = []
    lanes: list[LaneEntry] = []
    town_later_labels: list[LaneLabelEntry] = []
    cards: list[CardEntry] = []
    town_cards: list[TownCardEntry] = []
    """Cards expanded once per lane at the merge (town.py)."""
    workings: list[WorkingEntry] = []
    """Each expanded to one card at the merge (workings.py)."""
    chips: list[ChipEntry] = []
    triggers: list[TriggerEntry] = []
    features: list[FeatureEntry] = []
    order_cards: list[OrderCardEntry] = []
    offers: list[OfferEntry] = []
    offer_kinds: list[OfferKindEntry] = []
    journal: JournalDecl | None = None
    entries: list[JournalEntry] = []
    notes: list[NoteEntry] = []
    subjects: list[SubjectEntry] = []
    places: list[PlaceEntry] = []
    camp_levels: list[CampLevelEntry] = []
    """A level at a held level's at_items replaces it; the rest are added after the last."""
    prestige: PrestigeEntry | None = None
    """Declared once in the content: here only if no earlier file has it."""
    people: PeopleEntry | None = None
    """Declared once in the content, as prestige."""
    close_calls: list[CloseCallEntry] = []
    nodes: list[NodeEntry] = []
    """Appended after the content's so far, so each skill's track continues in file order."""
    phase_pays: list[PhasePaysEntry] = []
    """Later phases' level pays, expanded at the merge (phase_pays.py)."""
    curve_items: list[int] = []
    """Thresholds appended to the curve (levels past the last one so far)."""
    aims: list[AimEntry] = []
    """Aims appended after the content's so far, each with an `after`."""
    end_feature: str | None = None
    """The id of this chapter's last moment, one of its `features`: required of a chapter that declares features. The
    content's end card is attached to the last shipped chapter's (merge_chapters)."""
    while_running: dict[str, list[WhileRunningEntry]] = {}
    """Entries held while an earlier card runs, by card id, after any it holds: a side this chapter declares raised by a
    card an earlier one shipped (the card pays more)."""
    lane_labels: dict[str, list[LaneLabelEntry]] = {}
    """Later labels for a lane an earlier file declares, by lane id, after any it has: a joined person named later."""
    text: dict[str, str] = {}
    line_kinds: dict[str, LineKind] = {}
    line_doings: dict[str, LineDoingsEntry] = {}
    beat_lines: dict[str, list[str]] = {}


def load_opening(path: Path = OPENING, chapters: tuple[Path, ...] = CHAPTERS) -> Opening:
    """Parse and validate the file: Pydantic shape, then cross-references (ids, keys in text, exact fractions); then
    each chapter merged on in order, the result checked the same way. The opening alone is checked first, so it stays
    a whole game by itself."""
    with path.open("rb") as f:
        opening = Opening.model_validate(tomllib.load(f))
    if opening.town_cards:
        raise ValueError("the opening's file holds no town_cards: they expand in a chapter's merge")
    check_first_notes(opening.entries, opening.notes)
    check_opening(opening)
    return merge_chapters(opening, chapters)


def merge_chapters(opening: Opening, chapters: tuple[Path, ...]) -> Opening:
    """`opening` (already checked) with each chapter file merged on in order, each state checked for structure (so a
    chapter refers only to ids it or an earlier chapter defines), and the last one for its content rules too. An error
    names the chapter whose state fails."""
    states: list[Opening] = [opening]
    ends: list[str | None] = []
    for chapter in chapters:
        merged, end = _merged(states[-1], chapter)
        states.append(merged)
        ends.append(end)
    states[-1] = with_expansions(states[-1])
    last: list[str] = [e for e in ends if e is not None][-1:]
    if last and opening.end_card is not None:
        states[-1] = _with_end_card(states[-1], last[0], opening.end_card)
        check_structure(states[-1])
    if chapters:
        try:
            check_content(states[-1])
        except ValueError as e:
            _fail_naming_chapter(states, chapters, e)
    return states[-1]


def chapter_ends(opening: Opening, chapters: tuple[Path, ...]) -> list[Opening]:
    """The state at each chapter's end as merge_chapters builds it, each checked for structure only."""
    states = [opening]
    for chapter in chapters:
        states.append(_merged(states[-1], chapter)[0])
    return states[1:]


def _with_end_card(o: Opening, feature: str, card: FeatureCardEntry) -> Opening:
    return o.model_copy(update={"features": [f.model_copy(update={"card": card}) if f.id == feature else f
                                             for f in o.features]})


def _check_end_feature(ch: Chapter) -> None:
    if any(f.card is not None for f in ch.features):
        raise ValueError("a chapter's feature carries no card: the content's end_card is attached to the last chapter's end_feature")
    if ch.features and ch.end_feature not in {f.id for f in ch.features}:
        raise ValueError(f"end_feature {ch.end_feature!r} is not one of the chapter's features")


def _merged(opening: Opening, chapter: Path) -> tuple[Opening, str | None]:
    with chapter.open("rb") as f:
        ch = Chapter.model_validate(tomllib.load(f))
    try:
        check_first_notes(ch.entries, ch.notes)
        _check_end_feature(ch)
        merged = merge(opening, ch)
        check_structure(merged)
    except ValueError as e:
        raise ValueError(f"{e} (in {chapter.name})") from e
    return merged, ch.end_feature


def _fail_naming_chapter(states: list[Opening], chapters: tuple[Path, ...], error: ValueError) -> NoReturn:
    """Raise the full state's own error, naming the first chapter whose state fails with that same message. Early
    states fail on their own as partial worlds, so a different message is not this error and is skipped; when no
    prefix reproduces it (a later pass, such as the group unlocks, brought it) the last chapter is named."""
    named = chapters[-1]
    for chapter, state in zip(chapters, states[1:]):
        try:
            check_content(state)
        except ValueError as e:
            if str(e) == str(error):
                named = chapter
                break
    raise ValueError(f"{error} (in {named.name})") from error


def to_rules(opening: Opening) -> Rules:
    """The engine's Rules for the opening, validate_rules-clean. Pure; the same file always gives equal Rules."""
    rules = build_rules(opening)
    validate_rules(rules)
    return rules
