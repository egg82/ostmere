"""The track's reach over week one's typical play (decisions/pacing.md, "A sink shows what it buys"): every card that lays
track fills the one store, a person's beside the hands', each at its own share; and each reach the hunt reads is on the
hunt's work exactly when the track laid has passed it."""
import pytest

from ashfall_app.engine import QUANTITY_SCALE as Q, CardId, CardShare, Mix, SaveMix, StoreId, explain_work, segment
from ashfall_app.rules.schema import load_opening
from tests.daytwo.conftest import PLAY_TIMEOUT_S
from tests.daytwo.player import DayTwoPlayer
from tests.weekone.routes import week1

pytestmark = [pytest.mark.playthrough, pytest.mark.timeout(PLAY_TIMEOUT_S)]
LAID, HUNT = StoreId("track_laid"), CardId("hunt_wolf")
HANDS, HERS, HER_FORAGE = "field_track", "n1_field_track", "n1_forage"
H = 3600


def laid(p: DayTwoPlayer) -> float:
    return segment(p.save, p.rules, LAID).start_value / Q


def runs(p: DayTwoPlayer) -> dict[str, int]:
    return {str(c.card): c.completions for c in p.view().cards if str(c.card) in (HANDS, HERS)}


def reaches() -> dict[str, int]:
    """Each modifier source a trigger on the track laid pays, with the amount it waits on, in whole items."""
    return {m.source: t.when.value for t in load_opening().triggers
            if t.when.subject_kind == "store" and t.when.id == str(LAID) for m in t.outcome.modifiers}


@pytest.fixture(scope="module")
def both_laying() -> tuple[dict[str, int], float, dict[str, int], float]:
    """Week one's end, the hands' mix laying track as played and the first person moved from foraging to her track
    card at her share, six game hours on: the runs and the track laid before and after."""
    p = week1("typical").fork()
    town = next(m for m in p.save.mixes if str(m.id) == "town:camp")
    moved = tuple(CardShare(CardId(HERS), c.share_bp) if isinstance(c, CardShare) and str(c.card) == HER_FORAGE else c
                  for c in town.components)
    assert moved != town.components
    before, laid_before = runs(p), laid(p)
    p.decide("decision", (SaveMix(Mix(town.id, moved)),))
    p.advance(p.save.time + 6 * H)
    return before, laid_before, runs(p), laid(p)


def test_both_runners_lay_track(both_laying: tuple[dict[str, int], float, dict[str, int], float]):
    before, _, after, _ = both_laying
    assert after[HANDS] > before[HANDS] and after[HERS] > before[HERS]


def test_the_track_laid_is_the_sum_of_every_runners_runs(both_laying: tuple[dict[str, int], float, dict[str, int], float]):
    """Each run lays one length, paid as its work is done, so the store differs from the whole runs by the two bars'
    progress at either end: under one length per runner."""
    before, laid_before, after, laid_after = both_laying
    total = sum(after[c] - before[c] for c in (HANDS, HERS))
    assert abs((laid_after - laid_before) - total) < 2


def test_each_reach_passed_is_on_the_hunts_work_and_no_other():
    p = week1("typical")
    on = {str(m.source) for m in explain_work(p.save, p.rules, HUNT).muls}
    have = laid(p)
    passed = {s for s, at in reaches().items() if at <= have}
    assert passed and len(passed) < len(reaches())   # the play is between two reaches, so both sides are checked
    assert {s for s in on if s in reaches()} == passed
