"""The journal on week one's played routes (api/CONTRACT.txt, "JOURNAL"): each days note is written at the instant its
beat lands, and each section's pages are written in content order, so content order is writing order. Ids only."""
import pytest

from ashfall_app.engine import Unlock, UnlockKind
from ashfall_app.opening.schema import Opening
from tests.daythree import content as c3
from tests.daytwo.conftest import PLAY_TIMEOUT_S
from tests.daytwo.player import DayTwoPlayer
from tests.weekone.routes import PUSH_ROUTES

pytestmark = [pytest.mark.playthrough, pytest.mark.timeout(PLAY_TIMEOUT_S)]
Route = tuple[str, DayTwoPlayer]

STEP_OF = {"B2": Unlock(UnlockKind.FEATURE, "ledger")}
"""Beats the routes' landings do not name, by an unlock only their step's finish adds (the fire lit)."""


def beat_at(p: DayTwoPlayer, beat: str) -> int | None:
    if beat in p.landed_at:
        return p.landed_at[beat]
    step = STEP_OF.get(beat)
    return None if step is None else p.unlocked_at.get(step)


def misplaced_notes(p: DayTwoPlayer, o: Opening) -> tuple[int, list[str]]:
    """(days notes checked, those not written at their beat's landing)."""
    days = {e.id for e in o.entries if e.section == "days"}
    checked, wrong = 0, list[str]()
    for n in (n for n in o.notes if n.entry in days):
        assert n.beat is not None
        at, written = beat_at(p, n.beat), p.unlocked_at.get(Unlock(UnlockKind.NOTE, n.id))
        if at is None and written is None:
            continue
        checked += 1
        if at != written:
            wrong.append(f"note {n.id}: beat {n.beat} at {at}, written at {written}")
    return checked, wrong


def out_of_order(p: DayTwoPlayer, o: Opening) -> list[str]:
    """Pages written before a page declared ahead of them in the same section."""
    wrong: list[str] = []
    for section in ("days", "creatures", "places"):
        times = [(e.id, p.unlocked_at.get(Unlock(UnlockKind.ENTRY, e.id))) for e in o.entries if e.section == section]
        written = [(eid, t) for eid, t in times if t is not None]
        wrong += [f"{b} at {tb} before {a} at {ta}" for (a, ta), (b, tb) in zip(written, written[1:]) if tb < ta]
        if any(t is None for _, t in times[:len(written)]):
            wrong.append(f"{section}: a page declared earlier was never written")
    return wrong


@pytest.mark.parametrize("week_route", PUSH_ROUTES, indirect=True)
def test_each_days_note_is_written_at_its_beats_landing(week_route: Route):
    name, p = week_route
    checked, wrong = misplaced_notes(p, c3.opening3())
    assert checked >= 5, f"{name}: only {checked} days notes were checked"
    assert wrong == [], name


@pytest.mark.parametrize("week_route", PUSH_ROUTES, indirect=True)
def test_each_sections_pages_are_written_in_content_order(week_route: Route):
    name, p = week_route
    assert out_of_order(p, c3.opening3()) == [], name


@pytest.mark.parametrize("week_route", ["typical"], indirect=True)
def test_a_note_moved_off_its_beat_and_a_page_out_of_order_are_found(week_route: Route):
    _, p = week_route
    o = c3.opening3()
    moved = o.model_copy(update={"notes": [n.model_copy(update={"beat": "B7"}) if n.id == "n_day_b2" else n
                                           for n in o.notes]})
    assert any("n_day_b2" in w for w in misplaced_notes(p, moved)[1])
    days = [e for e in o.entries if e.section == "days"]
    swapped = o.model_copy(update={"entries": [days[1], days[0], *(e for e in o.entries if e not in days[:2])]})
    assert out_of_order(p, swapped) != []
