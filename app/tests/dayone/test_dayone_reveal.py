"""The reader of what the opening's screen draws (screen.py; docs/decisions.md, "The screen arrives when it means
something") can see a mechanic arrive: the readout (report.py) lists the Ashfall-specific mechanics drawn in the first
five minutes of the human-paced player's day, and a chip drawn the moment its store crosses is one more."""
import pytest

from tests.dayone.conftest import PLAY_TIMEOUT_S
from tests.dayone.human import HumanPlayer
from tests.dayone.human_flags import Session
from tests.dayone.screen import FIRST_S, chip_after, early

Run = tuple[HumanPlayer, list[Session]]


@pytest.mark.playthrough
@pytest.mark.timeout(PLAY_TIMEOUT_S)
def test_a_chip_drawn_as_soon_as_it_is_latched_is_one_more_mechanic(human_run: Run):
    """The plant: every chip drawn the moment its store crosses, whether or not it is unlocked or its cure is out."""
    p, _ = human_run
    assert any(save.time > FIRST_S for save, _ in p.history), "the play reaches past the window"
    latched = {"chips"} if any(any(save.chips) for save, _ in p.history if save.time <= FIRST_S) else set[str]()
    assert len(early(p, {}) | latched) > len(early(p, chip_after()))
