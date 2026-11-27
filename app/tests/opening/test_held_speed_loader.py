"""A while_running entry names a side or a lane (entries.WhileRunningEntry), and a standing action or a card may carry
one (engine DESIGN.txt, "HELD SPEED"); a card's upside_of names the runner whose entries its upside serves
(api/contract/, {pct}): the pot's card for a recipe (#473)."""
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from ashfall_app.api.content_models import Content
from ashfall_app.engine import CardId, HeldSpeed, LaneId
from ashfall_app.main import create_app
from ashfall_app.opening.entries import WhileRunningEntry
from ashfall_app.opening.refs import check_refs
from ashfall_app.opening.schema import load_opening, to_rules


def test_an_entry_names_exactly_one_of_side_and_lane() -> None:
    assert WhileRunningEntry.model_validate({"lane": "n2", "amount_bp": 1}).lane == "n2"
    for bad in ({"amount_bp": 1}, {"side": "hands", "lane": "n2", "amount_bp": 1}):
        with pytest.raises(ValidationError, match="exactly one of side and lane"):
            WhileRunningEntry.model_validate(bad)


def test_the_pot_holds_each_eaters_lane_speed_and_no_eater_holds_its_own() -> None:
    rules = to_rules(load_opening())
    pot = next(c for c in rules.cards if c.id == CardId("pot_stew"))
    lanes = [w.lane for w in pot.while_running if isinstance(w, HeldSpeed)]
    assert len(lanes) == len(pot.while_running) == len(set(lanes)) > 10
    assert LaneId("n2") in lanes
    assert not any(a.while_running for a in rules.standing if str(a.id).endswith("_eating"))


def test_upside_of_serves_the_eaters_change_on_the_recipe() -> None:
    o = load_opening()
    card = next(c for c in o.cards if c.upside_of is not None)
    eater = next(a for a in (*o.standing, *o.cards) if a.id == card.upside_of)
    served = Content.model_validate(TestClient(create_app()).get("/api/content").json())
    info = next(i for i in served.card_infos if i.card == card.id)
    assert info.change_bp[-1] == eater.while_running[0].amount_bp


def test_upside_of_naming_no_holder_is_refused() -> None:
    o = load_opening()
    bad = o.model_copy(update={"cards": [o.cards[0].model_copy(update={"upside_of": "n1_eating"}), *o.cards[1:]]})
    with pytest.raises(ValueError, match="unknown runner with while_running n1_eating"):
        check_refs(bad)
