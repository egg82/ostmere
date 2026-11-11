"""The goal counters the readout prints (goals.goal_summary) read what they claim: goals at least goals.CHOICE_S out
that every setup reaches together count as undriven, goals a setup reaches sooner as driven (and a weighting that
decides the order as decided), and when no goal is that far out no choice is due."""
import pytest

from ashfall_app.engine import Rules, Save, view
from tests.dayone import goals
from tests.dayone.conftest import PLAY_TIMEOUT_S
from tests.dayone.player import DayOnePlayer
from tests.dayone.routes import day

pytestmark = [pytest.mark.playthrough, pytest.mark.timeout(PLAY_TIMEOUT_S)]


@pytest.fixture(scope="module")
def play() -> DayOnePlayer:
    return day("typical")


def _etas(monkeypatch: pytest.MonkeyPatch, out: int, sooner: str = "") -> None:
    """Every skill's next level `out` s away under any setup. `sooner` "one": half that under a one-card mix of the
    skill's own card; "first": also under any mix whose first card is the skill's own."""
    def fake(save: Save, rules: Rules, shares: tuple[tuple[str, int], ...]) -> dict[str, int | None]:
        own = {str(c.skill) for c in rules.cards if str(c.id) == shares[0][0]}
        quick: set[str] = own if sooner == "first" or (sooner == "one" and len(shares) == 1) else set()
        return {b.skill: save.time + (out // 2 if b.skill in quick else out) for b in view(save, rules).skills}
    monkeypatch.setattr(goals, "etas", fake)


def _summary(play: DayOnePlayer) -> goals.GoalSummary:
    found = goals.goal_summary(goals.goal_samples(play))
    assert found.choice_due, "the play has no goal far enough out to plant against"
    return found


def test_goals_far_out_arriving_together_under_every_setup_count_as_undriven(play: DayOnePlayer,
                                                                            monkeypatch: pytest.MonkeyPatch):
    _etas(monkeypatch, 2 * goals.CHOICE_S)
    found = _summary(play)
    assert found.undriven == found.choice_due and found.judged == 0


def test_goals_far_out_where_the_weighting_never_decides_count_as_undecided(play: DayOnePlayer,
                                                                           monkeypatch: pytest.MonkeyPatch):
    _etas(monkeypatch, 4 * goals.CHOICE_S, "one")
    found = _summary(play)
    assert found.undriven == 0 and found.judged > 0 and found.decided == 0


def test_goals_far_out_that_setup_and_weighting_decide_count_as_decided(play: DayOnePlayer,
                                                                       monkeypatch: pytest.MonkeyPatch):
    _etas(monkeypatch, 4 * goals.CHOICE_S, "first")
    found = _summary(play)
    assert found.undriven == 0 and found.judged > 0 and found.decided == found.judged


def test_goals_all_nearer_than_the_floor_are_no_choice_due(play: DayOnePlayer, monkeypatch: pytest.MonkeyPatch):
    _etas(monkeypatch, goals.CHOICE_S // 2)
    found = goals.goal_summary(goals.goal_samples(play))
    assert found.samples and found.choice_due == 0 and found.undriven == 0
