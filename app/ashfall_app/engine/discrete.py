"""The value of a discrete subject: 0/1 for Unlocked and Running, a count for LaneRules. Reads only. A CardCount is solved, not discrete
(conditions.py)."""
from .gates import is_unlocked
from .index import index
from .lanes import TapCard
from .orders import AfterTime, DiscreteSubject, LaneRules, Unlocked
from .rates import running
from .rules import Rules
from .state import Save


def discrete_value(save: Save, rules: Rules, subject: DiscreteSubject) -> int:
    if isinstance(subject, Unlocked):
        return int(is_unlocked(save, rules, subject.unlock))
    if isinstance(subject, LaneRules):
        return _lane_rules(save, rules, subject)
    now = running(save, rules)
    run = now.runs.get(subject.runner)
    return int(run is not None and now.shares[subject.runner] > 0 and run.num > 0)


def _lane_rules(save: Save, rules: Rules, subject: LaneRules) -> int:
    """Orders tapping a known card on the lane whose `when` is not AfterTime(0); an unknown card is not counted."""
    cards = index(rules).cards
    return sum(1 for o in save.orders
               if isinstance(o.then, TapCard) and o.then.card in cards and cards[o.then.card].lane == subject.lane
               and o.when != AfterTime(0))
