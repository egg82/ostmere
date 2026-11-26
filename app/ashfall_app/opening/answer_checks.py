"""Every answer keeps a consequence (decisions/principles.md, "No blind permanent choices"): the answers of an offer
differ by a lasting part the player can see, and the roles of a kinded offer are counted.

Lasting parts of an answer: a modifier (it names its source), an unlock something reads (a condition on it, on the
answer itself, or on the card's completions or running), and its role's tally. A difference of lane alone is none: two
cards on different lanes that nothing reads differ by nothing.

`check_tally_stores` runs in the loader. `unlasting_offers` and `untallied_kinds` are findings for the held gate
(tests/opening/test_answer_gate.py), which holds today's and lets the list only shrink."""
from typing import TYPE_CHECKING

from .refs import conditions, fail

if TYPE_CHECKING:
    from .offer_entries import AnswerEntry, OfferEntry
    from .schema import Opening


def check_tally_stores(o: "Opening") -> None:
    """Fails for a role tally that is not a declared hidden tally store, or is shared by two roles."""
    stores = {s.id: s for s in o.stores}
    seen: dict[str, str] = {}
    for k in o.offer_kinds:
        for r in k.roles:
            if r.tally is None:
                continue
            where, role = f"offer kind {k.kind}", f"{k.kind}/{r.role}"
            if r.tally not in stores or not (stores[r.tally].tally and stores[r.tally].hidden):
                fail(where, f"role {r.role} names tally {r.tally}, which is not a declared hidden tally store")
            if seen.setdefault(r.tally, role) != role:
                fail(where, f"role {r.role} shares tally {r.tally} with {seen[r.tally]}")


def untallied_kinds(o: "Opening") -> list[str]:
    """The kinds with a role that names no tally."""
    return [k.kind for k in o.offer_kinds if any(r.tally is None for r in k.roles)]


def unlasting_offers(o: "Opening") -> list[str]:
    """The offers whose answers all have the same lasting parts."""
    read = _read(o)
    tallies = {(k.kind, r.role): r.tally for k in o.offer_kinds for r in k.roles}
    return [x.id for x in o.offers if len({_lasting(x, a, read, tallies) for a in x.answers}) == 1]


def _read(o: "Opening") -> frozenset[tuple[str, str]]:
    """Every (unlock_kind, id) a condition reads; a card's completions and running read as ("card", id)."""
    out: set[tuple[str, str]] = set()
    for _, c, _ in conditions(o):
        if c.subject_kind == "unlocked" and c.unlock_kind is not None and c.id is not None:
            out.add((c.unlock_kind, c.id))
        elif c.subject_kind in ("card_count", "running") and c.id is not None:
            out.add(("card", c.id))
    return frozenset(out)


def _lasting(x: "OfferEntry", a: "AnswerEntry", read: frozenset[tuple[str, str]],
             tallies: dict[tuple[str, str], str | None]) -> frozenset[str]:
    parts = {f"modifier {m.model_dump_json()}" for m in a.outcome.modifiers}
    parts |= {f"unlock {u.unlock_kind} {u.id}" for u in a.outcome.unlocks if (u.unlock_kind, u.id) in read}
    if ("answer", a.id) in read:
        parts.add(f"answer {a.id}")
    tally = tallies.get((x.kind or "", a.role or ""))
    if tally is not None:
        parts.add(f"tally {tally}")
    return frozenset(parts)
