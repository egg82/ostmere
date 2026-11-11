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
from .fight_entries import SideEntry, ThreatEntry
from .journal_entries import JournalDecl, JournalEntry, NoteEntry
from .offer_entries import OfferEntry
from .phase_pays import PhasePaysEntry
from .prestige import NodeEntry, PrestigeEntry
from .town import TownCardEntry
from .checks import check_content, check_opening, check_structure
from .line_kinds import LineKind
from .journal_checks import check_first_notes
from .convert import build_rules
from .camp_entries import CampEntry, CampLevelEntry
from .setting_entries import FirstMixEntry, RepeatOffersEntry
from .entries import (
    CardEntry, ChipEntry, Entry, LaneEntry, LevelPaysEntry, OrderCardEntry, SkillEntry, StandingEntry, StoreEntry,
    TriggerEntry, UnlockEntry, WhileRunningEntry,
)
from .feature_entries import AimEntry, FeatureCardEntry, FeatureEntry

OPENING = Path(__file__).resolve().parent / "opening.toml"
DAY_ONE = Path(__file__).resolve().parent / "day_one.toml"
DAY_TWO = Path(__file__).resolve().parent / "day_two.toml"
DAY_THREE = Path(__file__).resolve().parent / "day_three.toml"
DAY_FOUR = Path(__file__).resolve().parent / "day_four.toml"
DAY_FIVE = Path(__file__).resolve().parent / "day_five.toml"
B7 = Path(__file__).resolve().parent / "b7.toml"
DAY_SIX = Path(__file__).resolve().parent / "day_six.toml"
DAY_EIGHT = Path(__file__).resolve().parent / "day_eight.toml"
DAY_NINE = Path(__file__).resolve().parent / "day_nine.toml"
DAY_ELEVEN = Path(__file__).resolve().parent / "day_eleven.toml"
DAY_TWELVE = Path(__file__).resolve().parent / "day_twelve.toml"
DAY_FIFTEEN = Path(__file__).resolve().parent / "day_fifteen.toml"
PRESTIGE = Path(__file__).resolve().parent / "prestige.toml"
PHASE_PAYS = Path(__file__).resolve().parent / "phase_pays.toml"
CHAPTERS = (DAY_ONE, DAY_TWO, DAY_THREE, DAY_FOUR, DAY_FIVE, B7, DAY_SIX, DAY_EIGHT, DAY_NINE, DAY_ELEVEN,
            DAY_TWELVE, PRESTIGE, PHASE_PAYS)
"""The chapters after the opening, merged on in this order (Chapter): what ships."""
IN_WRITING: tuple[Path, ...] = (DAY_FIFTEEN,)
"""Chapters whose structure is in but whose lines are not, merged after CHAPTERS only by tests; each moves into
CHAPTERS once no text of it is UNWRITTEN (tests/opening/test_day_two.py) and its pacing holds."""
UNWRITTEN = "[day two: line to write]"
"""The text of a key whose line is still to write; no shipping release holds it."""


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
    cards: list[CardEntry]
    town_cards: list[TownCardEntry] = []
    """Only what chapters.merge carries; the opening's own file holds none (load_opening refuses it)."""
    chips: list[ChipEntry] = []
    triggers: list[TriggerEntry] = []
    features: list[FeatureEntry] = []
    order_cards: list[OrderCardEntry] = []
    offers: list[OfferEntry] = []
    journal: JournalDecl | None = None
    entries: list[JournalEntry] = []
    notes: list[NoteEntry] = []
    start: list[UnlockEntry]
    """The unlock set a new save starts with (Rules.opening)."""
    camp: CampEntry | None = None
    prestige: PrestigeEntry | None = None
    nodes: list[NodeEntry] = []
    phase_pays: list[PhasePaysEntry] = []
    """Only what chapters.merge carries, each entry kept so a later chapter's ranks expand their phases."""
    first_mix: FirstMixEntry
    repeat_offers: RepeatOffersEntry
    end_line_keys: list[str] = []
    """Lines the page appends at the end moment (api/CONTRACT.txt, "The end"): no engine event marks it."""
    end_feature: str
    """The feature the end is (api/CONTRACT.txt, "The end"): some trigger unlocks it, a milestone the page states as a
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
    cards: list[CardEntry] = []
    town_cards: list[TownCardEntry] = []
    """Cards expanded once per lane at the merge (town.py)."""
    chips: list[ChipEntry] = []
    triggers: list[TriggerEntry] = []
    features: list[FeatureEntry] = []
    order_cards: list[OrderCardEntry] = []
    offers: list[OfferEntry] = []
    journal: JournalDecl | None = None
    entries: list[JournalEntry] = []
    notes: list[NoteEntry] = []
    camp_levels: list[CampLevelEntry] = []
    """A level at a held level's at_items replaces it; the rest are added after the last."""
    prestige: PrestigeEntry | None = None
    """Declared once in the content: here only if no earlier file has it."""
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
    """Entries held while an earlier card runs, by card id, for a card that holds none: a side this chapter declares
    raised by a card an earlier one shipped (Safe under the release lock: the card pays more)."""
    text: dict[str, str] = {}
    line_kinds: dict[str, LineKind] = {}


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
    last: list[str] = [e for e in ends if e is not None][-1:]
    if last and opening.end_card is not None:
        states[-1] = _with_end_card(states[-1], last[0], opening.end_card)
        check_structure(states[-1])
    if chapters:
        try:
            check_content(states[-1])
        except ValueError:
            _fail_naming_chapter(states, chapters)
    return states[-1]


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


def _fail_naming_chapter(states: list[Opening], chapters: tuple[Path, ...]) -> NoReturn:
    for chapter, state in zip(chapters, states[1:]):
        try:
            check_content(state)
        except ValueError as e:
            raise ValueError(f"{e} (in {chapter.name})") from e
    raise AssertionError("the merged opening failed its content check but no chapter's state did")


def to_rules(opening: Opening) -> Rules:
    """The engine's Rules for the opening, validate_rules-clean. Pure; the same file always gives equal Rules."""
    rules = build_rules(opening)
    validate_rules(rules)
    return rules
