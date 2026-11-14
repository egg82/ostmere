"""The journal on week one's played routes (api/CONTRACT.txt, "JOURNAL"): each section's entry pages are written in
content order, so content order is writing order. Ids only."""
import pytest

from ashfall_app.engine import Unlock, UnlockKind
from ashfall_app.opening.journal_entries import Section
from ashfall_app.opening.schema import Opening
from tests.daythree import content as c3
from tests.daytwo.conftest import PLAY_TIMEOUT_S
from tests.daytwo.player import DayTwoPlayer
from tests.weekone.routes import PUSH_ROUTES

pytestmark = [pytest.mark.playthrough, pytest.mark.timeout(PLAY_TIMEOUT_S)]
Route = tuple[str, DayTwoPlayer]


def out_of_order(p: DayTwoPlayer, o: Opening) -> list[str]:
    """Pages written before a page declared ahead of them in the same section."""
    wrong: list[str] = []
    sections: tuple[Section, ...] = ("creatures", "places")
    for section in sections:
        times = [(e.id, p.unlocked_at.get(Unlock(UnlockKind.ENTRY, e.id))) for e in o.entries if e.section == section]
        written = [(eid, t) for eid, t in times if t is not None]
        wrong += [f"{b} at {tb} before {a} at {ta}" for (a, ta), (b, tb) in zip(written, written[1:]) if tb < ta]
        if any(t is None for _, t in times[:len(written)]):
            wrong.append(f"{section}: a page declared earlier was never written")
    return wrong


@pytest.mark.parametrize("week_route", PUSH_ROUTES, indirect=True)
def test_each_sections_pages_are_written_in_content_order(week_route: Route):
    name, p = week_route
    assert out_of_order(p, c3.opening3()) == [], name


@pytest.mark.parametrize("week_route", ["typical"], indirect=True)
def test_a_page_declared_ahead_of_a_written_one_and_never_written_is_found(week_route: Route):
    _, p = week_route
    o = c3.opening3()
    written = [e for e in o.entries if Unlock(UnlockKind.ENTRY, e.id) in p.unlocked_at]
    never = next(e for e in o.entries if e not in written)
    assert written, "the route writes a page"
    planted = o.model_copy(update={"entries": [never.model_copy(update={"section": written[0].section}), *written]})
    assert out_of_order(p, planted) != []
