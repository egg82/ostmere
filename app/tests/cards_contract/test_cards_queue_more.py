"""One run per entry (Plan's entries, CONTRACT.txt "Goal stints"): each is TapCard(c) until c's count reaches one more
than the runs planned before it (the tap under way and the earlier entries of c), so entries of a card a lane runs now
add runs after that tap. Each is checked when its turn comes: an entry of a card that reached its cap is dropped at that
instant (DESIGN.txt, "Greyed mix"), and one waiting on an input nothing makes is kept but passed over, so the hands go on
with what can run (DESIGN.txt, "Never ready")."""
import pytest

from ashfall_app.engine import (
    HANDS, Amount, AtLeast, CardCount, CardDef, CardId, QueueEntry, SetQueue, StoreDef, StoreId, TapCard, advance,
    decide, new_save,
)

from cards_world import Q, done, lane, rules, tap

B = StoreId("b")
C, D = CardId("c"), CardId("d")


def run(card: CardId, n: int) -> QueueEntry:
    """A planned run of `card`, the one that brings its count to n."""
    return QueueEntry(TapCard(card), AtLeast(CardCount(card), n, n))


def then_d() -> QueueEntry:
    return run(D, 1)


def test_entries_for_a_running_card_tap_it_again_after_the_tap_under_way():
    """c (100 s, uncapped) tapped at 0; at 10 the player plans two more runs. The tap under way lands at 100 and the
    first entry taps c at once: 3 completions at 300, and the queue empty."""
    r = rules([], cards=[CardDef(C, 100)])
    s = decide(tap(new_save(r), r, 0, C), r, 10, SetQueue((run(C, 2), run(C, 3))))
    a = advance(s, r, 100)
    assert done(a, r, C) == 1 and lane(a, HANDS).card == C and a.queue == (run(C, 2), run(C, 3))
    b = advance(s, r, 300)
    assert done(b, r, C) == 3 and b.queue == ()


def test_the_old_entry_for_a_running_card_added_nothing():
    """The entry the page sent before for a running card (its count reaching completions now + 1) holds at the tap
    under way's own landing: it pops then and c is not tapped again."""
    r = rules([], cards=[CardDef(C, 100)])
    s = decide(tap(new_save(r), r, 0, C), r, 10, SetQueue((run(C, 1),)))
    a = advance(s, r, 100)
    assert done(a, r, C) == 1 and a.queue == () and lane(a, HANDS).card is None


@pytest.mark.xfail(strict=True, reason="#494: a tap of a completed card is kept in the queue")
def test_more_runs_than_a_cap_allows_run_to_the_cap_and_leave_the_queue():
    """c has a cap of 2; five runs planned while the first runs: c lands twice, the three left are dropped at the cap,
    and d behind them runs."""
    r = rules([], cards=[CardDef(C, 100, cap=2), CardDef(D, 50, cap=1)])
    s = decide(tap(new_save(r), r, 0, C), r, 10, SetQueue((*(run(C, n) for n in range(2, 7)), then_d())))
    capped = advance(s, r, 200)
    assert done(capped, r, C) == 2 and capped.queue == (then_d(),)
    a = advance(s, r, 250)
    assert done(a, r, C) == 2 and done(a, r, D) == 1 and a.queue == ()


def test_a_run_on_an_input_nothing_makes_is_kept_and_passed_over():
    """c takes 1 b per completion and b holds 2, made by nothing; five runs planned while the first runs: c lands
    twice, then nothing can make it ready, so its entries stay while d behind them runs."""
    r = rules([StoreDef(B, 10 * Q, 2 * Q)], cards=[CardDef(C, 100, inputs=(Amount(B, Q),)), CardDef(D, 50, cap=1)])
    s = decide(tap(new_save(r), r, 0, C), r, 10, SetQueue((*(run(C, n) for n in range(2, 7)), then_d())))
    a = advance(s, r, 400)
    assert done(a, r, C) == 2 and done(a, r, D) == 1 and a.queue == tuple(run(C, n) for n in range(3, 7))
