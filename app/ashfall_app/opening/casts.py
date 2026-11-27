"""A role cast from per-lane counts (api/contract/casting.txt, "CASTING"): the `casts` an outcome holds, the features
they declare, and the picks the loader fills in once the content is merged. Pure; the checks are cast_checks.py."""
from collections.abc import Iterator
from typing import TYPE_CHECKING

from .entries import OutcomeEntry
from .move_entries import CastEntry, CastPickEntry
from .town import LANE_TOKEN

if TYPE_CHECKING:
    from .schema import Opening


def cast_outcomes(o: "Opening") -> Iterator[tuple[str, OutcomeEntry]]:
    """The outcomes that may cast a role (a trigger's and an answer's), with where each sits."""
    yield from ((f"trigger {t.id}", t.outcome) for t in o.triggers)
    yield from ((f"answer {a.id}", a.outcome) for x in o.offers for a in x.answers)


def casts(o: "Opening") -> Iterator[tuple[str, CastEntry]]:
    for where, out in cast_outcomes(o):
        yield from ((where, c) for c in out.casts)


def candidates(o: "Opening") -> list[str]:
    """The lanes a role may go to, in declaration order: a single person (ruled, never a group or a station) with a name."""
    return [x.id for x in o.lanes if x.ruled and not x.pooled and not x.station and x.name_key is not None]


def feature_id(role: str, lane: str) -> str:
    return f"{role}_{lane}"


def role_features(o: "Opening") -> dict[str, set[str]]:
    """Each role a cast names, with the features its cast may unlock: one per candidate lane."""
    lanes = candidates(o)
    return {c.role: {feature_id(c.role, lane) for lane in lanes} for _, c in casts(o)}


def cast_unlocks(o: "Opening") -> Iterator[tuple[str, tuple[str, str]]]:
    """Each outcome that casts a role, with each (kind, id) its cast may unlock."""
    lanes = candidates(o)
    for where, c in casts(o):
        yield from ((where, ("feature", feature_id(c.role, lane))) for lane in lanes)


def cast_feature_ids(o: "Opening") -> list[str]:
    return sorted({f for fs in role_features(o).values() for f in fs})


def with_cast_picks(o: "Opening") -> "Opening":
    """`o` with every cast holding its picks: each candidate lane, its feature and, per pattern, the card the pattern's
    town card made on that lane. Idempotent."""
    if not any(True for _ in casts(o)):
        return o
    lanes = candidates(o)
    town = {tc.id: set(tc.lanes) for tc in o.town_cards}
    cards = {c.id for c in o.cards}

    def counted(pattern: str, lane: str) -> str | None:
        card = pattern.replace(LANE_TOKEN, lane)
        return card if lane in town.get(pattern, ()) and card in cards else None

    def picked(c: CastEntry) -> CastEntry:
        return c.model_copy(update={"picks": [CastPickEntry(lane=lane, feature=feature_id(c.role, lane),
                                                           counted=[counted(p, lane) for p in c.patterns])
                                              for lane in lanes]})

    def out(x: OutcomeEntry) -> OutcomeEntry:
        return x.model_copy(update={"casts": [picked(c) for c in x.casts]}) if x.casts else x

    return o.model_copy(update={
        "triggers": [t.model_copy(update={"outcome": out(t.outcome)}) for t in o.triggers],
        "offers": [x.model_copy(update={"answers": [a.model_copy(update={"outcome": out(a.outcome)}) for a in x.answers]})
                   for x in o.offers],
    })
