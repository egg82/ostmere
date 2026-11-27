"""Row 13 of MUTANTS_guards.txt: exact cap: an at-most share guard is read off the exact cap, not its whole items."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/orders/latches.py',
     '''from ..core.state import Save
''',
     '''from ..core.state import Save
from dataclasses import replace as _replace

from ..unlocks.gates import store_cap as _store_cap
from .orders import AtLeast as _AtLeast, AtMost as _AtMost
from .sharelevels import _quantity, read_levels as _read_levels
from ..core.units import BP as _BP, QUANTITY_SCALE as _Q, ceil_div as _ceil_div


def _exact(save, rules, c):
    if not isinstance(c, _AtMost) or not (c.value_of_cap or c.release_of_cap):
        return c
    cap = _store_cap(save, rules, c.subject.store)
    if isinstance(c, _AtLeast):
        value = _ceil_div(c.value * cap, _BP) if c.value_of_cap else c.value
        return _AtLeast(c.subject, value, max(value - _Q, _Q))
    value = c.value * cap // _BP if c.value_of_cap else c.value
    return _AtMost(c.subject, value, min(value + _Q, cap - 1))
'''),
    ('ashfall_app/engine/orders/latches.py',
     '''        g = change_time(save, rules, cond, on)
''',
     '''        g = change_time(save, rules, _exact(save, rules, cond), on)
'''),
    ('ashfall_app/engine/orders/latches.py',
     '''        if changes_now(save, rules, cond, on):
''',
     '''        if changes_now(save, rules, _exact(save, rules, cond), on):
'''),
]
