"""The content side of invariants 116 and 117 (engine DESIGN.txt, "ENTRIES HELD WHILE A CARD RUNS": "Release lock",
"Content"): a card entry's while_running list reaches the engine card in declaration order; adding it to a released card
passes the release lock as Safe (the lock only wants a write; no id is added); the schema refuses an amount below 1;
the loader has no check of its own, so the engine's validation names the card and the side."""
from typing import Any

import pytest
from pydantic import ValidationError

from ashfall_app import engine as e
from ashfall_app.opening.fight_entries import SideEntry, ThreatEntry
from ashfall_app.opening.lock import Lock, load_lock, merged, snapshot
from ashfall_app.opening.lock_checks import problems
from ashfall_app.opening.renames import RenameEntry, load_renames
from ashfall_app.opening.schema import CardEntry, Opening, to_rules
from held_world import kills

SIDE, THREAT = "hand", "wolf"


def guarded(o: Opening, card_index: int, *entries: dict[str, Any]) -> Opening:
    """`o` (the shipped opening) with a side and a threat declared and one released card holding `entries` while it runs."""
    cards = [CardEntry.model_validate({**c.model_dump(), "while_running": list(entries)}) if i == card_index else c
             for i, c in enumerate(o.cards)]
    return o.model_copy(update={
        "cards": cards, "sides": [*o.sides, SideEntry(id=SIDE, label_key="side.hand", base=300)],
        "threats": [*o.threats, ThreatEntry(id=THREAT, label_key="threat.wolf", base=100)]})


def test_the_loader_hands_the_engine_the_entries_in_declaration_order(shipped_opening: Opening):
    o = guarded(shipped_opening, 0, {"side": SIDE, "amount_bp": 1500}, {"side": "other", "amount_bp": 20})
    o = o.model_copy(update={"sides": [*o.sides, SideEntry(id="other", label_key="side.other", base=100)]})
    card = to_rules(o).cards[0]
    assert [(w.side, w.amount_bp) for w in getattr(card, "while_running")] == [(SIDE, 1500), ("other", 20)]


@pytest.fixture(scope="module")
def added(shipped_opening: Opening) -> tuple[Lock, Lock, list[RenameEntry]]:
    """The released lock, the snapshot of the shipped content with a while_running entry added to a released card, and
    the renames: the snapshot is the cost, so it is taken once in setup."""
    o = guarded(shipped_opening, 0, {"side": SIDE, "amount_bp": 1500})
    renames = load_renames()
    return load_lock(), snapshot(o, to_rules(o), renames), renames


@kills(23)
def test_adding_while_running_to_a_released_card_only_wants_the_lock_written(added: tuple[Lock, Lock, list[RenameEntry]]):
    released, snap, renames = added
    assert {p.cls for p in problems(released, snap, renames)} <= {"out_of_date"}


@kills(23)
def test_once_the_lock_is_written_nothing_is_left_and_its_ids_are_those_it_had(added: tuple[Lock, Lock, list[RenameEntry]]):
    released, snap, renames = added
    now = merged(released, snap)
    assert problems(now, snap, renames) == [] and now.ids == released.ids


def test_the_schema_refuses_an_amount_below_one(shipped_opening: Opening):
    guarded(shipped_opening, 0, {"side": SIDE, "amount_bp": 1})  # the control: an amount of 1 loads
    for bad in (0, -1):
        with pytest.raises(ValidationError):
            guarded(shipped_opening, 0, {"side": SIDE, "amount_bp": bad})


@kills(19)
@pytest.mark.parametrize("side,entries", [("nope", [{"side": "nope", "amount_bp": 100}]),
                                          (SIDE, [{"side": SIDE, "amount_bp": 100}, {"side": SIDE, "amount_bp": 200}]),
                                          (THREAT, [{"side": THREAT, "amount_bp": 100}])])
def test_an_undeclared_side_a_threat_id_and_a_side_twice_are_refused_by_the_engine_naming_the_card_and_the_side(
        shipped_opening: Opening, side: str, entries: list[dict[str, Any]]):
    """AMBIGUITY H2: "names the card and the side" is read as both ids appearing in the error's text."""
    o = guarded(shipped_opening, 0, *entries)
    with pytest.raises(e.InvalidRulesError) as err:
        e.validate_rules(to_rules(o))
    assert o.cards[0].id in str(err.value) and side in str(err.value)
