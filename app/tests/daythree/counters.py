"""The two per-visit counters day three adds (docs/design/day-three-plan.md, item 6), read off the saves a route's player
saw, by kind and not by id (CLAUDE.md, "Never spoil the owner").

spend: the cards on offer at the return that a tap now would start and that take from a store already at SPEND_LEVEL
of its cap, so a full store has something to spend on. decide: the decisions of the visit that choose something: an
answer, a choice of builds (a capped card tapped while another was ready), or a change of mix or queue that moves
which of two goals lands first, or that moves what the next return finds by a meaningful amount: a fight's odds, a goal's
landing, a capped store's level (shifts.py; the thresholds below). A goal is a capped card on offer; it lands at its next
completion with nobody deciding. Both are counted per visit and per absence (the gap before the visit, which is what the
return finds)."""
from dataclasses import dataclass

from ashfall_app.engine import (
    AnswerOffer, CardId, QueueEntry, Rules, Save, SaveMix, SetQueue, SwitchMix, TapCard, Verb, View, value_at, view,
)
from tests.daythree import shifts
from tests.daythree.landings import first_of, goals, landings

SPEND_LEVEL_BP = 8000
"""A store counts as full for spending at this share of its cap (the plan's 80%)."""
MIX_VERBS = (SaveMix, SwitchMix, SetQueue)
ODDS_MIN_BP = 250
"""A change moves a fight's odds meaningfully at this much of the loss share (basis points of fights lost), averaged
over the absence: about one point of the strongest fight's side or threat."""
FINISH_MIN_S = 3600
"""... a goal's landing at this many seconds: two of shifts.GRID_S's reads, one of which is read noise."""
LEVEL_MIN_BP = 2500
"""... a capped store's level at the next return at this share of its cap."""
FALLBACK_S = 4 * 3600
"""How far ahead the next return is taken to be when a step has none after it (a route's last visit)."""


@dataclass(frozen=True)
class Step:
    """One decision: its time, the verb, and the saves just before and after it."""

    at: int
    verb: Verb
    before: Save
    after: Save
    return_at: int | None = None
    """When the next visit starts, if there is one."""


@dataclass(frozen=True)
class Visit:
    label: str
    gap: int
    """Seconds away before it."""
    returned: Save
    """The save at its start: what the return finds."""
    steps: tuple[Step, ...]


@dataclass(frozen=True)
class Counts:
    label: str
    gap: int
    spend: int
    decide: int


def takes(rules: Rules, card: CardId) -> tuple[str, ...]:
    c = next(c for c in rules.cards if c.id == card)
    return tuple(str(x.store) for x in (*c.inputs, *c.costs))


def full_stores(save: Save, rules: Rules, v: View) -> frozenset[str]:
    return frozenset(str(ln.store) for ln in v.ledger if ln.cap > 0
                     and value_at(ln.segment, save.time) * 10_000 >= ln.cap * SPEND_LEVEL_BP)


def spendable(save: Save, rules: Rules) -> tuple[str, ...]:
    """The cards a tap would start now that take from a store at SPEND_LEVEL of its cap."""
    v = view(save, rules)
    full = full_stores(save, rules, v)
    return tuple(str(c.card) for c in v.cards if c.blocker is None and full & set(takes(rules, c.card)))


def moves_the_order(step: Step, rules: Rules) -> bool:
    """The decision changes which of two goals lands first, with nobody deciding after it."""
    cards = goals(step.before, rules)
    if len(cards) < 2:
        return False
    a, b = landings(step.before, rules, cards), landings(step.after, rules, cards)
    return any(first_of(a, x, y) != first_of(b, x, y) for i, x in enumerate(cards) for y in cards[i + 1:])


def staged(rules: Rules) -> frozenset[CardId]:
    """The cards built in stages: a cap of more than one."""
    return frozenset(c.id for c in rules.cards if c.cap is not None and c.cap > 1)


def queues_a_stage(step: Step, rules: Rules) -> bool:
    """The step sets the queue and every entry it adds taps a staged build: queuing a stage, nothing more."""
    if not isinstance(step.verb, SetQueue):
        return False
    added = [e for e in step.verb.entries if e not in step.before.queue]
    builds = staged(rules)
    return bool(added) and all(_taps(e) in builds for e in added)


def _taps(e: QueueEntry) -> CardId | None:
    return e.verb.card if isinstance(e.verb, TapCard) else None


def moves_the_return(step: Step, rules: Rules) -> bool:
    """The decision moves a fight's odds, a goal's landing or a capped store's level at the next return meaningfully,
    with nobody deciding after it. Queuing a stage moves its own build's landing and nothing the player chose, so it
    never counts here (week-two.md, lesson 1)."""
    if queues_a_stage(step, rules):
        return False
    if step.after == step.before:
        return False
    return meaningful(shifts.shift(step.before, step.after, rules, step.return_at or step.at + FALLBACK_S))


def meaningful(sh: shifts.Shift) -> bool:
    """Any one reading of the shift at or over its threshold: a fight's odds, a goal's landing, a capped store's level."""
    return sh.finish_s >= FINISH_MIN_S or sh.level_bp >= LEVEL_MIN_BP or sh.odds_bp >= ODDS_MIN_BP


def moves(step: Step, rules: Rules) -> bool:
    """The decision changes which of two goals lands first, or what the next return finds."""
    return moves_the_return(step, rules) or moves_the_order(step, rules)


def chooses(step: Step, rules: Rules) -> bool:
    """A tap of a capped card while another capped card was ready: a choice of builds."""
    if not isinstance(step.verb, TapCard):
        return False
    ready = [c for c in view(step.before, rules).cards if c.cap is not None and c.blocker is None]
    return any(c.card == step.verb.card for c in ready) and len(ready) > 1


def decides(step: Step, rules: Rules) -> bool:
    if isinstance(step.verb, AnswerOffer):
        return True
    return chooses(step, rules) or (isinstance(step.verb, MIX_VERBS) and moves(step, rules))


def count(visit: Visit, rules: Rules) -> Counts:
    return Counts(visit.label, visit.gap, len(spendable(visit.returned, rules)),
                  sum(1 for s in visit.steps if decides(s, rules)))


def line(c: Counts) -> str:
    return f"spend {c.spend:2d}  decide {c.decide:2d}"
