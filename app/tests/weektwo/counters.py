"""Week two's per-visit decide counter (docs/design/week-two-plan.md, item 1): day three's (daythree/counters.py) with
two changes. A rule change counts as a mix or queue change does, when it moves which of two goals lands first or what
the next return finds (the numbers file's "a share or rule change"). And queuing a stage of a staged build is refused as a decision, whatever it
moves (week-two.md, lesson 1: every visit's decision comes from content, never from queuing a stage). Spend is day
three's. By kind and not by id (CLAUDE.md, "Never spoil the owner")."""
from ashfall_app.engine import Rules, SetOrders
from tests.daythree import counters as c3
from tests.daythree.counters import Step, queues_a_stage


def heavy(step: Step, rules: Rules) -> bool:
    """The step's reading runs the saves on (`decides` reaches daythree/shifts.py): a mix, queue or orders change that is
    not the queuing of a stage."""
    return isinstance(step.verb, (*c3.MIX_VERBS, SetOrders)) and not queues_a_stage(step, rules)


def decides(step: Step, rules: Rules) -> bool:
    if queues_a_stage(step, rules):
        return False
    return c3.decides(step, rules) or (isinstance(step.verb, SetOrders) and c3.moves(step, rules))
