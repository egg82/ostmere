"""A rule's latches over time: when the next of them changes, and the one that changes now. A rule's `when` latch and
each guard's latch are separate latches, each solved as an order condition is (DESIGN.txt, "RULE GUARDS")."""
from .conditions import change_time
from .orders import Latch, Order, guard_latches, latch_of, when_latch
from .rules import Rules
from .state import Save


def latch_change_time(save: Save, rules: Rules, order: Order, latch: Latch) -> int | None:
    """The first time any of the rule's latches changes; None when none will under the current rates."""
    t = change_time(save, rules, order.when, when_latch(latch))
    for cond, on in zip(order.unless, guard_latches(latch)):
        g = change_time(save, rules, cond, on)
        if g is not None and (t is None or g < t):
            t = g
    return t


def flipped_now(save: Save, rules: Rules, order: Order, latch: Latch) -> Latch | None:
    """The rule's latch with the first of its latches that changes now flipped, `when` before the guards in list order;
    None when none changes now."""
    when, guards = when_latch(latch), guard_latches(latch)
    if change_time(save, rules, order.when, when) == save.time:
        return latch_of(not when, guards)
    for j, (cond, on) in enumerate(zip(order.unless, guards)):
        if change_time(save, rules, cond, on) == save.time:
            return latch_of(when, guards[:j] + (not on,) + guards[j + 1:])
    return None
