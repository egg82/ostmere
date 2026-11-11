"""A skill's later phases' level pays, defined once: a `[[phase_pays]]` entry is what every level of every phase from 2
on pays, keyed by the level within the phase, and the merge expands it to ordinary triggers and row entries at the
counted levels (engine phases.level_counted). The engine sees only the triggers.

Expanded: each phase from 2 to the last a skill's track reaches (its ranks + 1; a finished track rests at its top),
each level 2..top_level, at a counted level past the curve's last level; the curve's own levels keep their authored
pays. Each expansion has a fixed id (`expanded_id`, `find_id`), so the release lock holds its outcome like any
trigger's, and an entry stays on the Opening so a chapter that adds ranks expands only the phases they add.

A later phase's find is the skill's staple good in an amount that grows by phase, with a line from the skill's pool
chosen by how many finds the track has paid (`find_line`), so no line comes twice running. Phases once paid finds at
`expanded_id` that gave story goods under one line each; those outcomes are released and cannot change. Each is kept
(`retired_finds`) under its id and gated at RETIRED_AT, a counted level no skill reaches, so it never fires again, and
the find is a new trigger under `find_id` that also carries the speed.

Checked (check_phase_pays): a later phase's work pay is an add, never a multiplier (docs/design/prestige-phases.md,
"The loop", spiral 2), and speeds only its own skill's cards; at most two levels in a row pay only speed, counted
around the phase; the find's store is one a card that stays available consumes (`staying_stores`)."""
from collections import Counter
from typing import TYPE_CHECKING, Literal

from pydantic import Field

from .entries import (
    ConditionEntry, Entry, ItemAmount, LevelPaysEntry, ModifierEntry, OutcomeEntry, SkillEntry, TriggerEntry,
)
from .refs import fail, outcomes

if TYPE_CHECKING:
    from .schema import Opening

MAX_SPEED_ONLY = 2
"""Levels in a row that may pay only speed (docs/decisions.md, "A level is a thing")."""
RETIRED_AT = 10_000
"""The counted level a retired find's trigger waits for: far past any track."""


class PhaseSpeedEntry(Entry):
    """A change to `id`'s (a card's) work that every later phase's level lands."""

    target: Literal["work"]
    id: str
    kind: Literal["add_bp", "mul_bp"]
    amount_bp: int = Field(ge=1)


class PhaseFindEntry(Entry):
    """What `levels` of every later phase find besides their speed: `items` of `store` in phase 2 and `items_per_phase`
    more in each phase after, one of `lines` (find_line), and the row's words `pays_key` (slot {pct}: the speed)."""

    levels: list[int] = Field(min_length=1)
    store: str
    items: int = Field(ge=1)
    items_per_phase: int = Field(default=0, ge=0)
    pays_key: str
    lines: list[str] = Field(min_length=2)


class RetiredFindEntry(Entry):
    """A find a phase once paid, as released: kept so its trigger's outcome stays what it was, and never fires."""

    level: int = Field(ge=2)
    line_key: str
    store: str
    items: int = Field(ge=1)


class PhasePaysEntry(Entry):
    """`skill`'s pays in every phase from 2: `speed` at each level, the row reading `speed_key`, and at a find's level
    the find as well."""

    skill: str
    speed: list[PhaseSpeedEntry] = Field(min_length=1)
    speed_key: str
    find: PhaseFindEntry
    retired_finds: list[RetiredFindEntry] = []
    retired_through: int = Field(default=0, ge=0)
    """The last phase that shipped the retired finds; later phases never had them."""


def expanded_id(skill: str, phase: int, level: int) -> str:
    return f"t_pp_{skill}_{phase}_{level}"


def find_id(skill: str, phase: int, level: int) -> str:
    return f"t_pf_{skill}_{phase}_{level}"


def find_line(find: PhaseFindEntry, phase: int, level: int) -> str:
    """The find's line: the pool rotated one step per find the track has paid, so with two lines or more no line
    comes twice in a row, across a phase's end too."""
    return find.lines[((phase - 2) * len(find.levels) + sorted(find.levels).index(level)) % len(find.lines)]


def find_items(find: PhaseFindEntry, phase: int) -> int:
    return find.items + (phase - 2) * find.items_per_phase


def expanded(o: "Opening") -> "Opening":
    """`o` with the triggers and row entries its phase_pays bring that it does not hold yet. ValueError for phase_pays
    with no [prestige], and for an expansion landing on a row the content already has."""
    if not o.phase_pays:
        return o
    if o.prestige is None:
        fail("phase_pays", "need [prestige]")
    have = {t.id for t in o.triggers}
    triggers: list[TriggerEntry] = []
    rows: dict[str, list[LevelPaysEntry]] = {}
    for pp in o.phase_pays:
        for phase, level, counted in _levels(o, pp.skill):
            made = [t for t in _triggers(pp, phase, level, counted) if t.id not in have]
            triggers += made
            if made:
                found = level in pp.find.levels
                rows.setdefault(pp.skill, []).append(
                    LevelPaysEntry(level=counted, pays_key=pp.find.pays_key if found else pp.speed_key))
    return o.model_copy(update={"triggers": [*o.triggers, *triggers],
                                "skills": [_rowed(s, rows.get(s.id, [])) for s in o.skills]})


def _levels(o: "Opening", skill: str) -> list[tuple[int, int, int]]:
    """(phase, level within it, counted level) of every later-phase level the skill's track reaches, past the curve."""
    assert o.prestige is not None
    top, last = o.prestige.top_level, len(o.curve_items) + 1
    ranks = sum(n.ranks for n in o.nodes if n.skill == skill)
    return [(p, lv, c) for p in range(2, ranks + 2) for lv in range(2, top + 1)
            if (c := (p - 1) * (top - 1) + lv) > last]


def _triggers(pp: PhasePaysEntry, phase: int, level: int, counted: int) -> list[TriggerEntry]:
    """The triggers of one later-phase level: its speed alone (`expanded_id`), or at a find's level the speed with the
    find (`find_id`), and, for a phase that shipped the old find there, that find's retired trigger as well."""
    speed = _speed(pp, expanded_id(pp.skill, phase, level))
    if level not in pp.find.levels:
        return [_trigger(pp, expanded_id(pp.skill, phase, level), counted, OutcomeEntry(modifiers=speed))]
    find, tid = pp.find, find_id(pp.skill, phase, level)
    out = [_trigger(pp, tid, counted, OutcomeEntry(
        modifiers=_speed(pp, tid), stores=[ItemAmount(store=find.store, items=find_items(find, phase))],
        line_keys=[find_line(find, phase, level)]))]
    old = next((r for r in pp.retired_finds if r.level == level), None)
    if old is not None and phase <= pp.retired_through:
        out.append(_trigger(pp, expanded_id(pp.skill, phase, level), RETIRED_AT, OutcomeEntry(
            modifiers=speed, stores=[ItemAmount(store=old.store, items=old.items)], line_keys=[old.line_key])))
    return out


def _speed(pp: PhasePaysEntry, tid: str) -> list[ModifierEntry]:
    return [ModifierEntry(target=s.target, id=s.id, kind=s.kind, amount_bp=s.amount_bp, source=tid.removeprefix("t_"))
            for s in pp.speed]


def _trigger(pp: PhasePaysEntry, tid: str, at: int, outcome: OutcomeEntry) -> TriggerEntry:
    return TriggerEntry(id=tid, when=ConditionEntry(test="at_least", subject_kind="skill_level", id=pp.skill, value=at),
                        outcome=outcome)


def _rowed(skill: SkillEntry, added: list[LevelPaysEntry]) -> SkillEntry:
    if not added:
        return skill
    clash = sorted({lv.level for lv in skill.levels} & {lv.level for lv in added})
    if clash:
        fail(f"phase_pays {skill.id}", f"expands onto row levels the content already has: {clash}")
    return skill.model_copy(update={"levels": sorted([*skill.levels, *added], key=lambda lv: lv.level)})


def check_phase_pays(o: "Opening") -> None:
    """ValueError naming the entry unless every phase_pays entry is one skill's only one, speeds by an add the work of
    cards its skill trains, finds at distinct levels 2..top_level leaving no more than MAX_SPEED_ONLY speed-only levels
    in a row around the phase; and unless no skill-level trigger past both the top level and the curve's last level
    (a later phase's pay written by hand) multiplies a card's work."""
    trains = {c.id: c.skill for c in o.cards}
    for skill, n in Counter(pp.skill for pp in o.phase_pays).items():
        if n > 1:
            fail(f"phase_pays {skill}", "is declared more than once")
    for pp in o.phase_pays:
        _check_entry(o, pp, trains)
    if o.prestige is not None:
        past = max(o.prestige.top_level, len(o.curve_items) + 1)
        for t in o.triggers:
            if t.when.subject_kind == "skill_level" and t.when.test == "at_least" and t.when.value > past:
                _check_later_trigger(t)


def _check_entry(o: "Opening", pp: PhasePaysEntry, trains: dict[str, str | None]) -> None:
    where = f"phase_pays {pp.skill}"
    for s in pp.speed:
        if s.kind != "add_bp":
            fail(where, f"work {s.id} is a multiplier: a later phase's work pay is an add (prestige-phases, \"The loop\")")
        if trains.get(s.id) != pp.skill:
            fail(where, f"work {s.id} is not a card {pp.skill} trains")
    top = o.prestige.top_level if o.prestige is not None else 0
    levels = pp.find.levels
    if len(set(levels)) != len(levels) or any(not 2 <= lv <= top for lv in levels):
        fail(where, f"finds need distinct levels in 2..{top}")
    if _longest_speed_only(set(levels), top) > MAX_SPEED_ONLY:
        fail(where, f"leaves more than {MAX_SPEED_ONLY} levels in a row paying only speed")
    if len(set(pp.find.lines)) != len(pp.find.lines):
        fail(where, "find lines repeat in the pool")
    if pp.find.store not in staying_stores(o):
        fail(where, f"finds {pp.find.store}, which no card that stays available consumes: a later phase's find is "
             "a good the rest of the game still spends")


def staying_stores(o: "Opening") -> set[str]:
    """The stores some card that stays available takes in: an input, a drain or a cost of a card with no completion
    cap that no outcome retires. A card with a cap is a one-off (a build, a told step), a standing action belongs to a
    person or a night, and neither is counted: a find into a store only they use is a good nothing spends later."""
    retired = {u.id for _, out in outcomes(o) for u in out.unlocks if u.unlock_kind == "retired"}
    return {x.store for c in o.cards if c.cap is None and c.id not in retired for x in (*c.inputs, *c.drains, *c.costs)}


def _longest_speed_only(named: set[int], top: int) -> int:
    """The longest run of levels not in `named`, the phase's levels 2..top read twice so a run across the click counts."""
    run = longest = 0
    for lv in [*range(2, top + 1)] * 2:
        run = 0 if lv in named else run + 1
        longest = max(longest, run)
    return min(longest, top - 1)


def _check_later_trigger(t: TriggerEntry) -> None:
    if any(m.target == "work" and m.kind == "mul_bp" for m in t.outcome.modifiers):
        fail(f"trigger {t.id}", f"multiplies a card's work at level {t.when.value}, a later phase's level: a later "
             "phase's work pay is an add (prestige-phases, \"The loop\")")
