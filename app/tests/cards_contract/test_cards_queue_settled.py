"""Settled queue entries ("Greyed mix" in part "CARDS", invariant 40): a dead entry whose `until` holds for good (an
AfterTime, or an AtLeast on a card count, a skill level or an unlock, once true) is popped, since a revival would pop
it at once. So the page's "when ready" entry for a one-off, TapCard(c) until c's count reaches 1, pops at the instant
c completes, though c is dead from that instant; and a save written before that rule recovers when it is next
resolved."""
from dataclasses import replace

import pytest
from hypothesis import given, strategies as st

from ashfall_app.engine import (
    AfterTime, AtLeast, AtMost, CardCount, CardDef, CardId, Condition, EventKind, Flow, MixId, QueueEntry, Rules,
    Save, SetOrders, SetQueue, SkillLevel, StoreDef, StoreId, StoreValue, SwitchMix, TapCard, Unlock, UnlockKind,
    Unlocked, advance, decide, decode, encode, level,
    new_save, next_event, rebase, view,
)
from ashfall_app.engine.gates import is_unlocked
from ashfall_app.engine.schedule import events
from cards_gen import Scenario, few, play, scenario_st, timeline, try_decide
from cards_world import K, Q, done, rules, running_mix, with_mix

Y = StoreId("y")
C, D, M = CardId("c"), CardId("d"), CardId("m")


def world() -> Rules:
    """c and d: one-offs on the hands (100 s and 50 s); m makes y in a mix, so time keeps having events."""
    return rules([StoreDef(Y, Q, 0)],
                 cards=[CardDef(C, 100, cap=1), CardDef(D, 50, cap=1), CardDef(M, 30, makes=(Flow(Y, 1000),))])


def when_ready(card: CardId) -> QueueEntry:
    """The entry the page's "When ready" queues: tap the card until it has completed once."""
    return QueueEntry(TapCard(card), AtLeast(CardCount(card), 1, 1))


def test_a_queued_one_off_pops_at_its_completion_instant():
    """c's entry controls and taps c at 0; c lands at 100 and its entry pops then, so d's controls and taps d, which
    lands at 150 and pops in turn: the queue is empty, not a list of finished steps."""
    r = world()
    s = decide(new_save(r), r, 0, SetQueue((when_ready(C), when_ready(D))))
    assert advance(s, r, 99).queue == (when_ready(C), when_ready(D))
    a = advance(s, r, 100)
    assert done(a, r, C) == 1 and a.queue == (when_ready(D),)
    assert advance(s, r, 149).queue == (when_ready(D),)
    b = advance(s, r, 150)
    assert done(b, r, D) == 1 and b.queue == ()


def test_a_switch_entry_that_dies_as_its_after_time_arrives_pops():
    """A switch to the mix holding c, until AfterTime(100): c completes at 100, greying the mix, the instant the
    `until` holds. The `until` can never fall, so the entry pops; the switch behind it controls."""
    r = world()
    s = with_mix(new_save(r), r, 0, {C: 10_000}, "m0")
    s = with_mix(s, r, 0, {M: 10_000}, "m1")
    tail = QueueEntry(SwitchMix(MixId("m1")), AfterTime(10**9))
    s = decide(s, r, 0, SetQueue((QueueEntry(SwitchMix(MixId("m0")), AfterTime(100)), tail)))
    assert running_mix(s, r) == MixId("m0")
    a = advance(s, r, 100)
    assert a.queue == (tail,) and running_mix(a, r) == MixId("m1")


def test_a_dead_entry_settles_when_its_after_time_arrives():
    """A dead entry whose `until` cannot fall but does not hold yet is watched: its AfterTime(500) is an event, and it
    pops then, while the live entry behind it keeps control."""
    r = world()
    s = advance(decide(with_mix(new_save(r), r, 0, {M: 10_000}), r, 0, TapCard(C)), r, 200)
    tail = QueueEntry(TapCard(D), AfterTime(10**9))
    s = decide(s, r, 200, SetQueue((QueueEntry(TapCard(C), AfterTime(500)), tail)))
    assert len(s.queue) == 2 and any(e.time == 500 and e.kind is EventKind.QUEUE_POP for e in events(s, r))
    assert len(advance(s, r, 499).queue) == 2
    assert advance(s, r, 500).queue == (tail,)


def _stale(r: Rules):
    """A save as the engine before this rule wrote it: c done, its entry still queued behind nothing live."""
    s = advance(decide(with_mix(new_save(r), r, 0, {M: 10_000}), r, 0, TapCard(C)), r, 200)
    assert done(s, r, C) == 1
    return replace(s, queue=(when_ready(C),))


def test_a_stale_entry_in_a_save_pops_when_it_is_next_resolved():
    """Loaded under the same rules (decode, no rebase), the stale entry goes at the next resolved instant: a decision
    at the load time, or the next event an advance reaches (y filling to its cap)."""
    r = world()
    text = encode(_stale(r), r)
    loaded = decode(text, r)
    assert decide(loaded, r, loaded.time, SetOrders(())).queue == ()
    e = next_event(loaded, r)
    assert e is not None
    assert advance(loaded, r, e.time - 1).queue == (when_ready(C),)
    assert advance(loaded, r, e.time).queue == ()


def test_a_stale_entry_in_a_save_pops_when_it_is_rebased():
    """Loaded under other rules, the rebase resolves the save's instant with evaluation, which pops it."""
    r = world()
    text = encode(_stale(r), r)
    r2 = rules([StoreDef(Y, 100 * Q, 0), StoreDef(StoreId("w"), Q, 0)], cards=list(world().cards))
    assert rebase(text, r2).queue == ()


def _settled(s: Save, r: Rules, e: QueueEntry) -> bool:
    """Read from the contract, not the engine's helper: the entry is dead (a tap of a completed card, a switch to a
    greyed mix) and its `until` holds and is of a kind that cannot fall."""
    v = view(s, r)
    dead = (e.verb.mix in v.greyed_mixes) if isinstance(e.verb, SwitchMix) else \
        isinstance(e.verb, TapCard) and e.verb.card in {c.card for c in v.completed}   # these worlds hold no offers
    u = e.until
    if isinstance(u, AfterTime):
        holds = s.time >= u.time
    elif isinstance(u, AtLeast) and isinstance(u.subject, CardCount):
        holds = done(s, r, u.subject.card) >= u.value
    elif isinstance(u, AtLeast) and isinstance(u.subject, SkillLevel):
        holds = level(s, r, u.subject.skill, s.time) >= u.value
    elif isinstance(u, AtLeast) and isinstance(u.subject, Unlocked):
        holds = int(is_unlocked(s, r, u.subject.unlock)) >= u.value
    else:
        return False
    return dead and holds


@few(10)
@given(sc=scenario_st(), extra=st.lists(st.integers(0, 3), min_size=1, max_size=3))
def test_no_resolved_save_keeps_a_settled_entry(sc: Scenario, extra: list[int]):
    """Over random worlds: put "when ready" entries for some capped cards (repeats allowed) ahead of the scenario's own
    plan, then at every timeline stop no entry is a dead one whose `until` holds for good."""
    r = sc.rules
    capped = [c.id for c in r.cards if c.cap is not None] or [r.cards[0].id]
    s = play(sc)
    picks = [capped[i % len(capped)] for i in extra]
    s = try_decide(s, r, s.time, SetQueue(tuple(when_ready(c) for c in picks) + s.queue))
    for t in timeline(s, r, sc.offsets, events=8):
        assert not [e for e in t.queue if _settled(t, r, e)], t.time


def _done_c(r: Rules):
    """c completed by the player's tap at 0; m's mix running."""
    return advance(decide(with_mix(new_save(r), r, 0, {M: 10_000}), r, 0, TapCard(C)), r, 200)


CANNOT_FALL = [AfterTime(0), AtLeast(CardCount(C), 1, 1), AtLeast(SkillLevel(K), 1, 1),
               AtLeast(Unlocked(Unlock(UnlockKind.CARD, C)), 1, 1)]
CAN_FALL = [AtLeast(StoreValue(Y), 0, 0), AtMost(CardCount(D), 5, 5), AtMost(StoreValue(Y), Q, Q)]


@pytest.mark.parametrize("until", CANNOT_FALL, ids=["after", "count", "level", "unlocked"])
def test_a_dead_entry_whose_until_cannot_fall_settles_at_once(until: Condition):
    r = world()
    tail = QueueEntry(TapCard(D), AfterTime(10**9))
    assert decide(_done_c(r), r, 200, SetQueue((QueueEntry(TapCard(C), until), tail))).queue == (tail,)


@pytest.mark.parametrize("until", CAN_FALL, ids=["store-least", "count-most", "store-most"])
def test_a_dead_entry_whose_until_holds_but_can_fall_is_kept(until: Condition):
    r = world()
    queue = (QueueEntry(TapCard(C), until), QueueEntry(TapCard(D), AfterTime(10**9)))
    s = decide(_done_c(r), r, 200, SetQueue(queue))
    assert s.queue == queue and advance(s, r, 3000).queue == queue


def test_a_players_switch_under_a_queue_mix_sets_only_the_mix_that_comes_back():
    """"Queue mix": the queue's m1 runs while its entry controls; the player's switch at 300 sets save.active alone,
    and the dead entry settling at 500 leaves m1 running and m0 as the mix that comes back."""
    r = world()
    s = with_mix(_done_c(r), r, 200, {M: 10_000}, "m1")
    s = with_mix(s, r, 200, {M: 10_000}, "m0")
    tail = QueueEntry(SwitchMix(MixId("m1")), AfterTime(10**9))
    s = decide(s, r, 200, SetQueue((QueueEntry(TapCard(C), AfterTime(500)), tail)))
    assert running_mix(s, r) == MixId("m1")
    s = decide(s, r, 300, SwitchMix(MixId("m0")))
    assert running_mix(s, r) == MixId("m1") and s.active == MixId("m0")
    a = advance(s, r, 500)
    assert a.queue == (tail,) and a.active == MixId("m0") and running_mix(a, r) == MixId("m1")


def test_a_live_entry_behind_the_head_waits_its_turn_though_its_until_holds_for_good():
    """Only dead entries settle: when the dead head settles at 500, the live entry behind the controlling one is kept,
    though its `until` (AfterTime(0)) holds for good; it pops when it comes to control."""
    r = world()
    s = with_mix(_done_c(r), r, 200, {M: 10_000}, "m1")
    head = QueueEntry(SwitchMix(MixId("m1")), AfterTime(10**9))
    behind = QueueEntry(TapCard(D), AfterTime(0))
    s = decide(s, r, 200, SetQueue((QueueEntry(TapCard(C), AfterTime(500)), head, behind)))
    assert advance(s, r, 500).queue == (head, behind)
