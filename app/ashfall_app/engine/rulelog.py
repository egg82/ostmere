"""Rule starts and let-gos: an order's `when` latch turning true (it comes on) or false (it lets go) across one instant
or one decision (DESIGN.txt, "Rule changes"; a guard pausing it is not one: "RULE GUARDS"), and an order the game
removed (DESIGN.txt, "Retired chores", "Logged"). Orders have no id, so a change names the order itself, matched
across the two saves by equality: a reorder keeps it, an edit makes it another order."""
from dataclasses import dataclass
from enum import Enum

from .conditions import is_true, subject_value
from .gone import left_lanes
from .ids import CardId, StoreId
from .index import index
from .lanes import TapCard
from .mixes import SwitchMix, flatten_shares
from .orders import AfterTime, Order, QueueEntry, StoreValue, pruned, when_latch
from .plan import controlling_entry
from .rules import Rules
from .state import Save


class Ended(Enum):
    """Why an order's entry ended: a season's turn retired its chore, its person left the town, or (STINT) a goal stint
    popped at its goal, or (DRY) one the game handed back because its card ran out of input. A stint is reported as
    Order(entry.until, entry.verb), so it is known by its mix and goal."""

    SEASON = "season"
    LEFT = "left"
    STINT = "stint"
    DRY = "dry"


@dataclass(frozen=True)
class RuleChange:
    """`level`: the amount of the store the order's condition reads, at `time` (after the instant's outcomes), in
    quantity units; None when its condition reads no store. `ended`: set only on an order an outcome removed, which
    reads `on` False, as a let-go does. `levels`: on a goal stint's start and its STINT end only, the amount at `time`
    (quantity units) of each store its mix's cards make (their makes and outcome stores), in rules.stores order."""

    time: int
    order: Order
    on: bool
    level: int | None
    ended: Ended | None = None
    levels: tuple[tuple[StoreId, int], ...] = ()


def rule_changes(before: Save, after: Save, rules: Rules) -> tuple[RuleChange, ...]:
    """Each order of `after` whose latch differs from the same order's in `before` (False where `before` has none), in
    `after`'s order; then each distinct order of `before` an outcome removed, in `before`'s order."""
    if before.orders == after.orders and before.latches == after.latches and before.queue == after.queue:
        return ()
    retired = _retired_cards(before, after, rules)
    latched = tuple(RuleChange(after.time, o, when_latch(on), _level(after, rules, o))
                    for o, on in zip(after.orders, after.latches) if when_latch(on) != _was_on(before, o, retired))
    return latched + _ended(before, after, rules) + _stints(before, after, rules)


def _stints(before: Save, after: Save, rules: Rules) -> tuple[RuleChange, ...]:
    """A goal stint (a queue entry that switches a mix) coming to control: on; then each one that left the queue with
    its goal holding in `after`: off, ended STINT; and, where time moved (the game's doing, not a decision's), one that
    left with its goal not holding: ended DRY. A stint the player removed before its goal holds reports nothing."""
    started = _controlling_stint(after, rules)
    changes = [RuleChange(after.time, _stint_order(started), True, None, None, _made_levels(after, rules, started))] \
        if started is not None and started != _controlling_stint(before, rules) else []
    changes += [RuleChange(after.time, _stint_order(q), False, None, Ended.STINT, _made_levels(after, rules, q))
                for q in dict.fromkeys(before.queue)
                if isinstance(q.verb, SwitchMix) and q not in after.queue and is_true(after, rules, q.until)]
    changes += [RuleChange(after.time, _stint_order(q), False, None, Ended.DRY, _made_levels(after, rules, q))
                for q in dict.fromkeys(before.queue)
                if after.time > before.time and isinstance(q.verb, SwitchMix) and q not in after.queue
                and not is_true(after, rules, q.until)]
    return tuple(changes)


def _made_levels(save: Save, rules: Rules, entry: QueueEntry) -> tuple[tuple[StoreId, int], ...]:
    """The amount now of each store a card in the stint's mix makes, at a share above 0, in rules.stores order."""
    assert isinstance(entry.verb, SwitchMix)
    cards = index(rules).cards
    made = {f.store for share in flatten_shares(save.mixes, entry.verb.mix) if share.share_bp > 0
            for f in (*cards[share.card].makes, *cards[share.card].outcome.stores)}
    return tuple((st.id, subject_value(save, rules, StoreValue(st.id))) for st in rules.stores if st.id in made)


def _controlling_stint(save: Save, rules: Rules) -> QueueEntry | None:
    i = controlling_entry(save, rules)
    return save.queue[i] if i is not None and isinstance(save.queue[i].verb, SwitchMix) else None


def _stint_order(entry: QueueEntry) -> Order:
    return Order(entry.until, entry.verb)


def _ended(before: Save, after: Save, rules: Rules) -> tuple[RuleChange, ...]:
    retired = _retired_cards(before, after, rules)
    gone = [o for o in dict.fromkeys(before.orders) if _kept(o, retired) not in after.orders]
    if not gone:
        return ()
    went = left_lanes(after) - left_lanes(before)
    cards = index(rules).cards
    found: list[RuleChange] = []
    for o in gone:
        if not isinstance(o.then, TapCard) or o.then.card not in cards:
            continue
        why = Ended.SEASON if o.then.card in retired else Ended.LEFT if cards[o.then.card].lane in went else None
        if why is not None:
            found.append(RuleChange(after.time, o, False, _level(after, rules, o), why))
    return tuple(found)


def _retired_cards(before: Save, after: Save, rules: Rules) -> frozenset[CardId]:
    """The cards named by the retire_orders of the triggers fired in `after` and not in `before`."""
    return frozenset(c for t, was, now in zip(rules.triggers, before.fired, after.fired) if now and not was
                     for c in t.outcome.retire_orders)


def _kept(order: Order, retired: frozenset[CardId]) -> Order | None:
    """What a season's retirement leaves of the order: a rule that keeps one of its actions keeps going, unlogged."""
    return pruned(order, lambda a: isinstance(a, TapCard) and a.card in retired)


def _was_on(save: Save, order: Order, retired: frozenset[CardId]) -> bool:
    return next((when_latch(on) for o, on in zip(save.orders, save.latches)
                 if order in (o, _kept(o, retired))), False)


def _level(save: Save, rules: Rules, order: Order) -> int | None:
    cond = order.when
    if isinstance(cond, AfterTime) or not isinstance(cond.subject, StoreValue):
        return None
    return subject_value(save, rules, cond.subject)
