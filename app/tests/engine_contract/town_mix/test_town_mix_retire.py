"""Engine engine/design/, "THE TOWN'S MIX", "Uncapped only", and "Greyed mix": a retired card stops only its own share in a
town mix (idle for that person, never handed to another); a hands mix holding one is greyed whole."""
from ashfall_app.engine import (
    BP, QUANTITY_SCALE as Q, AfterTime, CardId, CardShare, Mix, Order, Outcome, SaveMix, SwitchMix, TriggerDef, TriggerId, Unlock,
    UnlockKind, advance, view,
)
from town_mix_world import A1, B1, H1, H2, HM1, LA, LB, TM, V, X, joiner, orders, start, stored, world

RETIRE_AT = 100


def _retire(card: CardId) -> TriggerDef:
    return TriggerDef(TriggerId("ret"), AfterTime(RETIRE_AT), Outcome(unlocks=(Unlock(UnlockKind.RETIRED, card),)))


def test_a_retired_card_stops_only_its_own_share_in_a_town_mix():
    """a1 (la) and b1 (lb) share town:main; a1 retires at 100: the mix is not greyed and still runs, b1 keeps running,
    and la's share idles (x stops, v is not sped up)."""
    r = world((joiner("ja", LA, TM, A1), joiner("jb", LB, TM, B1), _retire(A1)), opening=())
    s = start(r, orders(Order(AfterTime(0), SwitchMix(TM))))
    after = view(advance(s, r, 150), r)
    assert (after.running_town_mix, after.greyed_mixes) == (TM, ())
    assert abs(stored(s, r, X, 150) - RETIRE_AT * Q) <= 150
    assert abs(stored(s, r, V, 150) - 150 * Q) <= 150
    assert abs(stored(s, r, V, 300) - 300 * Q) <= 300


def test_a_hands_mix_with_a_retired_card_still_greys_whole():
    r = world((_retire(H1),), opening=(Unlock(UnlockKind.CARD, H1), Unlock(UnlockKind.CARD, H2)))
    s = start(r, SaveMix(Mix(HM1, (CardShare(H1, BP // 2), CardShare(H2, BP // 2)))))
    assert view(advance(s, r, 50), r).greyed_mixes == ()
    assert view(advance(s, r, 150), r).greyed_mixes == (HM1,)
