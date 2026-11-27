"""Row 02 of MUTANTS_guards.txt: no band: a at-most guard in quantities is a plain threshold, its release ignored."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/orders/latches.py',
     '''from ..core.state import Save
''',
     '''from ..core.state import Save
from dataclasses import replace as _replace

from .orders import AtLeast as _AtLeast, AtMost as _AtMost


def _plain(save, rules, c):
    if isinstance(c, _AtMost) and not (c.value_of_cap or c.release_of_cap):
        return _replace(c, release=c.value)
    return c
'''),
    ('ashfall_app/engine/orders/latches.py',
     '''        g = change_time(save, rules, cond, on)
''',
     '''        g = change_time(save, rules, _plain(save, rules, cond), on)
'''),
    ('ashfall_app/engine/orders/latches.py',
     '''        if changes_now(save, rules, cond, on):
''',
     '''        if changes_now(save, rules, _plain(save, rules, cond), on):
'''),
]
