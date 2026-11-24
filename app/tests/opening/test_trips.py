"""An expedition's pieces on fixtures/trips.toml merged after the shipped chapters (week-four-plan item 5; engine DESIGN
"BANKED TIME"): a hands trip and its town twin adding to one count, finds on that count, and a skill whose first card is the
trip. What the loader and its checks accept, what the player-only check refuses, and the engine's reading: the nth find
lands the instant the nth trip completes however the count is split, and a trip whose materials sit at their caps keeps
running and counting."""
import tempfile
from collections.abc import Callable
from pathlib import Path

import pytest

from ashfall_app.engine import (
    BP, QUANTITY_SCALE, CardId, CardShare, Mix, MixId, RunKind, Rules, Save, SaveMix, StoreId, SwitchMix, advance, value_at, decide, new_save, view,
)
from ashfall_app.engine.work import completions
from ashfall_app.opening.checks import check_opening
from ashfall_app.opening.player_checks import check_player_only
from ashfall_app.opening.schema import Opening, merge_chapters, to_rules
from tests.dayone.growth import runaway
from tests.opening.blank_levels import mixed_skills, top_level, unmarked_levels
from tests.opening.test_level_pays import unpaid_markers
from tests.opening.test_second_skill import rows

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "trips.toml"
TRIP, TWIN, COUNT, ORE = CardId("t_trip"), CardId("t_scout_trip"), StoreId("t_trips"), StoreId("t_ore")
H = 3600


def loaded(shipped: Opening, old: str = "", new: str = "", count: int = 1) -> tuple[Opening, Rules]:
    top = top_level(to_rules(shipped))
    text = FIXTURE.read_text()
    if old:
        assert text.count(old) == count, f"anchor is not unique: {old!r}"
        text = text.replace(old, new)
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / FIXTURE.name
        path.write_text(text.replace("\n[text]\n", "\n" + rows(top) + "\n[text]\n", 1))
        o = merge_chapters(shipped, (path,))
    return o, to_rules(o)


@pytest.fixture(scope="module")
def shipped_plus(shipped_opening: Opening) -> tuple[Opening, Rules]:
    return loaded(shipped_opening)


def test_the_trip_its_twin_and_the_finds_on_the_count_load_and_pass_every_check(shipped_plus: tuple[Opening, Rules]):
    o, _ = shipped_plus
    check_opening(o)
    assert {t.id for t in o.triggers} >= {"t_find_3", "t_find_5"}


def test_the_skill_checks_cover_the_new_row_from_the_trips_first_card(shipped_plus: tuple[Opening, Rules]):
    o, rules = shipped_plus
    assert "t_lore" in mixed_skills(rules), "the trip is a hands card that trains it, so the row is read to the top"
    assert unpaid_markers(o, rules) == [] and runaway(rules) == [] and unmarked_levels(o, rules) == []


def test_a_row_left_short_of_the_top_is_found_for_the_trips_skill(shipped_opening: Opening):
    top = top_level(to_rules(shipped_opening))
    o, rules = loaded(shipped_opening, old='t_pays_lore = "faster"', new='t_pays_lore = "faster"')
    short = o.model_copy(update={"skills": [s.model_copy(update={"levels": s.levels[:-1]}) if s.id == "t_lore" else s
                                            for s in o.skills]})
    assert unmarked_levels(o, rules) == [] and unmarked_levels(short, rules) == [f"t_lore {top}"]


def test_a_twin_adding_the_same_to_the_count_passes_the_player_only_check(shipped_plus: tuple[Opening, Rules]):
    o, _ = shipped_plus
    assert any(s.tally and s.id == "t_trips" for s in o.stores)
    check_player_only(o)


def test_a_twin_adding_something_else_to_the_count_fails_the_player_only_check(shipped_opening: Opening):
    twin = 'outcome = { stores = [{ store = "t_ore", items = 1 }, { store = "t_trips", items = 1 }] }\ntwin_of'
    with pytest.raises(ValueError, match="card t_scout_trip: adds to a tally store differently from its twin_of t_trip"):
        loaded(shipped_opening, old=twin, new=twin.replace('"t_trips", items = 1', '"t_trips", items = 2'))


def test_a_twin_leaving_the_count_out_fails_the_player_only_check(shipped_opening: Opening):
    twin = 'outcome = { stores = [{ store = "t_ore", items = 1 }, { store = "t_trips", items = 1 }] }\ntwin_of'
    with pytest.raises(ValueError, match="adds to a tally store differently"):
        loaded(shipped_opening, old=twin, new=twin.replace(', { store = "t_trips", items = 1 }', ""))


NO_SCOUT = ("value = 100 }", "value = 999999 }")


def hands_trip(r: Rules, share: int) -> Save:
    """A new save at 200 s, past the scout's arrival, with the hands' trip alone in the mix at `share` of the hands."""
    mix = Mix(MixId("trip_only"), (CardShare(TRIP, share),))
    s = advance(new_save(r), r, 200)
    return decide(decide(s, r, 200, SaveMix(mix)), r, 200, SwitchMix(mix.id))


def value(s: Save, store: StoreId) -> int:
    return value_at(next(x.segment for x in s.stores if x.store == store), s.time)


def first_second(held: Callable[[int], bool], lo: int, hi: int) -> int:
    """The first whole second in (lo, hi] where a predicate that only goes from false to true holds."""
    assert held(hi) and not held(lo)
    while hi - lo > 1:
        mid = (lo + hi) // 2
        lo, hi = (lo, mid) if held(mid) else (mid, hi)
    return hi


def count_rate(shipped: Opening, share: int | None, scout: bool) -> int:
    """The count store's rate with the hands' trip at `share` (or off) and the scout's twin running (or not)."""
    _, r = loaded(shipped, *(("", "") if scout else NO_SCOUT))
    s = hands_trip(r, share) if share else advance(new_save(r), r, 200)
    return next(x.segment.rate for x in advance(s, r, 1000).stores if x.store == COUNT)


@pytest.mark.parametrize(("share", "scout"), [(BP, True), (BP // 2, True), (BP // 3, True), (BP, False), (None, True)])
def test_the_nth_find_lands_the_second_the_count_reaches_n_however_it_is_split(
        shipped_opening: Opening, share: int | None, scout: bool):
    """The hands' trip at `share` and the twin on its lane (or either alone) add to one count; the find on n lands the
    second that count first reaches n, not a second sooner or later, whichever card's work made it."""
    _, r = loaded(shipped_opening, *(("", "") if scout else NO_SCOUT))

    def at(t: int) -> Save:
        s = hands_trip(r, share) if share else advance(new_save(r), r, 200)
        return advance(s, r, t)

    for n, relics_then in ((3, 1), (5, 3)):
        landed = first_second(lambda t: value(at(t), StoreId("t_relics")) >= relics_then * QUANTITY_SCALE, 200, 40_000)
        assert value(at(landed), COUNT) >= n * QUANTITY_SCALE > value(at(landed - 1), COUNT)


def test_the_count_is_the_sum_of_what_each_card_adds(shipped_opening: Opening):
    """Alone the hands' trip adds at one rate and the twin at another; together, and at any share between, the count's
    rate is the shares' sum, so how the work is split between them cannot move a find except through the sum."""
    hands, twin = count_rate(shipped_opening, BP, False), count_rate(shipped_opening, None, True)
    assert hands > 0 < twin and hands != twin
    assert count_rate(shipped_opening, BP, True) == hands + twin
    assert count_rate(shipped_opening, BP // 2, True) == hands // 2 + twin


def test_a_trip_whose_materials_sit_at_their_caps_keeps_running_and_counting(shipped_plus: tuple[Opening, Rules]):
    """The ore is at its cap and nothing refills the pool, so the full rule (engine DESIGN, "FULL OUTPUT") reads the trip:
    its count store has room, so it is no fully-stopped card and its inputs go on paying for a count."""
    _, r = shipped_plus
    s = advance(hands_trip(r, BP), r, 200 + 5 * 600)
    card = next(c for c in view(s, r).cards if c.card == TRIP)
    assert card.run != RunKind.PAUSED
    assert completions(s, r, TRIP) >= 2 and value(s, COUNT) >= 2 * QUANTITY_SCALE
    assert value(s, ORE) == 5 * QUANTITY_SCALE, "the ore stayed at its cap"


def test_without_a_count_store_the_same_trip_pauses_full(shipped_opening: Opening):
    """The control: the trip's outcome holds the ore alone, which is at its cap, so every output is full and it pauses."""
    count = ', { store = "t_trips", items = 1 }'
    _, r = loaded(shipped_opening, old=count, new="", count=2)
    s = advance(hands_trip(r, BP), r, 200 + 5 * 600)
    assert next(c for c in view(s, r).cards if c.card == TRIP).run == RunKind.PAUSED
