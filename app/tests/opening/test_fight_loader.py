"""The loader's fights (combat-plan item 5): sides, threats and a `fight` table on cards and standing actions, tally
stores, and the ramp as triggers, on fixtures/fights.toml merged onto the opening alone. Each refusal is the fixture
edited to break it, beside a control that loads. The planted slots for item 6's content checks sit at the end."""
import tomllib
from pathlib import Path

import pytest

from ashfall_app.engine import (
    InvalidRulesError, ModifierKind, Rules, SideDef, SideId, SourceId, ThreatDef, ThreatId, ThreatStrength, WhileRunning,
    units,
)
from ashfall_app.opening.chapters import merge
from ashfall_app.opening.schema import OPENING, Chapter, Opening, load_opening, to_rules
from tests.opening.fight_plants import PLANTS, Plant

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "fights.toml"
TEXT = FIXTURE.read_text()
HUNT_FIGHT = 'fight = { side = "t_hands", threat = "t_rats", lost = "t_lost_hunt", loses'


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


def rules() -> Rules:
    return to_rules(load_with(FIXTURE))


def test_the_fixture_chapter_loads_with_one_of_each():
    r = rules()
    assert r.sides == (SideDef(SideId("t_hands"), 4),) and r.threats == (ThreatDef(ThreatId("t_rats"), 3),)
    hunt = next(c.fight for c in r.cards if c.id == "t_hunt")
    raid = next(a.fight for a in r.standing if a.id == "t_raid")
    assert hunt is not None and raid is not None
    assert (hunt.side, hunt.threat, hunt.lost, hunt.fought, hunt.per_hour) == ("t_hands", "t_rats", "t_lost_hunt", None, 0)
    assert [(a.store, a.quantity) for a in hunt.loses] == [("damp_wood", units(1))]
    assert [(a.store, a.quantity) for a in hunt.wounds] == [("t_bitten", units(1))]
    assert (raid.lost, raid.fought, raid.per_hour) == ("t_lost_raid", "t_fought_raid", 2_000)
    assert raid.wounds == ()


def test_the_ramp_is_a_trigger_aiming_at_the_threat_with_its_own_id_as_source():
    ramp = next(t for t in rules().triggers if t.id == "t_ramp_1")
    (m,) = ramp.outcome.modifiers
    assert m.target == ThreatStrength(ThreatId("t_rats")) and m.kind == ModifierKind.MUL_BP and m.amount_bp == 12_000
    assert m.source == SourceId("t_ramp_1")


def test_rules_without_fights_declare_none():
    r = to_rules(load_opening(OPENING, ()))
    assert r.sides == () and r.threats == () and all(c.fight is None for c in r.cards)


@pytest.mark.parametrize("old,new,match", [
    ('fight = { side = "t_hands", threat = "t_rats", lost = "t_lost_hunt"',
     'fight = { side = "t_nobody", threat = "t_rats", lost = "t_lost_hunt"', "unknown side t_nobody"),
    ('fight = { side = "t_hands", threat = "t_rats", lost = "t_lost_hunt"',
     'fight = { side = "t_hands", threat = "t_nothing", lost = "t_lost_hunt"', "unknown threat t_nothing"),
    ('lost = "t_lost_raid", fought', 'lost = "t_missing", fought', "unknown store t_missing"),
    ('fought = "t_fought_raid", fights', 'fought = "t_missing", fights', "unknown store t_missing"),
    ('loses = [{ store = "stones", items = 1 }]', 'loses = [{ store = "t_missing", items = 1 }]', "unknown store t_missing"),
    ('wounds = [{ store = "t_bitten", items = 1 }]', 'wounds = [{ store = "t_bitten", items = 1, every = 7 }]',
     "does not divide exactly"),
    ('id = "t_rats", kind = "mul_bp"', 'id = "t_nothing", kind = "mul_bp"', "unknown threat t_nothing"),
    ('t_threat_rats = "Rats"\n', "", "key 't_threat_rats' is not in text"),
    ("base = 4\n\n[[threats]]", 'base = 4\n\n[[sides]]\nid = "t_hands"\nlabel_key = "t_side_hands"\nbase = 1\n\n[[threats]]',
     "duplicate id t_hands"),
])
def test_a_fight_the_loader_cannot_resolve_fails_naming_it(tmp_path: Path, old: str, new: str, match: str):
    with pytest.raises(ValueError, match=match):
        load_with(edited(tmp_path, (old, new)))


@pytest.mark.parametrize("old,new,match", [
    ("fights_per_hour = 2, ", "", "per_hour"),
    (HUNT_FIGHT, 'fight = { side = "t_hands", threat = "t_rats", fights_per_hour = 1, lost = "t_lost_hunt", loses', "per_hour"),
])
def test_a_fight_the_engine_refuses_is_refused_by_to_rules(tmp_path: Path, old: str, new: str, match: str):
    opening = load_with(edited(tmp_path, (old, new)))
    with pytest.raises(InvalidRulesError, match=match):
        to_rules(opening)


def test_a_threat_aimed_at_from_a_cards_outcome_is_refused_by_to_rules(tmp_path: Path):
    """Who may aim at a threat is the engine's rule (invariant 83); the loader carries the modifier faithfully."""
    mod = '{ target = "threat", id = "t_rats", kind = "mul_bp", amount_bp = 12000, source = "t_tend" }'
    path = edited(tmp_path, ('inputs = [{ store = "t_bitten", items = 1 }]', f'inputs = [{{ store = "t_bitten", items = 1 }}]\nfinished = {{ modifiers = [{mod}] }}'))
    with pytest.raises(InvalidRulesError):
        to_rules(load_with(path))


def held(tmp_path: Path, *entries: str) -> Path:
    return edited(tmp_path, (HUNT_FIGHT, f"while_running = [{', '.join(entries)}]\n{HUNT_FIGHT}"))


def test_a_cards_while_running_entries_load_as_the_engines_in_order(tmp_path: Path):
    r = to_rules(load_with(held(tmp_path, '{ side = "t_hands", amount_bp = 2500 }')))
    assert next(c.while_running for c in r.cards if c.id == "t_hunt") == (WhileRunning(SideId("t_hands"), 2500),)
    assert all(c.while_running == () for c in r.cards if c.id != "t_hunt")


def test_a_while_running_the_loader_or_the_engine_refuses_fails(tmp_path: Path):
    with pytest.raises(ValueError, match="amount_bp"):
        load_with(held(tmp_path, '{ side = "t_hands", amount_bp = 0 }'))
    with pytest.raises(InvalidRulesError, match="unknown side"):
        to_rules(load_with(held(tmp_path, '{ side = "t_nobody", amount_bp = 1 }')))
    with pytest.raises(InvalidRulesError, match="side t_hands twice"):
        to_rules(load_with(held(tmp_path, '{ side = "t_hands", amount_bp = 1 }, { side = "t_hands", amount_bp = 2 }')))


# ---------- the slots for combat-plan item 6 ----------

def chapter(tmp_path: Path, plant: Plant) -> Opening:
    """The plant merged without check_opening, so it stays a test of the plant's shape once item 6's checks land."""
    path = edited(tmp_path, *plant.edits)
    opening = load_opening(OPENING, ())
    return merge(opening, Chapter.model_validate(tomllib.loads(path.read_text())))


@pytest.mark.parametrize("plant", PLANTS, ids=lambda p: p.name)
def test_each_planted_fixture_is_valid_rules_and_breaks_only_its_check(tmp_path: Path, plant: Plant):
    to_rules(chapter(tmp_path, plant))


@pytest.mark.parametrize("plant", PLANTS, ids=lambda p: p.name)
def test_each_planted_fixture_fails_its_content_check_naming_the_id(tmp_path: Path, plant: Plant):
    with pytest.raises(ValueError, match=plant.failing_id):
        load_with(edited(tmp_path, *plant.edits))
