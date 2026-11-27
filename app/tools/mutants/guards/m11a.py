"""Row 11 of MUTANTS_guards.txt: start cap: a share guard's latch is read off the store's starting cap."""
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


def _read(save, rules, c):
    if not (getattr(c, "value_of_cap", False) or getattr(c, "release_of_cap", False)):
        return c
    whole = next(s.cap for s in rules.stores if s.id == c.subject.store) // _Q
    at_most = isinstance(c, _AtMost)
    value = _quantity(c.value, whole, at_most, at_most) if c.value_of_cap else c.value
    release = _quantity(c.release, whole, at_most, not at_most) if c.release_of_cap else c.release
    if at_most:
        return _AtMost(c.subject, value, max(release, value, min(value + _Q, whole * _Q - 1)))
    return _AtLeast(c.subject, value, min(release, value, max(value - _Q, _Q)))
'''),
    ('ashfall_app/engine/orders/latches.py',
     '''        g = change_time(save, rules, cond, on)
''',
     '''        g = change_time(save, rules, _read(save, rules, cond), on)
'''),
    ('ashfall_app/engine/orders/latches.py',
     '''        if changes_now(save, rules, cond, on):
''',
     '''        if changes_now(save, rules, _read(save, rules, cond), on):
'''),
]
