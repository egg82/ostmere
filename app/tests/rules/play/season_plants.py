"""One planted failing variant of fixtures/season.toml for each part of week-two-plan item 6's check, as edits of the
good file: (old, new) pairs, each `old` unique in it. A plant is valid rules and breaks only its check; the failing id
is what the check must name."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Plant:
    name: str
    failing_id: str
    edits: tuple[tuple[str, str], ...]


TURN_STORES = 'stores = [{ store = "t_pool", items = 4 }, { store = "t_pool_card", items = 3 }]'
RATE = '{ target = "rate", id = "t_burn", flow = "cost", store = "t_pool", kind = "mul_bp", amount_bp = 5000, source = "t_turn_1" }'

PLANTS = (
    Plant("season card with no pool input", "t_gather", (('inputs = [{ store = "t_pool_card", items = 1 }]\n', ""),)),
    Plant("season card whose pool the turn does not fill", "t_gather",
          ((TURN_STORES, 'stores = [{ store = "t_pool", items = 4 }]'),)),
    Plant("season standing action whose pool the turn does not fill", "t_burn",
          ((TURN_STORES, 'stores = [{ store = "t_pool_card", items = 3 }]'),)),
    Plant("season rate modifier", "t_turn_1", ((TURN_STORES, TURN_STORES + f", modifiers = [{RATE}]"),)),
    Plant("season turn that is not a clock", "t_turn_2",
          (('id = "t_turn_2"\nseason = true\nwhen = { test = "after_time", value = 50400 }',
            'id = "t_turn_2"\nseason = true\nwhen = { test = "at_least", subject_kind = "store", id = "t_pool", value = 1 }'),)),
    Plant("season lane modifier", "t_turn_1",
          ((TURN_STORES, TURN_STORES + ', modifiers = [{ target = "lane", id = "hands", kind = "mul_bp", '
                                       'amount_bp = 12000, source = "t_turn_1" }]'),)),
)
