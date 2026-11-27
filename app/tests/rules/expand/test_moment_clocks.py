"""A moment clock is one authored field (`clock = "<id>"` on an outcome or a `[line_doings]` line) that the loader expands
(rules/expand/clocks.py): the hidden store, the standing action and the unlock. A line's clock starts from its owner's own
condition, so editing the owner moves the window with it."""
import pytest

from ashfall_app.rules.expand.clocks import PER_HOUR, clock_ids, with_moment_clocks
from ashfall_app.rules.schema import Opening

LINE_CLOCKS = {"l_bedding_4": "bedding_4_clock", "l_road_pair_2": "road_pair_clock", "l_choir_2": "choir_2_clock"}


def unexpanded(o: Opening) -> Opening:
    """`o` as the chapters author it: no clock store, standing action or line trigger yet."""
    ids = set(clock_ids(o))
    return o.model_copy(update={
        "stores": [s for s in o.stores if s.id not in ids], "standing": [s for s in o.standing if s.id not in ids],
        "triggers": [t for t in o.triggers if t.id not in {f"t_{i}" for i in ids}],
    })


def test_every_marked_clock_is_expanded_to_a_hidden_store_and_a_standing_action(shipped_opening: Opening):
    ids = clock_ids(shipped_opening)
    assert len(ids) == len(set(ids)) > 10
    stores = {s.id: s for s in shipped_opening.stores}
    standing = {s.id: s for s in shipped_opening.standing}
    for i in ids:
        assert stores[i].hidden and standing[i].makes[0].store == i and standing[i].makes[0].items_per_hour == PER_HOUR


def test_an_outcome_clock_is_unlocked_in_its_own_outcome_and_a_line_clock_by_a_trigger_on_its_owner(shipped_opening: Opening):
    o = shipped_opening
    caught = [t for t in o.triggers if t.id == "t_his_watch"][0]
    assert any(u.id == "his_watch_clock" for u in caught.outcome.unlocks)
    by_id = {t.id: t for t in o.triggers}
    cutter = [x for x in o.offers if "l_road_pair_2" in x.line_keys][0]
    assert by_id["t_road_pair_clock"].when == cutter.gate and by_id["t_road_pair_clock"].requires == cutter.requires
    card = [c for c in o.cards if "l_bedding_4" in c.line_keys][0]
    assert by_id["t_bedding_4_clock"].when.value == card.line_keys.index("l_bedding_4") + 1


def test_a_line_clock_follows_an_edit_of_its_owner(shipped_opening: Opening):
    """The planted change: raise the offer's gate and reorder the card's lines; the loader's triggers move with them."""
    o = unexpanded(shipped_opening)
    offer = [x for x in o.offers if "l_road_pair_2" in x.line_keys][0]
    card = [c for c in o.cards if "l_bedding_4" in c.line_keys][0]
    keys = card.line_keys
    assert keys.index("l_bedding_4") == 3
    edited = o.model_copy(update={
        "offers": [x.model_copy(update={"gate": x.gate.model_copy(update={"value": 999})}) if x is offer else x for x in o.offers],
        "cards": [c.model_copy(update={"line_keys": [*keys[:2], keys[3], keys[2], *keys[4:]]}) if c is card else c for c in o.cards],
    })
    by_id = {t.id: t for t in with_moment_clocks(edited).triggers}
    assert by_id["t_road_pair_clock"].when.value == 999
    assert by_id["t_bedding_4_clock"].when.value == 3, "l_bedding_4 moved to third place"


def test_a_line_told_by_a_card_and_an_offer_fails_loudly(shipped_opening: Opening):
    o = unexpanded(shipped_opening)
    offer = o.offers[0]
    both = o.model_copy(update={"offers": [offer.model_copy(update={"line_keys": [*offer.line_keys, "l_bedding_4"]}), *o.offers[1:]]})
    with pytest.raises(ValueError, match="l_bedding_4"):
        with_moment_clocks(both)


def test_a_clock_over_another_store_and_a_clock_marked_twice_fail(shipped_opening: Opening):
    o = unexpanded(shipped_opening)
    first = o.line_doings["l_bedding_4"]
    twice = o.model_copy(update={"line_doings": {**o.line_doings, "l_pelt_ask": o.line_doings["l_pelt_ask"].model_copy(
        update={"clock": first.clock})}})
    with pytest.raises(ValueError, match="marked twice"):
        with_moment_clocks(twice)
    other = o.model_copy(update={"stores": [*o.stores, shipped_opening.stores[0].model_copy(update={"id": first.clock})]})
    with pytest.raises(ValueError, match="not a moment clock"):
        with_moment_clocks(other)


def test_expanding_an_expanded_opening_changes_nothing(shipped_opening: Opening):
    again = with_moment_clocks(shipped_opening)
    assert [s.id for s in again.stores] == [s.id for s in shipped_opening.stores]
    assert [t.id for t in again.triggers] == [t.id for t in shipped_opening.triggers]
