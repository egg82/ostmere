"""The loader's chains (engine design/spells.txt, "SPELLS"; week-five-plan item 6): a threat's members, a fight's chained
tally, a card's chain and a modifier aimed at its reach, on fixtures/chains.toml merged onto the opening alone. Each
refusal is the fixture edited to break it, beside the control that loads."""
from pathlib import Path

import pytest

from ashfall_app.engine import (
    ActionId, ChainDef, ChainReach, CardId, InvalidRulesError, LineKey, ModifierKind, SourceId, StoreId, ThreatDef,
    ThreatId,
)
from ashfall_app.rules.schema import OPENING, Opening, load_opening, to_rules

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "chains.toml"
TEXT = FIXTURE.read_text()
CHAIN = 'chain = { runner = "t_prowl", reach = 2, link_line_keys = ["t_link_1", "t_link_next"] }'


def edited(tmp_path: Path, *edits: tuple[str, str]) -> Path:
    text = TEXT
    for old, new in edits:
        assert text.count(old) == 1, f"anchor is not unique: {old!r}"
        text = text.replace(old, new)
    path = tmp_path / FIXTURE.name
    path.write_text(text)
    return path


def load_with(path: Path) -> Opening:
    return load_opening(OPENING, (path,))


def test_the_fixture_loads_a_group_a_chained_tally_a_chain_and_a_reach_pay() -> None:
    r = to_rules(load_with(FIXTURE))
    assert ThreatDef(ThreatId("t_pack"), 3, 4) in r.threats
    prowl = next(a.fight for a in r.standing if a.id == "t_prowl")
    assert prowl is not None and prowl.chained == StoreId("t_chained")
    jump = next(c for c in r.cards if c.id == "t_jump")
    assert jump.chain == ChainDef(ActionId("t_prowl"), 2, (LineKey("t_link_1"), LineKey("t_link_next")))
    (pay,) = next(t for t in r.triggers if t.id == "t_reach_pay").outcome.modifiers
    assert (pay.target, pay.kind, pay.amount_bp, pay.source) == (
        ChainReach(CardId("t_jump")), ModifierKind.ADD_BP, 5000, SourceId("t_reach_pay"))


def test_shipped_threats_are_single_creatures_and_no_card_has_a_chain() -> None:
    r = to_rules(load_opening())
    assert all(t.members == 1 for t in r.threats)
    assert all(c.chain is None for c in r.cards) and all(a.fight is None or a.fight.chained is None for a in r.standing)


@pytest.mark.parametrize("edit,message", [
    (('members = 4', 'members = 1'), "card t_jump: chain names t_prowl, whose threat t_pack is not a group"),
    (('runner = "t_prowl"', 'runner = "t_nobody"'), "card t_jump: chain names t_nobody, which is not a standing fight"),
    ((', chained = "t_chained"', ''), "card t_jump: chain names t_prowl, which has no fought or chained tally"),
    (('"t_link_next"]', '"t_link_missing"]'), "card t_jump: key 't_link_missing' is not in text"),
    (('chained = "t_chained"', 'chained = "t_unknown"'), "action t_prowl: unknown store t_unknown"),
])
def test_a_chain_that_cannot_be_exact_is_refused_naming_the_card(tmp_path: Path, edit: tuple[str, str], message: str) -> None:
    with pytest.raises(ValueError, match=message):
        load_with(edited(tmp_path, edit))


def test_a_reach_pay_aimed_at_a_card_with_no_chain_is_refused(tmp_path: Path) -> None:
    path = edited(tmp_path, ('id = "t_jump", kind = "add_bp"', 'id = "gather_wood", kind = "add_bp"'))
    with pytest.raises(InvalidRulesError, match="trigger t_reach_pay: a modifier aims at an unknown id"):
        to_rules(load_with(path))


def test_a_lowering_reach_pay_is_refused(tmp_path: Path) -> None:
    path = edited(tmp_path, ('amount_bp = 5000, source = "t_reach_pay"', 'amount_bp = -5000, source = "t_reach_pay"'))
    with pytest.raises(InvalidRulesError, match="a chain's reach only rises"):
        to_rules(load_with(path))


def test_a_chain_line_needs_a_key_and_reach_at_least_one(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="link_line_keys"):
        load_with(edited(tmp_path, (CHAIN, 'chain = { runner = "t_prowl", reach = 2, link_line_keys = [] }')))
    with pytest.raises(ValueError, match="reach"):
        load_with(edited(tmp_path, ('reach = 2,', 'reach = 0,')))
