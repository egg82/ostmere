"""The loader's stake check (opening/stake_checks.py): an uncapped card that takes stores and gives nothing by itself
declares what it feeds and says it on its face, and the whole content bears a side stake out. Each refusal is a card
merged onto the opening alone, beside a control that passes. Any card that takes stores and shows nothing gained says
what it is for with an upside_key, stake or not (decisions.md, "Every option offered works as worded")."""
from typing import Any

import pytest

from ashfall_app.opening.chapters import merge
from ashfall_app.opening.schema import Chapter, Opening, load_opening
from ashfall_app.opening.stake_checks import check_stakes, check_stakes_hold

SINK: dict[str, Any] = {"id": "t_sink", "presentation": "action", "label_key": "t_c", "work_s": 60,
                        "inputs": [{"store": "dry_wood", "items": 1}]}
STAKED = {**SINK, "stake": "side", "upside_key": "t_up"}
SIDE = {"id": "t_gap", "label_key": "t_side", "base": 4}
FIGHT: dict[str, Any] = {"id": "t_raid", "label_key": "t_a", "fight": {
    "side": "t_gap", "threat": "t_rats", "lost": "dry_wood", "fights_per_hour": 1, "won_line_keys": [], "lost_line_keys": []}}


def merged(*cards: dict[str, Any], **parts: Any) -> Opening:
    return merge(load_opening(chapters=()), Chapter.model_validate({"version": 1, "cards": list(cards), **parts}))


def test_a_bare_sink_without_a_stake_is_refused_by_name():
    with pytest.raises(ValueError, match="cards t_sink: take stores and give nothing"):
        check_stakes(merged(SINK))


def test_every_bare_sink_is_named_at_once():
    with pytest.raises(ValueError, match="cards t_sink, t_sink_2: "):
        check_stakes(merged(SINK, {**SINK, "id": "t_sink_2"}))


def test_a_stake_without_an_upside_is_refused():
    with pytest.raises(ValueError, match="card t_sink: has a stake and no upside_key"):
        check_stakes(merged({**SINK, "stake": "side"}))


def test_a_declared_stake_with_its_upside_passes():
    check_stakes(merged(STAKED))


@pytest.mark.parametrize("gives", [
    {"outcome": {"stores": [{"store": "damp_wood", "items": 1}]}},
    {"makes": [{"store": "damp_wood", "items_per_hour": 1}]},
    {"cap": 2, "upside_key": "t_up"},
])
def test_a_card_that_gives_something_or_has_a_cap_is_no_sink(gives: dict[str, Any]):
    check_stakes(merged({**SINK, **gives}))


@pytest.mark.parametrize("silent", [
    {"cap": 2},
    {"cap": 3, "finished": {"unlocks": [{"unlock_kind": "feature", "id": "t_feat"}]}},
])
def test_a_card_that_shows_nothing_gained_needs_an_upside(silent: dict[str, Any]):
    with pytest.raises(ValueError, match="cards t_sink: take stores and show nothing gained"):
        check_stakes(merged({**SINK, **silent}))


def test_a_narrative_card_is_its_own_story_and_needs_no_upside():
    check_stakes(merged({**SINK, "cap": 1, "presentation": "narrative"}))


def test_a_card_that_takes_nothing_is_no_sink():
    check_stakes(merged({**SINK, "inputs": []}))


def test_a_card_read_past_its_first_completion_is_no_sink():
    def reading(value: int) -> dict[str, Any]:
        return {"id": "t_read", "when": {"test": "at_least", "subject_kind": "card_count", "id": "t_sink", "value": value},
                "outcome": {"line_keys": ["t_l"]}}
    check_stakes(merged({**SINK, "upside_key": "t_up"}, triggers=[reading(2)]))
    with pytest.raises(ValueError, match="cards t_sink: "):
        check_stakes(merged(SINK, triggers=[reading(1)]))


def test_a_card_that_takes_a_chips_store_is_a_cure_not_a_sink():
    chip = {"id": "t_wet", "label_key": "t_ch", "tone": "cold", "when": {"test": "at_least", "subject_kind": "store",
                                                                             "id": "dry_wood", "value": 3}}
    check_stakes(merged({**SINK, "upside_key": "t_up"}, chips=[chip]))


def test_a_side_stake_needs_an_entry_on_a_fought_side_once_any_fight_exists():
    threat = [{"id": "t_rats", "label_key": "t_t", "base": 4}]
    check_stakes_hold(merged(STAKED, sides=[SIDE]))
    with pytest.raises(ValueError, match="card t_sink: has the stake side but holds no entry on a side any fight"):
        check_stakes_hold(merged(STAKED, sides=[SIDE], threats=threat, standing=[FIGHT]))
    other = {**SIDE, "id": "t_wall"}
    with pytest.raises(ValueError, match="card t_sink: has the stake side"):
        check_stakes_hold(merged({**STAKED, "while_running": [{"side": "t_wall", "amount_bp": 1}]},
                                 sides=[SIDE, other], threats=threat, standing=[FIGHT]))
    check_stakes_hold(merged({**STAKED, "while_running": [{"side": "t_gap", "amount_bp": 1}]},
                             sides=[SIDE], threats=threat, standing=[FIGHT]))


REACH: dict[str, Any] = {**SINK, "stake": "reach", "upside_key": "t_up",
                         "outcome": {"stores": [{"store": "damp_wood", "items": 1}]}}


def reading(store: str, modifiers: list[dict[str, Any]]) -> dict[str, Any]:
    return {"id": "t_reach", "when": {"test": "at_least", "subject_kind": "store", "id": store, "value": 5},
            "outcome": {"modifiers": modifiers}}


SPEED = [{"target": "work", "id": "gather_wood", "kind": "mul_bp", "amount_bp": 11000, "source": "t_reach"}]


def test_a_reach_stake_needs_a_trigger_on_the_store_it_fills_that_pays_a_modifier():
    check_stakes_hold(merged(REACH, triggers=[reading("damp_wood", SPEED)]))
    with pytest.raises(ValueError, match="card t_sink: has the stake reach but no trigger on a store it fills pays"):
        check_stakes_hold(merged(REACH))
    with pytest.raises(ValueError, match="card t_sink: has the stake reach"):
        check_stakes_hold(merged(REACH, triggers=[reading("dry_wood", SPEED)]))   # a store it takes, not fills
    with pytest.raises(ValueError, match="card t_sink: has the stake reach"):
        check_stakes_hold(merged(REACH, triggers=[{**reading("damp_wood", []), "outcome": {"line_keys": ["t_l"]}}]))


def test_a_card_that_takes_a_fights_wound_is_a_cure_not_a_sink():
    wounding = {**FIGHT, "fight": {**FIGHT["fight"], "wounds": [{"store": "dry_wood", "items": 1}]}}
    threat = [{"id": "t_rats", "label_key": "t_t", "base": 4}]
    check_stakes(merged({**SINK, "upside_key": "t_up"}, sides=[SIDE], threats=threat, standing=[wounding]))
    with pytest.raises(ValueError, match="cards t_sink: "):
        check_stakes(merged(SINK, sides=[SIDE], threats=threat, standing=[FIGHT]))
