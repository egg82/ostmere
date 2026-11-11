"""The parts the engine's stack-keyed memos compare by identity (gates.stack_inputs): with fights in the rules the
lanes enter them only as the speeds a fight tap kept, so a lane change that leaves those alone is a memo hit."""
from dataclasses import replace

from ashfall_app.engine import TapCard, decide, new_save
from ashfall_app.engine.gates import stack_inputs
from fight_world import HUNT, world


def same_parts(a: tuple[object, ...], b: tuple[object, ...]) -> bool:
    return len(a) == len(b) and all(x is y for x, y in zip(a, b))


def test_lanes_rebuilt_around_the_same_kept_speeds_leave_the_stack_inputs_as_they_were():
    r = world(2, 6)
    tapped = decide(new_save(r), r, 0, TapCard(HUNT))
    assert any(ls.speed is not None for ls in tapped.lanes)    # control: the tap keeps its odds entries as a speed
    fresh = replace(tapped, lanes=tuple(replace(ls) for ls in tapped.lanes))
    assert fresh.lanes is not tapped.lanes
    assert same_parts(stack_inputs(fresh, r), stack_inputs(tapped, r))


def test_a_fight_tap_starting_changes_the_stack_inputs():
    r = world(2, 6)
    idle = new_save(r)
    tapped = decide(idle, r, 0, TapCard(HUNT))
    assert not same_parts(stack_inputs(tapped, r), stack_inputs(idle, r))
