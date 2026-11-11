"""Prestige phases built (engine phases.py, phaseevents.py, prestige.py, pickentries.py): topping out and the carry's
end as solved instants, the click and the undo through decide(), each refusal, rank entries derived from the picks,
counted levels in conditions, and a rebase keeping the phase."""
from dataclasses import replace

import pytest

from ashfall_app.engine import (
    AtLeast, Flow, IdKind, NodeDef, NodeId, PacingCurve, Prestige, PrestigeDef, PrestigeRefusal, PrestigeRefused,
    RateRef, Rename, Rules, Save, SkillDef, SkillId, SkillLevel, StandingDef, StoreCap, StoreDef, StoreId, UndoPick,
    ActionId, FlowKind, Unlock, UnlockKind, advance, decide, encode, new_save, next_event, per_hour, rebase, units,
    validate_rules, value,
)
from ashfall_app.engine.cards import Outcome
from ashfall_app.engine.ids import TriggerId
from ashfall_app.engine.status import TriggerDef
from ashfall_app.engine.triggers import trigger_events, triggers_now
from ashfall_app.engine.conditions import rise_time, subject_value
from ashfall_app.engine.gates import effective_stack, store_cap
from ashfall_app.engine.phases import (
    counted_xp, level_counted, level_shown, next_level_xp, phase_state, phase_top, skill_state, waiting_levels,
    xp_ceiling,
)
from ashfall_app.engine.prestige import menu, ranks_taken, undo_open
from ashfall_app.engine.segments import value_at

H = 3600
GATHER, CRAFT = SkillId("gather"), SkillId("craft")
WOOD, PLANK = StoreId("wood"), StoreId("plank")
PICK, SAW = ActionId("pick"), ActionId("saw")
A, B, C, D = NodeId("a"), NodeId("b"), NodeId("c"), NodeId("d")
CURVE = PacingCurve((units(10), units(40), units(100), units(200)))
PRESTIGE = PrestigeDef(top_level=4, carry_window_s=48 * H, menu_size=2)
"""A phase spans units(100): 100 h of gather's 1 XP per hour."""
RULES = Rules(
    stores=(StoreDef(WOOD, units(10_000)), StoreDef(PLANK, units(10_000))),
    skills=(SkillDef(GATHER), SkillDef(CRAFT)),
    standing=(StandingDef(PICK, makes=(Flow(WOOD, per_hour(1)),), skill=GATHER, xp_per_hour=per_hour(1)),
              StandingDef(SAW, makes=(Flow(PLANK, per_hour(1)),), skill=CRAFT, xp_per_hour=per_hour(1) // 4)),
    curve=CURVE, prestige=PRESTIGE,
    nodes=(NodeDef(A, GATHER, StoreCap(WOOD), ranks=2, per_rank_bp=1_000),
           NodeDef(B, GATHER, RateRef(SAW, FlowKind.MAKE, PLANK), ranks=1, per_rank_bp=1_000),
           NodeDef(C, GATHER, StoreCap(PLANK), ranks=1, per_rank_bp=1_000),
           NodeDef(D, CRAFT, RateRef(PICK, FlowKind.MAKE, WOOD), ranks=1, per_rank_bp=1_000)),
)
START = new_save(RULES)


def gxp(save: Save) -> int:
    return value_at(skill_state(save, GATHER).xp, save.time)


def shown(save: Save) -> int:
    return level_shown(CURVE, PRESTIGE, phase_state(save, RULES, GATHER).phase, gxp(save))


def refused(save: Save, rules: Rules, t: int, verb: Prestige | UndoPick) -> PrestigeRefusal:
    with pytest.raises(PrestigeRefused) as found:
        decide(save, rules, t, verb)
    return found.value.reason


def test_the_fixture_is_valid():
    validate_rules(RULES)


def test_phase_arithmetic():
    assert phase_top(CURVE, PRESTIGE, 2) == units(200)
    assert xp_ceiling(CURVE, PRESTIGE, 1) == units(200) - 1
    assert xp_ceiling(CURVE, None, 1) == units(200)
    assert level_shown(CURVE, PRESTIGE, 1, units(150)) == 4
    assert level_shown(CURVE, PRESTIGE, 2, units(150)) == 3
    assert level_counted(CURVE, PRESTIGE, 2, units(100)) == 4 == level_counted(CURVE, PRESTIGE, 1, units(100))
    assert waiting_levels(CURVE, PRESTIGE, 1, units(140)) == 2
    assert waiting_levels(CURVE, PRESTIGE, 1, units(99)) == 0
    assert next_level_xp(CURVE, PRESTIGE, 1, units(99)) == units(100)
    assert next_level_xp(CURVE, PRESTIGE, 1, units(100)) is None
    assert next_level_xp(CURVE, PRESTIGE, 2, units(100)) == units(110)
    assert counted_xp(CURVE, PRESTIGE, 2, 5) == units(110)
    assert counted_xp(CURVE, PRESTIGE, 2, 8) is None
    with pytest.raises(ValueError):
        phase_top(CURVE, PRESTIGE, 0)


def test_topping_out_is_an_instant_solved_off_the_xp():
    s = advance(START, RULES, 50 * H)
    found = next_event(s, RULES)
    assert found is not None and found.time == 100 * H
    assert phase_state(advance(START, RULES, 100 * H - 1), RULES, GATHER).topped_at is None
    assert phase_state(advance(START, RULES, 120 * H), RULES, GATHER).topped_at == 100 * H


def test_xp_stops_at_the_carrys_end_and_the_other_lines_run_on():
    s = advance(START, RULES, 300 * H)
    assert gxp(s) == units(148)
    assert skill_state(s, GATHER).xp.rate == 0
    assert value(s, RULES, WOOD, 300 * H) == units(300)


def test_xp_stops_short_of_the_next_top_however_long_the_carry():
    rules = replace(RULES, prestige=replace(PRESTIGE, carry_window_s=1_000 * H))
    s = advance(new_save(rules), rules, 400 * H)
    assert value_at(skill_state(s, GATHER).xp, s.time) == units(200) - 1
    after = decide(s, rules, 400 * H, Prestige(GATHER, A))
    ps = phase_state(after, rules, GATHER)
    assert (ps.phase, ps.click_level, ps.topped_at) == (2, 3, None)
    assert value_at(skill_state(advance(after, rules, 410 * H), GATHER).xp, 410 * H) == units(210) - 1


def test_a_click_at_the_top_and_one_thirty_hours_later_end_equal():
    at_top = advance(decide(START, RULES, 100 * H, Prestige(GATHER, A)), RULES, 130 * H)
    later = decide(START, RULES, 130 * H, Prestige(GATHER, A))
    assert gxp(at_top) == gxp(later) == units(130)
    assert shown(at_top) == shown(later) == 2
    end_p, end_q = advance(at_top, RULES, 200 * H), advance(later, RULES, 200 * H)
    assert (gxp(end_p), shown(end_p)) == (gxp(end_q), shown(end_q))


def test_the_click_lifts_the_phase_and_keeps_the_xp_and_the_counted_level():
    s = advance(START, RULES, 100 * H)
    after = decide(s, RULES, 100 * H, Prestige(GATHER, A))
    assert phase_state(after, RULES, GATHER) == replace(phase_state(s, RULES, GATHER), phase=2, picks=(A,),
                                                         topped_at=None, click_level=1)
    assert gxp(after) == gxp(s) == units(100)
    assert subject_value(after, RULES, SkillLevel(GATHER)) == subject_value(s, RULES, SkillLevel(GATHER)) == 4
    assert skill_state(after, GATHER).xp.rate > 0


def test_a_level_condition_counts_across_phases():
    after = decide(START, RULES, 100 * H, Prestige(GATHER, A))
    assert subject_value(advance(after, RULES, 130 * H), RULES, SkillLevel(GATHER)) == 5
    assert rise_time(after, RULES, AtLeast(SkillLevel(GATHER), 5, 5)) == 110 * H
    assert rise_time(after, RULES, AtLeast(SkillLevel(GATHER), 8, 8)) is None


def test_a_trigger_on_a_level_fires_at_the_counted_level():
    rules = replace(RULES, triggers=(TriggerDef(TriggerId("five"), AtLeast(SkillLevel(GATHER), 5, 5), Outcome()),))
    after = decide(new_save(rules), rules, 100 * H, Prestige(GATHER, A))
    assert advance(after, rules, 110 * H - 1).fired == (False,)
    assert advance(after, rules, 110 * H).fired == (True,)
    assert [e.time for e in trigger_events(after, rules)] == [110 * H]
    unfired = replace(advance(after, rules, 130 * H), fired=(False,))
    assert [e.time for e in triggers_now(unfired, rules)] == [130 * H]


def test_a_rank_is_an_entry_derived_from_the_pick_and_an_undo_is_exact():
    s = advance(START, RULES, 100 * H)
    after = decide(s, RULES, 100 * H, Prestige(GATHER, A))
    assert store_cap(after, RULES, WOOD) == units(11_000)
    assert [m.source for m in effective_stack(after, RULES)] == ["node:a"]
    undone = decide(after, RULES, 100 * H, UndoPick(GATHER))
    assert store_cap(undone, RULES, WOOD) == units(10_000)
    assert effective_stack(undone, RULES) == effective_stack(s, RULES)
    assert phase_state(undone, RULES, GATHER).phase == 2 and gxp(undone) == units(100)


def test_after_an_undo_the_next_prestige_fills_the_owed_pick_from_the_same_menu():
    s = advance(START, RULES, 100 * H)
    offered = menu(s, RULES, GATHER)
    undone = decide(decide(s, RULES, 100 * H, Prestige(GATHER, A)), RULES, 100 * H, UndoPick(GATHER))
    assert offered == menu(undone, RULES, GATHER) == (A, B)
    filled = decide(undone, RULES, 101 * H, Prestige(GATHER, B))
    ps = phase_state(filled, RULES, GATHER)
    assert (ps.phase, ps.picks, ps.click_level) == (2, (B,), 1)
    assert ranks_taken(filled, RULES, B) == 1 and ranks_taken(filled, RULES, NodeId("nope")) == 0


def test_a_full_node_leaves_the_menu():
    s = decide(START, RULES, 100 * H, Prestige(GATHER, A))
    s = decide(s, RULES, 200 * H, Prestige(GATHER, A))
    assert menu(s, RULES, GATHER) == (B, C)


def test_the_undo_closes_at_the_first_level_from_work():
    after = decide(START, RULES, 100 * H, Prestige(GATHER, A))
    assert undo_open(advance(after, RULES, 110 * H - 1), RULES, GATHER)
    assert refused(after, RULES, 110 * H, UndoPick(GATHER)) is PrestigeRefusal.UNDO_CLOSED


def test_a_finished_track_is_mastered():
    rules = replace(RULES, nodes=(replace(RULES.nodes[0], ranks=1), RULES.nodes[3]))
    s = decide(new_save(rules), rules, 100 * H, Prestige(GATHER, A))
    assert refused(s, rules, 200 * H, Prestige(GATHER, A)) is PrestigeRefusal.TRACK_DONE
    rested = advance(s, rules, 400 * H)
    assert phase_state(rested, rules, GATHER).topped_at == 200 * H
    assert value_at(skill_state(rested, GATHER).xp, rested.time) == units(248)


@pytest.mark.parametrize(("rules", "t", "verb", "reason"), [
    (replace(RULES, prestige=None, nodes=()), 100 * H, Prestige(GATHER, A), PrestigeRefusal.NO_PRESTIGE),
    (RULES, 100 * H, Prestige(SkillId("nope"), A), PrestigeRefusal.UNKNOWN_SKILL),
    (replace(RULES, opening=(Unlock(UnlockKind.SKILL, CRAFT),)), 100 * H, Prestige(GATHER, A),
     PrestigeRefusal.LOCKED_SKILL),
    (RULES, 99 * H, Prestige(GATHER, A), PrestigeRefusal.NOT_AT_TOP),
    (RULES, 100 * H, Prestige(GATHER, C), PrestigeRefusal.NOT_ON_MENU),
    (RULES, 100 * H, Prestige(GATHER, D), PrestigeRefusal.NOT_ON_MENU),
    (RULES, 100 * H, UndoPick(GATHER), PrestigeRefusal.NOTHING_TO_UNDO),
    (replace(RULES, prestige=None, nodes=()), 100 * H, UndoPick(GATHER), PrestigeRefusal.NO_PRESTIGE),
    (RULES, 100 * H, UndoPick(SkillId("nope")), PrestigeRefusal.UNKNOWN_SKILL),
    (replace(RULES, opening=(Unlock(UnlockKind.SKILL, CRAFT),)), 100 * H, UndoPick(GATHER),
     PrestigeRefusal.LOCKED_SKILL),
], ids=["no-prestige", "unknown-skill", "locked", "not-at-top", "past-the-menu", "other-track", "nothing-to-undo",
        "undo-no-prestige", "undo-unknown-skill", "undo-locked"])
def test_each_refusal(rules: Rules, t: int, verb: Prestige | UndoPick, reason: PrestigeRefusal):
    assert refused(new_save(rules), rules, t, verb) is reason


def test_an_owed_pick_cannot_be_undone_again():
    undone = decide(decide(START, RULES, 100 * H, Prestige(GATHER, A)), RULES, 100 * H, UndoPick(GATHER))
    assert refused(undone, RULES, 100 * H, UndoPick(GATHER)) is PrestigeRefusal.NOTHING_TO_UNDO


def test_a_rebase_keeps_the_phase_and_renames_its_picks():
    s = decide(START, RULES, 100 * H, Prestige(GATHER, A))
    assert rebase(encode(s, RULES), RULES) == s
    renamed = replace(RULES, nodes=(replace(RULES.nodes[0], id=NodeId("a2")), *RULES.nodes[1:]))
    moved = rebase(encode(s, RULES), renamed, (Rename(IdKind.NODE, "a", "a2"),))
    assert phase_state(moved, renamed, GATHER).picks == (NodeId("a2"),)
    assert store_cap(moved, renamed, WOOD) == units(11_000)
