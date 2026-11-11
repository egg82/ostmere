"""A find's amount (api/CONTRACT.txt, "Text and numbers", {found}): the trigger's outcome names its line with
found_line_key, the content serves the amount as a FindInfo, and the checks hold the slot and the key together."""
from functools import cache

import pytest

from ashfall_app import engine as e
from ashfall_app.api.service import Game
from ashfall_app.opening.checks import check_opening
from ashfall_app.opening.entries import ItemAmount, OutcomeEntry
from ashfall_app.opening.schema import Opening, load_opening
from ashfall_app.saves.ruleset import ruleset

FIND, LINE = "t_arcana_5", "l_arcana_5"


@cache
def everything() -> Opening:
    return load_opening()


@pytest.fixture(scope="module", autouse=True)
def built() -> Opening:
    """The cached opening, loaded in setup so no test's timed call pays for it."""
    return everything()


def with_outcome(o: Opening, **fields: object) -> Opening:
    triggers = [t.model_copy(update={"outcome": t.outcome.model_copy(update=fields)}) if t.id == FIND else t
                for t in o.triggers]
    return o.model_copy(update={"triggers": triggers})


def test_the_find_names_its_line_and_the_line_holds_the_slot_once():
    o = everything()
    out = next(t.outcome for t in o.triggers if t.id == FIND)
    assert out.found_line_key == LINE and LINE in out.line_keys and o.text[LINE].count("{found}") == 1
    check_opening(o)


def test_the_content_serves_the_amount_found_in_quantity():
    o = everything()
    served = [x for x in Game(o, ruleset(o, [], "test", 1)).content().find_infos if x.line_key == LINE]
    items = next(t.outcome.stores[0].items for t in o.triggers if t.id == FIND)
    assert [(x.store, x.quantity) for x in served] == [("dry_wood", items * e.QUANTITY_SCALE)]


def test_a_found_line_key_outside_the_outcomes_lines_fails():
    with pytest.raises(ValueError, match="is not one of its line_keys"):
        check_opening(with_outcome(everything(), line_keys=[]))


def test_a_find_of_two_stores_fails():
    stores = [ItemAmount(store="dry_wood", items=1), ItemAmount(store="stones", items=1)]
    with pytest.raises(ValueError, match="exactly one store"):
        check_opening(with_outcome(everything(), stores=stores))


def test_a_line_without_the_slot_fails():
    o = everything()
    text = {**o.text, LINE: "twigs snap clean."}
    with pytest.raises(ValueError, match="must hold the slot"):
        check_opening(o.model_copy(update={"text": text}))


def test_the_slot_in_a_text_no_find_names_fails():
    o = everything()
    with pytest.raises(ValueError, match="is no trigger's found_line_key"):
        check_opening(o.model_copy(update={"text": {**o.text, "l_his_watch": "{found} more."}}))


def test_a_card_outcome_may_not_carry_a_found_line_key():
    o = everything()
    card = o.cards[0].model_copy(update={"outcome": OutcomeEntry(found_line_key=LINE)})
    with pytest.raises(ValueError, match="only a trigger's outcome may"):
        check_opening(o.model_copy(update={"cards": [card, *o.cards[1:]]}))
