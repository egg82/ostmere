"""A Chapter merged onto an Opening (schema.Chapter): its lists appended, its text added, its Camp levels and skill
levels filling the markers the content so far left past its end. Pure; raises ValueError on a merge that would
overwrite rather than add. Ids are checked unique afterwards, by check_opening on the result."""
from typing import TYPE_CHECKING

from .convert import camp_cap
from .phase_pays import expanded
from .town import expand

if TYPE_CHECKING:
    from .camp_entries import CampEntry, CampLevelEntry
    from .entries import CardEntry, LevelPaysEntry, SkillEntry, WhileRunningEntry
    from .schema import Chapter, Opening, SkillLevelsEntry


def merge(o: "Opening", ch: "Chapter") -> "Opening":
    clash = sorted(set(o.text) & set(ch.text))
    if clash:
        raise ValueError(f"chapter text: keys already in the text: {clash}")
    kinds = sorted(set(o.line_kinds) & set(ch.line_kinds))
    if kinds:
        raise ValueError(f"chapter line_kinds: keys already have a kind: {kinds}")
    camp = _camp(o.camp, ch.camp_levels)
    town, lanes = [*o.town_cards, *ch.town_cards], [*o.lanes, *ch.lanes]
    stores = [*o.stores, *ch.stores]
    if camp is not None:
        stores = [s.model_copy(update={"cap_items": camp_cap(camp)}) if s.id == camp.store else s for s in stores]
    return expanded(o.model_copy(update={
        "stores": stores,
        "skills": [*_skills(o.skills, ch.skill_levels), *ch.skills],
        "standing": [*o.standing, *ch.standing],
        "sides": [*o.sides, *ch.sides], "threats": [*o.threats, *ch.threats], "lanes": [*o.lanes, *ch.lanes],
        "cards": expand([*_held(o.cards, ch.while_running), *ch.cards], town, {x.id for x in lanes}, {x.id for x in ch.lanes}, len(ch.town_cards)),
        "town_cards": town,
        "chips": [*o.chips, *ch.chips], "triggers": [*o.triggers, *ch.triggers],
        "features": [*o.features, *ch.features], "order_cards": [*o.order_cards, *ch.order_cards],
        "offers": [*o.offers, *ch.offers],
        "journal": _once("journal", o.journal, ch.journal), "entries": [*o.entries, *ch.entries], "notes": [*o.notes, *ch.notes],
        "prestige": _once("prestige", o.prestige, ch.prestige), "nodes": [*o.nodes, *ch.nodes],
        "people": _once("people", o.people, ch.people),
        "camp": camp, "curve_items": [*o.curve_items, *ch.curve_items], "aims": [*o.aims, *ch.aims],
        "phase_pays": [*o.phase_pays, *ch.phase_pays],
        "text": {**o.text, **ch.text}, "line_kinds": {**o.line_kinds, **ch.line_kinds},
    }))


def _once[T](name: str, old: T | None, new: T | None) -> T | None:
    """A table declared once in the content: by an earlier file or by this chapter, never both."""
    if old is not None and new is not None:
        raise ValueError(f"chapter {name}: [{name}] is declared twice")
    return old if new is None else new


def _held(cards: "list[CardEntry]", added: "dict[str, list[WhileRunningEntry]]") -> "list[CardEntry]":
    """Earlier cards given the entries they hold while running (Chapter.while_running), each card one that holds none."""
    known = {c.id: c for c in cards}
    for cid in added:
        if cid not in known:
            raise ValueError(f"chapter while_running: unknown card {cid}")
        if known[cid].while_running:
            raise ValueError(f"chapter while_running: card {cid} already holds entries")
    return [c.model_copy(update={"while_running": added[c.id]}) if c.id in added else c for c in cards]


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
