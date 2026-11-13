"""Feature cards: the dusk has none, since the night's real-time wait is taught by the clock lesson on the countdown it
explains (client game/lessons.ts, CLOCK). The edge's card is test_edge_card.py's."""
import pytest

from ashfall_app.opening.schema import Opening
from tests.opening.playthrough import opening


@pytest.fixture(scope="module", autouse=True)
def shipped() -> Opening:
    """The cached shipped opening."""
    return opening()


def card_of(feature: str):
    return next(f.card for f in opening().features if f.id == feature)


def test_the_dusk_has_no_card():
    assert card_of("keeps_going") is None


def test_the_clock_lessons_line_is_served_with_no_number_in_it():
    line = opening().text["ui.lesson.clock"]
    assert line and not any(ch.isdigit() for ch in line)
