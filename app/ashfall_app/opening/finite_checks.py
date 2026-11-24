"""No soft-lock on a finite store (issue #438): for every store whose supply is finite, what it can ever supply covers
what progress needs of it, nothing optional can spend that, and no converter's cap can throw it away. On the built
Rules, ids and fields only, base amounts (finite_runners.py). Raises ValueError naming the store (refs.fail).

- Finite: every maker progress can count on is bounded: a capped card, or one that stops on a finite store (the
  largest such set, as the engine's spent stores are found). Its supply: its initial value, the triggers' and sure
  finished outcomes, sure capped cards' gives times their cap, and each pool a converter draws times the best ratio.
  Answers count for nothing: the player may decline them.
- Required: a capped card (a project or a told step: its cap says it ends) whose completions a trigger's condition
  reads at_least n needs those n completions' takes. A finite store progress needs makes its converters (uncapped runners drawing a
  pool into it) need what its other supply leaves short.
- Optional: every other consumer. A capped one spends at most the rest of its cap, one stopping on another finite
  store at most what that store lets it run, anything else without limit. A converter also stockpiles up to its
  target's cap, which counts when the pool has another use.
- Caps: a card converting a pool into a store whose cap is below what progress needs of it can lose the pool at that
  cap: the engine's full rule stops a mix card whose every outcome store is full (engine DESIGN.txt, "FULL OUTPUT"), but
  not a tap, nor a card a by-product keeps running. A standing action converting a pool is the world's clock, not the
  player's choice: what it loses at a cap passes.

Not read: an uncapped card's count a trigger reads (a reaction to repeatable work, which that card's town twins can
also spend the pool on), and outcomes (triggers, capped cards) landing on a store at its cap.
"""
from fractions import Fraction

from ..engine import AtLeast, CardCount, Rules, StoreId
from .finite_runners import Runner, runners, sure_outcomes, sure_unlocks
from .refs import fail

ONCE = StoreId("")
"""The key of a store's supply that lands once (initial, outcomes, capped cards), beside one key per pool."""


def check_finite_supply(rules: Rules) -> None:
    _Reading(rules).check()


class _Reading:
    def __init__(self, rules: Rules) -> None:
        self.rules = rules
        self.caps = {d.id: d.cap for d in rules.stores}
        self.all = runners(rules)
        self.sure = [r for r in self.all if r.sure]
        self.finite = _finite(self.sure, set(self.caps))
        self.required = _required(rules)
        self.outcomes = list(sure_outcomes(rules, sure_unlocks(rules)))
        self._supply: dict[StoreId, dict[StoreId, Fraction]] = {}
        self._demand: dict[StoreId, Fraction] = {}

    def check(self) -> None:
        for store in sorted(self.finite):
            if self.demand(store) > 0:
                self._check_store(store)

    def supply(self, store: StoreId) -> dict[StoreId, Fraction]:
        """The store's supply in parts: ONCE, and what each pool feeds it through converters."""
        if store not in self._supply:
            self._supply[store] = {}   # a cycle reads nothing more
            self._supply[store] = self._parts(store)
        return self._supply[store]

    def total(self, store: StoreId) -> Fraction:
        return sum(self.supply(store).values(), Fraction(0))

    def _parts(self, store: StoreId) -> dict[StoreId, Fraction]:
        d = next(d for d in self.rules.stores if d.id == store)
        once = Fraction(d.initial) + sum((Fraction(a.quantity * n) for out, n in self.outcomes
                                          for a in out.stores if a.store == store), Fraction(0))
        parts: dict[StoreId, Fraction] = {}
        for r in self.sure:
            if store not in r.gives:
                continue
            if r.units is not None:
                once += r.gives[store] * r.units
                continue
            pool = self._binding(r)
            if pool is not None:
                parts[pool] = max(parts.get(pool, Fraction(0)), self.total(pool) * r.gives[store] / r.takes[pool])
        return {ONCE: once, **parts}

    def _binding(self, r: Runner) -> StoreId | None:
        """The finite store that runs out first for an uncapped runner, or None when it stops on none."""
        pools = [s for s in r.stops if s in self.finite]
        return min(pools, key=lambda s: (self.total(s) / r.takes[s], s), default=None)

    def demand(self, store: StoreId) -> Fraction:
        """What progress needs of the store, consumed."""
        if store not in self._demand:
            self._demand[store] = Fraction(0)
            self._demand[store] = self._direct(store) + sum(self._via(store, u) for u in self._targets(store))
        return self._demand[store]

    def _direct(self, store: StoreId) -> Fraction:
        return sum((Fraction(self.required[r.id]) * r.takes[store] for r in self.all
                    if store in r.takes and r.id in self.required), Fraction(0))

    def _path(self, store: StoreId, target: StoreId) -> list[Runner]:
        return [r for r in self.all if r.units is None and store in r.stops and target in r.gives]

    def _targets(self, store: StoreId) -> list[StoreId]:
        found = {u for r in self.all if r.units is None and store in r.stops for u in r.gives}
        return sorted(u for u in found if u in self.finite and u != store and self.demand(u) > 0)

    def _via(self, store: StoreId, target: StoreId) -> Fraction:
        """What the converters from `store` into `target` must draw: target's need less its other supply, at the best
        ratio."""
        short = max(Fraction(0), self.demand(target) - (self.total(target) - self.supply(target).get(store, Fraction(0))))
        return short / max(r.gives[target] / r.takes[store] for r in self._path(store, target))

    def _check_store(self, store: StoreId) -> None:
        targets = self._targets(store)
        spare = self.total(store) - self.demand(store) - self._optional(store, targets)
        if spare < 0:
            fail(f"store {store}", f"finite: supplies {_items(self.total(store))} items, progress needs "
                                   f"{_items(self.demand(store))} and what else can spend it leaves {_items(spare)}")
        for u in targets:
            for r in self._path(store, u):
                self._check_cap(store, u, r)

    def _optional(self, store: StoreId, targets: list[StoreId]) -> Fraction:
        """What else can spend the store. A required card's completions past those progress reads come after them, so
        they can spend only what the other required cards need: the one finishing last spends its rest too late."""
        spent = Fraction(0)
        rests: list[Fraction] = []
        for r in self.all:
            if store not in r.takes or (r.units is None and store in r.stops and set(r.gives) & set(targets)):
                continue
            units = self._units(r, store)
            if units is None:
                fail(f"store {store}", f"finite and needed by progress, but {r.id} can spend it without limit")
            rest = max(0, units - self.required.get(r.id, 0)) * r.takes[store]
            if r.id in self.required:
                rests.append(rest)
            else:
                spent += rest
        spent += sum(rests, Fraction(0)) - min(rests, default=Fraction(0))
        uses = len(targets) + (1 if self._direct(store) > 0 else 0)
        if uses > 1:
            spent += sum((self.caps[u] / max(r.gives[u] / r.takes[store] for r in self._path(store, u))
                          for u in targets), Fraction(0))
        return spent

    def _units(self, r: Runner, store: StoreId) -> Fraction | None:
        """How many units a runner can run while `store` lasts: its cap, or what the first other finite store it stops
        on runs out at."""
        if r.units is not None:
            return Fraction(r.units)
        pools = [s for s in r.stops if s in self.finite and s != store]
        return min((self.total(s) / r.takes[s] for s in pools), default=None)

    def _check_cap(self, store: StoreId, target: StoreId, r: Runner) -> None:
        if self.caps[target] < self.demand(target) and r.card is not None:
            fail(f"store {store}", f"{r.id} draws it into {target}, whose cap is below what progress needs of it, so "
                                   "a tap or a by-product can lose it at that cap")


def _finite(sure: list[Runner], stores: set[StoreId]) -> set[StoreId]:
    finite = set(stores)
    changed = True
    while changed:
        changed = False
        for r in sure:
            if r.units is None and not (r.stops & finite) and set(r.gives) & finite:
                finite -= set(r.gives)
                changed = True
    return finite


def _required(rules: Rules) -> dict[str, int]:
    """Each capped card a trigger's condition reads at_least n completions of, at its largest n."""
    capped = {str(c.id) for c in rules.cards if c.cap is not None}
    found: dict[str, int] = {}
    for t in rules.triggers:
        for cond in (t.when, *t.requires):
            if isinstance(cond, AtLeast) and isinstance(cond.subject, CardCount) and str(cond.subject.card) in capped:
                found[str(cond.subject.card)] = max(found.get(str(cond.subject.card), 0), cond.value)
    return found


def _items(q: Fraction) -> str:
    return f"{float(q / 3_600_000):g}"
