"""A play on (DayTwoPlayer.play_on) runs its schedule on past the new stop beat's target day. The schedule a saved end
carries was made for the chapters it was played through, so without that a later chapter's beat that lands after it
ends is never seen."""
from dataclasses import replace

import pytest

from tests.daythree import content as c3
from tests.daytwo import abs_band
from tests.daytwo.player import DayTwoPlayer
from tests.dayone.player.player import DayOnePlayer
from tests.dayone.player.schedules import schedule
from tests.weekone import content as w1
from tests.weekone.routes import HORIZON_S

STOP = "B25"
"""Week five's last spine beat, past the week-one schedule's horizon."""



def no_play(self: DayOnePlayer) -> None:
    """Day one's play on, skipped: the test reads the schedule the play would follow, not the play."""


@pytest.mark.parametrize("name",["typical", "lazy", "evenings", "whenever", "babysitter"])
def test_a_play_on_runs_the_schedule_past_its_stop_beats_target_day(name: str, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(DayOnePlayer, "play_on", no_play)
    target = abs_band.load_pace().targets[STOP] * abs_band.DAY_S
    p = DayTwoPlayer(c3.rules3(), seed=3, schedule=schedule(name, 3600, 3, HORIZON_S),
                     laters=(replace(w1.chapters()[-1], stop=STOP),))
    assert p.schedule.visits[-1].start + p.schedule.visits[-1].length < target
    p.play_on()
    last = p.schedule.visits[-1]
    assert last.start + last.length > target
