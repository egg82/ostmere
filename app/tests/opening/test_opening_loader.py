"""The opening loader: the shipped file loads and converts, and each validation fails on a file built to break it."""
from pathlib import Path

import pytest

from ashfall_app.engine import (
    HANDS, QUANTITY_SCALE, LaneId, AtLeast, AtMost, InvalidRulesError, Rules, StoreId, StoreValue, per_hour, rules_digest, units,
    validate_rules,
)
from ashfall_app.opening.ui_keys import UI_KEYS
from ashfall_app.opening.convert import camp_lands, camp_trigger_id
from ashfall_app.opening.entries import ChipEntry
from ashfall_app.opening.schema import OPENING, load_opening, to_rules
from tests.opening.playthrough import opening, opening_rules

TEXT = OPENING.read_text()


def broken(tmp_path: Path, old: str, new: str) -> Path:
    """The shipped file with exactly one occurrence of `old` replaced; the anchor must exist once."""
    assert TEXT.count(old) == 1, f"anchor is not unique in opening.toml: {old!r}"
    path = tmp_path / "opening.toml"
    path.write_text(TEXT.replace(old, new))
    return path


def test_the_shipped_file_loads_and_its_rules_are_valid():
    rules = to_rules(load_opening())
    validate_rules(rules)
    assert rules.opening is not None and rules.cards and rules.chips and rules.triggers


@pytest.fixture(scope="module")
def two_loads() -> tuple[Rules, Rules]:
    """The shipped file loaded and converted twice, independently."""
    return to_rules(load_opening()), to_rules(load_opening())


def test_the_same_file_gives_equal_rules_and_one_digest(two_loads: tuple[Rules, Rules]):
    a, b = two_loads
    assert a == b and hash(a) == hash(b) and rules_digest(a) == rules_digest(b)


def test_a_control_edit_still_loads(tmp_path: Path):
    """The harness can pass: a harmless change (a longer label) loads, so the failures below are the rule's doing."""
    load_opening(broken(tmp_path, 'c_rest = "Rest"', 'c_rest = "Rest a while"'))


def test_authoring_units_become_the_engines_fixed_point():
    o = load_opening()
    rules = to_rules(o)
    assert next(s for s in rules.stores if s.id == "stones").cap == units(12)
    lay = next(c for c in rules.cards if c.id == "lay_to_dry")
    assert [(a.store, a.quantity) for a in lay.inputs] == [("damp_wood", 3 * QUANTITY_SCALE)]
    assert lay.lane == "rack" and lay.cap is None
    fire = next(a for a in rules.standing if a.id == "fire")
    assert {f.store: f.per_hour for f in fire.costs} == {"dry_wood": 6000}
    cold = next(c for c in rules.chips if c.id == "cold")
    assert cold.when == AtMost(StoreValue(StoreId("warmth")), units(3), units(5))
    assert rules.curve.thresholds == tuple(units(n) for n in o.curve_items)


@pytest.mark.parametrize("chapters", [(), None], ids=["opening alone", "with its chapters"])
def test_every_hands_card_fills_the_camp_and_no_other_card_does(chapters: tuple[Path, ...] | None):
    """The Camp bar fills by work done (a make flow on every hands card and every card of a ruled lane), and each level is a trigger on the store,
    except a held one nothing lifts, which the content never reaches: the opening alone ends on one, and so do its
    chapters (a goal on screen the next chapter lifts), so the exception is exercised either way; a held level a step
    lifts is a trigger like the rest."""
    o = load_opening() if chapters is None else load_opening(chapters=chapters)
    assert o.camp is not None
    rules = to_rules(o)
    camp = StoreId(o.camp.store)
    fills = {HANDS, *(LaneId(x.id) for x in o.lanes if x.ruled)}
    for c in rules.cards:
        flows = [f.per_hour for f in c.makes if f.store == camp]
        assert flows == ([per_hour(o.camp.items_per_hour)] if c.lane in fills else []), c.id
    levels = [t for t in rules.triggers if t.id.startswith("camp_")]
    reached = [(n, lv) for n, lv in enumerate(o.camp.levels, start=1) if camp_lands(lv)]
    held = [lv for lv in o.camp.levels if lv.held]
    assert held and [lv for _, lv in reached] == o.camp.levels[:-1] and not camp_lands(o.camp.levels[-1])
    assert (chapters == ()) or any(lv.held and lv.lifted_by for lv in o.camp.levels)
    assert [t.id for t in levels] == [camp_trigger_id(n) for n, _ in reached]
    assert [t.when for t in levels] == [AtLeast(StoreValue(camp), units(lv.at_items), units(lv.at_items))
                                        for _, lv in reached]


@pytest.mark.parametrize("old,new", [
    ('version = 1', 'version = 1\nbogus = 1'),
    ('id = "damp_wood"\nlabel_key = "store_damp_wood"', 'id = "damp_wood"\nlabel_key = "store_damp_wood"\ncolour = "red"'),
    ('amount_bp = 6667, source = "fireback"', 'amount_bp = 6667, source = "fireback", extra = 1'),
])
def test_an_unknown_field_fails_the_load(tmp_path: Path, old: str, new: str):
    with pytest.raises(ValueError, match="extra|bogus|colour|Extra"):
        load_opening(broken(tmp_path, old, new))


@pytest.mark.parametrize("old,new", [
    ('label_key = "store_damp_wood"', 'label_key = "nope"'),
    ('label_key = "skill_scavenging"', 'label_key = "nope"'),
    ('label_key = "action_chill"', 'label_key = "nope"'),
    ('label_key = "lane_rack"', 'label_key = "nope"'),
    ('label_key = "c_rest"', 'label_key = "nope"'),
    ('upside_key = "up_stool"', 'upside_key = "nope"'),
    ('line_keys = ["l_up_1", "l_up_2", "l_up_3"]', 'line_keys = ["l_up_1", "l_up_2", "nope"]'),
    ('failed_line_key = "l_strike_fail"', 'failed_line_key = "nope"'),
    ('line_keys = ["l_look"]', 'line_keys = ["nope"]'),
    ('line_keys = ["l_fire_lit"]', 'line_keys = ["nope"]'),
    ('outcome = { line_keys = ["l_wc_2"] }', 'outcome = { line_keys = ["nope"] }'),
    ('label_key = "chip_cold"', 'label_key = "nope"'),
    ('on_line_key = "l_hungry"', 'on_line_key = "nope"'),
    ('cost_key = "chip_tired_cost"', 'cost_key = "nope"'),
    ('id = "ledger"\n', 'id = "ledger"\nhint_key = "nope"\n'),
    ('start_line_keys = []', 'start_line_keys = ["nope"]'),
    ('end_line_keys = ["l_dusk_1", "l_dusk_2"]', 'end_line_keys = ["l_dusk_1", "nope"]'),
    ('pays_key = "camp_pays_1"', 'pays_key = "nope"'),
    ('line_keys = ["l_camp_1"]', 'line_keys = ["nope"]'),
    ('{ level = 2, pays_key = "pays_crafts" }', '{ level = 2, pays_key = "nope" }'),
    ('label_key = "feature_book"', 'label_key = "nope"'),
])
def test_a_key_missing_from_text_fails_the_load(tmp_path: Path, old: str, new: str):
    with pytest.raises(ValueError, match="nope"):
        load_opening(broken(tmp_path, old, new))


@pytest.mark.parametrize("old,new,why", [
    ('offered_after = { unlock_kind = "action", id = "eating" }', 'offered_after = { unlock_kind = "action", id = "nope" }',
     "unknown action nope"),
    ('{ target = "cap", id = "roots",', '{ target = "cap", id = "nope",', "unknown store nope"),
    ('pays_key = "camp_pays_1"', 'pays_key = "camp_pays_1"\nheld = true', "only the last level may be held"),
    ('pays_key = "pays_unknown"\nheld = true', 'pays_key = "pays_unknown"\nheld = true\nline_keys = ["l_camp_2"]',
     "it lands nothing"),
])
def test_an_order_offer_a_cap_modifier_and_a_held_level_are_checked(tmp_path: Path, old: str, new: str, why: str):
    with pytest.raises(ValueError, match=why):
        load_opening(broken(tmp_path, old, new))


@pytest.mark.parametrize("old,new,why", [
    ('cost_key = "chip_tired_cost"\n', '', "a cost_key exactly when it has effects"),
    ('effects = [{ target = "lane", id = "hands", kind = "mul_bp", amount_bp = 5000, source = "tired" }]\n', '',
     "a cost_key exactly when it has effects"),
    ('cost_key = "chip_tired_cost"', 'cost_key = "chip_tired_cost"\noffered_after = { unlock_kind = "action", id = "fire" }',
     "its cost runs before it is drawn"),
])
def test_a_chip_says_its_cost_and_is_drawn_while_it_costs(tmp_path: Path, old: str, new: str, why: str):
    with pytest.raises(ValueError, match=why):
        load_opening(broken(tmp_path, old, new))


def test_a_template_holding_a_digit_fails_the_load(tmp_path: Path):
    with pytest.raises(ValueError, match="holds a digit"):
        load_opening(broken(tmp_path, '"ui.rate.per_minute" = "{n}/min"', '"ui.rate.per_minute" = "{n}/1min"'))


@pytest.mark.parametrize("old,new,match", [
    ('when = { test = "at_most", subject_kind = "store", id = "roots"',
     'when = { test = "at_most", subject_kind = "store", id = "dry_wood"', "on its own store"),
    ('when = { test = "at_most", subject_kind = "store", id = "roots"',
     'when = { test = "at_least", subject_kind = "store", id = "roots"', "does not take roots"),
])
def test_an_order_card_not_watching_its_own_store_fails_the_load(tmp_path: Path, old: str, new: str, match: str):
    """The page words every order card as a level on its store, so `when` is on that store; an at_least card is the
    rule for a rising line and so must tap a card that takes the store (forage makes roots, so it cannot be)."""
    with pytest.raises(ValueError, match=match):
        load_opening(broken(tmp_path, old, new))


@pytest.mark.parametrize("key", UI_KEYS)
def test_a_missing_fixed_ui_key_fails_the_load(tmp_path: Path, key: str):
    line = next(ln for ln in TEXT.splitlines() if ln.startswith(f'"{key}" = '))
    with pytest.raises(ValueError, match="missing the fixed key"):
        load_opening(broken(tmp_path, line + "\n", ""))


@pytest.mark.parametrize("old,new", [
    ('failed_line_key = "l_stool_fail"\n', ""),   # inputs, no line
    ('label_key = "c_rest"\nwork_s = 10\n',          # requires, no line
     'label_key = "c_rest"\nwork_s = 10\nrequires = [{ test = "at_least", subject_kind = "store", id = "roots", value = 1 }]\n'),
])
def test_a_card_that_can_be_tapped_unready_without_a_failed_line_fails_the_load(tmp_path: Path, old: str, new: str):
    """Every card with inputs or requires says something when it fails; one with neither (rest, as shipped) need not."""
    with pytest.raises(ValueError, match="no failed_line_key"):
        load_opening(broken(tmp_path, old, new))


def test_an_end_feature_nothing_unlocks_fails_the_load(tmp_path: Path):
    path = broken(tmp_path, '[[features]]\nid = "book"\n', '[[features]]\nid = "orphan"\n\n[[features]]\nid = "book"\n')
    path.write_text(path.read_text().replace('end_feature = "keeps_going"', 'end_feature = "orphan"'))
    with pytest.raises(ValueError, match="no card or trigger unlocks"):
        load_opening(path)


def test_the_first_mix_name_is_a_valid_mix_id():
    assert 1 <= len(opening().text["ui.mix.default"]) <= 40


@pytest.mark.parametrize("old,new,match", [
    ('cards = ["gather_wood", "scavenge"]', 'cards = ["gather_wood"]', "two or more"),
    ('cards = ["gather_wood", "scavenge"]', 'cards = ["gather_wood", "lay_to_dry"]', "not a hands card"),
    ('cards = ["gather_wood", "scavenge"]', 'cards = ["gather_wood", "ghost"]', "unknown card"),
    ('first_mix = { feature = "mix"', 'first_mix = { feature = "ghost"', "unknown feature"),
])
def test_a_first_mix_that_cannot_be_a_mix_fails_the_load(tmp_path: Path, old: str, new: str, match: str):
    with pytest.raises(ValueError, match=match):
        load_opening(broken(tmp_path, old, new))


@pytest.mark.parametrize("old,new,match", [
    ('cap_items = 1500', 'cap_items = 1400', "cap_items must be what its levels allow"),
    ('at_items = 360', 'at_items = 100', "strictly increasing"),
    ('store = "camp"\nitems_per_hour', 'store = "ghost"\nitems_per_hour', "unknown store"),
])
def test_a_camp_that_does_not_add_up_fails_the_load(tmp_path: Path, old: str, new: str, match: str):
    with pytest.raises(ValueError, match=match):
        load_opening(broken(tmp_path, old, new))


def test_a_fraction_that_does_not_divide_exactly_fails_the_load(tmp_path: Path):
    with pytest.raises(ValueError, match="divide exactly"):
        load_opening(broken(tmp_path, 'outcome = { stores = [{ store = "stones", items = 1 }] }',
                            'outcome = { stores = [{ store = "stones", items = 1, every = 7 }] }'))


@pytest.fixture(scope="module")
def fraction_rules(tmp_path_factory: pytest.TempPathFactory) -> Rules:
    """The file with scavenge's stone split in three, loaded and converted."""
    path = broken(tmp_path_factory.mktemp("fraction"), 'outcome = { stores = [{ store = "stones", items = 1 }] }',
                  'outcome = { stores = [{ store = "stones", items = 1, every = 3 }] }')
    return to_rules(load_opening(path))


def test_a_fraction_that_divides_exactly_loads(fraction_rules: Rules):
    scavenge = next(c for c in fraction_rules.cards if c.id == "scavenge")
    assert scavenge.outcome.stores[0].quantity == QUANTITY_SCALE // 3


@pytest.mark.parametrize("old,new,match", [
    ('id = "lay_to_dry"\nlane = "rack"', 'id = "lay_to_dry"\nlane = "nowhere"', "unknown lane"),
    ('skill = "scavenging"\nxp_per_hour = 360', 'skill = "nothing"\nxp_per_hour = 360', "unknown skill"),
    ('outcome = { stores = [{ store = "roots", items = 1 }] }', 'outcome = { stores = [{ store = "mud", items = 1 }] }',
     "unknown store"),
    ('finished = { unlocks = [{ unlock_kind = "card", id = "look_around" }] }',
     'finished = { unlocks = [{ unlock_kind = "card", id = "ghost" }] }', "unknown card"),
    ('{ unlock_kind = "feature", id = "book" }', '{ unlock_kind = "feature", id = "undeclared" }', "unknown feature"),
    ('{ unlock_kind = "retired", id = "gather_wood", replaced_by = "woodcutting" }', '{ unlock_kind = "retired", id = "ghost" }', "unknown retired"),
    ('id = "clear_spot", value = 2', 'id = "ghost", value = 2', "unknown card"),
    ('tap_card = "forage"', 'tap_card = "ghost"', "unknown card"),
    ('tap_card = "forage"', 'tap_card = "forage"\nswitch_mix = "m"', "exactly one"),
    ('release = 5 }', 'release = 2 }', "wrong side"),
    ('id = "roots", value = 3, release = 6 }', 'id = "roots", value = 3, release = 8 }', "never let go"),
    ('id = "rest", flow = "make", store = "energy"', 'id = "rest", flow = "make"', "needs a flow"),
    ('id = "rest", flow', 'id = "ghost", flow', "unknown runner"),
    ('curve_items = [6, 10, 20, 36]', 'curve_items = [6, 6, 20]', "strictly increasing"),
])
def test_a_dangling_or_malformed_reference_fails_the_load(tmp_path: Path, old: str, new: str, match: str):
    with pytest.raises(ValueError, match=match):
        load_opening(broken(tmp_path, old, new))


def test_a_duplicate_id_fails_the_load(tmp_path: Path):
    with pytest.raises(ValueError, match="duplicate id"):
        load_opening(broken(tmp_path, '[[stores]]\nid = "dry_wood"', '[[stores]]\nid = "damp_wood"'))


def test_a_card_and_a_standing_action_sharing_an_id_fails_the_load(tmp_path: Path):
    """Cards and standing actions are one namespace of runners."""
    with pytest.raises(ValueError, match="duplicate id"):
        load_opening(broken(tmp_path, '[[standing]]\nid = "eating"', '[[standing]]\nid = "rest"'))


def test_a_chip_effect_not_sourced_by_its_chip_fails_the_engines_validation(tmp_path: Path):
    """The loader passes it; to_rules runs the engine's validation and refuses."""
    o = load_opening(broken(tmp_path, 'amount_bp = 5000, source = "tired"', 'amount_bp = 5000, source = "other"'))
    with pytest.raises(InvalidRulesError):
        to_rules(o)


CHIP_CARD = 'chip = "tired"\nafter_end = true\nwhen = { test = "at_most", subject_kind = "store", id = "energy", value = 3, release = 6 }'


@pytest.mark.parametrize("new,match", [
    (CHIP_CARD.replace('chip = "tired"', 'chip = "nope"'), "unknown chip nope"),
    (CHIP_CARD.replace('chip = "tired"', 'chip = "cold"'), "does not watch its store energy"),
    (CHIP_CARD.replace("release = 6", "release = 5"), "is not chip tired's"),
    (CHIP_CARD.replace('chip = "tired"\n', ""), "after_end needs a chip"),
])
def test_a_chip_order_card_that_does_not_match_its_chip_fails_the_load(tmp_path: Path, new: str, match: str):
    """A chip's order card is worded as the chip, so its chip must exist, watch its store and share its `when`; only
    such a card waits for the end."""
    with pytest.raises(ValueError, match=match):
        load_opening(broken(tmp_path, CHIP_CARD, new))


def test_a_chip_order_card_without_after_end_still_loads(tmp_path: Path):
    """The control: the chip rules are what fail above, not the edit."""
    o = load_opening(broken(tmp_path, CHIP_CARD, CHIP_CARD.replace("after_end = true", "after_end = false")))
    assert [(c.chip, c.after_end) for c in o.order_cards if c.chip] == \
        [("tired", False), ("hungry", True), ("ash_laden", False), ("draughty", False)]


def chips_with_tired_moved() -> list[ChipEntry]:
    return [c.model_copy(update={"when": c.when.model_copy(update={"release": 5})}) if c.id == "tired" else c
            for c in opening().chips]


@pytest.fixture(scope="module")
def order_digests() -> tuple[str, str, str]:
    """The cached opening's rules digest, that of the same without its order cards, and that with a chip's release moved,
    converted once."""
    o = opening()
    return (rules_digest(opening_rules()), rules_digest(to_rules(o.model_copy(update={"order_cards": []}))),
            rules_digest(to_rules(o.model_copy(update={"chips": chips_with_tired_moved()}))))


def test_order_cards_never_reach_the_rules_or_their_digest(order_digests: tuple[str, str, str]):
    """Order cards are offers the page shows, not rules: the shipped file's digest is that of its rules with every order
    card removed, so adding one never resets a save. The control (a chip's release moved) shows the comparison can
    differ."""
    shipped, without_orders, with_moved_chip = order_digests
    assert without_orders == shipped
    assert any(m != c for m, c in zip(chips_with_tired_moved(), opening().chips))   # control: the chip was found
    assert with_moved_chip != shipped   # the control: the digest does differ when a chip's release does
