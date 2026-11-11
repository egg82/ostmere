"""The hands' queued one-off (engine DESIGN.txt, part "TOWNSFOLK, INSTALLED RULES AND OFFERS": "Queued one-off";
invariant 66; api CONTRACT.txt, "A LANE RUN BY RULES", the answer's one-off of the hands). Outcome.queues (c) puts
QueueEntry(TapCard(c), AtLeast(CardCount(c), n, n)), n = c's completions at that instant + 1, at the front of the queue
unless an equal entry is queued; c starts at the first instant that evaluates with the hands free, no order's mix
running, no true order tapping the hands first and c ready; the entry is gone once c's completions reach n."""
from ashfall_app.engine import (
    HANDS, AtLeast, AtMost, CardCount, CardDef, CardId, Order, Outcome, QueueEntry, SetOrders, SetQueue, SwitchMix,
    TapCard, advance,
)
from cards_world import done
from town_world import H, H2, HC, MIX, NEVER, NO, answer, mixing, running, started, town

HC2 = CardId("hc2")


def when_ready(card: CardId, n: int) -> QueueEntry:
    """The page's "When ready" entry (CONTRACT: tap_card c until c's card_count reaches its next completion)."""
    return QueueEntry(TapCard(card), AtLeast(CardCount(card), n, n))


def test_with_the_hands_free_the_one_off_starts_at_the_answer_and_pops_on_completion():
    """Invariant 66: answered at 60 with the hands free, hc starts at 60; the entry is gone from 160, hc's first
    completion."""
    r = town()
    s = answer(advance(started(r), r, 60), r, 60, NO)
    assert s.queue == (when_ready(HC, 1),) and running(s, HANDS) == HC
    assert advance(s, r, 159).queue == (when_ready(HC, 1),)
    s = advance(s, r, 160)
    assert done(s, r, HC) == 1 and s.queue == ()


def test_on_busy_hands_the_one_off_starts_when_they_come_free():
    """"a start does nothing while the hands are mid-tap": the player's tap of h at 0 holds the hands to 100; hc,
    queued at 60, starts at h's landing and is done at 200."""
    r = town()
    s = answer(advance(started(r, TapCard(H)), r, 60), r, 60, NO)
    assert running(s, HANDS) == H and s.queue == (when_ready(HC, 1),)
    s = advance(s, r, 100)
    assert running(s, HANDS) == HC
    s = advance(s, r, 200)
    assert done(s, r, HC) == 1 and s.queue == () and running(s, HANDS) is None


def test_it_goes_in_front_of_the_queue_and_the_players_plan_resumes_after_it():
    """In front of the queue as it was: h2's entry (running, never popping) is pushed down; at h2's landing hc
    controls and starts; once hc completes at 200 h2's entry controls again and taps h2."""
    r = town()
    plan = QueueEntry(TapCard(H2), NEVER)
    s = started(r, SetQueue((plan,)))
    assert running(s, HANDS) == H2
    s = answer(advance(s, r, 60), r, 60, NO)
    assert s.queue == (when_ready(HC, 1), plan)
    assert running(advance(s, r, 100), HANDS) == HC
    s = advance(s, r, 200)
    assert s.queue == (plan,) and running(s, HANDS) == H2


def test_several_one_offs_go_to_the_front_in_tuple_order():
    """"Each puts ... at the front of the queue (several in tuple order)"."""
    r = town(no=Outcome(queues=(HC, HC2)), cards=(CardDef(HC2, 100, cap=2),))
    plan = QueueEntry(TapCard(H2), NEVER)
    s = answer(advance(started(r, TapCard(H), SetQueue((plan,))), r, 60), r, 60, NO)
    assert s.queue == (when_ready(HC, 1), when_ready(HC2, 1), plan)


def test_an_equal_entry_already_queued_is_not_added_or_moved():
    """"unless an equal entry is already queued": the player's own When ready entry for hc, behind h's, stays where it
    is and is not doubled."""
    r = town()
    mine = (QueueEntry(TapCard(H), NEVER), when_ready(HC, 1))
    s = answer(advance(started(r, SetQueue(mine)), r, 60), r, 60, NO)
    assert s.queue == mine


def test_its_target_is_the_next_completion_counted_at_the_answer():
    """n is the card's completions at that instant plus one: hc tapped once by hand (done at 100) gets an entry
    until its second completion, answered at 150."""
    r = town()
    s = advance(started(r, TapCard(HC)), r, 150)
    assert done(s, r, HC) == 1
    s = answer(s, r, 150, NO)
    assert s.queue[0] == when_ready(HC, 2) and running(s, HANDS) == HC
    assert advance(s, r, 250).queue == ()


def test_a_true_order_tapping_the_hands_comes_first():
    """Invariant 66, "no true order taps the hands first": while AtMost(count(h), 1) holds, h is retapped at its
    landing (tap orders before the queue); it lets go at h's second landing, 200, where hc starts."""
    r = town()
    s = started(r, SetOrders((Order(AtMost(CardCount(H), 1, 1), TapCard(H)),)))
    s = answer(advance(s, r, 60), r, 60, NO)
    assert running(advance(s, r, 100), HANDS) == H
    s = advance(s, r, 200)
    assert done(s, r, H) == 2 and running(s, HANDS) == HC


def test_it_waits_while_an_orders_mix_runs():
    """Invariant 66, "no order's mix runs": a latched mix order keeps the queue unread, so hc does not start at the
    answer with the hands free, nor later."""
    r = town()
    s = started(r, *mixing(), SetOrders((Order(AtLeast(CardCount(H), 0, 0), SwitchMix(MIX)),)))
    s = answer(advance(s, r, 60), r, 60, NO)
    assert s.queue == (when_ready(HC, 1),) and running(s, HANDS) is None
    assert running(advance(s, r, 1000), HANDS) is None

