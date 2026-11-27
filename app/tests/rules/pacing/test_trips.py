"""An expedition's pieces on fixtures/trips.toml merged after the shipped chapters (week-four-plan item 5; engine design/banked-time.txt
"BANKED TIME"): a hands trip and its town twin adding to one count, finds on that count, and a skill whose first card is the
trip. What the loader and its checks accept, what the player-only check refuses, and the engine's reading: the nth find
lands the instant the nth trip completes however the count is split, and a trip whose materials sit at their caps keeps
running and counting."""
import tempfile
from pathlib import Path

import pytest

from ashfall_app.engine import (
    BP, QUANTITY_SCALE, CardId, CardShare, Mix, MixId, RunKind, Rules, Save, Segment, SaveMix, StoreId, SwitchMix, advance, value_at, decide, new_save, view,
)
from ashfall_app.engine.core.segments import reach_time
from ashfall_app.engine.loop.work import completions
from ashfall_app.rules.checks.run import check_opening
from ashfall_app.rules.checks.people.player_checks import check_player_only
from ashfall_app.rules.schema import Opening, merge_chapters, to_rules
from tests.dayone.pacing.growth import runaway
from tests.rules.play.blank_levels import mixed_skills, top_level, unmarked_levels
from tests.rules.pacing.test_level_pays import unpaid_markers
from tests.rules.pacing.test_second_skill import rows

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "trips.toml"
TRIP, TWIN, COUNT, ORE, RELIC = CardId("t_trip"), CardId("t_scout_trip"), StoreId("t_trips"), StoreId("t_ore"), StoreId("t_relics")
H = 3600


def loaded(shipped: Opening, old: str = "", new: str = "", count: int = 1,
           more: tuple[tuple[str, str, int], ...] = ()) -> tuple[Opening, Rules]:
    top = top_level(to_rules(shipped))
    text = FIXTURE.read_text()
    for a, b, n in ((old, new, count), *more) if old else more:
        assert text.count(a) == n, f"anchor is not unique: {a!r}"
        text = text.replace(a, b)
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


@pytest.fixture(scope="module")
def without_scout(shipped_opening: Opening) -> Rules:
    """The same chapter with the scout arriving long after every probe below."""
    return loaded(shipped_opening, *NO_SCOUT)[1]


def count_segment(s: Save, r: Rules, at: int) -> Segment:
    """The count's segment at `at`."""
    return next(x.segment for x in advance(s, r, at).stores if x.store == COUNT)


def reached_at(s: Save, r: Rules, target: int) -> int:
    """The second the count first holds `target`: the segment's exact reach time, re-read at the second before it until
    the rate holds across it (a level, or a completion, can change the rate on the way)."""
    at = 200
    while True:
        landed = reach_time(count_segment(s, r, at), target)
        assert landed is not None
        if landed - 1 <= at:
            return landed
        at = landed - 1


@pytest.mark.parametrize(("share", "scout"), [(BP, True), (BP // 2, True), (BP // 3, True), (BP, False), (None, True)])
def test_the_nth_find_lands_the_second_the_count_reaches_n_however_it_is_split(
        shipped_plus: tuple[Opening, Rules], without_scout: Rules, share: int | None, scout: bool):
    """The hands' trip at `share` and the twin on its lane (or either alone) add to one count; the find on n lands the
    second that count first reaches n (the segment's exact reach time), not a second sooner or later, whichever card's
    work made it."""
    r = shipped_plus[1] if scout else without_scout
    s = hands_trip(r, share) if share else advance(new_save(r), r, 200)
    for n, relics_then in ((3, 1), (5, 3)):
        landed = reached_at(s, r, n * QUANTITY_SCALE)
        assert value(advance(s, r, landed - 1), RELIC) < relics_then * QUANTITY_SCALE
        assert value(advance(s, r, landed), RELIC) >= relics_then * QUANTITY_SCALE


def test_the_count_is_the_sum_of_what_each_card_adds(shipped_plus: tuple[Opening, Rules], without_scout: Rules):
    """Alone the hands' trip adds at one rate and the twin at another; together, and at any share between, the count's
    rate is the shares' sum, so how the work is split between them cannot move a find except through the sum."""
    r = shipped_plus[1]

    def rate(rules: Rules, share: int | None) -> int:
        s = hands_trip(rules, share) if share else advance(new_save(rules), rules, 200)
        return count_segment(s, rules, 1100).rate

    hands, twin = rate(without_scout, BP), rate(r, None)
    assert hands > 0 < twin and hands != twin
    assert rate(r, BP) == hands + twin
    assert rate(r, BP // 2) == hands // 2 + twin


def test_a_trip_whose_materials_sit_at_their_caps_keeps_running_and_counting(shipped_plus: tuple[Opening, Rules]):
    """The ore is at its cap and nothing refills the pool, so the full rule (engine design/full-output.txt, "FULL OUTPUT") reads the trip:
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
    finds = ('id = "t_trips", value =', 'id = "t_ore", value =', 2)
    _, r = loaded(shipped_opening, old=count, new="", count=2, more=(finds,))
    s = advance(hands_trip(r, BP), r, 200 + 5 * 600)
    assert next(c for c in view(s, r).cards if c.card == TRIP).run == RunKind.PAUSED
