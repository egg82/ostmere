"""Later phases' level pays (rules/expand/phase_pays.py): no pay lies past the last phase a skill's track reaches, its work
pays are adds, and the loader refuses a later phase's work pay written as a multiplier (docs/design/prestige-phases.md,
"The loop", spiral 2). Static: read off the shipped content, with planted changes."""
from typing import Literal

import pytest

from ashfall_app.rules.checks.run import check_structure
from ashfall_app.rules.entries.entries import (
    CardEntry, ConditionEntry, ModifierEntry, OutcomeEntry, TriggerEntry, UnlockEntry,
)
from ashfall_app.rules.expand.phase_pays import (
    check_phase_pays, expanded, expanded_id, find_id, find_items, find_line, staying_stores,
)
from ashfall_app.rules.prestige import NodeEntry
from ashfall_app.rules.schema import Opening, to_rules
from tests.rules.play.blank_levels import blank_lines, level_pays, phase_blanks
from tests.rules.play.report import samey_lines
from tests.rules.play.speed_reach import reach_lines

PREFIXES = ("t_pp_", "t_pf_")


def curve_last(o: Opening) -> int:
    return len(o.curve_items) + 1


def stripped(o: Opening) -> Opening:
    """`o` without what its phase_pays expanded: the triggers they made and the rows past the curve."""
    last = curve_last(o)
    return o.model_copy(update={
        "triggers": [t for t in o.triggers if not t.id.startswith(PREFIXES)],
        "skills": [s.model_copy(update={"levels": [lv for lv in s.levels if lv.level <= last]}) for s in o.skills]})


def with_table(o: Opening, skill: str, **update: object) -> Opening:
    return o.model_copy(update={"phase_pays": [pp.model_copy(update=update) if pp.skill == skill else pp
                                               for pp in o.phase_pays]})


def test_the_levels_a_track_reaches_that_pay_nothing_are_reported_never_refused(shipped_opening: Opening):
    """Which levels pay is the opening readout's figure (blank_levels.py), taste and not a check."""
    o = shipped_opening
    assert o.prestige is not None and o.phase_pays
    skill = o.phase_pays[0].skill
    last = o.prestige.top_level + 1
    assert last in level_pays(o, skill)
    bare = o.model_copy(update={"triggers": [t for t in o.triggers if not (t.when.id == skill and t.when.value == last)]})
    check_phase_pays(bare)
    assert phase_blanks(bare)[skill] == [last]
    line = next(ln for ln in blank_lines(bare, to_rules(bare)) if ln.split()[0] == skill)
    assert f"later phases [{last}]" in line


def test_no_track_reaches_a_pay_past_its_last_phase(shipped_opening: Opening):
    o = shipped_opening
    assert o.prestige is not None
    top = o.prestige.top_level
    for pp in o.phase_pays:
        last = sum(n.ranks for n in o.nodes if n.skill == pp.skill) * (top - 1) + top
        assert last + 1 not in level_pays(o, pp.skill), f"{pp.skill}: a pay past the last phase the track reaches"


def test_every_later_phase_work_pay_past_the_curve_is_an_add(shipped_opening: Opening):
    o = shipped_opening
    assert o.prestige is not None
    later = [t for t in o.triggers if t.when.subject_kind == "skill_level" and t.when.value > curve_last(o)]
    mods = [m for t in later for m in t.outcome.modifiers]
    assert len(later) > 100 and all(t.id.startswith(PREFIXES) for t in later)
    assert mods and all(m.target == "work" and m.kind == "add_bp" for m in mods)


def test_a_new_phase_finds_at_its_first_level(shipped_opening: Opening):
    o = shipped_opening
    assert o.prestige is not None
    by_id = {t.id: t for t in o.triggers}
    for pp in o.phase_pays:
        ranks = sum(n.ranks for n in o.nodes if n.skill == pp.skill)
        assert all(by_id[find_id(pp.skill, p, 2)].outcome.line_keys for p in range(3, ranks + 2)), pp.skill
        live = [t for t in o.triggers if t.when.id == pp.skill and t.id.startswith(PREFIXES)]
        assert any(t.outcome.line_keys for t in live), pp.skill


def test_the_rows_name_each_expanded_level(shipped_opening: Opening):
    o = shipped_opening
    rows = {(s.id, lv.level) for s in o.skills for lv in s.levels}
    made = {(t.when.id, t.when.value) for t in o.triggers if t.id.startswith(PREFIXES)}
    assert made and made <= rows


def by_id(o: Opening) -> Opening:
    """`o` with its triggers in id order: the loader's later passes (moment clocks) add triggers after the phase pays'."""
    return o.model_copy(update={"triggers": sorted(o.triggers, key=lambda t: t.id)})


def test_the_expansion_is_a_function_of_the_table(shipped_opening: Opening):
    assert stripped(shipped_opening) != shipped_opening
    assert by_id(expanded(stripped(shipped_opening))) == by_id(shipped_opening)


def test_expanding_twice_adds_nothing(shipped_opening: Opening):
    assert expanded(shipped_opening) == shipped_opening


def test_a_rank_added_later_expands_one_more_phase_only(shipped_opening: Opening):
    o = shipped_opening
    assert o.prestige is not None
    node = next(n for n in o.nodes if n.skill == "melee")
    ranks = sum(n.ranks for n in o.nodes if n.skill == "melee")
    more = expanded(o.model_copy(update={"nodes": [*o.nodes, NodeEntry.model_validate(
        {**node.model_dump(), "id": "planted_node", "ranks": 1})]}))
    added = [t.id for t in more.triggers[len(o.triggers):]]
    finds = next(pp for pp in o.phase_pays if pp.skill == "melee").find.levels
    assert added == [(find_id if lv in finds else expanded_id)("melee", ranks + 2, lv)
                     for lv in range(2, o.prestige.top_level + 1)]


def test_the_shipped_tables_pass_the_check(shipped_opening: Opening):
    check_phase_pays(shipped_opening)


def test_a_table_work_pay_written_as_a_multiplier_is_refused(shipped_opening: Opening):
    pp = next(p for p in shipped_opening.phase_pays if p.skill == "woodcutting")
    mul = [s.model_copy(update={"kind": "mul_bp", "amount_bp": 10400}) for s in pp.speed]
    with pytest.raises(ValueError, match="phase_pays woodcutting: work woodcutting is a multiplier"):
        check_phase_pays(with_table(shipped_opening, "woodcutting", speed=mul))


def test_a_hand_written_later_phase_trigger_that_multiplies_work_is_refused(shipped_opening: Opening):
    o = shipped_opening
    assert o.prestige is not None

    def planted(level: int, kind: Literal["add_bp", "mul_bp"]) -> Opening:
        t = TriggerEntry(id="t_planted", when=ConditionEntry(test="at_least", subject_kind="skill_level",
                                                             id="woodcutting", value=level),
                         outcome=OutcomeEntry(modifiers=[ModifierEntry(
                             target="work", id="woodcutting", kind=kind, amount_bp=11000, source="planted")]))
        return o.model_copy(update={"triggers": [*o.triggers, t]})
    with pytest.raises(ValueError, match="trigger t_planted: multiplies a card's work at level 30"):
        check_phase_pays(planted(30, "mul_bp"))
    check_phase_pays(planted(30, "add_bp"))
    check_phase_pays(planted(curve_last(o), "mul_bp"))   # the curve's own levels keep their authored pays


def test_a_table_speeding_another_skills_work_loads_and_is_reported(shipped_opening: Opening):
    """Whose card a pay speeds is the opening readout's figure (speed_reach.py), not a check; a card that is not one is refused."""
    pp = next(p for p in shipped_opening.phase_pays if p.skill == "woodcutting")
    other = next(c for c in shipped_opening.cards if c.skill not in (None, "woodcutting"))
    planted = with_table(shipped_opening, "woodcutting", speed=[s.model_copy(update={"id": other.id}) for s in pp.speed])
    check_phase_pays(planted)
    line = next(ln for ln in reach_lines(planted) if ln.split()[0] == "woodcutting")
    assert f"also speeds {other.id} ({other.skill})" in line
    assert "only its own" in next(ln for ln in reach_lines(shipped_opening) if ln.split()[0] == "woodcutting")
    nothing = [s.model_copy(update={"id": "no_such_card"}) for s in pp.speed]
    with pytest.raises(ValueError, match="work no_such_card is not a card"):
        check_phase_pays(with_table(shipped_opening, "woodcutting", speed=nothing))


def test_finds_leaving_speed_only_stretches_are_reported_never_refused(shipped_opening: Opening):
    """How samey a phase reads is the opening readout's figure (report.samey_lines), not a check."""
    pp = next(p for p in shipped_opening.phase_pays if p.skill == "woodcutting")

    def levels(*at: int) -> Opening:
        return with_table(shipped_opening, "woodcutting", find=pp.find.model_copy(update={"levels": list(at)}))

    def woodcutting(o: Opening) -> str:
        return next(ln for ln in samey_lines(o) if ln.split()[0] == "woodcutting")

    for at, longest in (((2, 6, 9, 12, 15, 18, 21), 3), ((4, 7, 10, 13, 16, 19), 5), ((4, 7, 10, 13, 16, 19, 22), 2)):
        o = levels(*at)
        check_phase_pays(o)
        assert f" {longest} levels in a row" in woodcutting(o), at


def test_the_load_runs_the_check(shipped_opening: Opening):
    pp = next(p for p in shipped_opening.phase_pays if p.skill == "melee")
    mul = [s.model_copy(update={"kind": "mul_bp"}) for s in pp.speed]
    with pytest.raises(ValueError, match="is a multiplier"):
        check_structure(with_table(shipped_opening, "melee", speed=mul))


def test_no_find_line_comes_twice_in_a_row_and_the_pool_is_used(shipped_opening: Opening):
    """The lines a skill's track pays, in the order the player meets them across every phase it reaches."""
    o = shipped_opening
    for pp in o.phase_pays:
        ranks = sum(n.ranks for n in o.nodes if n.skill == pp.skill)
        order = [find_line(pp.find, p, lv) for p in range(2, ranks + 2) for lv in sorted(pp.find.levels)]
        assert len(order) > len(pp.find.lines) and set(order) == set(pp.find.lines), pp.skill
        assert all(a != b for a, b in zip(order, order[1:])), pp.skill
        by_id = {t.id: t for t in o.triggers}
        paid = [by_id[find_id(pp.skill, p, lv)].outcome.line_keys[0]
                for p in range(3, ranks + 2) for lv in sorted(pp.find.levels)]
        assert paid == order[len(pp.find.levels):], pp.skill   # phase 2's first levels sit inside the curve


def test_a_finds_amount_grows_with_the_phase_and_is_the_staple(shipped_opening: Opening):
    o = shipped_opening
    by_id = {t.id: t for t in o.triggers}
    for pp in o.phase_pays:
        ranks = sum(n.ranks for n in o.nodes if n.skill == pp.skill)
        got = [by_id[find_id(pp.skill, p, 8)].outcome.stores for p in range(3, ranks + 2)]
        assert all(len(g) == 1 and g[0].store == pp.find.store for g in got), pp.skill
        assert [g[0].items for g in got] == [find_items(pp.find, p) for p in range(3, ranks + 2)], pp.skill
        assert pp.find.items_per_phase >= 1 and got[0][0].items > pp.find.items, pp.skill


def test_every_shipped_find_is_a_good_a_staying_card_consumes(shipped_opening: Opening):
    staying = staying_stores(shipped_opening)
    assert len(staying) > 5
    assert {pp.find.store for pp in shipped_opening.phase_pays} <= staying


def test_a_find_of_a_good_only_one_off_cards_or_standing_actions_use_is_refused(shipped_opening: Opening):
    o = shipped_opening
    pp = next(p for p in o.phase_pays if p.skill == "woodcutting")
    taken = {x.store for c in o.cards if c.cap is None for x in (*c.inputs, *c.drains, *c.costs)}
    capped = {x.store for c in o.cards if c.cap is not None for x in (*c.inputs, *c.drains, *c.costs)}
    standing = {x.store for a in o.standing for x in a.costs}
    for store in ("flint", "wire", "warmth"):   # only a one-off card, or only a standing action, takes each
        assert store in capped | standing and store not in taken, store
        with pytest.raises(ValueError, match=f"phase_pays woodcutting: finds {store}, which no card that stays"):
            check_phase_pays(with_table(o, "woodcutting", find=pp.find.model_copy(update={"store": store})))


def test_a_card_that_stays_makes_a_store_findable_until_something_retires_it(shipped_opening: Opening):
    o = shipped_opening
    pp = next(p for p in o.phase_pays if p.skill == "woodcutting")
    base = pp.find.model_copy(update={"store": "wire"})
    card = CardEntry.model_validate({**next(c for c in o.cards if c.id == "knap_edge").model_dump(), "id": "planted_card",
                                     "cap": None, "inputs": [{"store": "wire", "items": 1}]})
    with_card = with_table(o.model_copy(update={"cards": [*o.cards, card]}), "woodcutting", find=base)
    check_phase_pays(with_card)
    gone = TriggerEntry(id="t_planted_retire", when=ConditionEntry(test="at_least", subject_kind="skill_level",
                        id="woodcutting", value=3),
                        outcome=OutcomeEntry(unlocks=[UnlockEntry(unlock_kind="retired", id="planted_card")]))
    with pytest.raises(ValueError, match="finds wire, which no card that stays"):
        check_phase_pays(with_card.model_copy(update={"triggers": [*with_card.triggers, gone]}))
