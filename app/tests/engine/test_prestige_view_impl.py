"""The read model under prestige phases (engine phaseview.py): a skill's row reads its shown level and the bar's ends
within the phase, and its SkillPhase serves the phase, counted level, top, waiting levels, menu with each target's
value before and after one more rank, the undo and mastery. api.level reads the shown level."""
from dataclasses import replace

from ashfall_app.engine import (
    BP, MenuNode, Prestige, SkillBar, advance, decide, level, new_save, per_hour, units, view,
)
from tests.engine.test_prestige_impl import A, B, CRAFT, GATHER, H, RULES, START
from tests.prestige_contract import prestige_world as world


def bar(*, at: int, clicked_at: int | None = None) -> SkillBar:
    """Gather's row at `at`, after a click of A at `clicked_at` when given."""
    s = START if clicked_at is None else decide(START, RULES, clicked_at, Prestige(GATHER, A))
    s = advance(s, RULES, max(at, s.time))
    return next(b for b in view(s, RULES).skills if b.skill == GATHER)


def test_phase_one_below_its_top():
    b = bar(at=50 * H)
    assert (b.level, b.level_xp, b.next_level_xp, b.next_level_at) == (3, units(40), units(100), 100 * H)
    assert b.prestige is not None
    p = b.prestige
    assert (p.phase, p.level_counted, p.at_top, p.waiting_levels, p.undo_open, p.mastered) == (1, 3, False, 0, False,
                                                                                               False)
    assert p.menu == (MenuNode(A, 0, 2, units(10_000), units(11_000)),
                      MenuNode(B, 0, 1, per_hour(1), per_hour(1) * 11 // 10))


def test_at_the_top_the_row_is_full_and_counts_the_levels_waiting():
    b = bar(at=130 * H)
    assert (b.level, b.level_xp, b.next_level_xp, b.next_level_at) == (4, units(100), None, None)
    assert b.prestige is not None
    assert (b.prestige.at_top, b.prestige.waiting_levels, b.prestige.level_counted) == (True, 1, 4)
    assert level(START, RULES, GATHER, 130 * H) == 4


def test_after_the_click_the_row_counts_from_the_new_phase():
    just = bar(at=100 * H, clicked_at=100 * H)
    assert just.prestige is not None and just.prestige.undo_open
    b = bar(at=130 * H, clicked_at=100 * H)
    assert (b.level, b.level_xp, b.next_level_xp, b.next_level_at) == (2, units(110), units(140), 140 * H)
    assert b.prestige is not None
    p = b.prestige
    assert (p.phase, p.level_counted, p.at_top, p.waiting_levels, p.undo_open) == (2, 5, False, 0, False)
    assert p.menu[0] == MenuNode(A, 1, 2, units(11_000), units(12_000))
    clicked = decide(START, RULES, 100 * H, Prestige(GATHER, A))
    assert level(clicked, RULES, GATHER, 130 * H) == 2


def test_a_skill_with_its_track_done_is_mastered_with_no_menu():
    craft_only = replace(RULES, nodes=tuple(n for n in RULES.nodes if n.skill == CRAFT))
    rows = {b.skill: b.prestige for b in view(new_save(craft_only), craft_only).skills}
    gather, craft = rows[GATHER], rows[CRAFT]
    assert gather is not None and craft is not None
    assert (gather.mastered, gather.menu, craft.mastered) == (True, (), False)


def test_no_prestige_no_phase():
    plain = replace(RULES, prestige=None, nodes=())
    assert all(b.prestige is None for b in view(new_save(plain), plain).skills)


def test_a_work_node_reads_the_cards_work_speed():
    r = world.rules()
    row = next(b for b in view(new_save(r), r).skills if b.skill == world.K)
    assert row.prestige is not None
    assert row.prestige.menu[1] == MenuNode(world.N2, 0, 1, BP, BP * 12 // 10)
