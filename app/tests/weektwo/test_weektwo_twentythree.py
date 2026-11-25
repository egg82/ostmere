"""Day twenty-three's checks on its played routes (docs/design/week-four-plan.md, items 3, 7 and 10; verdicts.py): each
push route plays from B19's visit to B20's, week four's second chapter and the edge of written content; B20 lands at
A39's finish, which opens at dawn 25; the post is built by its order card; O-book's book is made on the answer that
queues it and on the one that only shows it, tapped later; every chip shown has a cure; the babysitter ends level with
the whenever player from the visit before B19's to an hour past B20; and typical's save at day twenty-two's end, written
under the rules without day twenty-three, loads under today's and plays on with nobody deciding. The rhythm is the
readouts' (test_weektwo_readouts.py). Ids only (CLAUDE.md, "Never spoil the owner")."""
import pytest

from ashfall_app.engine import AnswerOffer, CardId, Unlock, UnlockKind
from ashfall_app.engine.work import completions
from tests.daythree.content import rules3
from tests.daytwo.conftest import PLAY_TIMEOUT_S
from tests.daytwo.player import DayTwoPlayer
from tests.dayone.parity import Measured, compare
from tests.weektwo.rebased import Rebased, fired, rules22
from tests.weektwo.routes import TWENTYTHREE_PUSH_ROUTES

pytestmark = [pytest.mark.playthrough, pytest.mark.timeout(PLAY_TIMEOUT_S)]
Route = tuple[str, DayTwoPlayer]
A39_READY_S = 576 * 3600
"""The season's seventy-second hour on the calendar (week-four-numbers.md, "Landing bands")."""
BOOK_GIVEN = Unlock(UnlockKind.FEATURE, "book_given")


def test_a_save_from_day_twenty_twos_end_loads_under_day_twenty_three_and_plays_on(rebased_twentytwo: Rebased):
    r = rebased_twentytwo
    assert fired(r.before, rules22(), "t_b19"), "the replay under day twenty-two's rules reached B19"
    assert fired(r.later, rules3(), "t_named"), "the stranger is named a day on"
    assert not fired(r.later, rules3(), "t_b20"), "B20 waits on A39, which nobody set out on"


@pytest.mark.parametrize("twentythree_route", TWENTYTHREE_PUSH_ROUTES, indirect=True)
def test_the_route_plays_day_twenty_three_to_b20(twentythree_route: Route):
    name, p = twentythree_route
    assert p.stop_beat() == "B20" and "B20" in p.seen_at, f"{name} saw B20"
    assert {"SL31", "I5", "I6", "O-book", "SL32", "I7", "SL33", "A39"} <= set(p.landed_at), name


@pytest.mark.parametrize("twentythree_route", TWENTYTHREE_PUSH_ROUTES, indirect=True)
def test_b20_lands_at_a39s_finish_after_its_dawn_and_the_post_by_its_order(twentythree_route: Route):
    name, p = twentythree_route
    start = p.history[0][0].time
    assert p.landed_at["B20"] - start >= A39_READY_S, f"{name}: A39 opens at dawn 25"
    assert completions(p.save, p.rules, CardId("post")) >= 1, f"{name}: the post's first stage, by its order card"


@pytest.mark.parametrize("twentythree_route", ["typical", "sharp"], indirect=True)
def test_the_book_is_made_on_either_answer(twentythree_route: Route):
    """Typical makes the book on the answer that queues it; sharp says not now and taps it later (item 3)."""
    name, p = twentythree_route
    answers = {v.answer for _, _, v in p.decisions if isinstance(v, AnswerOffer) and str(v.offer) == "o_book"}
    assert answers == {"o_book_make" if name == "typical" else "o_book_later"}, name
    assert BOOK_GIVEN in p.save.unlocked, f"{name}: the book given"


def test_every_chip_shown_in_day_twenty_three_has_a_cure(twentythree_cures: list[str]):
    assert twentythree_cures == []


def test_the_babysitter_ends_level_across_day_twenty_three(two_am_twentythree_run: tuple[Measured, Measured]):
    assert compare(*two_am_twentythree_run) == []
