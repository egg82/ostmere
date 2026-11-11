"""The 2 AM test on day two (parity.py): the babysitter given the whenever player's reveals ends level with it in every
store, every skill's XP, each boost's landing (day two's builds among them) and what each store lost at its cap, with
her lane and the installed rules running in both. The probes show the measure can tell: a replay without the
whenever player's woodstack differs from the one with it."""
import pytest

from ashfall_app.engine import AfterTime, CardId, Order, SetOrders, SetQueue, TapCard, Verb, advance
from tests.daytwo.conftest import PLAY_TIMEOUT_S
from tests.daytwo.parity import BOOSTS, log_from, start, task_change, until
from tests.daytwo.routes import day2
from tests.dayone.parity import Measured, compare, replay

pytestmark = [pytest.mark.playthrough, pytest.mark.timeout(PLAY_TIMEOUT_S)]
Pair = tuple[Measured, Measured]
WOODSTACK = TapCard(CardId("build_woodstack"))


@pytest.mark.xfail(strict=True, reason="raised_bed: When ready lines up one stage of three, and the route queues no "
                                       "stage while A16 or a build waits")
def test_the_babysitter_ends_no_further_ahead(two_am2_run: Pair):
    assert compare(*two_am2_run) == []


@pytest.fixture(scope="module")
def the_real_run(two_am2_run: Pair) -> tuple[bool, list[str]]:
    """The whenever player's own play at the replay's end (its last save by then, run on to it; the player may have
    played on past it), against the replay (the instrument measures the real run), and the replay compared with
    itself."""
    w = day2("whenever")
    end = two_am2_run[0].save.time
    last = next(s for s, _ in reversed(w.history) if s.time <= end)
    assert not [at for at, _ in log_from(w, last.time + 1) if at <= end], "no decision between the last save and the end"
    run_on = advance(last, w.rules, end)
    return run_on == two_am2_run[0].save, compare(two_am2_run[0], two_am2_run[0])


def test_the_replay_is_the_play(the_real_run: tuple[bool, list[str]]):
    same, self_diff = the_real_run
    assert same and self_diff == []


@pytest.fixture(scope="module")
def without_woodstack() -> Pair:
    """The whenever player's day two replayed with and without its woodstack (its tap and its queue entry), to the 2 AM
    replay's end: the build takes its work_s after the decision, longer when queued behind another."""
    w = day2("whenever")
    i, t = start(w)
    s0, log = w.history[i][0], log_from(w, t)
    bare: list[tuple[int, Verb]] = [(at, _without(v)) for at, v in log if v != WOODSTACK]
    assert bare != log, "the whenever player built the woodstack"
    end = until(w)
    return (replay(w.rules, s0, log, end, False, boosts=BOOSTS), replay(w.rules, s0, bare, end, False, boosts=BOOSTS))


def _without(v: Verb) -> Verb:
    """`v` with any queue entry tapping the woodstack taken out."""
    if not isinstance(v, SetQueue):
        return v
    return SetQueue(tuple(e for e in v.entries if e.verb != WOODSTACK))


def test_a_missing_build_turns_it_red(without_woodstack: Pair):
    w, bare = without_woodstack
    assert "build_woodstack#1" in w.landed and "build_woodstack#1" not in bare.landed
    assert compare(w, bare)


def test_the_first_task_change_is_found():
    """parity.task_change finds the first SetOrders that moves her default rule to another task, not one that only
    restates it."""
    def orders(card: str) -> SetOrders:
        return SetOrders((Order(AfterTime(0), TapCard(CardId(card))),))
    log: list[tuple[int, Verb]] = [(0, orders("n1_forage")), (1, orders("n1_forage")), (2, WOODSTACK),
                                   (3, orders("n1_cut"))]
    assert task_change(log) == 3
    assert task_change(log[:3]) is None
