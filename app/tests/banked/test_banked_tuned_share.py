"""The player's remembered share (tests/dayone/sinks.py, tuned_share) is only ever the answer the full search gives: on the
fixture chapter's mixed trip, whatever share was remembered, and on a monotone preview for every remembered share."""
import pytest

from ashfall_app.engine import Save
from tests.banked.chapter import CHAPTER, rules
from tests.banked.play import play
from tests.dayone.player import sinks
from tests.dayone.player.sinks import SINKS, TUNE_STEP_BP, Trip

H = 3600
STEP = TUNE_STEP_BP


@pytest.fixture(name="at")
def _at() -> tuple[Save, Trip]:
    p = play(((0, 3 * H),), SINKS["typical"], 3 * H)
    return p.save, CHAPTER.trips[0]


def fresh(save: Save, trip: Trip, top: int) -> int:
    sinks.TUNED.clear()
    return sinks.tuned_share(rules(), save, trip, None, top)


def test_a_remembered_share_never_changes_the_answer(at: tuple[Save, Trip]):
    save, trip = at
    tops = range(STEP, trip.share_bp + 1, 7 * STEP)
    answers = {top: fresh(save, trip, top) for top in tops}
    assert len(set(answers.values())) > 1, "the fixture's preview must stop the share somewhere, or it proves nothing"
    for top in tops:
        for remembered in range(0, trip.share_bp + 2 * STEP, STEP):
            sinks.TUNED[(trip.card, True)] = remembered
            assert sinks.tuned_share(rules(), save, trip, None, top) == answers[top], (top, remembered)


@pytest.mark.parametrize("edge", range(0, 9))
def testconfirmed_agrees_with_the_search_on_a_monotone_preview(edge: int):
    """`holds` true up to `edge` steps: every remembered share and top either goes to the full search or agrees with it."""
    def holds(share: int) -> bool:
        return share <= edge * STEP
    seen = 0
    for top in range(STEP, 8 * STEP + 1, STEP // 2):
        want = sinks.searched(top, holds)
        for last in (None, *range(0, 9 * STEP + 1, STEP // 2)):
            got = sinks.confirmed(last, top, holds)
            seen += got is not None
            assert got in (None, want), (edge, top, last)
    assert seen, "the shortcut never confirmed anything"
