"""Invariants 111 and 112, the card states (engine DESIGN.txt, "ENTRIES HELD WHILE A CARD RUNS": "Why paused, waiting and
yielded count 0", "Pause"): a mix card paused on a dry store or waiting on a requires holds nothing, and holds again at
the instant it resumes or its requires holds; the dry rule reads the stack the pauses so far leave."""
from ashfall_app.engine import BP, FlowKind, RateRef, RunKind, advance, explain, segment, view
from held_world import (
    FOOD, GDRY, GREQ, MKFOOD, RAID, first, hands, held_mods, held_of, kills, loss, odds_loss, paused, raised, run_of, world,
)


def dry_world():
    """gdry (6000, costs 1 food an hour) alone in the hands' mix; food starts at 1, mkfood makes 2.5 an hour, and the
    raid's lost fights take food (3 a lost fight, two fights an hour), so the guard's raise moves the drain."""
    r = world(drain=FOOD)
    return r, hands(r, (GDRY, BP))


@kills(2, 3, 4, 8, 12, 13, 14, 17)
def test_a_guard_paused_on_a_dry_store_holds_nothing_until_it_resumes():
    r, s = dry_world()
    assert held_of(s, r, GDRY) == [6000] and loss(s, r) == odds_loss(6000)
    dry = first(s, r, lambda x: paused(x, GDRY))
    assert run_of(dry, r, GDRY) is RunKind.PAUSED, "the premise: the dry rule paused the guard"
    assert held_mods(dry, r) == () and raised(dry, r) == 0 and loss(dry, r) == odds_loss(0)
    again = first(dry, r, lambda x: not paused(x, GDRY))
    assert again.time > dry.time and run_of(again, r, GDRY) is not RunKind.PAUSED
    assert held_of(again, r, GDRY) == [6000]


@kills(2, 4, 8, 12, 13, 14)
def test_a_paused_guard_holds_nothing_between_its_pause_and_its_resume():
    """Nothing changes between events (invariant 112), so the first instant after the pause and the last before the
    resume read as the pause itself does."""
    r, s = dry_world()
    dry = first(s, r, lambda x: paused(x, GDRY))
    again = first(dry, r, lambda x: not paused(x, GDRY))
    for t in (dry.time + 1, (dry.time + again.time) // 2, again.time - 1):
        assert held_mods(advance(dry, r, t), r) == (), t


@kills(4, 21)
def test_the_dry_rule_reads_the_stack_the_pauses_so_far_leave():
    """Pausing the guard drops its raise, which raises the raid's losses of the very store that ran dry: after the dry
    instant the store does not still fall at the guarded drain. With the raid's drain read off the stack from before
    the first pause the store would be left falling at 0 (it needs a second pause at that instant)."""
    r, s = dry_world()
    dry = first(s, r, lambda x: paused(x, GDRY))
    assert next(st for st in dry.stores if st.store == FOOD).segment.start_value == 0, "the premise: food ran out"
    lines = ((MKFOOD, FlowKind.MAKE), (GDRY, FlowKind.COST), (RAID, FlowKind.COST))
    net = sum((1 if kind is FlowKind.MAKE else -1) * explain(dry, r, RateRef(runner, kind, FOOD)).per_hour
              for runner, kind in lines)
    assert net >= 0, "food is at 0 and the lines, read under the stack the pauses leave, must not leave it falling"
    assert segment(advance(dry, r, dry.time + 5), r, FOOD).start_value >= 0


@kills(2, 4, 8, 12, 13, 14, 21)
def test_pausing_the_guard_raises_the_raids_losses_so_the_raid_is_paused_in_the_same_instant():
    """The guard's pause drops its raise, the raid's losses of food rise past what mkfood makes, and the dry rule's next
    pause (last-in-mix first: the guard, then the standing raid) takes the raid at that same instant."""
    r, s = dry_world()
    dry = first(s, r, lambda x: paused(x, GDRY))
    assert paused(dry, GDRY) and paused(dry, RAID)
    assert dry.time == first(s, r, lambda x: paused(x, RAID)).time


@kills(2, 4, 9, 12, 13, 14, 17)
def test_a_card_waiting_on_a_requires_holds_nothing_until_it_holds():
    """greq (3000) requires rq <= 2, which rq (rising one a second) stops meeting after 2 s: it holds at the start and
    holds nothing once its requires is false, waiting."""
    r = world()
    s = hands(r, (GREQ, BP))
    assert held_of(s, r, GREQ) == [3000]
    waiting = first(s, r, lambda x: run_of(x, r, GREQ) is RunKind.WAITING)
    assert held_mods(waiting, r) == () and raised(waiting, r) == 0
    assert held_mods(advance(waiting, r, waiting.time + 500), r) == ()


@kills(2, 4, 9, 12, 13, 18)
def test_the_views_held_list_agrees_with_the_waiting_card():
    r = world()
    s = hands(r, (GREQ, BP))
    assert [h.card for h in view(s, r).held] == [GREQ]
    waiting = first(s, r, lambda x: run_of(x, r, GREQ) is RunKind.WAITING)
    assert view(waiting, r).held == ()
