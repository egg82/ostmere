"""MovePick as its docstring states it: the rank leaves its node and parks on a menu node, is out of play until the click
into the phase after next, costs the same whenever in a phase it is made, and never shows in the stack while parked.
Also the refusals only MovePick has (the shared ones: test_refusals.py)."""
import pytest

from ashfall_app.engine import (
    MovePick, NodeId, ParkedRank, PhaseState, PrestigeRefusal, PrestigeRefused, Save, UndoPick, advance, decide,
    decode, encode,
)
from ashfall_app.engine.pickentries import pick_entries
from ashfall_app.engine.phases import phase_state
from ashfall_app.engine.prestige import menu, refusal
from prestige_world import J1, K, N1, N2, N3, N4, at_second, click, rules, undo

R = rules()
P = PrestigeRefusal


def move(save: Save, node: NodeId, to: NodeId, t: int | None = None) -> Save:
    return decide(save, R, save.time if t is None else t, MovePick(K, node, to))


def stack_nodes(save: Save) -> list[str]:
    return [m.source for m in pick_entries(save, R)]


def phase_two() -> Save:
    """K clicked n1 at its first top: phase 2, picks (n1,), menu (n1, n2)."""
    return click(at_second(R, 300), R, N1)


def test_a_move_takes_the_rank_off_its_node_and_parks_it_two_phases_out():
    after = move(phase_two(), N1, N2)
    state = phase_state(after, R, K)
    assert (state.phase, state.picks, state.parked) == (2, (), (ParkedRank(N2, 4),))
    assert (state.topped_at, state.click_level) == (None, 1)


def test_a_parked_rank_is_in_no_stack_and_its_node_leaves_the_menu():
    start = phase_two()
    assert stack_nodes(start) == ["node:n1"] and menu(start, R, K) == (N1, N2)
    after = move(start, N1, N2)
    assert stack_nodes(after) == []
    assert menu(after, R, K) == (N1, N3)   # n2 is full with its parked rank, so the menu moves on


def test_the_next_click_leaves_it_parked_and_the_one_after_settles_it():
    after = move(phase_two(), N1, N2)
    third = click(advance(after, R, 600), R, N1)
    assert phase_state(third, R, K).parked == (ParkedRank(N2, 4),) and stack_nodes(third) == ["node:n1"]
    fourth = click(advance(third, R, 900), R, N3)
    state = phase_state(fourth, R, K)
    assert (state.phase, state.picks, state.parked) == (4, (N1, N2, N3), ())
    assert sorted(stack_nodes(fourth)) == ["node:n1", "node:n2", "node:n3"]


@pytest.mark.parametrize("t", [301, 450, 599])
def test_the_cost_is_the_same_whenever_in_the_phase_the_move_is_made(t: int):
    after = move(advance(phase_two(), R, t), N1, N2)
    assert phase_state(after, R, K).parked == (ParkedRank(N2, 4),)


def test_an_undo_after_a_settling_click_takes_back_the_clicks_own_pick():
    after = move(phase_two(), N1, N2)
    fourth = click(advance(click(advance(after, R, 600), R, N1), R, 900), R, N3)
    undone = undo(fourth, R)
    assert phase_state(undone, R, K).picks == (N1, N2)


def test_a_move_of_a_multi_rank_node_takes_one_rank():
    two = click(advance(click(at_second(R, 300), R, N1), R, 600), R, N1)
    assert phase_state(two, R, K).picks == (N1, N1)
    after = move(two, N1, N2)
    assert phase_state(after, R, K).picks == (N1,)


def test_every_refusal_only_a_move_has_is_reached():
    owed = undo(phase_two(), R)
    cases = [
        (owed, MovePick(K, N1, N2), P.PICK_OWED),
        (phase_two(), MovePick(K, N2, N1), P.NOT_PICKED),
        (phase_two(), MovePick(K, J1, N2), P.NOT_PICKED),
        (at_second(R, 300), MovePick(K, N1, N2), P.NOT_PICKED),
        (phase_two(), MovePick(K, N1, N3), P.NOT_ON_MENU),
        (phase_two(), MovePick(K, N1, NodeId("ghost")), P.NOT_ON_MENU),
        (move(phase_two(), N1, N2), MovePick(K, N2, N3), P.NOT_PICKED),   # a parked rank is not held
        (phase_two(), MovePick(K, N1, N1), P.NOT_ON_MENU),   # n1 holds one of its two ranks and is on the menu: still no
    ]
    for save, verb, reason in cases:
        assert refusal(save, R, verb) is reason, verb
        with pytest.raises(PrestigeRefused) as found:
            decide(save, R, save.time, verb)
        assert found.value.reason is reason


def test_a_pick_owed_is_refused_before_a_missing_pick():
    assert refusal(undo(phase_two(), R), R, MovePick(K, N4, N2)) is P.PICK_OWED


def test_a_move_to_a_full_node_is_refused():
    full = advance(click(at_second(R, 300), R, N2), R, 600)   # n2 has one rank, taken
    assert N2 not in menu(full, R, K)
    assert refusal(full, R, MovePick(K, N2, N2)) is P.NOT_ON_MENU


def test_a_skill_with_a_parked_rank_round_trips_through_the_save_text():
    after = move(phase_two(), N1, N2)
    assert decode(encode(after, R), R) == after
    assert phase_state(after, R, K) != PhaseState(phase=2, picks=(), topped_at=None, click_level=1)


def test_a_skill_with_nothing_parked_encodes_without_the_field():
    assert "parked" not in encode(phase_two(), R)
    assert "parked" in encode(move(phase_two(), N1, N2), R)


def test_a_move_changes_no_xp_unlock_or_latch():
    start = phase_two()
    after = move(start, N1, N2)
    assert (after.time, after.skills[0].xp, after.unlocked, after.fired) == (
        start.time, start.skills[0].xp, start.unlocked, start.fired)


def test_an_undo_with_every_pick_moved_away_has_nothing_to_undo():
    moved = move(phase_two(), N1, N2)
    assert phase_state(moved, R, K).picks == ()
    assert refusal(moved, R, UndoPick(K)) is P.NOTHING_TO_UNDO
