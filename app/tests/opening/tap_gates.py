"""The one hard check behind "Progress never needs the same tap repeated by hand" (docs/decisions/pacing.md): a story
gate the player can meet only by tapping one card many times, before anything can tap it for them.

**Before automation** is structural: what the player can reach from a new save's unlock set without the features that
open mixes (the content's `first_mix.feature`) and rules (`LEDGER`, which opens the Rules tab: client
`game/orders.ts`, `rulesTabDrawn`). An outcome that unlocks either of them is never followed, and a count of the card
whose completion lands it is never met, so what arrives with mixes counts as after them. The reach follows the player's
own steps: a condition only the clock makes true (a time, a store falling, a store or level nothing but a standing
action fills) is not one, since mixes open within the opening's first steps. On the shipped opening the reach is
exactly what the scripted routes hold when mixes open (`test_tap_gates.py`).

**Many** is `MANY_TAPS`: the old rule's counter-example was 12 gathers to open the ruin and 10 scavenges for the fire,
so 10 taps of one card, the smaller of the two, is where a gate turns red.

A gate is counted when it is reachable before automation and its condition is a count of one card's completions, or a
store's amount that exactly one repeatable reachable card makes (no standing action making it too), read as the taps
that card needs at its own yield per completion. A gate on a skill level is never counted: a level is earned over time,
and a mix trains it as well as hands do."""
from math import ceil

from ashfall_app.engine import (
    AfterTime, AtLeast, CardCount, CardDef, Condition, FeatureId, Outcome, Rules, Running, SkillLevel, StoreValue,
    Unlock, UnlockKind, Unlocked,
)

MANY_TAPS = 10
LEDGER = FeatureId("ledger")


def _makes(card: CardDef) -> dict[str, int]:
    """Quantity one completion of the card puts into each store it makes, at its base speed."""
    out: dict[str, int] = {}
    for f in card.makes:
        out[f.store] = out.get(f.store, 0) + f.per_hour * card.work_s // 3600
    for a in card.outcome.stores:
        out[a.store] = out.get(a.store, 0) + a.quantity
    return out


class _Reach:
    """The unlock set reachable without automation, grown to a fixpoint."""

    def __init__(self, rules: Rules, automation: frozenset[FeatureId]):
        self.rules = rules
        self.held = {Unlock(UnlockKind.FEATURE, f) for f in automation}
        self.got: set[Unlock] = set(rules.opening or ())
        grew = True
        while grew:
            before = len(self.got)
            self._grow()
            grew = len(self.got) > before

    def has(self, kind: UnlockKind, id: str) -> bool:
        return self.rules.opening is None or Unlock(kind, id) in self.got

    def cards(self) -> list[CardDef]:
        return [c for c in self.rules.cards if self.has(UnlockKind.CARD, c.id)]

    def _brings(self, outcome: Outcome) -> bool:
        return bool(self.held & set(outcome.unlocks))

    def _land(self, outcome: Outcome) -> None:
        if not self._brings(outcome):
            self.got |= set(outcome.unlocks)

    def _grow(self) -> None:
        r = self.rules
        for c in self.cards():
            if all(self.can(q) for q in c.requires):
                self._land(c.outcome)
                self._land(c.finished)
        for t in r.triggers:
            if self.can(t.when) and all(self.can(q) for q in t.requires):
                self._land(t.outcome)
        for o in r.offers:
            if self.has(UnlockKind.OFFER, o.id):
                for a in o.answers:
                    self._land(a.outcome)

    def can(self, cond: Condition) -> bool:
        """The condition can come true by the player's own steps before automation, from a new save's state."""
        r = self.rules
        if isinstance(cond, AfterTime):
            return False
        s = cond.subject
        initial = next(d.initial for d in r.stores if d.id == s.store) if isinstance(s, StoreValue) else 0
        if not isinstance(cond, AtLeast):
            return initial <= cond.value
        if cond.value <= initial:
            return True
        if isinstance(s, Unlocked):
            return s.unlock in self.got
        if isinstance(s, CardCount):
            c = next(c for c in r.cards if c.id == s.card)
            brings = self._brings(c.outcome) or (self._brings(c.finished) and cond.value >= (c.cap or 0))
            return self.has(UnlockKind.CARD, s.card) and not brings
        if isinstance(s, StoreValue):
            return any(s.store in _makes(c) for c in self.cards())
        if isinstance(s, SkillLevel):
            return any(c.skill == s.skill for c in self.cards())
        if isinstance(s, Running):
            return self.has(UnlockKind.CARD, s.runner)
        return False   # LaneRules: counts the player's rules, which wait on automation


def _taps(reach: _Reach, cond: AtLeast) -> tuple[str, int] | None:
    """The one card this condition makes the player tap, and how many times; None when it needs no one card."""
    s = cond.subject
    if isinstance(s, CardCount):
        return s.card, cond.value
    if not isinstance(s, StoreValue):
        return None
    if any(s.store in {f.store for f in a.makes} for a in reach.rules.standing if reach.has(UnlockKind.ACTION, a.id)):
        return None
    makers = [(c, _makes(c).get(s.store, 0)) for c in reach.cards()]
    repeatable = [(c, q) for c, q in makers if q > 0 and c.cap is None]
    if len(repeatable) != 1:
        return None
    lump = sum(q * (c.cap or 0) for c, q in makers if c.cap is not None)
    initial = next(d.initial for d in reach.rules.stores if d.id == s.store)
    card, per_tap = repeatable[0]
    return card.id, ceil(max(0, cond.value - initial - lump) / per_tap)


def tap_heavy_gates(rules: Rules, first_mix_feature: str) -> list[str]:
    """Every gate reachable before automation that needs MANY_TAPS or more taps of one card, as text naming it."""
    reach = _Reach(rules, frozenset({FeatureId(first_mix_feature), LEDGER}))
    gates: list[tuple[str, bool, tuple[Condition, ...]]] = [
        (f"trigger {t.id}", True, (t.when, *t.requires)) for t in rules.triggers]
    gates += [(f"card {c.id}", reach.has(UnlockKind.CARD, c.id), c.requires) for c in rules.cards]
    gates += [(f"chip {c.id}", reach.has(UnlockKind.CHIP, c.id), (c.when,)) for c in rules.chips]
    found: list[str] = []
    for where, shown, conds in gates:
        if not (shown and all(reach.can(q) for q in conds)):
            continue
        for cond in conds:
            if isinstance(cond, AtLeast) and (n := _taps(reach, cond)) and n[1] >= MANY_TAPS:
                found.append(f"{where} needs {n[1]} taps of {n[0]} before automation")
    return found


def reachable_before_automation(rules: Rules, first_mix_feature: str) -> set[Unlock]:
    """The unlock set the check treats as reachable before automation (for its own test against a played route)."""
    return _Reach(rules, frozenset({FeatureId(first_mix_feature), LEDGER})).got
