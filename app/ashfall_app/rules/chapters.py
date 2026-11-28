"""A Chapter merged onto an Opening (schema.Chapter): its lists appended, its text added, its Camp levels and skill
levels filling the markers the content so far left past its end. Pure; raises ValueError on a merge that would
overwrite rather than add. Ids are checked unique afterwards, by check_opening on the result."""
from typing import TYPE_CHECKING, Protocol, Self

from .expand.camp_convert import camp_cap
from .groups import with_crews
from .expand.phase_pays import expanded
from .expand.town import expand
from .expand.workings import expand as expand_workings

if TYPE_CHECKING:
    from .entries.camp_entries import CampEntry, CampLevelEntry
    from .entries.entries import CardEntry, LaneLabelEntry, LevelPaysEntry, SkillEntry, WhileRunningEntry
    from .schema import Chapter, Opening, SkillLevelsEntry


def merge(o: "Opening", ch: "Chapter") -> "Opening":
    clash = sorted(set(o.text) & set(ch.text))
    if clash:
        raise ValueError(f"chapter text: keys already in the text: {clash}")
    kinds = sorted(set(o.line_kinds) & set(ch.line_kinds))
    if kinds:
        raise ValueError(f"chapter line_kinds: keys already have a kind: {kinds}")
    doings = sorted(set(o.line_doings) & set(ch.line_doings))
    if doings:
        raise ValueError(f"chapter line_doings: lines already marked: {doings}")
    beats = sorted(set(o.beat_lines) & set(ch.beat_lines))
    if beats:
        raise ValueError(f"chapter beat_lines: beats already have a first line: {beats}")
    camp = _camp(o.camp, ch.camp_levels)
    town, lanes = [*o.town_cards, *ch.town_cards], with_crews([*_labelled(o.lanes, ch.lane_labels, "lane_labels", "lanes"), *ch.lanes])
    stores = [*o.stores, *ch.stores]
    if camp is not None:
        stores = [s.model_copy(update={"cap_items": camp_cap(camp)}) if s.id == camp.store else s for s in stores]
    return expanded(o.model_copy(update={
        "stores": stores,
        "skills": [*_skills(o.skills, ch.skill_levels), *ch.skills],
        "standing": [*_labelled(o.standing, ch.standing_labels, "standing_labels", "actions"), *ch.standing],
        "sides": [*o.sides, *ch.sides], "threats": [*o.threats, *ch.threats], "lanes": lanes,
        "town_later_labels": [*o.town_later_labels, *ch.town_later_labels],
        "cards": expand([*_held(o.cards, ch.while_running), *ch.cards, *expand_workings(ch.workings)], town, {x.id for x in lanes}, {x.id for x in ch.lanes}, len(ch.town_cards),
                         {x.id: x.kind for x in lanes if x.pooled and x.kind is not None}),
        "town_cards": town,
        "chips": [*o.chips, *ch.chips], "triggers": [*o.triggers, *ch.triggers],
        "features": [*o.features, *ch.features], "order_cards": [*o.order_cards, *ch.order_cards],
        "offers": [*o.offers, *ch.offers], "offer_kinds": [*o.offer_kinds, *ch.offer_kinds],
        "journal": _once("journal", o.journal, ch.journal), "entries": [*o.entries, *ch.entries], "notes": [*o.notes, *ch.notes],
        "subjects": [*o.subjects, *ch.subjects], "places": [*o.places, *ch.places],
        "prestige": _once("prestige", o.prestige, ch.prestige), "nodes": [*o.nodes, *ch.nodes],
        "people": _once("people", o.people, ch.people), "close_calls": [*o.close_calls, *ch.close_calls],
        "camp": camp, "curve_items": [*o.curve_items, *ch.curve_items], "aims": [*o.aims, *ch.aims],
        "phase_pays": [*o.phase_pays, *ch.phase_pays],
        "text": {**o.text, **ch.text}, "line_kinds": {**o.line_kinds, **ch.line_kinds},
        "line_doings": {**o.line_doings, **ch.line_doings}, "beat_lines": {**o.beat_lines, **ch.beat_lines},
    }))


def _once[T](name: str, old: T | None, new: T | None) -> T | None:
    """A table declared once in the content: by an earlier file or by this chapter, never both."""
    if old is not None and new is not None:
        raise ValueError(f"chapter {name}: [{name}] is declared twice")
    return old if new is None else new


def _held(cards: "list[CardEntry]", added: "dict[str, list[WhileRunningEntry]]") -> "list[CardEntry]":
    """Earlier cards given more entries to hold while running (Chapter.while_running), after the ones they hold, each on
    a side or lane the card holds nothing on yet."""
    known = {c.id: c for c in cards}
    for cid, entries in added.items():
        if cid not in known:
            raise ValueError(f"chapter while_running: unknown card {cid}")
        held = {w.side or w.lane or "" for w in known[cid].while_running} & {w.side or w.lane or "" for w in entries}
        if held:
            raise ValueError(f"chapter while_running: card {cid} already holds an entry on {sorted(held)}")
    return [c.model_copy(update={"while_running": [*c.while_running, *added[c.id]]}) if c.id in added else c for c in cards]


class Labelled(Protocol):
    """An entry that takes later labels: a lane, a standing action."""

    @property
    def id(self) -> str: ...
    @property
    def later_labels(self) -> "list[LaneLabelEntry]": ...
    def model_copy(self, *, update: dict[str, object] | None = None, deep: bool = False) -> Self: ...


def _labelled[T: Labelled](items: list[T], added: "dict[str, list[LaneLabelEntry]]", table: str, what: str) -> list[T]:
    """Earlier lanes or standing actions given more later labels (Chapter.lane_labels, Chapter.standing_labels), after
    the ones they have."""
    unknown = sorted(set(added) - {x.id for x in items})
    if unknown:
        raise ValueError(f"chapter {table}: unknown {what} {unknown}")
    return [x.model_copy(update={"later_labels": [*x.later_labels, *added[x.id]]}) if x.id in added else x for x in items]


def _camp(camp: "CampEntry | None", added: "list[CampLevelEntry]") -> "CampEntry | None":
    """A level at a held level's at_items replaces it (the marker filled in); every other must come after the last."""
    if not added:
        return camp
    if camp is None:
        raise ValueError("chapter camp_levels: the content so far has no camp")
    levels = list(camp.levels)
    for lv in added:
        at = next((i for i, old in enumerate(levels) if old.at_items == lv.at_items), None)
        if at is not None and not levels[at].held:
            raise ValueError(f"chapter camp level at {lv.at_items}: replaces a level that is not held")
        if at is None and lv.at_items <= levels[-1].at_items:
            raise ValueError(f"chapter camp level at {lv.at_items}: inserted before the last level")
        levels = levels[:at] + [lv] + levels[at + 1:] if at is not None else [*levels, lv]
    return camp.model_copy(update={"levels": levels})


def _skills(skills: "list[SkillEntry]", added: "list[SkillLevelsEntry]") -> "list[SkillEntry]":
    known = {s.id for s in skills}
    for a in added:
        if a.skill not in known:
            raise ValueError(f"chapter skill_levels: unknown skill {a.skill} (a new skill goes in skills)")
    return [s.model_copy(update={"levels": _levels(s.levels, [lv for a in added if a.skill == s.id
                                                                 for lv in a.levels])}) for s in skills]


def _levels(old: "list[LevelPaysEntry]", new: "list[LevelPaysEntry]") -> "list[LevelPaysEntry]":
    by_level = {lv.level: lv for lv in old} | {lv.level: lv for lv in new}
    return [by_level[n] for n in sorted(by_level)]
