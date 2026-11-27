"""Until done (api/contract/until-done.txt, "UNTIL DONE"), from that section alone: a staged card a tap started, switched mid-run to
the plan the page sends, ends exactly as the same plan made before the tap: the same completions, lane and save at the
same times. Decisions go through the wire models and api/convert, as the page's would.

World: the hands build B (100 s a stage, cap 4) over the player's own mix O; a townsperson's ruled lane N, free, can
take the one-off W (50 s a stage, cap 3)."""
from typing import Any

import pytest
from pydantic import TypeAdapter

from ashfall_app import engine as e
from ashfall_app.api import convert
from ashfall_app.api import models as w

DECISION = TypeAdapter[w.Decision](w.Decision)
N = e.LaneId("n")
B, W, O = e.CardId("b"), e.CardId("w"), e.CardId("o")
X = e.StoreId("x")
MIX = e.MixId("own")
TIMES = (0, 60, 99, 100, 150, 250, 300, 399, 400, 450, 600)


def world() -> e.Rules:
    r = e.Rules(stores=(e.StoreDef(X, 100 * e.QUANTITY_SCALE),), skills=(), standing=(),
                curve=e.PacingCurve((10**9 * e.QUANTITY_SCALE,)), lanes=(e.LaneDef(N, ruled=True),),
                cards=(e.CardDef(B, 100, cap=4), e.CardDef(O, 60, makes=(e.Flow(X, 10),)),
                       e.CardDef(W, 50, lane=N, cap=3)))
    e.validate_rules(r)
    return r


def wire(r: e.Rules, d: dict[str, Any]) -> e.Verb:
    return convert.verb(DECISION.validate_python(d), r)


def tap(card: str) -> dict[str, Any]:
    return {"kind": "tap_card", "card": card}


def entry(card: str, n: int) -> dict[str, Any]:
    until = {"kind": "at_least", "watched": {"kind": "card_count", "card": card}, "value": n, "release": n}
    return {"verb": tap(card), "until": until}


def always(card: str) -> dict[str, Any]:
    return {"when": {"kind": "after_time", "at": 0}, "then": tap(card)}


def start(r: e.Rules) -> e.Save:
    """The player's own mix runs on the hands."""
    s = e.new_save(r)
    s = e.decide(s, r, 0, e.SaveMix(e.Mix(MIX, (e.CardShare(O, e.BP),))))
    return e.decide(s, r, 0, e.SwitchMix(MIX))


def at(s: e.Save, r: e.Rules, t: int, d: dict[str, Any]) -> e.Save:
    return e.decide(e.advance(s, r, t), r, t, wire(r, d))


def same_from(r: e.Rules, planned: e.Save, switched: e.Save, after: int) -> None:
    for t in (x for x in TIMES if x >= after):
        a, b = e.advance(planned, r, t), e.advance(switched, r, t)
        va, vb = e.view(a, r), e.view(b, r)
        assert [(c.card, c.completions) for c in vb.cards] == [(c.card, c.completions) for c in va.cards], t
        assert [(c.card, c.completions) for c in vb.completed] == [(c.card, c.completions) for c in va.completed], t
        assert [(ln.lane, ln.card, ln.completes_at, ln.order) for ln in vb.lanes] == \
            [(ln.lane, ln.card, ln.completes_at, ln.order) for ln in va.lanes], t
        assert b == a, t


def completions(s: e.Save, r: e.Rules, card: e.CardId) -> int:
    v = e.view(s, r)
    return next((c.completions for c in (*v.cards, *v.completed) if c.card == card), -1)


@pytest.mark.parametrize("switch_at", [1, 60, 99])
def test_a_hands_tap_switched_mid_run_ends_as_the_entry_queued_before_it(switch_at: int):
    r = world()
    planned = at(start(r), r, 0, {"kind": "set_queue", "entries": [entry("b", 4)]})
    switched = at(start(r), r, 0, tap("b"))
    switched = at(switched, r, switch_at, {"kind": "set_queue", "entries": [entry("b", 4)]})
    same_from(r, planned, switched, switch_at)
    done = e.advance(switched, r, 400)
    assert completions(done, r, B) == 4 and done.queue == ()
    assert e.view(done, r).running_mix == MIX


def test_a_running_when_ready_entry_held_on_to_the_cap_ends_as_the_cap_entry_queued_first():
    r = world()
    planned = at(start(r), r, 0, {"kind": "set_queue", "entries": [entry("b", 4)]})
    switched = at(start(r), r, 0, {"kind": "set_queue", "entries": [entry("b", 1)]})
    switched = at(switched, r, 60, {"kind": "set_queue", "entries": [entry("b", 4)]})
    same_from(r, planned, switched, 60)


def test_a_hand_tap_left_alone_stops_after_one_stage():
    """The control: without the switch the tap does one stage, so the cases above are not equal by accident."""
    r = world()
    alone = e.advance(at(start(r), r, 0, tap("b")), r, 400)
    assert completions(alone, r, B) == 1


@pytest.mark.parametrize("switch_at", [1, 25, 49])
def test_a_persons_one_off_switched_mid_run_ends_as_the_rule_set_before_it(switch_at: int):
    r = world()
    rules = {"kind": "set_orders", "orders": [always("w")]}
    planned = at(start(r), r, 0, rules)
    switched = at(start(r), r, 0, tap("w"))
    switched = at(switched, r, switch_at, rules)
    same_from(r, planned, switched, switch_at)
    done = e.advance(switched, r, 150)
    assert completions(done, r, W) == 3
    assert next(ln.card for ln in done.lanes if ln.lane == N) is None


def test_a_persons_one_off_left_alone_stops_after_one_stage():
    r = world()
    alone = e.advance(at(start(r), r, 0, tap("w")), r, 150)
    assert completions(alone, r, W) == 1
