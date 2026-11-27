"""A promise is broken only by a choice (decisions/principles.md, "A promise is broken only by a choice, never by a
clock"). A promise is an answer that queues the player's own work. A dilemma is an offer that names it in `tests` and
sets it against something else the player values; its answers either keep it or, in `breaks`, give it up.

`check_promises` runs in the loader. `unread_promises` is a finding for the held gate (tests/rules/checks/test_promise_gate.py),
which holds today's list and lets it only shrink."""
from typing import TYPE_CHECKING

from ...entries.entries import ConditionEntry
from ...refs import fail

if TYPE_CHECKING:
    from ...entries.offer_entries import AnswerEntry, OfferEntry
    from ...schema import Opening


def promises(o: "Opening") -> dict[str, list[str]]:
    """Each answer that queues the player's own work, with the cards it queues."""
    return {a.id: list(a.outcome.queues) for x in o.offers for a in x.answers if a.outcome.queues}


def unread_promises(o: "Opening") -> list[str]:
    """The promises no offer sets against anything: no `tests` names them."""
    tested = {p for x in o.offers for p in x.tests}
    return [p for p in promises(o) if p not in tested]


def _has(conds: list[ConditionEntry], test: str, kind: str, id_: str, value: int, unlock: str | None = None) -> bool:
    return any(c.test == test and c.subject_kind == kind and c.id == id_ and c.value == value and c.unlock_kind == unlock
               for c in conds)


def check_promises(o: "Opening") -> None:
    """Fails, naming the offer, for a dilemma that tests what is no promise, does not require the
    promise made and its work running, has no answer that keeps and one that breaks, prices an answer by nothing it
    names, or breaks without retiring the queued work; and, naming the trigger, for a payoff of a promise that does not
    also require it not broken."""
    made = promises(o)
    for x in o.offers:
        where = f"offer {x.id}"
        for a in x.answers:
            if a.breaks and not x.tests:
                fail(f"answer {a.id}", "breaks a promise but its offer tests none")
        if x.tests:
            _check_dilemma(x, made, where)
    broken = {p: [a.id for x in o.offers for a in x.answers if p in a.breaks] for p in made}
    for t in o.triggers:
        for p, ends in broken.items():
            if ends and _has(t.requires, "at_least", "unlocked", p, 1, "answer"):
                for e in ends:
                    if not _has(t.requires, "at_most", "unlocked", e, 0, "answer"):
                        fail(f"trigger {t.id}", f"pays promise {p} without requiring {e} not given")


def _check_dilemma(x: "OfferEntry", made: dict[str, list[str]], where: str) -> None:
    for p in x.tests:
        if p not in made:
            fail(where, f"tests {p}, which is not an answer that queues work")
        if not _has(x.requires, "at_least", "unlocked", p, 1, "answer"):
            fail(where, f"tests {p} but does not require it given")
        for card in made[p]:
            if not _has(x.requires, "at_least", "running", card, 1):
                fail(where, f"tests {p} but does not require {card} running: a promise kept is no dilemma")
    breaking = [a for a in x.answers if a.breaks]
    if not breaking or len(breaking) == len(x.answers):
        fail(where, "needs an answer that keeps every promise it tests and one that breaks")
    for a in x.answers:
        _check_answer(a, x, made, f"answer {a.id}")


def _check_answer(a: "AnswerEntry", x: "OfferEntry", made: dict[str, list[str]], where: str) -> None:
    if not any(m.source == a.id for m in a.outcome.modifiers):
        fail(where, "has no modifier sourced to itself: a dilemma shows what each answer costs")
    for p in a.breaks:
        if p not in x.tests:
            fail(where, f"breaks {p}, which its offer does not test")
        retired = {u.id for u in a.outcome.unlocks if u.unlock_kind == "retired"}
        if not set(made[p]) <= retired:
            fail(where, f"breaks {p} but does not retire {', '.join(made[p])}")
