"""The shipped cards and chips that client/fixtures/real_chip_cards.json mirrors (client/test/rulechipsreal.test.ts runs
the rule editor's simple view on them) are the shipped content's: a card or chip the content changes fails here until the
fixture is regenerated: `shipped_slice` is what it holds, as JSON with two-space indent."""
import json
from pathlib import Path
from typing import Any

from tests.shipped_ruleset import ShippedRuleset

FILE = Path(__file__).resolve().parents[1] / "client/fixtures/real_chip_cards.json"
CARDS = ["clear_roofs", "n2_clear_roofs", "peg_flaps", "n1_peg_flaps"]
CHIPS = ["ash_laden", "draughty"]


def shipped_slice(game: ShippedRuleset) -> dict[str, Any]:
    content = game.make_game(game.opening, game.rs).content().model_dump(mode="json")
    cards = [{"card": c["card"], "takes": c["takes"]} for c in content["card_infos"] if c["card"] in CARDS]
    chips = [{"chip": c["chip"], "when": c["when"]} for c in content["chip_infos"] if c["chip"] in CHIPS]
    return {"cards": cards, "chips": chips}


def test_fixture_is_the_shipped_slice(shipped_ruleset: ShippedRuleset) -> None:
    got = shipped_slice(shipped_ruleset)
    assert len(got["cards"]) == len(CARDS)
    assert len(got["chips"]) == len(CHIPS)
    assert json.loads(FILE.read_text()) == got

