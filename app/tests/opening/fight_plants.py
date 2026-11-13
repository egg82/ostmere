"""One planted failing variant of fixtures/fights.toml for each content check of combat-plan item 6, as edits of the
good file: (old, new) pairs, each `old` unique in it. A plant is a valid chapter for the loader's shape and the
engine's rules and breaks only its check; the failing id is what the check must name."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Plant:
    name: str
    failing_id: str
    edits: tuple[tuple[str, str], ...]


CLOCK_WHEN = 'when = { test = "at_least", subject_kind = "store", id = "t_clock", value = 5 }'
UNLOCKS = '{ unlock_kind = "feature", id = "combat" }, '
TEND = '''[[cards]]
id = "t_tend"
presentation = "action"
label_key = "t_c_tend"
work_s = 30
inputs = [{ store = "t_bitten", items = 1 }]

'''
TEND_UNLOCK = ', { unlock_kind = "card", id = "t_tend" }'
LOST_STORE = '''[[stores]]
id = "t_lost_hunt"
label_key = "t_s_lost_hunt"
cap_items = 100000
'''

PLANTS = (
    Plant("ramp reads a non-clock store", "t_ramp_1",
          ((CLOCK_WHEN, 'when = { test = "at_least", subject_kind = "store", id = "damp_wood", value = 5 }'),)),
    Plant("clock fed by a card", "t_ramp_1",
          (('work_s = 30\ncap = 1\nfinished = { unlocks = [{ unlock_kind = "action", id = "t_dusk" }] }',
            'work_s = 30\ncap = 1\nmakes = [{ store = "t_clock", items_per_hour = 1 }]\nfinished = { unlocks = [{ unlock_kind = "action", id = "t_dusk" }] }'),)),
    Plant("fight unlocked without combat", "t_hunt", ((UNLOCKS, ""),)),
    Plant("wound store with no cure", "t_bitten", ((TEND, ""), (TEND_UNLOCK, ""))),
    Plant("tally store unlocked by an outcome", "t_lost_hunt",
          ((UNLOCKS, UNLOCKS + '{ unlock_kind = "store", id = "t_lost_hunt" }, '),)),
)
