"""A dilemma offer sets a promise (an answer that queued the player's own work) against something else the player values
(rules/checks/cards/promise_checks.py): each way it can be malformed fails the loader, and the shipped dilemmas pass."""
from collections.abc import Callable

import pytest

from ashfall_app.rules.entries.entries import TriggerEntry
from ashfall_app.rules.entries.offer_entries import AnswerEntry, OfferEntry
from ashfall_app.rules.checks.cards.promise_checks import check_promises, promises, unread_promises
from ashfall_app.rules.schema import Opening

DILEMMA = "o_pair_pot"


def dilemmas_of(o: Opening) -> list[OfferEntry]:
    found = [x for x in o.offers if x.tests]
    assert len(found) >= 3, "found almost no dilemmas: the check is blind"
    return found


def edit_dilemma(o: Opening, change: Callable[[OfferEntry], OfferEntry]) -> Opening:
    return o.model_copy(update={"offers": [change(x) if x.id == DILEMMA else x for x in o.offers]})


def edit_answers(o: Opening, change: Callable[[AnswerEntry], AnswerEntry]) -> Opening:
    return edit_dilemma(o, lambda x: x.model_copy(update={"answers": [change(a) for a in x.answers]}))


def test_every_shipped_dilemma_passes_and_names_a_promise(shipped_opening: Opening):
    check_promises(shipped_opening)
    made = promises(shipped_opening)
    for x in dilemmas_of(shipped_opening):
        assert set(x.tests) <= set(made)
    assert not set(unread_promises(shipped_opening)) & {p for x in dilemmas_of(shipped_opening) for p in x.tests}


def test_each_malformed_dilemma_fails_by_name(shipped_opening: Opening):
    o = shipped_opening

    def keep(a: AnswerEntry) -> AnswerEntry:
        return a.model_copy(update={"breaks": []})
    cases: list[tuple[str, Opening]] = [
        ("which is not an answer that queues work", edit_dilemma(o, lambda x: x.model_copy(update={"tests": ["o_pair_pot_pot"]}))),
        ("does not require it given", edit_dilemma(o, lambda x: x.model_copy(update={"requires": [r for r in x.requires if r.unlock_kind != "answer"]}))),
        ("a promise kept is no dilemma", edit_dilemma(o, lambda x: x.model_copy(update={"requires": [r for r in x.requires if r.subject_kind != "running"]}))),
        ("one that breaks", edit_answers(o, keep)),
        ("has no modifier sourced to itself", edit_answers(o, lambda a: a.model_copy(update={"outcome": a.outcome.model_copy(update={"modifiers": []})}))),
        ("does not retire", edit_answers(o, lambda a: a.model_copy(update={"outcome": a.outcome.model_copy(update={"unlocks": [u for u in a.outcome.unlocks if u.unlock_kind != "retired"]})}))),
        ("which its offer does not test", edit_answers(o, lambda a: a.model_copy(update={"breaks": [*a.breaks, "o_stay_room"] if a.breaks else []}))),
    ]
    for match, bad in cases:
        with pytest.raises(ValueError, match=match):
            check_promises(bad)


def test_a_payoff_of_a_broken_promise_must_require_it_not_broken(shipped_opening: Opening):
    def drop(t: TriggerEntry) -> TriggerEntry:
        keep = [r for r in t.requires if r.test != "at_most"]
        return t.model_copy(update={"requires": keep})
    paid = [t for t in shipped_opening.triggers if any(r.test == "at_most" and r.unlock_kind == "answer" for r in t.requires)]
    assert len(paid) >= 3, "found almost no guarded payoffs: the check is blind"
    for t in paid:
        bad = shipped_opening.model_copy(update={"triggers": [drop(x) if x.id == t.id else x for x in shipped_opening.triggers]})
        with pytest.raises(ValueError, match="not given"):
            check_promises(bad)


def test_the_held_list_is_what_no_dilemma_tests(shipped_opening: Opening):
    bare = shipped_opening.model_copy(update={"offers": [x.model_copy(update={"tests": []}) for x in shipped_opening.offers]})
    bare = bare.model_copy(update={"offers": [x.model_copy(update={"answers": [a.model_copy(update={"breaks": []}) for a in x.answers]}) for x in bare.offers]})
    assert {"o_stay_room", "o_pair_room", "o_family_room"} <= set(unread_promises(bare))
    assert not {"o_stay_room", "o_pair_room", "o_family_room"} & set(unread_promises(shipped_opening))

