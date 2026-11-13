"""A tap of an unready card through the saves service and the API's Step: answered at once with the card's failed line
at the tap's instant, the card named as the failed tap (Played.failed, Step.failed_tap), no lane holding it, and
written as a decision like any other (CONTRACT.txt, ENDPOINTS, the decisions route)."""
import pytest

from ashfall_app import engine as e
from ashfall_app.api.service import Game
from ashfall_app.saves.interface import Played, Ruleset
from ashfall_app.saves.service import PgSaves
from tests.fake_clock import FakeClock
from tests.opening.playthrough import opening


def to_first_unready(saves: PgSaves, account: int, save_id: int, played: Played, clock: FakeClock,
                     rs: Ruleset) -> tuple[Played, e.CardId]:
    """Tap the first ready card on a free lane until some card on a free lane is unready; that card."""
    lane_of = {c.id: c.lane for c in rs.rules.cards}
    for _ in range(200):
        free = {ls.lane for ls in played.save.lanes if ls.card is None}
        cards = [c for c in e.view(played.save, rs.rules).cards if lane_of[c.card] in free]
        unready = next((c.card for c in cards if c.blocker is not None), None)
        if unready is not None:
            return played, unready
        ready = next((c.card for c in cards if c.blocker is None), None)
        if ready is not None:
            played = saves.decide(account, save_id, e.TapCard(ready), after=played.decisions)
            continue
        nxt = e.next_event(played.save, rs.rules)
        assert nxt is not None
        clock.tick(nxt.time - played.save.time)
        played = saves.advance(account, save_id)
    raise AssertionError("no card turned unready")


@pytest.fixture
def at_first_unready(saves: PgSaves, account: int, clock: FakeClock, rs: Ruleset) -> tuple[int, Played, e.CardId]:
    """A new save played on until some card on a free lane is unready, in setup: the save id, the save, that card."""
    info, played = saves.create(account)
    played, card = to_first_unready(saves, account, info.save_id, played, clock, rs)
    return info.save_id, played, card


def test_an_unready_tap_answers_at_once_with_no_line_and_names_the_card(
        saves: PgSaves, account: int, clock: FakeClock, rs: Ruleset, at_first_unready: tuple[int, Played, e.CardId]):
    save_id, played, card = at_first_unready
    clock.tick(1)
    failed = saves.decide(account, save_id, e.TapCard(card), after=played.decisions)
    assert failed.failed == card and failed.decisions == played.decisions + 1
    assert [ln for ln in failed.lines if ln.card == card] == []
    assert all(ls.card != card for ls in failed.save.lanes)
    assert failed.save == e.advance(played.save, rs.rules, failed.save.time)
    step = Game(opening(), rs).step(failed)
    assert step.failed_tap == card
    clock.tick(1)
    assert saves.decide(account, save_id, e.TapCard(card), after=failed.decisions).failed == card
