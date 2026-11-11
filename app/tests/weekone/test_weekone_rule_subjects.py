"""Every subject the page has shown in the week is one the full condition editor offers (rule_subjects.py): a player
who meets a need and goes to write its rule finds it there. Over week one's typical play and the babysitter's (whose
lost fight shows the hurt chip), from the first save."""
import pytest

from ashfall_app.api import content_models as cm
from ashfall_app.api import models as w
from tests.daytwo.conftest import PLAY_TIMEOUT_S
from tests import rule_subjects
from tests.weekone.routes import week1

pytestmark = [pytest.mark.playthrough, pytest.mark.timeout(PLAY_TIMEOUT_S)]


@pytest.fixture(scope="module")
def content() -> cm.Content:
    return rule_subjects.content()


@pytest.fixture(scope="module", params=["typical", "babysitter"])
def views(request: pytest.FixtureRequest) -> list[w.View]:
    return rule_subjects.wire(week1(request.param).history)


def test_every_subject_shown_in_the_week_is_offered(content: cm.Content, views: list[w.View]):
    assert rule_subjects.unoffered(content, views) == []


def test_the_check_reads_every_kind_of_subject(content: cm.Content, views: list[w.View]):
    """Control: the play shows a chip, a store line, a skill, the Camp and a task, so the check is not looking at
    nothing; and a view with a chip drawn that the save has not marked shown is a problem."""
    kept = {c for v in views for c in rule_subjects.drawn_chips(content, v)}
    lines = {s for v in views for s in rule_subjects.drawable_lines(content, v)}
    now = {s for v in views for s in rule_subjects.shown_now(content, v)}
    assert kept and lines and "camp" in now
    assert any(s.startswith("level:") for s in now) and any(s.startswith("count:") for s in now)
    planted = views[0].model_copy(update={"chips": ["cold"], "cards": []})
    assert rule_subjects.unoffered(content, [planted]) == ["chip:cold shown and not offered at minute 0"]
