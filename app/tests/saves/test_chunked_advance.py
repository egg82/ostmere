"""A long absence catches up in bounded slices (engine `advance_logged(save, rules, t, stop)`): for any stop pattern,
chaining slices (each resumed from the last one's save, through encode and decode as the database does) ends in the
save, lines and rule changes of one unbounded call. Written from the contract, over golden saves."""
from dataclasses import dataclass

import pytest

from ashfall_app import engine as e
from tests.saves.chunks import (
    DAY_S, Chained, MakeStop, always, chain, counting, every, golden, irregular, never, todays_rules,
)

SPANS = {"f7/03-seed0-t241": DAY_S, "f7/04-seed0-t404": DAY_S // 3, "f7/05-seed0-end526": DAY_S // 4,
         "f7/15-seed2-end526": DAY_S // 4, "f6/05-seed0-end526": DAY_S // 4}
"""Golden saves and the seconds each is advanced: mid-game and end-of-opening saves, one of an older format. Spans are
sized so a slice per instant fits the per-test time gate."""
CARRIES_A_RULE_CHANGE = "f7/05-seed0-end526"
"""A span whose unbounded advance changes a rule, so the slices have one to carry across."""
PATTERNS: dict[str, MakeStop] = {
    "every-1": every(1), "every-2": every(2), "every-5": every(5), "every-13": every(13),
    "irregular-7": irregular(7), "irregular-11": irregular(11, 0.6),
}


@dataclass(frozen=True)
class Unbounded:
    start: e.Save
    t: int
    step: e.Step
    instants: int
    """How many times a never-firing stop was asked: the instants in start -> t."""


@pytest.fixture(scope="module", params=SPANS)
def name(request: pytest.FixtureRequest) -> str:
    """The span under test, module-scoped so each span's unbounded advance is built once, in its own setup (the
    pytest-timeout bound covers setup)."""
    return request.param


@pytest.fixture(scope="module")
def ref(name: str) -> Unbounded:
    start = golden(name)
    t = start.time + SPANS[name]
    asked: list[int] = []
    step = e.advance_logged(start, todays_rules(), t, counting(never(), asked))
    return Unbounded(start, t, step, len(asked))


def test_the_span_is_worth_chunking(name: str, ref: Unbounded):
    assert ref.instants >= 10 and ref.step.lines, ref.instants
    assert ref.step.rule_changes or name != CARRIES_A_RULE_CHANGE, "no rule change to carry across slices"


def same_as_unbounded(got: Chained, ref: Unbounded) -> None:
    rules = todays_rules()
    assert got.final == e.encode(ref.step.save, rules), "the chained save is not the unbounded save"
    assert got.lines == ref.step.lines, "the slices' lines are not the unbounded lines"
    assert got.changes == ref.step.rule_changes, "the slices' rule changes are not the unbounded ones"


@pytest.fixture
def chained(pattern: str, ref: Unbounded) -> Chained:
    """The span's chain under the pattern, run in setup so the test times only what it checks."""
    return chain(ref.start, todays_rules(), ref.t, PATTERNS[pattern])


@pytest.mark.parametrize("pattern", PATTERNS)
def test_chained_slices_equal_one_unbounded_advance(pattern: str, chained: Chained, ref: Unbounded):
    got = chained
    assert len(got.times) > 1, "the pattern never stopped short: nothing was chained"
    same_as_unbounded(got, ref)


@pytest.fixture
def unstopped(ref: Unbounded) -> tuple[e.Step, e.Step, e.Save]:
    """The span advanced with a stop that never fires, with no stop, and as a plain advance, run in setup."""
    rules = todays_rules()
    return (e.advance_logged(ref.start, rules, ref.t, never()), e.advance_logged(ref.start, rules, ref.t),
            e.advance(ref.start, rules, ref.t))


def test_a_stop_that_never_fires_is_no_stop(ref: Unbounded, unstopped: tuple[e.Step, e.Step, e.Save]):
    step, no_stop, plain = unstopped
    assert step == ref.step and not step.stopped_short and step.save.time == ref.t
    assert no_stop == step
    assert plain == step.save


@pytest.fixture
def one_instant_a_call(ref: Unbounded) -> Chained:
    return chain(ref.start, todays_rules(), ref.t, always)


def test_a_stop_that_always_fires_still_resolves_an_instant_a_call(ref: Unbounded, one_instant_a_call: Chained):
    got = one_instant_a_call
    assert len(got.times) == ref.instants, "one instant a call: as many calls as instants"
    assert list(got.times) == sorted(set(got.times)), "each call moved the save on"
    assert got.stopped == (True,) * (ref.instants - 1) + (False,)
    same_as_unbounded(got, ref)


@pytest.mark.parametrize("k", [2, 5])
def test_a_slice_ends_at_the_instant_its_stop_fired_on(k: int, ref: Unbounded):
    got = chain(ref.start, todays_rules(), ref.t, every(k))
    assert len(got.times) == -(-ref.instants // k), f"{ref.instants} instants in slices of {k}"


def test_a_stop_on_the_last_instant_is_not_stopped_short(ref: Unbounded):
    rules = todays_rules()
    whole = e.advance_logged(ref.start, rules, ref.t, every(ref.instants)())
    assert not whole.stopped_short and whole.save.time == ref.t and whole == ref.step
    nearly = e.advance_logged(ref.start, rules, ref.t, every(ref.instants - 1)())
    assert nearly.stopped_short and ref.start.time < nearly.save.time < ref.t
    rest = e.advance_logged(e.decode(e.encode(nearly.save, rules), rules), rules, ref.t, always())
    assert not rest.stopped_short and rest.save.time == ref.t
    assert nearly.lines + rest.lines == ref.step.lines
    assert nearly.rule_changes + rest.rule_changes == ref.step.rule_changes


def test_nothing_to_resolve_is_not_stopped_short():
    start, rules = golden("f7/05-seed0-end526"), todays_rules()
    step = e.advance_logged(start, rules, start.time, always())
    assert not step.stopped_short and step.save == start and step.lines == () and step.rule_changes == ()
