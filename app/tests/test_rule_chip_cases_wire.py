"""The shipped cards, chips and stores that client/fixtures/real_chip_cards.json mirrors (client/test/rulechipsreal.test.ts runs
the rule editor's simple view on every pair) are the shipped content's: a card or chip the content changes fails here until the
fixture is regenerated: `shipped_slice` is what it holds, as JSON with two-space indent."""
import json
from pathlib import Path
from typing import Any

from tests.shipped_ruleset import ShippedRuleset

FILE = Path(__file__).resolve().parents[1] / "client/fixtures/real_chip_cards.json"


def shipped_slice(game: ShippedRuleset) -> dict[str, Any]:
    content = game.make_game(game.opening, game.rs).content().model_dump(mode="json")
    cards = [{"card": c["card"], "makes": c["makes"], "takes": c["takes"], "wounds": [w["store"] for w in (c["fight"] or {"wounds": []})["wounds"]]} for c in content["card_infos"]]
    chips = [{"chip": c["chip"], "when": c["when"]} for c in content["chip_infos"]]
    stores = [{"store": s["store"], "made_by": s["made_by"]} for s in content["store_infos"]]
    return {"cards": cards, "chips": chips, "stores": stores}


def test_fixture_is_the_shipped_slice(shipped_ruleset: ShippedRuleset) -> None:
    got = shipped_slice(shipped_ruleset)
    assert got["cards"] and got["chips"] and got["stores"]
    assert json.loads(FILE.read_text()) == got

