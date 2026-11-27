"""Row 12 of MUTANTS_guards.txt: no share band: an at-most share guard whose levels meet is a plain threshold."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/latches.py',
     '''from .state import Save
''',
     '''from .state import Save
from dataclasses import replace as _replace

from .gates import store_cap as _store_cap
from .orders import AtLeast as _AtLeast, AtMost as _AtMost
from .sharelevels import _quantity, read_levels as _read_levels
from .units import BP as _BP, QUANTITY_SCALE as _Q, ceil_div as _ceil_div


def _plain(save, rules, c):
    if isinstance(c, _AtMost) and c.value_of_cap and c.release_of_cap and c.value == c.release:
        r = _read_levels(save, rules, c)
        return _replace(r, release=r.value)
    return c
'''),
    ('ashfall_app/engine/latches.py',
     '''        g = change_time(save, rules, cond, on)
''',
     '''        g = change_time(save, rules, _plain(save, rules, cond), on)
'''),
    ('ashfall_app/engine/latches.py',
     '''        if changes_now(save, rules, cond, on):
''',
     '''        if changes_now(save, rules, _plain(save, rules, cond), on):
'''),
]
