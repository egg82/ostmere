"""The line state lists for the four chapter files (report.py, `--lines`): each file's keys are read against the typical
route, the ones that fired or showed have states, and a key no file carries is listed with none. A fight's pool keys
are drawn by the page per fight, which the plays never roll, so they never have a state and are not counted."""
import pytest

from tests.daythree import content as c3
from tests.daythree import lines
from ashfall_app.opening.fight_refs import fights
from ashfall_app.opening.schema import DAY_TWO
from tests.daytwo.conftest import PLAY_TIMEOUT_S
from tests.daytwo.player import DayTwoPlayer
from tests.weekone import report
from tests.weekone.routes import week1

pytestmark = [pytest.mark.playthrough, pytest.mark.timeout(PLAY_TIMEOUT_S)]


@pytest.fixture(scope="module")
def typical() -> DayTwoPlayer:
    return week1("typical")


@pytest.mark.parametrize("file", list(report.FILES))
def test_each_chapter_files_keys_have_states_on_the_typical_route(typical: DayTwoPlayer, file: str):
    keys = lines.chapter_keys(DAY_TWO.parent / file)
    beat = report.FILES[file]
    o = c3.opening3()
    found = lines.states({"typical": typical}, keys, o, {"typical": 1}, {"typical": typical.landed_at[beat]})
    pools = {k for _, f in fights(o) for k in (*f.won_line_keys, *f.lost_line_keys)}
    counted = [k for k in keys if k not in pools]
    assert len(found) == len(keys) > 0
    assert sum(1 for k in counted if found[k]) > len(counted) // 4, f"{file}: too few keys showed or fired"


def test_a_key_no_chapter_file_carries_has_no_state(typical: DayTwoPlayer):
    keys = lines.chapter_keys(DAY_TWO.parent / "day_four.toml")
    real = next(k for k, s in lines.states({"typical": typical}, keys, c3.opening3(), {"typical": 1},
                                           {"typical": typical.landed_at["B5"]}).items() if s)
    out = lines.states({"typical": typical}, (real, "no_such_key"), c3.opening3(), {"typical": 1}, {"typical": typical.landed_at["B5"]})
    assert out["no_such_key"] == set() and out[real]
