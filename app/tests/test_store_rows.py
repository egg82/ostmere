"""View.store_rows on test_goal_rows' fixture world (api/world/storerows.py; contract/store-rows.txt, "Store rows"): each store's net as
set, where it heads, and whether a card of the hands' mix touches it. `fell` makes log (3 an hour), `saw` costs log
(6 an hour) into plank."""
from ashfall_app import engine as e
from ashfall_app.api.world import store_models as s
from ashfall_app.api.world.storerows import store_rows
from ashfall_app.engine import BP, CardId, Rules, Save
from ashfall_app.engine.lanes import TapCard
from ashfall_app.engine.units import per_hour, units
from tests.test_goal_rows import running, world


def rows(r: Rules, sv: Save) -> dict[str, s.StoreRow]:
    return {x.store: x for x in store_rows(sv, r, e.view(sv, r))}


def test_a_store_whose_consumer_share_rises_nets_less_and_heads_to_empty() -> None:
    r, sv = world(logs=10)
    before = rows(r, running(r, sv, {"fell": BP}))["log"]
    after = rows(r, running(r, sv, {"fell": BP // 2, "saw": BP // 2}))["log"]
    assert (before.per_hour, before.heading, before.at) == (per_hour(3), s.Heading.FILLS, sv.time + e.ceil_div(units(40), per_hour(3)))
    assert after.per_hour == per_hour(3) // 2 - per_hour(6) // 2 < before.per_hour
    assert after.heading is s.Heading.EMPTIES and after.at == sv.time + e.ceil_div(units(10), -after.per_hour)


def test_a_store_nothing_moves_is_steady_and_a_card_of_the_mix_marks_its_stores() -> None:
    r, sv = world(logs=10)
    got = rows(r, running(r, sv, {"fell": BP}))
    assert (got["plank"].heading, got["plank"].at, got["plank"].mixed) == (s.Heading.STEADY, None, False)
    assert got["log"].mixed
    assert rows(r, running(r, sv, {"saw": BP}))["plank"].mixed, "a maker of plank is in the mix"


def test_a_tap_of_the_hands_is_set_aside() -> None:
    r, sv = world(logs=10)
    sv = running(r, sv, {"fell": BP // 2, "saw": BP // 2})
    tapped = e.decide(sv, r, sv.time, TapCard(CardId("nap")))
    assert e.view(tapped, r).ledger[0].net_per_hour != rows(r, sv)["log"].per_hour, "control: the ledger yields to the tap"
    assert rows(r, tapped) == rows(r, sv)
