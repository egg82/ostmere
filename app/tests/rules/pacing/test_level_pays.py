"""Every marker pays when its level lands (docs/decisions.md: a promise shown is kept; a level with no marker is the
readout's, blank_levels.py); and the loop between a level's pay and the next level stays tame (tests/dayone/pacing/growth.py). Static: read off the merged content and its rules, no play."""
from dataclasses import replace
from functools import cache

from ashfall_app.engine import (
    CardDef, CardId, FlowKind, Modifier, ModifierKind, Outcome, PacingCurve, RateRef, Rules, SkillDef, SkillId, SourceId,
    TriggerDef, TriggerId, per_hour, units,
)
from ashfall_app.engine.orders import AtLeast, SkillLevel
from ashfall_app.rules.schema import Opening, load_opening, to_rules
from tests.dayone.pacing.growth import climb_hours, fastest_rates, level_times, runaway
from tests.rules.play.blank_levels import top_level


@cache
def merged() -> tuple[Opening, Rules]:
    o = load_opening()
    return o, to_rules(o)


def paid_levels(rules: Rules) -> dict[str, set[int]]:
    """Levels something lands on or reads: a trigger on the level, or a card's requires on it."""
    out: dict[str, set[int]] = {}
    conds = [t.when for t in rules.triggers] + [r for c in rules.cards for r in c.requires]
    for w in conds:
        if isinstance(w, AtLeast) and isinstance(w.subject, SkillLevel):
            out.setdefault(str(w.subject.skill), set()).add(w.value)
    return out


def unpaid_markers(o: Opening, rules: Rules) -> list[str]:
    paid = paid_levels(rules)
    return [f"{s.id} {lv.level} ({lv.pays_key})" for s in o.skills for lv in s.levels
            if lv.level not in paid.get(s.id, set())]


def test_every_marker_pays_when_its_level_lands():
    assert unpaid_markers(*merged()) == []


def test_a_level_never_comes_sooner_than_the_one_before():
    assert runaway(merged()[1]) == []


def test_a_planted_runaway_is_caught():
    """Each level doubling its card's XP outruns a curve whose steps grow by less than double: the gate goes red."""
    _, rules = merged()
    card: CardDef = next(c for c in rules.cards if c.skill is not None and c.xp_per_hour > 0)
    assert card.skill is not None
    planted = tuple(
        TriggerDef(TriggerId(f"planted_{n}"), AtLeast(SkillLevel(card.skill), n, n),
                   Outcome(modifiers=(Modifier(RateRef(card.id, FlowKind.XP), ModifierKind.MUL_BP, 20_000,
                                               SourceId(f"planted_{n}")),)))
        for n in range(2, top_level(rules) + 1))
    found = runaway(replace(rules, triggers=rules.triggers + planted))
    assert any(card.id in f for f in found)


def test_level_times_are_hours():
    """Steps of 40 then 56 items at 20 XP an hour take 2 h then 2.8 h."""
    gather = SkillId("gather")
    rules = Rules(stores=(), skills=(SkillDef(gather),), standing=(), curve=PacingCurve((units(40), units(96))),
                  cards=(CardDef(CardId("chop"), 60, skill=gather, xp_per_hour=per_hour(20)),))
    assert level_times(rules, "gather") == {"chop": [2.0, 2.8]}


def slowed(rules: Rules, skill: str, factor: float) -> Rules:
    return replace(rules, cards=tuple(replace(c, xp_per_hour=int(c.xp_per_hour * factor)) if str(c.skill) == skill else c
                                      for c in rules.cards))


def test_a_slowed_skill_reads_a_longer_climb_and_only_it():
    """The climb the readout prints (tests/rules/play/report.py) reads each skill's own fastest runner: a skill whose cards
    run at half the rate reads twice the hours, and every other skill reads as before."""
    rules = merged()[1]
    before = climb_hours(rules)
    assert len(before) >= 2
    skill = min(s for s, r in fastest_rates(rules).items() if any(str(c.skill) == s and c.xp_per_hour == r for c in rules.cards))
    after = climb_hours(slowed(rules, skill, 0.5))
    assert after[skill] == before[skill] * 2
    assert {s: h for s, h in after.items() if s != skill} == {s: h for s, h in before.items() if s != skill}
