"""Retired chores at the loader (engine DESIGN.txt, "Retired chores", "Content (the loader)", invariant 146). Written
blind from that part and the loader's public functions; the `kills` marker names the rows of MUTANTS_leaves.txt each
test must turn red for. fixtures/chores_chapter.toml is merged onto the opening alone: a season opens a standing action
that fills t_pool and a chip on it; t_scoop drains the pool (the chore's cure), t_other is a plain card."""
import re
from pathlib import Path

from ashfall_app.engine import CardId
from leaves_world import kills
from retire_world import close_outcome, loaded, refused



def retiring(*cards: str) -> str:
    return "retire_orders = [" + ", ".join(f'"{c}"' for c in cards) + "]"


def test_a_season_turn_may_retire_the_orders_on_the_cure_of_a_chip_whose_store_only_the_season_makes(tmp_path: Path):
    """Invariant 146: the chapter loads and its closing turn carries the retirement as the engine's field."""
    r = loaded(tmp_path, CLOSE=retiring("t_scoop"))
    assert close_outcome(r).retire_orders == (CardId("t_scoop"),)


@kills(31)
def test_a_planted_retirement_naming_a_card_that_cures_nothing_fails_the_loader_naming_the_trigger_and_the_card(
        tmp_path: Path):
    msg = re.escape("trigger t_close: retires the orders on t_other, which cures no chip whose store only a season's "
                    "standing makes")
    refused(tmp_path, msg, CLOSE=retiring("t_other"))
    loaded(tmp_path, CLOSE=retiring("t_scoop"))   # the control the refusal edits


@kills(31)
def test_a_cure_whose_store_something_else_also_makes_is_refused(tmp_path: Path):
    """A card that makes the pool outside any season's standing: "only a season's standing makes" no longer holds."""
    filler = ('[[cards]]\nid = "t_fill"\npresentation = "action"\nlabel_key = "t_c_other"\nwork_s = 60\n'
              'makes = [{ store = "t_pool", items_per_hour = 1 }]\n')
    refused(tmp_path, "trigger t_close: retires the orders on t_scoop", CLOSE=retiring("t_scoop"), EXTRA=filler)


@kills(32)
def test_a_retirement_on_a_trigger_that_is_not_a_season_turn_is_refused(tmp_path: Path):
    refused(tmp_path, re.escape("trigger t_close: retires orders but is not a season's turn"),
            CLOSE=retiring("t_scoop"), SEASON="false")


@kills(32)
def test_a_retirement_on_a_cards_outcome_is_refused_naming_the_card(tmp_path: Path):
    refused(tmp_path, re.escape("t_other: retires orders outside a season's turn"),
            OTHER='outcome = { retire_orders = ["t_scoop"] }')
