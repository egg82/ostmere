"""Week one's plays leave a copy for the job that holds the saved week one to them (tests/weekone_saved), so that job plays
nothing and week one's job waits on nothing. The export is written and read back in the `week_export` fixture's setup."""
import pytest

from tests.daytwo.conftest import PLAY_TIMEOUT_S
from tests.weektwo.routes import SAVED

pytestmark = [pytest.mark.playthrough, pytest.mark.timeout(PLAY_TIMEOUT_S)]


@pytest.mark.parametrize("week_route", SAVED["week1"], indirect=True)
def test_week_ones_play_is_exported_and_loads_back_equal(week_export: list[str]):
    assert week_export == []
