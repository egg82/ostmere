"""Arrivals as a gate (docs/design/day-three-plan.md, item 4): `arrivals: n` is an at_least on a tally store that the
first arrival's trigger and each later join add one to; a save already past the first arrival gets 1 at rebase; no
card takes a tally store. Built on fixtures/arrivals.toml merged after the shipped chapters."""
from dataclasses import replace
from functools import cache
from pathlib import Path

import pytest

from ashfall_app.engine import (
    QUANTITY_SCALE as Q, Rules, Save, StoreId, TriggerId, Unlock, UnlockKind, advance, encode, new_save, rebase,
)
from ashfall_app.engine.ids import FeatureId
from ashfall_app.opening.schema import CHAPTERS, OPENING, Opening, load_opening, to_rules

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "arrivals.toml"
TEXT = FIXTURE.read_text()
ARRIVALS = StoreId("t_arrivals")
TWO = Unlock(UnlockKind.FEATURE, FeatureId("t_two_here"))


@cache
def loaded() -> Opening:
    return load_opening(OPENING, (*CHAPTERS, FIXTURE))


@cache
def rules() -> Rules:
    return to_rules(loaded())


@pytest.fixture(scope="module", autouse=True)
def built() -> Rules:
    """The fixture chapter's content and its rules, built in setup so no test's timed call pays for them."""
    return rules()


def tally(s: Save) -> int:
    return next(st.segment.start_value for st in s.stores if st.store == ARRIVALS) // Q


def at(r: Rules, t: int) -> Save:
    return advance(new_save(r), r, t)


def before_the_tally(new: Rules) -> Rules:
    """The rules as released before the tally: no store, and no trigger that adds to it or reads it."""
    gone = {TriggerId(t) for t in ("t_first_counted", "t_second_arrives", "t_third_arrives", "t_gate_on_two")}
    return replace(new, stores=tuple(s for s in new.stores if s.id != ARRIVALS),
                   triggers=tuple(t for t in new.triggers if t.id not in gone))


def test_the_first_arrival_sets_the_tally_to_one_and_each_join_adds_one():
    r = rules()
    assert [tally(at(r, t)) for t in (50, 100, 299, 300, 499, 500)] == [0, 1, 1, 2, 2, 3]


def test_a_gate_on_two_fires_at_the_second_join_and_not_before():
    r = rules()
    assert TWO not in at(r, 299).unlocked
    assert TWO in at(r, 300).unlocked


def test_a_save_already_past_the_first_arrival_reads_one_after_a_rebase():
    new = rules()
    old = before_the_tally(new)
    s = at(old, 200)
    assert Unlock(UnlockKind.FEATURE, FeatureId("t_first_here")) in s.unlocked
    rebased = rebase(encode(s, old), new)
    assert tally(rebased) == 1
    assert tally(advance(rebased, new, 300)) == 2


def test_the_rebase_control_a_save_before_the_first_arrival_reads_zero():
    new = rules()
    old = before_the_tally(new)
    assert tally(rebase(encode(at(old, 50), old), new)) == 0


def broken(tmp_path: Path, old: str, new: str) -> Path:
    assert TEXT.count(old) == 1, f"anchor is not unique: {old!r}"
    path = tmp_path / FIXTURE.name
    path.write_text(TEXT.replace(old, new))
    return path


@pytest.fixture(scope="module")
def control(tmp_path_factory: pytest.TempPathFactory) -> Opening:
    """The harmless edit, loaded."""
    return load_opening(OPENING, (*CHAPTERS, broken(tmp_path_factory.mktemp("control"), 't_c_work = "Work"', 't_c_work = "Toil"')))


def test_the_control_loads(control: Opening):
    assert control.cards


CARD = 'presentation = "action"\nlabel_key = "t_c_work"\nwork_s = 60\n'


@pytest.mark.parametrize("old, new, match", [
    (CARD + "\n[[cards]]\nid = \"t_p3_work\"", CARD + 'costs = [{ store = "t_arrivals", items_per_hour = 1 }]\n\n[[cards]]\nid = "t_p3_work"',
     "t_p2_work: takes a tally store"),
    (CARD + "\n[[features]]", CARD + 'inputs = [{ store = "t_arrivals", items = 1 }]\n\n[[features]]', "t_p3_work: takes a tally store"),
    ('outcome = { stores = [{ store = "t_arrivals", items = 1 }], unlocks = [{ unlock_kind = "card", id = "t_p2_work" }]',
     'outcome = { unlocks = [{ unlock_kind = "card", id = "t_p2_work" }]', "joins 1 not yet counted but adds 0"),
    ('mix = "town:main", card = "t_p2_work" }', 'mix = "town:main", card = "t_p2_work", counted = true }', "joins 0 not yet counted but adds 1"),
])
def test_the_content_check_refuses_a_taken_tally_and_a_join_that_does_not_count(tmp_path: Path, old: str, new: str, match: str):
    with pytest.raises(ValueError, match=match):
        load_opening(OPENING, (*CHAPTERS, broken(tmp_path, old, new)))


def test_a_join_of_someone_counted_on_arrival_adds_nothing(tmp_path: Path):
    old = 'outcome = { stores = [{ store = "t_arrivals", items = 1 }], unlocks = [{ unlock_kind = "card", id = "t_p2_work" }], joins = [{ lane = "t_p2", mix = "town:main", card = "t_p2_work" }] }'
    new = 'outcome = { unlocks = [{ unlock_kind = "card", id = "t_p2_work" }], joins = [{ lane = "t_p2", mix = "town:main", card = "t_p2_work", counted = true }] }'
    assert load_opening(OPENING, (*CHAPTERS, broken(tmp_path, old, new))).cards

