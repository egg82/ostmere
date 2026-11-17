"""A person's rule watching another lane's card running (api/CONTRACT.txt, "Decisions"): set_orders takes a Running
condition only on a rule whose every action taps a card on one lane other than the hands, watching a card of another
lane. Such a rule taps while the card runs, lets go when it stops, and the instant settles: its verb cannot start or
stop what it watches. Every other Running condition is refused, a pair of mix rules that would flip above all; the
control shows that pair, planted past the API, does hit the firing cap a loop would."""
import pytest
from pydantic import TypeAdapter

from ashfall_app import engine as e
from ashfall_app.api import convert
from ashfall_app.api import models as w

DECISION = TypeAdapter[w.Decision](w.Decision)
N4, N5 = e.LaneId("n4"), e.LaneId("n5")
HUNT, MEND, SORT, SAW = e.CardId("hunt"), e.CardId("mend"), e.CardId("sort"), e.CardId("saw")
FIRE = e.ActionId("fire")
CAP = 50


def world() -> e.Rules:
    """The player hunts on the hands for 60 s; Edward mends (25 s) or sorts on n4; someone saws on n5."""
    r = e.Rules(stores=(e.StoreDef(e.StoreId("x"), 100 * e.QUANTITY_SCALE),), skills=(e.SkillDef(e.SkillId("k")),),
                standing=(e.StandingDef(FIRE),), curve=e.PacingCurve((10**9 * e.QUANTITY_SCALE,)),
                lanes=(e.LaneDef(N4, ruled=True), e.LaneDef(N5, ruled=True)),
                cards=(e.CardDef(HUNT, 60), e.CardDef(MEND, 25, lane=N4, lines=(e.LineKey("mend"),)),
                       e.CardDef(SORT, 25, lane=N4), e.CardDef(SAW, 40, lane=N5)),
                max_firings_per_instant=CAP)
    e.validate_rules(r)
    return r


def running(runner: str, at_least: bool = True) -> dict[str, object]:
    kind, value = ("at_least", 1) if at_least else ("at_most", 0)
    return {"kind": kind, "watched": {"kind": "running", "runner": runner}, "value": value, "release": value}


def tap(card: str) -> dict[str, str]:
    return {"kind": "tap_card", "card": card}


def set_orders(r: e.Rules, *orders: dict[str, object]) -> e.Verb:
    return convert.verb(DECISION.validate_python({"kind": "set_orders", "orders": list(orders)}), r)


def test_edwards_rule_mends_while_the_player_hunts_and_lets_go_when_the_hunt_ends():
    r = world()
    s = e.decide(e.new_save(r), r, 0, set_orders(r, {"when": running("hunt"), "then": tap("mend")}))
    assert [ln.lane for ln in s.lanes if ln.card is not None] == []
    s = e.decide(s, r, 0, e.TapCard(HUNT))
    assert {ln.lane: ln.card for ln in s.lanes} == {e.HANDS: HUNT, N4: MEND, N5: None}
    step = e.advance_logged(s, r, 300)
    assert [(ln.time, ln.key) for ln in step.lines] == [(25, "mend"), (50, "mend"), (75, "mend")]
    assert all(ln.card is None for ln in step.save.lanes)
    assert step.save.cascade_count == 0


def test_a_rule_watching_another_persons_task_settles_at_every_instant():
    """Both rules watch the other's card through or_else and an unless: each instant still settles with no cascade."""
    r = world()
    s = e.decide(e.new_save(r), r, 0, set_orders(
        r, {"when": running("saw"), "then": tap("mend"), "or_else": [tap("sort")], "unless": [running("hunt")]},
        {"when": running("mend", at_least=False), "then": tap("saw")}))
    a = e.advance(s, r, 1000)
    assert a.cascade_count == 0 and a.last_cascade is None


def test_the_flip_pair_planted_past_the_api_hits_the_cap():
    """The control: two mix rules on whether hunt runs, planted in the engine directly, flip until the cap."""
    r = world()
    run, stop = e.MixId("run"), e.MixId("stop")
    s = e.decide(e.decide(e.new_save(r), r, 0, e.SaveMix(e.Mix(run, (e.CardShare(HUNT, e.BP),)))), r, 0,
                 e.SaveMix(e.Mix(stop, ())))
    s = e.decide(s, r, 0, e.SwitchMix(run))
    s = e.decide(s, r, 0, e.SetOrders((e.Order(e.AtLeast(e.Running(HUNT), 1, 1), e.SwitchMix(stop)),
                                       e.Order(e.AtMost(e.Running(HUNT), 0, 0), e.SwitchMix(run)))))
    assert s.cascade_count == 1


@pytest.mark.parametrize(("orders", "reason"), [
    ([{"when": running("hunt"), "then": {"kind": "switch_mix", "mix_id": "stop"}},
      {"when": running("hunt", at_least=False), "then": {"kind": "switch_mix", "mix_id": "run"}}], "person's lane"),
    ([{"when": running("sort"), "then": tap("mend")}], "own lane"),
    ([{"when": running("mend"), "then": tap("mend")}], "own lane"),
    ([{"when": running("saw"), "then": tap("hunt")}], "person's lane"),
    ([{"when": running("saw"), "then": tap("mend"), "or_else": [tap("saw")]}], "person's lane"),
    ([{"when": running("fire"), "then": tap("mend")}], "not a card"),
    ([{"when": {"kind": "after_time", "at": 0}, "then": tap("hunt"), "unless": [running("mend")]}], "person's lane"),
], ids=["the flip pair", "same lane", "its own card", "a hands tap", "two lanes", "a standing action",
        "a hands guard"])
def test_a_rule_whose_verb_could_reach_the_watched_card_is_refused(orders: list[dict[str, object]], reason: str):
    with pytest.raises(e.InvalidVerbError, match=reason):
        set_orders(world(), *orders)


def test_a_queue_entry_cannot_watch_running():
    r = world()
    with pytest.raises(e.InvalidVerbError, match="person's lane"):
        convert.verb(DECISION.validate_python(
            {"kind": "set_queue", "entries": [{"verb": tap("hunt"), "until": running("saw")}]}), r)
