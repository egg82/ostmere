"""The click and the undo as the verbs' docstrings state them: what changes (phase, picks, click_level, topped_at, the
stack) and what does not (XP, unlocks, the stack's other entries), the undo window, and that an undo is exact."""
from hypothesis import given, strategies as st

from ashfall_app.engine import BP, ModifierKind, NodeId, PhaseState, Save, advance, explain
from ashfall_app.engine.nodes import NODE_PREFIX
from ashfall_app.engine.phases import at_top, level_shown, phase_state
from ashfall_app.engine.prestige import menu, undo_open
from prestige_world import (
    CURVE, K, MAKE_OTHER, P, N1, N2, N3, SPAN, at_second, click, rules, undo, xp_now,
)

R = rules()


def node_entries(save: Save) -> list[tuple[ModifierKind, int, str]]:
    return [(m.kind, m.amount_bp, m.source) for m in explain(save, R, MAKE_OTHER).muls if m.source.startswith(NODE_PREFIX)]


def test_a_skill_that_has_not_topped_out_is_in_its_first_phase():
    state = phase_state(at_second(R, 299), R, K)
    assert state == PhaseState() and not at_top(at_second(R, 299), R, K)


def test_topping_out_sets_topped_at_to_the_instant_xp_reached_the_top():
    top = at_second(R, SPAN)
    assert at_top(top, R, K)
    assert phase_state(top, R, K) == PhaseState(topped_at=SPAN)
    assert phase_state(advance(top, R, 450), R, K).topped_at == SPAN   # set once, not moved by waiting


def test_the_click_lifts_the_phase_and_keeps_everything_earned():
    top = at_second(R, SPAN)
    after = click(top, R, N1)
    assert phase_state(after, R, K) == PhaseState(phase=2, picks=(N1,), topped_at=None, click_level=1)
    assert xp_now(after, R) == xp_now(top, R) == SPAN
    assert (after.time, after.unlocked, after.fired, after.modifiers) == (top.time, top.unlocked, top.fired, top.modifiers)
    assert not at_top(after, R, K)


def test_the_click_puts_its_rank_in_the_stack_without_storing_it():
    top = at_second(R, SPAN)
    assert node_entries(top) == []
    assert node_entries(click(top, R, N1)) == [(ModifierKind.MUL_BP, BP + 1000, "node:n1")]
    assert click(top, R, N1).modifiers == top.modifiers


def test_xp_goes_on_in_the_new_phase_and_tops_it_at_the_next_top():
    after = click(at_second(R, SPAN), R, N1)
    assert xp_now(advance(after, R, 450), R) == 450
    assert phase_state(advance(after, R, 599), R, K).topped_at is None
    topped = advance(after, R, 600)
    assert at_top(topped, R, K) and phase_state(topped, R, K).topped_at == 600
    assert xp_now(advance(topped, R, 5000), R) == 3 * SPAN - 1   # this phase's ceiling, inside the 1000 s window


def test_a_click_after_a_long_wait_lands_below_the_new_top():
    waited = at_second(R, 2000)
    assert phase_state(waited, R, K) == PhaseState(topped_at=SPAN)   # one click waiting, in the phase it was in
    assert xp_now(waited, R) == 2 * SPAN - 1
    after = click(waited, R, N1)
    state = phase_state(after, R, K)
    assert (state.phase, state.click_level, state.topped_at) == (2, 2, None)   # no second click waiting
    assert level_shown(CURVE, P, 2, xp_now(after, R)) == 2
    assert not at_top(after, R, K)


def test_a_click_when_the_carried_xp_is_short_of_the_new_top_has_no_topped_at():
    after = click(at_second(R, 450), R, N1)
    state = phase_state(after, R, K)
    assert (state.phase, state.topped_at, state.click_level) == (2, None, 2)   # 150 XP into the new phase: level 2


def test_a_second_click_adds_a_second_rank_to_the_same_entry():
    first = click(at_second(R, SPAN), R, N1)
    second = click(advance(first, R, 600), R, N1)
    assert phase_state(second, R, K) == PhaseState(phase=3, picks=(N1, N1), topped_at=None, click_level=1)
    assert node_entries(second) == [(ModifierKind.MUL_BP, BP + 2000, "node:n1")]


# The undo.

def test_the_undo_window_is_open_until_work_after_the_click_earns_a_level():
    after = click(at_second(R, SPAN), R, N1)
    assert [undo_open(advance(after, R, t), R, K) for t in (300, 399, 400, 599)] == [True, True, False, False]


def test_levels_the_carry_lands_at_the_click_do_not_close_the_window():
    after = click(at_second(R, 500), R, N1)   # 200 XP into phase 2: shown level 2 at the click
    assert phase_state(after, R, K).click_level == 2
    assert [undo_open(advance(after, R, t), R, K) for t in (500, 599, 600)] == [True, True, False]


def test_the_undo_takes_the_pick_and_leaves_the_phase_and_its_levels():
    clicked = click(at_second(R, SPAN), R, N1)
    after = undo(advance(clicked, R, 350), R)
    assert phase_state(after, R, K) == PhaseState(phase=2, picks=(), topped_at=None, click_level=1)
    assert xp_now(after, R) == 350
    assert node_entries(after) == []
    assert not undo_open(after, R, K)   # a pick is owed: nothing more to undo


def test_the_menu_after_an_undo_is_the_one_the_undone_pick_came_from():
    top = at_second(R, SPAN)
    before = menu(top, R, K)
    clicked = click(top, R, N1)
    assert menu(undo(advance(clicked, R, 350), R), R, K) == before
    assert menu(clicked, R, K) == before   # n1 has two ranks: still on the menu after one


def test_the_menu_is_fixed_while_the_phase_runs():
    clicked = click(at_second(R, SPAN), R, N2)
    assert {menu(advance(clicked, R, t), R, K) for t in (300, 350, 450, 599)} == {(N1, N3)}


def test_a_pick_fills_the_owed_slot_without_moving_the_phase_xp_or_click_level():
    clicked = click(at_second(R, SPAN), R, N1)
    undone = undo(advance(clicked, R, 350), R)
    refilled = click(undone, R, N2)
    assert phase_state(refilled, R, K) == PhaseState(phase=2, picks=(N2,), topped_at=None, click_level=1)
    assert xp_now(refilled, R) == 350
    assert [m.source for m in explain(refilled, R, MAKE_OTHER).muls if m.source.startswith(NODE_PREFIX)] == []   # n2 aims at work


@given(first=st.sampled_from([N1, N2]), again=st.sampled_from([N1, N2]), wait=st.integers(0, 98),
       at=st.sampled_from([SPAN, 450]))
def test_undo_then_the_same_pick_is_a_save_equal_to_never_undoing(first: NodeId, again: NodeId, wait: int, at: int):
    """Two runs to one instant. `again` is the pick refilled; the control run clicks it directly."""
    base = at_second(R, at)
    t = at + wait
    clicked = click(base, R, first)
    refilled = click(undo(advance(clicked, R, t), R), R, first)
    never = advance(clicked, R, t)
    assert refilled == never
    # Control: a different pick after an undo is the save of clicking that pick, plus the wait.
    other = click(undo(advance(clicked, R, t), R), R, again)
    assert other == advance(click(base, R, again), R, t)
