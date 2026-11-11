"""Every subject the page has shown in a chapter of week two and day fifteen is one the full condition editor offers
(tests/rule_subjects.py; week one's own is test_weekone_rule_subjects.py). Each chapter's typical play is read from
the save it starts on, so a chapter costs its own play alone. Ids only (CLAUDE.md, "Never spoil the owner")."""
import pytest

from ashfall_app.api import content_models as cm
from ashfall_app.api import models as w
from tests.daytwo.conftest import PLAY_TIMEOUT_S
from tests.daytwo.player import DayTwoPlayer
from tests import rule_subjects
from tests.weektwo.routes import start

pytestmark = [pytest.mark.playthrough, pytest.mark.timeout(PLAY_TIMEOUT_S)]
Route = tuple[str, DayTwoPlayer]
TYPICAL = ["typical"]


def chapter_views(chapter: str, route: Route) -> list[w.View]:
    """The wire Views of the chapter's own saves: from the last save of the play it starts on."""
    name, p = route
    begun = len(start(chapter, name, 0).history)
    assert 0 < begun < len(p.history), f"{chapter}: no saves of its own"
    return rule_subjects.wire(p.history[begun - 1:])


@pytest.fixture(scope="session")
def content() -> cm.Content:
    return rule_subjects.content()


@pytest.fixture(scope="session")
def eight_views(eight_route: Route) -> list[w.View]:
    return chapter_views("eight", eight_route)


@pytest.fixture(scope="session")
def nine_views(nine_route: Route) -> list[w.View]:
    return chapter_views("nine", nine_route)


@pytest.fixture(scope="session")
def eleven_views(eleven_route: Route) -> list[w.View]:
    return chapter_views("eleven", eleven_route)


@pytest.fixture(scope="session")
def twelve_views(twelve_route: Route) -> list[w.View]:
    return chapter_views("twelve", twelve_route)


@pytest.fixture(scope="session")
def fifteen_views(fifteen_route: Route) -> list[w.View]:
    return chapter_views("fifteen", fifteen_route)


@pytest.mark.parametrize("eight_route", TYPICAL, indirect=True)
def test_every_subject_shown_on_day_eight_is_offered(content: cm.Content, eight_views: list[w.View]):
    assert rule_subjects.unoffered(content, eight_views) == []


@pytest.mark.parametrize("nine_route", TYPICAL, indirect=True)
def test_every_subject_shown_on_day_nine_is_offered(content: cm.Content, nine_views: list[w.View]):
    assert rule_subjects.unoffered(content, nine_views) == []


@pytest.mark.parametrize("eleven_route", TYPICAL, indirect=True)
def test_every_subject_shown_on_day_eleven_is_offered(content: cm.Content, eleven_views: list[w.View]):
    assert rule_subjects.unoffered(content, eleven_views) == []


@pytest.mark.parametrize("twelve_route", TYPICAL, indirect=True)
def test_every_subject_shown_on_day_twelve_is_offered(content: cm.Content, twelve_views: list[w.View]):
    assert rule_subjects.unoffered(content, twelve_views) == []


@pytest.mark.parametrize("fifteen_route", TYPICAL, indirect=True)
def test_every_subject_shown_on_day_fifteen_is_offered(content: cm.Content, fifteen_views: list[w.View]):
    assert rule_subjects.unoffered(content, fifteen_views) == []
