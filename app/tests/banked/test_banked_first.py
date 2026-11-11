"""Two choices of the day-three moves on the fixture chapter (banked/chapter.py) with a second comfort and a one-off
step added: a ready step is tapped before a comfort is queued, a comfort named in `Chapter.first` is queued ahead
of one that is ready sooner, and the trips are put aside while that comfort is short of a store one of them takes."""
from dataclasses import replace

from ashfall_app.engine import (
    AfterTime, BP, CardDef, CardId, CardShare, Mix, MixId, Outcome, Rules, Save, SaveMix, SetQueue, SwitchMix,
    TapCard, TriggerDef, TriggerId, Unlock, UnlockKind, Amount, advance, decide, new_save, view,
)
from tests.banked.chapter import CHAPTER, COMFORT, FOUND, GATHER, HOUR, RATE, TRIP, WOOD, rules
from tests.daythree import moves
from tests.daythree.chapter import Later
from tests.dayone import sinks
from tests.dayone.policy import Move

SLOW, STEP = CardId("slow_comfort"), CardId("step")


def rules_with_more() -> Rules:
    """The fixture's rules with a comfort that takes the whole store (ready after COMFORT) and a step that needs nothing,
    both shown at the half hour with COMFORT."""
    r = rules()
    cards = (*r.cards, CardDef(SLOW, HOUR, inputs=(Amount(WOOD, 4 * RATE * HOUR),), cap=1), CardDef(STEP, 60))
    shown = tuple(TriggerDef(TriggerId(f"show_{c}"), AfterTime(HOUR // 2), Outcome(unlocks=(Unlock(UnlockKind.CARD, str(c)),)))
                  for c in (SLOW, STEP))
    return replace(r, cards=cards, triggers=(*r.triggers, *shown))


def gathering(r: Rules) -> Save:
    """An hour in, with the gatherer running: both comforts show a ready time, COMFORT's the sooner."""
    s = decide(advance(new_save(r), r, HOUR), r, HOUR, SaveMix(Mix(MixId("g"), (CardShare(GATHER, BP),))))
    return decide(s, r, HOUR, SwitchMix(MixId("g")))


def queued(m: Move | None) -> list[CardId]:
    assert m is not None and isinstance(m[1][0], SetQueue)
    return [e.verb.card for e in m[1][0].entries if isinstance(e.verb, TapCard)]


def test_a_comfort_in_first_is_queued_ahead_of_one_that_is_ready_sooner():
    r = rules_with_more()
    s = gathering(r)
    both = replace(CHAPTER, comforts=(COMFORT, SLOW))
    assert queued(sinks.queue_comforts(view(s, r), s, both)) == [COMFORT, SLOW], "soonest ready first without `first`"
    assert queued(sinks.queue_comforts(view(s, r), s, replace(both, first=(SLOW,)))) == [SLOW, COMFORT]


def test_a_ready_step_is_tapped_before_a_comfort_is_queued():
    r = rules_with_more()
    s = gathering(r)
    later = Later("B4", "B5", replace(CHAPTER, comforts=(COMFORT, SLOW)), (STEP,), (), (), lambda _s, _r: set(), ())
    v = view(s, r)
    assert sinks.queue_comforts(v, s, later.sinks) is not None, "a comfort is waiting to be queued"
    m = moves.move(v, s, r, later, sinks.SinkKnobs(queue_comforts=True), False)
    assert m is not None and m[1] == (TapCard(STEP),)


def test_the_trips_are_put_aside_while_the_comfort_the_story_waits_on_is_short_of_a_store_they_take():
    """The trip's supply is another store, so only its input ties it to the comfort's: held flat by the trip, the store
    gives the comfort no ready time and When ready is not on offer, so the player takes the trip out of the mix."""
    r = rules_with_more()
    s = gathering(r)
    s = decide(s, r, HOUR, SaveMix(Mix(MixId("gt"), (CardShare(GATHER, BP // 2), CardShare(TRIP, BP // 2)))))
    s = decide(s, r, HOUR, SwitchMix(MixId("gt")))
    v = view(s, r)
    assert next(c for c in v.cards if c.card == SLOW).blocker is not None, "the comfort waits on wood"
    chapter = replace(CHAPTER, trips=(sinks.Trip(TRIP, FOUND),), comforts=(COMFORT, SLOW))
    def later(first: tuple[CardId, ...]) -> Later:
        return Later("B4", "B5", replace(chapter, first=first), (), (), (), lambda _s, _r: set(), ())
    assert moves.release(v, s, r, later(())) is None, "a comfort the story does not wait on leaves the mix alone"
    m = moves.release(v, s, r, later((SLOW,)))
    assert m is not None and isinstance(m[1][0], SaveMix)
    assert {c.card for c in m[1][0].mix.components if isinstance(c, CardShare)} == {GATHER}
