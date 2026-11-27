"""mixruns.town_entries is kept across saves while every input of its build is as it was (mixruns._town_key): a save
that differs in one of them gets a fresh result, and the same one the kept value."""
from dataclasses import replace

import pytest

from ashfall_app.engine import (
    QUANTITY_SCALE as Q, AfterTime, AtLeast, CardDef, CardId, CardShare, Flow, Join, LaneDef, LaneId, LaneState, Mix,
    MixId, Outcome, PacingCurve, Pause, Rules, Save, Segment, StoreDef, StoreId, StoreState, StoreValue, TriggerDef,
    TriggerId, Unlock, UnlockKind, advance, new_save, validate_rules,
)
from ashfall_app.engine import mixruns
from ashfall_app.engine.memo import KeyedMemo

X, W, Y, Z = (StoreId(n) for n in "xwyz")
G, P1, P3 = LaneId("g"), LaneId("p1"), LaneId("p3")
GWORK, A1, A3, MAKEY = CardId("gwork"), CardId("a1"), CardId("a3"), CardId("makey")
TOWN = MixId("town:main")


def world() -> Rules:
    """A pooled g (p1 in its group, unmarked) and p3 with their own split, both joined to the town mix; a3 requires w;
    makey on the hands makes y from z, so y is spent while z is empty."""
    r = Rules(stores=tuple(StoreDef(s, 10**9 * Q, 0) for s in (X, W, Y, Z)), skills=(), standing=(),
              curve=PacingCurve((10**9 * Q,)),
              lanes=(LaneDef(G, True, pooled=True), LaneDef(P1, True, group=G), LaneDef(P3, True)),
              cards=(CardDef(GWORK, 100, lane=G, makes=(Flow(X, Q),)), CardDef(A1, 100, lane=P1, makes=(Flow(X, Q),)),
                     CardDef(A3, 100, lane=P3, makes=(Flow(X, Q),), requires=(AtLeast(StoreValue(W), Q, Q),)),
                     CardDef(MAKEY, 100, makes=(Flow(Y, Q),), costs=(Flow(Z, Q),))),
              triggers=(TriggerDef(TriggerId("j1"), AfterTime(1), Outcome(joins=(Join(P1, TOWN, GWORK, own_split=False),))),
                        TriggerDef(TriggerId("j3"), AfterTime(2), Outcome(joins=(Join(P3, TOWN, A3),)))),
              opening=(Unlock(UnlockKind.CARD, MAKEY),))
    validate_rules(r)
    return r


def stored(s: Save, **values: int) -> Save:
    return replace(s, stores=tuple(StoreState(st.store, Segment(s.time, values[st.store], 0)) if st.store in values
                                   else st for st in s.stores))


def lane(s: Save, which: LaneId, **fields: object) -> Save:
    return replace(s, lanes=tuple(replace(ls, **fields) if ls.lane == which else ls for ls in s.lanes))


def first_paused(s: Save) -> Save:
    return replace(s, pauses=(Pause(A3, Y, Q),))


def halved(s: Save) -> Save:
    return replace(s, mixes=tuple(Mix(m.id, (CardShare(GWORK, 10000), CardShare(A3, 5000))) if m.id == TOWN else m
                                  for m in s.mixes))


def unjoined(s: Save) -> Save:
    return replace(s, unlocked=tuple(u for u in s.unlocked if u != Unlock(UnlockKind.JOINED, P3)))


CHANGES = {
    "the shares of the running mix": (lambda s: s, halved),
    "a lane's tap held": (lambda s: stored(s, w=Q), lambda s: lane(s, P3, card=A3)),
    "a person's own split": (lambda s: s, lambda s: lane(s, P1, own_split=True)),
    "the unlock set": (lambda s: s, unjoined),
    "a pause": (lambda s: s, first_paused),
    "a require turning true": (lambda s: s, lambda s: stored(s, w=Q)),
    "the spent stores, under a pause": (first_paused, lambda s: stored(first_paused(s), z=Q)),
}


def fresh(s: Save, r: Rules, monkeypatch: pytest.MonkeyPatch) -> object:
    """town_entries of `s` built with nothing kept: a memo of its own, and a copy of the save no per-save memo knows."""
    with monkeypatch.context() as m:
        m.setattr(mixruns, "_TOWN_BUILT", KeyedMemo())
        return mixruns.town_entries(replace(s), r), mixruns.mix_gains(replace(s), r)


def test_the_same_inputs_keep_the_result_across_saves():
    r = world()
    s = advance(new_save(r), r, 500)
    kept = mixruns.town_entries(s, r)
    assert kept and mixruns.town_entries(replace(s), r) is kept


@pytest.mark.parametrize("name", CHANGES)
def test_a_change_to_each_input_gets_a_fresh_result(name: str, monkeypatch: pytest.MonkeyPatch):
    r = world()
    prime, change = CHANGES[name]
    base = prime(advance(new_save(r), r, 500))
    before = mixruns.town_entries(base, r)
    changed = change(base)
    want = fresh(changed, r, monkeypatch)
    assert want[0] != before, "the change alters what the build gives, or the test shows nothing"
    assert (mixruns.town_entries(replace(changed), r), mixruns.mix_gains(replace(changed), r)) == want
