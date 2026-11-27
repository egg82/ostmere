"""Week five's readings of a played route (docs/design/week-five-plan.md, item 9) that the week-two readouts do not
make: the lane a role was cast on, each chain's length per cast, the preparation gap, the visits with no decision, and the
order a card opens in against the beat its outcome lands. Each reads saves and lines and takes its ids from the caller,
so a chapter plugs in by naming them (policy.py). Readouts report; the unlock-order and undecided-visit checks return what
they found for a test to assert. Ids and numbers only (CLAUDE.md, "Never spoil the owner")."""
from collections import Counter
from collections.abc import Callable, Collection, Iterable, Mapping, Sequence

from ashfall_app.engine import CardId, Line, Rules, Save, SetQueue, TapCard, Unlock, UnlockKind, Verb
from ashfall_app.engine.people.castparts import cast_features
from tests.daythree.counters import Counts, Visit, spendable
from tests.weektwo.counters import decides
from tests.weekone import fights


def cast_lane(save: Save, rules: Rules, role: str) -> str | None:
    """The lane `role` was cast on in `save`: the one whose `<role>_<lane>` feature is held, None before the cast."""
    held = {u.id for u in save.unlocked if u.kind is UnlockKind.FEATURE}
    found = [str(lane) for lane in cast_features(rules) if f"{role}_{lane}" in held]
    return found[0] if found else None


def cast_line(route: str, save: Save, rules: Rules, roles: Sequence[str]) -> str:
    """One line of the cast-lane readout: each role and the lane it was cast on ("none" before the cast)."""
    return f"{route}: " + ", ".join(f"{r} -> {cast_lane(save, rules, r) or 'none'}" for r in roles)


def chain_lengths(lines: Iterable[Line], rules: Rules) -> dict[str, list[int]]:
    """For each card with a chain, the links of each cast that resolved any, in time order: the link lines the card wrote
    at one instant. A cast that resolved none wrote no line and is not listed."""
    keys = {c.id: frozenset(c.chain.lines) for c in rules.cards if c.chain is not None}
    per = Counter((x.card, x.time) for x in lines if x.card is not None and x.card in keys and x.key in keys[x.card])
    out: dict[str, list[int]] = {str(card): [] for card in keys}
    for (card, _), n in sorted(per.items(), key=lambda kv: kv[0][1]):
        out[str(card)].append(n)
    return out


def chain_text(route: str, found: Mapping[str, Sequence[int]]) -> list[str]:
    """The chain-length readout: per card, the casts that chained and their lengths."""
    return [f"{route} {card}: {len(n)} casts chained, lengths {list(n)}" for card, n in found.items()]


def count(visit: Visit, rules: Rules) -> Counts:
    """A visit's counters as week two reads them: spend as day three's, a queued stage never a decision."""
    return Counts(visit.label, visit.gap, len(spendable(visit.returned, rules)),
                  sum(1 for s in visit.steps if decides(s, rules)))


def undecided_visits(counts: Sequence[Counts]) -> list[str]:
    """The labels of visits where nothing was decided (the plan's target is none: every visit decides)."""
    return [c.label for c in counts if c.decide == 0]


def decision_ratio(counts: Sequence[Counts]) -> tuple[int, int]:
    """(visits with a decision, visits): sharp's ratio is read against the week's floor of three in four."""
    return sum(1 for c in counts if c.decide > 0), len(counts)


def first_held(saves: Iterable[Save], wanted: Collection[Unlock]) -> dict[Unlock, int]:
    """The first save time each of `wanted` is held, over `saves` in time order; one never held is absent."""
    found: dict[Unlock, int] = {}
    for s in saves:
        held = set(s.unlocked)
        found |= {u: s.time for u in wanted if u not in found and u in held}
    return found


def unlock_order(opened: Mapping[Unlock, int], landed: Mapping[str, int], pairs: Sequence[tuple[Unlock, str]]) -> list[str]:
    """The pairs (an unlock, the beat whose outcome opens it) where the unlock was held before the beat landed, or the
    beat never did: a card that shows ahead of the story that makes it."""
    out: list[str] = []
    for unlock, beat in pairs:
        at, beat_at = opened.get(unlock), landed.get(beat)
        if at is not None and (beat_at is None or at < beat_at):
            out.append(f"{unlock.kind.value} {unlock.id} held at {at} s, before {beat} landed at {beat_at}")
    return out


def strip_cards(v: Verb, cards: Collection[CardId]) -> Verb | None:
    """`v` without `cards`: a tap of one is dropped, a queue loses its entries that tap one."""
    if isinstance(v, TapCard):
        return None if v.card in cards else v
    if isinstance(v, SetQueue):
        return SetQueue(tuple(e for e in v.entries if not (isinstance(e.verb, TapCard) and e.verb.card in cards)))
    return v


def prepared_gap(week: fights.Week, cards: Collection[CardId], measure: Callable[[Save], int]) -> tuple[int, int]:
    """(measure with `cards` built, measure without) over the same span, the log's taps and queue entries of `cards`
    taken out for the second: the line held against unheld, the gap with the new card against without."""
    bare = [(at, v) for at, v in ((at, strip_cards(v, cards)) for at, v in week.log) if v is not None]
    return measure(fights.run(week, week.log)), measure(fights.run(week, bare, strict=False))
