"""The Camp's held levels and lifts (engine DESIGN.txt, "THE CAMP") with day two merged, as test_day_two.py loads it:
a save past day one's lift reaches day two's levels (invariant 72), no lift rounds past the next held level (69), and
either of Camp 8's lifting cards lifts it, the same (71). Levels are named by number, cards by id."""
from dataclasses import replace
from functools import cache
from pathlib import Path

import pytest

from ashfall_app.engine import (
    BP, AtLeast, CardId, Modifier, ModifierKind, Rules, Save, StoreCap, StoreId, StoreState, StoreValue, encode,
    new_save, rebase, units,
)
from ashfall_app.engine.gates import store_cap
from ashfall_app.engine.segments import Segment
from ashfall_app.opening.renames import engine_renames, load_renames
from ashfall_app.opening.schema import DAY_ONE, DAY_TWO, OPENING, Opening, load_opening, to_rules
from tests.opening.test_day_two import with_day_two

CAMP = StoreId("camp")
WALKS = ("walk_ridge", "n1_walk_ridge")


@cache
def day_one() -> Rules:
    return to_rules(load_opening(chapters=(DAY_ONE,)))


@cache
def day_two() -> Rules:
    return to_rules(with_day_two())


def at(n: int) -> int:
    """Camp level n's at, in quantity units, with day two merged."""
    camp = with_day_two().camp
    assert camp is not None
    return units(camp.levels[n - 1].at_items)


def camp_raises(mods: tuple[Modifier, ...]) -> int:
    return sum(m.amount_bp for m in mods if m.target == StoreCap(CAMP) and m.kind is ModifierKind.ADD_BP)


def lift(r: Rules, card: str) -> int:
    """The raise of the camp cap a card's finish lands."""
    return camp_raises(next(c for c in r.cards if c.id == CardId(card)).finished.modifiers)


def climbed(r: Rules, landed_bp: int) -> int:
    """The cap once the bar has filled as far as it can, with `landed_bp` already in the stack from finishes: each
    trigger on the camp store's value that the cap lets fire lands its raise, until none more can."""
    base = next(s.cap for s in r.stores if s.id == CAMP)
    on_camp = [t for t in r.triggers if isinstance(t.when, AtLeast) and t.when.subject == StoreValue(CAMP)]
    fired: set[str] = set()
    s = landed_bp
    while True:
        cap = base * (BP + s) // BP
        now = [t for t in on_camp if t.id not in fired and isinstance(t.when, AtLeast) and t.when.value <= cap]
        if not now:
            return cap
        fired |= {t.id for t in now}
        s += sum(camp_raises(t.outcome.modifiers) for t in now)


def past_day_ones_lift() -> Save:
    """A day-one save at its camp store's cap after take_stock's finish: the stack holds the lift as day one released
    it, and every camp level that cap reaches has fired."""
    r = day_one()
    card = next(c for c in r.cards if c.id == CardId("take_stock"))
    s = new_save(r)
    s = replace(s, modifiers=s.modifiers + tuple(m for m in card.finished.modifiers if m.target == StoreCap(CAMP)))
    cap = store_cap(s, r, CAMP)
    stores = tuple(StoreState(x.store, Segment(s.time, cap, 0)) if x.store == CAMP else x for x in s.stores)
    fired = tuple(f or (t.id.startswith("camp_") and isinstance(t.when, AtLeast) and t.when.value <= cap)
                  for t, f in zip(r.triggers, s.fired))
    return replace(s, stores=stores, fired=fired)


def test_a_save_past_day_ones_lift_reaches_camp_7_at_its_rebase():
    """Fault 1: the save keeps day one's raise; day two's rules must give it Camp 7's room at the load."""
    s = past_day_ones_lift()
    assert store_cap(s, day_one(), CAMP) >= units(54000)   # control: day one's lift landed
    s2 = rebase(encode(s, day_one()), day_two(), engine_renames(load_renames()))
    assert store_cap(s2, day_two(), CAMP) >= at(7)


def test_day_ones_lift_as_released_climbs_to_camp_7_and_holds_under_camp_8():
    """Faults 1 and 2 with the bar filled as far as it goes: from the raise day one released, Camp 7 lands and Camp 8
    does not."""
    cap = climbed(day_two(), lift(day_one(), "take_stock"))
    assert at(7) <= cap < at(8)


def test_no_lift_rounds_past_camp_8():
    """Fault 2: take_stock's lift under day two's rules, the bar filled, stays under Camp 8."""
    cap = climbed(day_two(), lift(day_two(), "take_stock"))
    assert at(7) <= cap < at(8)


@pytest.mark.parametrize("walk", WALKS)
def test_either_walk_lifts_camp_8_by_the_same_raise(walk: str):
    """Fault 3: each answer's walk carries Camp 8's lift, and from either the bar reaches Camp 8."""
    r = day_two()
    assert lift(r, walk) > 0 and lift(r, walk) == lift(r, WALKS[0])
    assert climbed(r, lift(r, "take_stock") + lift(r, walk)) >= at(8)
    assert climbed(r, lift(day_one(), "take_stock") + lift(r, walk)) >= at(8)


def test_day_twos_camp_8_names_both_walks():
    camp = with_day_two().camp
    assert camp is not None
    assert sorted(camp.levels[7].lifted_by) == sorted(WALKS) and camp.levels[7].held


# ---------- the loader refuses a lift it cannot keep ----------

def load_broken(tmp_path: Path, old: str, new: str) -> Opening:
    text = DAY_TWO.read_text()
    assert text.count(old) == 1, f"anchor is not unique in {DAY_TWO.name}: {old!r}"
    path = tmp_path / DAY_TWO.name
    path.write_text(text.replace(old, new))
    return load_opening(OPENING, (DAY_ONE, path))


def test_a_control_edit_of_day_two_still_loads(tmp_path: Path):
    to_rules(load_broken(tmp_path, 'pays_key = "pays_unknown"\nheld = true', 'pays_key = "pays_unknown"\nheld = true'))


@pytest.mark.parametrize("old,new,match", [
    ('lifted_by = ["walk_ridge", "n1_walk_ridge"]', 'lifted_by = ["walk_ridge", "take_stock"]', "only by answers"),
    ('unlocks = [{ unlock_kind = "card", id = "n1_walk_ridge" }, { unlock_kind = "action", id = "walk_out" }]',
     'unlocks = [{ unlock_kind = "card", id = "n1_walk_ridge" }, { unlock_kind = "action", id = "walk_out" }, '
     '{ unlock_kind = "card", id = "walk_ridge" }]',
     "unlocks two"),
    ('[[camp_levels]]\nat_items = 90000', '[[camp_levels]]\nat_items = 54002', "basis point"),
    ('id = "catch", kind = "mul_bp", amount_bp = 15000, source = "camp_8"',
     'id = "camp", kind = "add_bp", amount_bp = 100, source = "camp_8"', "the camp store's cap"),
])
def test_a_lift_the_cap_cannot_keep_fails_the_load(tmp_path: Path, old: str, new: str, match: str):
    with pytest.raises(ValueError, match=match):
        load_broken(tmp_path, old, new)
