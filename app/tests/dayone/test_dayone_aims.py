"""Every aim the opening and day one declare is stated at some view of the human-paced player's day (screen.py), so each
one's `after` is content that really lands in play. The page reads every chapter's aims (later chapters' come after
day one's in content order), so the aim stated is read through them all; day two's own aims land in day two's play,
not this one. How many views state no aim is the readout's (report.py). Aims are named by id, never by their text."""
import pytest

from ashfall_app.opening.entries import UnlockEntry
from ashfall_app.opening.feature_entries import AimEntry
from tests.dayone.conftest import PLAY_TIMEOUT_S
from tests.dayone.human import HumanPlayer
from tests.dayone.human_flags import Session
from tests.dayone.screen import aimless, stated, unstated, views
from tests.opening.playthrough import day_one, opening

pytestmark = [pytest.mark.playthrough, pytest.mark.timeout(PLAY_TIMEOUT_S)]
Run = tuple[HumanPlayer, list[Session]]


def test_every_aim_is_stated_at_some_view(human_run: Run):
    p, _ = human_run
    assert "B3" in p.seen_at, "the play reaches B3"
    assert p.history[0][0].time == 0 and p.history[-1][0].time > p.seen_at["B3"], "the play spans the first screen to past B3"
    assert unstated(day_one().aims, stated(opening().aims, views(p))) == []


def test_the_readers_see_an_aim_never_stated_and_a_stretch_with_no_aim(human_run: Run):
    p, _ = human_run
    aims = day_one().aims
    unreached = [*aims, AimEntry(id="planted", text_key=aims[-1].text_key,
                                 after=UnlockEntry(unlock_kind="feature", id="never_unlocked"))]
    assert unstated(unreached, stated(unreached, views(p))) == ["planted"]
    late_first = [aims[0].model_copy(update={"after": aims[1].after}), *aims[1:]]
    assert len(aimless(stated(late_first, views(p)))) > len(aimless(stated(aims, views(p))))
