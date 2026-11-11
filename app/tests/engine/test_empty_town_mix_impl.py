"""A town mix left with no card never takes the hands (engine DESIGN.txt, "THE TOWN'S MIX", "Layer"; "LEAVES", step 4:
its rule stays and runs nothing): the town's always rule does not switch the hands to the game's town mix, whether a
leave emptied it or a join made it with no share card. One the player named is the same."""
from dataclasses import replace

import pytest

from ashfall_app.engine import (
    QUANTITY_SCALE as Q, AfterTime, CardDef, CardId, CardShare, Flow, InvalidVerbError, Join, LaneDef, LaneId, Leave,
    Mix, MixId, Order, Outcome, PacingCurve, Rules, Save, SaveMix, SetOrders, StoreDef, StoreId, SwitchMix,
    TriggerDef, TriggerId, advance, decide, new_save, validate_rules,
)
from ashfall_app.engine.mixes import MixLayer
from ashfall_app.engine.plan import OrderState, order_states, running_mix_id, running_town_mix_id

X, W = StoreId("x"), StoreId("w")
LA = LaneId("la")
R1, TA = CardId("r1"), CardId("ta")
M, TOWN, OWN = MixId("m"), MixId("town:main"), MixId("winter")


def world(share_card: CardId | None = TA, leave_at: int | None = 10) -> Rules:
    """r1 on the hands making x; la's person joins town:main at 0 (with `share_card`) and leaves at `leave_at`."""
    triggers = [TriggerDef(TriggerId("join"), AfterTime(0), Outcome(joins=(Join(LA, TOWN, share_card),)))]
    if leave_at is not None:
        triggers.append(TriggerDef(TriggerId("leave"), AfterTime(leave_at), Outcome(leaves=(Leave(LA),))))
    r = Rules(stores=(StoreDef(X, 10**6 * Q, 0), StoreDef(W, 10**6 * Q, 0)), skills=(), standing=(),
              curve=PacingCurve((10**9 * Q,)), lanes=(LaneDef(LA, True),),
              cards=(CardDef(R1, 10, makes=(Flow(X, Q),)), CardDef(TA, 10, lane=LA, makes=(Flow(W, Q),))),
              triggers=tuple(triggers))
    validate_rules(r)
    return r


def playing(r: Rules) -> Save:
    """The player's own mix m, r1 whole, switched at 1."""
    s = advance(new_save(r), r, 1)
    return decide(decide(s, r, 1, SaveMix(Mix(M, (CardShare(R1, 10000),)))), r, 1, SwitchMix(M))


def town_rule(s: Save, mix: MixId) -> int:
    return next(i for i, o in enumerate(s.orders) if o.then == SwitchMix(mix))


def test_a_leave_that_empties_the_town_mix_leaves_the_hands_on_the_players_mix():
    r = world()
    s = playing(r)
    assert (running_mix_id(advance(s, r, 5), r), running_town_mix_id(advance(s, r, 5), r)) == (M, TOWN)
    after = advance(s, r, 50)
    assert next(m for m in after.mixes if m.id == TOWN).components == ()
    assert (running_mix_id(after, r), running_town_mix_id(after, r)) == (M, TOWN)
    assert order_states(after, r)[town_rule(after, TOWN)] is OrderState.ON
    with pytest.raises(InvalidVerbError):
        decide(after, r, 50, SwitchMix(TOWN))


def test_a_join_with_no_share_card_makes_a_town_mix_that_takes_nobodys_hands():
    r = world(share_card=None, leave_at=None)
    s = advance(playing(r), r, 5)
    assert next(m for m in s.mixes if m.id == TOWN).components == ()
    assert (running_mix_id(s, r), running_town_mix_id(s, r)) == (M, TOWN)


def named(r: Rules) -> Save:
    """The player's own town mix `OWN` with la's share in it, the town's always rule pointed at it, at 1."""
    s = playing(r)
    s = decide(s, r, 1, SaveMix(Mix(OWN, (CardShare(TA, 10000),))))
    return decide(s, r, 1, SetOrders(tuple(Order(o.when, SwitchMix(OWN)) if o.then == SwitchMix(TOWN) else o
                                           for o in s.orders)))


def test_a_town_mix_the_player_named_never_takes_the_hands_once_a_leave_empties_it():
    """The page's new town mix has the player's name and the town's always rule pointed at it (CONTRACT.txt)."""
    r = world(leave_at=20)
    s = named(r)
    assert (running_mix_id(advance(s, r, 10), r), running_town_mix_id(advance(s, r, 10), r)) == (M, OWN)
    after = advance(s, r, 50)
    assert next(m for m in after.mixes if m.id == OWN).components == ()
    assert running_mix_id(after, r) == M


def test_a_player_named_town_mix_saved_before_it_had_a_layer_is_still_a_town_mix_after_a_leave():
    r = world(leave_at=20)
    s = named(r)
    s = replace(s, mixes=tuple(replace(m, layer=MixLayer.HANDS) if m.id == OWN else m for m in s.mixes))
    after = advance(s, r, 50)
    assert next(m for m in after.mixes if m.id == OWN).components == ()
    assert running_mix_id(after, r) == M


def test_a_town_mix_the_player_empties_stays_a_town_mix_that_takes_nobodys_hands():
    r = world(leave_at=None)
    s = decide(named(r), r, 2, SaveMix(Mix(OWN, ())))
    assert (running_mix_id(advance(s, r, 10), r), running_town_mix_id(advance(s, r, 10), r)) == (M, OWN)
