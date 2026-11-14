"""The habits' formulas (statements 10-12), each from the numbers it names and nothing else."""
import math

from ..journal import Fade, Habits, Press


def diligence(settled: float, habits: Habits) -> float:
    return habits.floor + (1 - habits.floor) * 0.5 ** (settled / habits.halflife)


def budget(settled: float, habits: Habits) -> int:
    span = habits.lines_start - habits.lines_floor
    return math.floor(habits.lines_floor + span * 0.5 ** (settled / habits.lines_halflife) + 0.5)


def faded(fade: Fade, w: int) -> float:
    return fade.base * fade.fade**w


def pressed(press: Press, days_in_a_row: int) -> float:
    return min(1.0, press.base * (1 + press.press * (days_in_a_row - 1)))
