"""Saves written before lumps were paid by work (d3400d5) load and run on as if played here: a store's saved rate then
held the old rounded lump rate, which store_segment must not read back as part of the store's flow.

The fixture is that engine's own encoder output (record_lump_saves.py), each save mid-lump at a speed with no whole
duration and followed by a long stretch with no event. Its values at the save already differ from a native play (the
old rates paid differently before it), so the two are compared by what they do after it, which only the cards' work,
equal in both, decides."""
import json
from pathlib import Path

import pytest

from ashfall_app.engine import QUANTITY_SCALE as Q, Rules, Save, advance, advance_logged, rebase, segment
from tests.engine.lump_saves_world import ONE, SAVED_AT, Y, rules, started

FIXTURE = Path(__file__).parent / "fixtures" / "lump_saves_d3400d5.json"
HORIZON = {"tap": 16_000, "mix": 86_400}


def recorded(r: Rules, name: str) -> Save:
    return rebase(json.loads(FIXTURE.read_text())[name], r)   # format 7: rebase upgrades it, as a player's load does


def values(s: Save, r: Rules) -> dict[str, int]:
    return {st.store: segment(s, r, st.store).start_value for st in s.stores}


@pytest.mark.parametrize("name", sorted(SAVED_AT))
def test_an_old_save_runs_on_as_a_native_one_does(name: str):
    """From the save on, every store moves by what a native play's moves by, at every sampled second, no store below
    0, the same pauses; the work and the trigger's line land at the same seconds."""
    r = rules()
    old, native = recorded(r, name), advance(started(r, name), r, SAVED_AT[name])
    assert old.cards == native.cards and old.pauses == native.pauses
    o0, n0 = values(old, r), values(native, r)
    a, b = old, native
    for t in range(old.time + 1, old.time + HORIZON[name], 613):
        a, b = advance(a, r, t), advance(b, r, t)
        va, vb = values(a, r), values(b, r)
        assert {k: va[k] - o0[k] for k in va} == {k: vb[k] - n0[k] for k in vb}, t
        assert min(va.values()) >= 0 and a.pauses == b.pauses and a.cards == b.cards, t


def test_an_old_walk_save_lands_short_only_by_what_the_old_rate_had_under_paid():
    """The walk: the old save had paid the floor of its rounded rate so far, under one unit a second short of the work
    it had done. That shortfall is history no save field records, so it stays: from the save y gains exactly what a
    native play gains, the item lands that much short, and the trigger on a whole item does not fire, as it did not on
    the engine that wrote the save. A native play lands the whole item and fires at the completion."""
    r = rules()
    old, native = recorded(r, "tap"), advance(started(r, "tap"), r, SAVED_AT["tap"])
    end = SAVED_AT["tap"] + HORIZON["tap"]
    so, sn = advance_logged(old, r, end), advance_logged(native, r, end)
    assert values(sn.save, r)[Y] == Q and [ln.key for ln in sn.lines] == [ONE]
    short = Q - values(so.save, r)[Y]
    assert 0 < short <= SAVED_AT["tap"] and so.lines == ()
