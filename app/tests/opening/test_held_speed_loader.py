"""A while_running entry names a side or a lane (entries.WhileRunningEntry), and a standing action may carry one
(engine DESIGN.txt, "HELD SPEED"); a card's upside_of names the standing action whose entries its upside serves
(api/CONTRACT.txt, {pct})."""
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from ashfall_app.api.content_models import Content
from ashfall_app.engine import ActionId, HeldSpeed, LaneId
from ashfall_app.main import create_app
from ashfall_app.opening.entries import WhileRunningEntry
from ashfall_app.opening.refs import check_refs
from ashfall_app.opening.schema import load_opening, to_rules


def test_an_entry_names_exactly_one_of_side_and_lane() -> None:
    assert WhileRunningEntry.model_validate({"lane": "n2", "amount_bp": 1}).lane == "n2"
    for bad in ({"amount_bp": 1}, {"side": "hands", "lane": "n2", "amount_bp": 1}):
        with pytest.raises(ValidationError, match="exactly one of side and lane"):
            WhileRunningEntry.model_validate(bad)


def test_each_eater_holds_its_own_lane_speed_in_the_rules() -> None:
    rules = to_rules(load_opening())
    held = {a.id: a.while_running for a in rules.standing if a.while_running}
    assert held, "the content holds no standing holder"
    for action, entries in held.items():
        lane = LaneId(str(action).removesuffix("_eating"))
        assert entries == (HeldSpeed(lane, entries[0].amount_bp),), action
    assert ActionId("n2_eating") in held


def test_upside_of_serves_the_eaters_change_on_the_recipe() -> None:
    o = load_opening()
    card = next(c for c in o.cards if c.upside_of is not None)
    eater = next(a for a in o.standing if a.id == card.upside_of)
    served = Content.model_validate(TestClient(create_app()).get("/api/content").json())
    info = next(i for i in served.card_infos if i.card == card.id)
    assert info.change_bp[-1] == eater.while_running[0].amount_bp


def test_upside_of_naming_no_holder_is_refused() -> None:
    o = load_opening()
    bad = o.model_copy(update={"cards": [o.cards[0].model_copy(update={"upside_of": "n1_eating"}), *o.cards[1:]]})
    with pytest.raises(ValueError, match="unknown standing action with while_running n1_eating"):
        check_refs(bad)
