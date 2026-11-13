"""A chapter file merged onto the opening (schema.Chapter, chapters.merge), a held Camp level a step lifts, and an order
card on a rising line: the shipped files load, and each rule fails on a file built to break it."""
from dataclasses import replace
from pathlib import Path

import pytest

from ashfall_app.engine import BP, CardId, ModifierKind, StoreCap, StoreId, new_save, units
from ashfall_app.engine.gates import store_cap
from ashfall_app.opening.convert import camp_cap, camp_lifts, camp_trigger_id
from ashfall_app.opening.schema import CHAPTERS, OPENING, Opening, load_opening, to_rules
from tests.opening.playthrough import opening

DAY_ONE = CHAPTERS[0]
CHAPTER = DAY_ONE.read_text()


def broken_chapter(tmp_path: Path, old: str, new: str) -> Path:
    """The shipped chapter with exactly one occurrence of `old` replaced."""
    assert CHAPTER.count(old) == 1, f"anchor is not unique in {DAY_ONE.name}: {old!r}"
    path = tmp_path / DAY_ONE.name
    path.write_text(CHAPTER.replace(old, new))
    return path


def load_with(path: Path) -> Opening:
    return load_opening(OPENING, (path,))


def test_the_opening_alone_is_a_whole_game_and_the_chapter_adds_to_it():
    alone, merged = load_opening(chapters=()), load_opening()
    to_rules(alone)
    to_rules(merged)
    assert {c.id for c in alone.cards} < {c.id for c in merged.cards}
    assert merged.curve_items[:len(alone.curve_items)] == alone.curve_items
    assert set(alone.text) < set(merged.text)


def test_a_control_edit_of_the_chapter_still_loads(tmp_path: Path):
    """The harness can pass: a harmless change loads, so the failures below are the rule's doing."""
    load_with(broken_chapter(tmp_path, 'c_take_stock = "Take stock"', 'c_take_stock = "Count the food"'))


def test_the_chapter_fills_the_openings_markers():
    """The held Camp level at 1500 lands now, and the "?" rows past the opening pay what the chapter says."""
    alone, merged = load_opening(chapters=()), load_opening()
    assert alone.camp is not None and merged.camp is not None
    assert alone.camp.levels[-1].held and not merged.camp.levels[2].held
    assert merged.camp.levels[2].at_items == alone.camp.levels[-1].at_items
    scav = next(s for s in merged.skills if s.id == "scavenging")
    assert [lv.level for lv in scav.levels] == sorted({lv.level for lv in scav.levels})
    assert next(lv for lv in scav.levels if lv.level == 4).pays_key != "pays_unknown"


@pytest.mark.parametrize("old,new,match", [
    ('c_take_stock = "Take stock"', 'c_take_stock = "Take stock"\nc_rest = "Rest"', "already in the text"),
    ('[[camp_levels]]\nat_items = 10800', '[[camp_levels]]\nat_items = 1000', "inserted before the last"),
    ('[[camp_levels]]\nat_items = 1500', '[[camp_levels]]\nat_items = 360', "not held"),
    ('skill = "foraging"\nlevels', 'skill = "cooking"\nlevels', "unknown skill cooking"),
    ('[[stores]]\nid = "wire"', '[[stores]]\nid = "roots"', "duplicate id roots"),
])
def test_a_chapter_that_overwrites_rather_than_adds_fails_the_load(tmp_path: Path, old: str, new: str, match: str):
    with pytest.raises(ValueError, match=match):
        load_with(broken_chapter(tmp_path, old, new))


def test_a_check_failure_names_the_chapter_that_broke_it_though_a_later_chapter_follows(tmp_path: Path):
    """The merged opening is checked once, at the end; the error still names the first chapter whose state fails."""
    plant = broken_chapter(tmp_path, '[[stores]]\nid = "wire"', '[[stores]]\nid = "roots"')
    with pytest.raises(ValueError, match="duplicate id roots") as shipped_order:
        load_opening(OPENING, (plant, *CHAPTERS[1:]))
    assert str(shipped_order.value).endswith(f" (in {DAY_ONE.name})")


EARLY = '[[cards]]\nid = "t_early"\nlane = "t_late"\npresentation = "action"\nlabel_key = "t_c_early"\nwork_s = 60\ncap = 1\n\n[text]\nt_c_early = "Early"\n'
LATE = '[[lanes]]\nid = "t_late"\nlabel_key = "t_l_late"\nruled = true\n\n[text]\nt_l_late = "Late"\n'


def test_a_chapter_naming_a_lane_only_a_later_chapter_adds_fails_naming_it(tmp_path: Path):
    early, late = tmp_path / "early.toml", tmp_path / "late.toml"
    early.write_text("version = 1\n\n" + EARLY)
    late.write_text("version = 1\n\n" + LATE)
    load_opening(OPENING, (late, early))
    with pytest.raises(ValueError, match="t_late") as forward:
        load_opening(OPENING, (early, late))
    assert str(forward.value).endswith(" (in early.toml)")


# ---------- a held level a step lifts ----------

def test_the_bar_holds_one_under_the_lifted_level_and_the_lift_reaches_it():
    o = load_opening()
    assert o.camp is not None
    lifted = next(lv for lv in o.camp.levels if lv.lifted_by)
    assert lifted.held and camp_cap(o.camp) == lifted.at_items - 1
    rules = to_rules(o)
    camp = StoreId(o.camp.store)
    assert next(s.cap for s in rules.stores if s.id == camp) == units(lifted.at_items - 1)
    n = o.camp.levels.index(lifted) + 1
    assert camp_trigger_id(n) in {t.id for t in rules.triggers}
    card, raise_ = camp_lifts(o.camp)[0]
    assert raise_.target == StoreCap(camp) and raise_.kind is ModifierKind.ADD_BP and raise_.amount_bp > 0
    lifter = next(c for c in rules.cards if c.id == CardId(card))
    assert raise_ in lifter.finished.modifiers
    s = new_save(rules)
    before = store_cap(s, rules, camp)
    after = store_cap(replace(s, modifiers=(*s.modifiers, raise_)), rules, camp)
    assert before < units(lifted.at_items) <= after < units(lifted.at_items) + units(lifted.at_items) // BP + units(1)


@pytest.mark.parametrize("old,new,match", [
    ('lifted_by = ["take_stock"]', 'lifted_by = ["ghost"]', "unknown card ghost"),
    ('lifted_by = ["take_stock"]', 'lifted_by = ["smoke_catch"]', "has no cap"),
    ('pays_key = "pays_unknown"\nheld = true\nlifted_by = ["take_stock"]', 'pays_key = "pays_unknown"\nlifted_by = ["take_stock"]',
     "this one is not held"),
    ('held = true\nlifted_by = ["take_stock"]', 'held = true', "it lands nothing"),
])
def test_a_lift_that_cannot_lift_fails_the_load(tmp_path: Path, old: str, new: str, match: str):
    with pytest.raises(ValueError, match=match):
        load_with(broken_chapter(tmp_path, old, new))


# ---------- an order card on a rising line ----------

@pytest.fixture(scope="module")
def shipped() -> Opening:
    """The cached shipped opening."""
    return opening()


def test_the_rising_line_card_is_an_at_least_on_a_store_its_card_takes(shipped: Opening):
    card = next(c for c in shipped.order_cards if c.when.test == "at_least")
    assert card.tap_card is not None and card.when.id == card.store
    taken = next(c for c in shipped.cards if c.id == card.tap_card)
    assert any(a.store == card.store for a in taken.inputs)


@pytest.mark.parametrize("old,new,match", [
    ('tap_card = "smoke_catch"\nwhen', 'tap_card = "smoke_roots"\nwhen', "does not take catch"),
    ('id = "catch", value = 4, release = 4', 'id = "catch", value = 7, release = 4', "past the store's cap"),
    ('id = "catch", value = 4, release = 4', 'id = "catch", value = 4, release = 0', "never let go"),
])
def test_a_rising_line_card_that_cannot_work_fails_the_load(tmp_path: Path, old: str, new: str, match: str):
    with pytest.raises(ValueError, match=match):
        load_with(broken_chapter(tmp_path, old, new))


# ---------- a rule offered once a cap has risen ----------

@pytest.mark.parametrize("old,new", [
    ('id = "roots", value = 12, release = 15', 'id = "roots", value = 12, release = 16'),    # the larder's cap: 16
    ('offered_after = { unlock_kind = "feature", id = "roots_to_stock" }', ''),            # no larder yet: 8
])
def test_a_rule_past_the_cap_it_is_offered_at_fails_the_load(tmp_path: Path, old: str, new: str):
    """The roots card lets go at 15: under what the larder holds once it is offered (the larder's finish counts toward
    its offer), never under the roots' first cap. One past that, or offered before the larder, fails."""
    with pytest.raises(ValueError, match="never let go"):
        load_with(broken_chapter(tmp_path, old, new))
