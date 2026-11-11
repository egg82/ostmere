"""What the rules did lately (docs/design/opening-screen.md, "Lately"): one entry per rule, built from the engine's
rule changes (engine DESIGN.txt, "Rule changes") and kept on the save's row. A rule is known by what it says, its
condition and verb, since rules have no id: a reorder keeps its entry, an edit makes another rule. The write that adds
to it prunes it: an entry whose rule the save no longer has goes, unless the game ended the rule (it stays, `ended`
set), and past KEPT, the entries changed longest ago go. A slice of a long absence that stops short of now adds without
pruning (gathered), so slices end as one write would. A goal stint's entry keeps, while it runs, the levels its start
reported, and once it lands, what the save gained in those stores while it ran (`made`)."""

from dataclasses import dataclass, replace

from .. import engine as e
from ..engine.codec import Json

KEPT = 8
MADE_KEPT = 2
"""How many stores an ended stint's `made` names: its goal's store first, then the largest gains."""

type Levels = tuple[tuple[str, int], ...]


@dataclass(frozen=True)
class RuleRun:
    """A rule's starts since its entry began, its last start and its last let-go, each with the level of the store its
    condition reads (None for one on no store). off_at is None until it first lets go. `ended`: the game removed the
    rule (engine RuleChange.ended), off_at being when; on_at is None only on an ended rule that never came on.
    on_levels: a running goal stint's levels at its start (engine RuleChange.levels); made: an ended stint's gains
    (stint_made), () on every other entry."""

    order: e.Order
    starts: int
    on_at: int | None
    on_level: int | None
    off_at: int | None = None
    off_level: int | None = None
    ended: e.Ended | None = None
    on_levels: Levels = ()
    made: Levels = ()

    @property
    def last(self) -> int:
        return max(self.on_at or 0, self.off_at or 0)


def standing(orders: tuple[e.Order, ...], queue: tuple[e.QueueEntry, ...]) -> tuple[e.Order, ...]:
    """The orders whose entries are kept live: the save's rules, and each goal stint in its queue (reported as
    Order(until, verb), engine rulelog)."""
    return orders + tuple(e.Order(q.until, q.verb) for q in queue if isinstance(q.verb, e.SwitchMix))


def merged(runs: tuple[RuleRun, ...], changes: tuple[e.RuleChange, ...],
           orders: tuple[e.Order, ...]) -> tuple[RuleRun, ...]:
    """`runs` with `changes` applied in order, pruned to the rules in `orders`, the most recent change first. A let-go
    of a rule with no recorded start makes no entry. merged(gathered(r, c1), c2, o) == merged(r, c1 + c2, o): a save
    caught up in slices keeps its runs gathered, unpruned, until the slice that reaches now."""
    return pruned(gathered(runs, changes), orders)


def gathered(runs: tuple[RuleRun, ...], changes: tuple[e.RuleChange, ...]) -> tuple[RuleRun, ...]:
    """`runs` with `changes` applied in order and nothing pruned: entries in the order they were first made. A start of
    a rule whose entry ended begins a fresh entry, as does an end of one with no live entry."""
    by = {r.order: r for r in runs}
    for c in changes:
        r = by.get(c.order)
        live = r if r is not None and r.ended is None else None
        if c.ended is not None:
            start = live or RuleRun(c.order, 0, None, None)
            made = stint_made(c.order, start.on_levels, c.levels) if c.ended is e.Ended.STINT else ()
            by[c.order] = replace(start, off_at=c.time, off_level=c.level, ended=c.ended, on_levels=(), made=made)
        elif c.on:
            by[c.order] = RuleRun(c.order, (live.starts if live else 0) + 1, c.time, c.level,
                                  live.off_at if live else None, live.off_level if live else None,
                                  on_levels=c.levels)
        elif live is not None:
            by[c.order] = replace(live, off_at=c.time, off_level=c.level)
    return tuple(by.values())


def stint_made(order: e.Order, on: Levels, off: Levels) -> Levels:
    """What each store reported at both ends gained between them, gains of a whole item or more only: the store
    `order`'s condition reads first, then the largest, ties in `off`'s order, at most MADE_KEPT."""
    was = dict(on)
    gains = [(st, n - was[st]) for st, n in off if st in was and n - was[st] >= e.QUANTITY_SCALE]
    cond = order.when
    goal = None if isinstance(cond, e.AfterTime) or not isinstance(cond.subject, e.StoreValue) else cond.subject.store
    return tuple(sorted(gains, key=lambda g: (g[0] != goal, -g[1]))[:MADE_KEPT])


def pruned(runs: tuple[RuleRun, ...], orders: tuple[e.Order, ...]) -> tuple[RuleRun, ...]:
    """The entries of rules in `orders` or ended, the most recent change first, at most KEPT."""
    kept = [r for r in runs if r.order in orders or r.ended is not None]
    return tuple(sorted(kept, key=lambda r: r.last, reverse=True)[:KEPT])


def runs_to_json(runs: tuple[RuleRun, ...]) -> Json:
    """The stored form: the orders as the decision log keeps a SetOrders, and each entry's numbers beside them, an
    ended entry's reason after them (a live entry keeps the five numbers a build without `ended` reads), and a
    stint's levels under keys of their own, left out while no entry has any, which a build without them ignores."""
    stored: dict[str, Json] = {"orders": e.verb_to_json(e.SetOrders(tuple(r.order for r in runs))),
                               "runs": [_stored(r) for r in runs]}
    if any(r.on_levels or r.made for r in runs):
        stored |= {"on_levels": [_pairs(r.on_levels) for r in runs], "made": [_pairs(r.made) for r in runs]}
    return stored


def _pairs(levels: Levels) -> Json:
    return [[st, n] for st, n in levels]


def _stored(r: RuleRun) -> Json:
    nums: list[Json] = [r.starts, r.on_at, r.on_level, r.off_at, r.off_level]
    return nums if r.ended is None else [*nums, r.ended.value]


def runs_from_json(value: Json) -> tuple[RuleRun, ...]:
    """What runs_to_json wrote; () for None (a save no write of this kind has touched) or anything else."""
    if not isinstance(value, dict):
        return ()
    nums = value.get("runs")
    try:
        verb = e.verb_from_json(value.get("orders"))
    except e.StateFormatError:
        return ()
    if not isinstance(verb, e.SetOrders) or not isinstance(nums, list) or len(nums) != len(verb.orders):
        return ()
    entries = tuple(_entry(o, n) for o, n in zip(verb.orders, nums))
    if None in entries:
        return ()
    ons, made = _levels_list(value.get("on_levels"), len(nums)), _levels_list(value.get("made"), len(nums))
    return tuple(replace(r, on_levels=a, made=b) for r, a, b in zip(entries, ons, made) if r is not None)


def _levels_list(value: Json, n: int) -> list[Levels]:
    """One Levels per entry; () for each when the key is missing or malformed (a row an older build wrote)."""
    if not isinstance(value, list) or len(value) != n:
        return [()] * n
    return [_levels(v) for v in value]


def _levels(value: Json) -> Levels:
    if not isinstance(value, list):
        return ()
    pairs = [(p[0], _whole(p[1])) for p in value if isinstance(p, list) and len(p) == 2 and isinstance(p[0], str)]
    return tuple((st, n) for st, n in pairs if n is not None) if len(pairs) == len(value) else ()


def _entry(order: e.Order, value: Json) -> RuleRun | None:
    if not isinstance(value, list) or len(value) not in (5, 6):
        return None
    ended = _ended(value[5]) if len(value) == 6 else None
    starts, on_at, on_level, off_at, off_level = (_whole(v) for v in value[:5])
    if len(value) == 6 and ended is None:
        return None
    if starts is None or (on_at is None and ended is None) or not _nulls_ok(value[:5]):
        return None
    return RuleRun(order, starts, on_at, on_level, off_at, off_level, ended)


def _ended(v: Json) -> e.Ended | None:
    return next((x for x in e.Ended if x.value == v), None)


def _whole(v: Json) -> int | None:
    return v if isinstance(v, int) and not isinstance(v, bool) else None


def _nulls_ok(value: list[Json]) -> bool:
    """Every number is a whole number or null."""
    return all(v is None or _whole(v) is not None for v in value)
