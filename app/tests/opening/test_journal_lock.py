"""The release lock keeps the journal's subject ids and slot keys like any released id (docs/design/journal.md, "What it
reads, and when it writes"): a stored day names a subject and a slot's text key, so renaming either needs an entry in
renames.toml. Each case is the shipped content edited, against a lock that released the unedited one."""
from functools import cache

import pytest

from ashfall_app.opening.lock import Lock, load_lock, merged, snapshot
from ashfall_app.opening.lock_checks import Problem, problems
from ashfall_app.opening.renames import RenameEntry, load_renames
from ashfall_app.opening.schema import Opening, to_rules
from ashfall_app.opening.people import BandEntry
from ashfall_app.opening.subject_entries import SlotEntry, SubjectEntry
from tests.opening.playthrough import opening

SUBJECT = "s_n3_joined"
"""A shipped subject, given its slots here."""


@pytest.fixture(scope="module", autouse=True)
def shipped_loaded() -> None:
    """The cached opening, built in setup so no test's timed call pays for it."""
    opening()


def with_subject(o: Opening, sid: str, key: str, mention_key: str) -> Opening:
    """`o` with SUBJECT renamed `sid`, `key` added to its first slot and a band holding `mention_key` added; its own
    keys are kept, so nothing the shipped lock holds goes missing."""
    def edit(s: SubjectEntry) -> SubjectEntry:
        first = [*(s.first.keys if s.first else []), key]
        return s.model_copy(update={"id": sid, "first": SlotEntry(keys=first),
                                    "mention": [*s.mention, BandEntry(at_least=1, keys=[mention_key])]})
    return o.model_copy(update={"subjects": [edit(s) if s.id == SUBJECT else s for s in o.subjects]})


@cache
def released_lock() -> Lock:
    """The shipped lock as if `with_subject(opening(), SUBJECT, "j_a", "j_m")` had been released."""
    renames = load_renames()
    o = with_subject(opening(), SUBJECT, "j_a", "j_m")
    return merged(load_lock(), snapshot(o, to_rules(o), renames))


def found(o: Opening, extra: list[RenameEntry]) -> list[Problem]:
    renames = [*load_renames(), *extra]
    return problems(released_lock(), snapshot(o, to_rules(o), renames), renames)


def rename(kind: str, old: str, new: str) -> RenameEntry:
    return RenameEntry.model_validate({"kind": kind, "from": old, "to": new})


def test_the_lock_holds_the_subjects_and_the_slot_keys():
    lock = released_lock()
    assert SUBJECT in lock.ids["subject"]
    assert {"j_a", "j_m"} <= set(lock.ids["slot_key"])


def test_the_content_the_lock_was_made_from_has_nothing_to_map():
    assert {p.cls for p in found(with_subject(opening(), SUBJECT, "j_a", "j_m"), [])} <= {"out_of_date"}


def test_a_renamed_subject_needs_its_mapping():
    o = with_subject(opening(), "s_n3_arrived", "j_a", "j_m")
    ps = found(o, [])
    assert any(p.cls == "needs_mapping" and f"subject {SUBJECT} was removed" in p.message for p in ps), ps
    assert {p.cls for p in found(o, [rename("subject", SUBJECT, "s_n3_arrived")])} == {"out_of_date"}


@pytest.mark.parametrize("old, new, edited", [("j_a", "j_b", ("j_b", "j_m")), ("j_m", "j_n", ("j_a", "j_n"))])
def test_a_renamed_slot_key_needs_its_mapping(old: str, new: str, edited: tuple[str, str]):
    o = with_subject(opening(), SUBJECT, *edited)
    ps = found(o, [])
    assert any(p.cls == "needs_mapping" and f"slot_key {old} was removed" in p.message for p in ps), ps
    assert {p.cls for p in found(o, [rename("slot_key", old, new)])} == {"out_of_date"}
