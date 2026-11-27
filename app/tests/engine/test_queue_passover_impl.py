"""engine/design/, "Orders", "Never ready": a queue entry whose tap nothing will ever make ready (no ready time) waits where
it is and the entries behind it run; with nothing else runnable the hands are idle because nothing can run."""
from ashfall_app.engine import (
    BP, HANDS, QUANTITY_SCALE as Q, Amount, AtLeast, CardCount, CardDef, CardId, PacingCurve, QueueEntry, Rules, Save,
    SetQueue, SkillDef, SkillId, StoreDef, StoreId, StoreValue, SwitchMix, MixId, Mix, CardShare, SaveMix, TapCard, advance, decide, new_save,
    validate_rules,
)

from ashfall_app.engine import plan

STONE = StoreId("stone")
FENCE, SHED = CardId("fence"), CardId("shed")


def world() -> Rules:
    r = Rules(stores=(StoreDef(STONE, 100 * Q),), skills=(SkillDef(SkillId("k")),), standing=(),
              curve=PacingCurve((10**9 * Q,)), max_firings_per_instant=1000,
              cards=(CardDef(FENCE, 100, cap=1, inputs=(Amount(STONE, Q),)), CardDef(SHED, 100, cap=1)))
    validate_rules(r)
    return r


def queued(r: Rules, *cards: CardId) -> Save:
    entries = tuple(QueueEntry(TapCard(c), AtLeast(CardCount(c), 1, 1)) for c in cards)
    return decide(new_save(r), r, 0, SetQueue(entries))


def hands(s: Save) -> CardId | None:
    return next(ls.card for ls in s.lanes if ls.lane == HANDS)


def test_an_entry_nothing_makes_ready_does_not_hold_the_entries_behind_it():
    r = world()
    s = queued(r, FENCE, SHED)
    assert hands(advance(s, r, 50)) == SHED
    after = advance(s, r, 150)
    assert hands(after) is None and [e.verb for e in after.queue] == [TapCard(FENCE)]


def test_with_only_such_an_entry_the_hands_are_idle_and_the_entry_stays():
    r = world()
    after = advance(queued(r, FENCE), r, 500)
    assert hands(after) is None and [e.verb for e in after.queue] == [TapCard(FENCE)]


def test_a_goal_stint_behind_such_an_entry_waits_behind_it():
    r = world()
    s = decide(new_save(r), r, 0, SaveMix(Mix(MixId("m"), (CardShare(SHED, BP),))))
    s = decide(s, r, 0, SetQueue((QueueEntry(TapCard(FENCE), AtLeast(CardCount(FENCE), 1, 1)),
                                            QueueEntry(SwitchMix(MixId("m")), AtLeast(StoreValue(STONE), Q, Q)))))
    assert plan.controlling_entry(s, r) == 0
