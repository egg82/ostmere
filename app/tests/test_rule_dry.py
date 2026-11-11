"""View.order_dry on the goal-rows world (api/ruledry.py; CONTRACT.txt, "Dry rules"): "Under 6 plank, until 15 ->
saw", a mix of one card that turns the input `log` into `plank`."""
from ashfall_app import engine as e
from ashfall_app.api import goal_models as g
from ashfall_app.api.ruledry import order_dry
from ashfall_app.engine import BP, CardId, CardShare, MixId, Order, Save, SaveMix, SetOrders, SwitchMix
from ashfall_app.engine.mixes import Mix
from ashfall_app.engine.orders import AtMost, StoreValue
from ashfall_app.engine.units import units
from tests.test_goal_rows import LOG, PLANK, world

RULE = Order(AtMost(StoreValue(PLANK), units(6), units(15)), SwitchMix(MixId("weave")))


def _ruled(shares: dict[str, int], logs: int) -> tuple[e.Rules, Save]:
    r, s = world(logs=logs)
    mix = Mix(MixId("weave"), tuple(CardShare(CardId(c), bp) for c, bp in shares.items()))
    s = e.decide(s, r, s.time, SaveMix(mix))
    return r, e.decide(s, r, s.time, SetOrders((RULE,)))


def _dry(r: e.Rules, s: Save) -> g.RuleDry | None:
    [dry] = order_dry(s, r, e.view(s, r))
    return dry


def test_a_rule_holding_a_starved_mix_names_the_dry_input() -> None:
    r, s = _ruled({"saw": BP}, logs=1)
    s = e.advance(s, r, s.time + 3600)
    assert e.view(s, r).order_states == (e.OrderState.ON,) and any(p.store == LOG for p in s.pauses), "control: held, dry"
    assert _dry(r, s) == g.RuleDry(store="log", holding=True)


def test_a_refilling_input_is_not_dry() -> None:
    r, s = _ruled({"saw": BP // 4, "fell": 3 * BP // 4}, logs=0)
    s = e.advance(s, r, s.time + 60)
    assert e.view(s, r).order_states == (e.OrderState.ON,) and not s.pauses, "control: held, nothing waits on the log"
    assert _dry(r, s) is None


def test_a_reachable_release_is_not_stuck_but_a_mix_with_no_maker_of_its_input_may_stop_short() -> None:
    r, s = _ruled({"saw": BP}, logs=40)
    assert e.view(s, r).order_states == (e.OrderState.ON,) and not s.pauses, "control: held and fed"
    assert _dry(r, s) == g.RuleDry(store="log", holding=False)


def test_a_mix_with_a_maker_of_its_input_is_not_flagged_at_write_time() -> None:
    r, s = _ruled({"saw": BP // 2, "fell": BP // 2}, logs=40)
    assert _dry(r, s) is None


def test_a_rule_that_is_not_on_still_flags_what_its_mix_lacks() -> None:
    r, s = _ruled({"saw": BP}, logs=40)
    s = e.decide(s, r, s.time, SetOrders((Order(AtMost(StoreValue(PLANK), units(-1), units(15)), RULE.then),)))
    assert e.view(s, r).order_states == (e.OrderState.WAITING,), "control: the rule is not on"
    assert _dry(r, s) == g.RuleDry(store="log", holding=False)
