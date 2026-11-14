"""A refused card shows why on its face, on the saves week one's typical route plays through days four to six
(docs/decisions/principles.md, "Progress is stated, never hinted"): each unmet require of a card on the panel is one
the page draws from the served view and content, a store the player has been shown as its have/need, a level or a
step as its row, a clock with a part of the day as when it opens, and anything else only as the card's countdown.
The content-wide check is tests/opening/test_requires_shown.py; this one reads real saves."""
import pytest

from ashfall_app.api.content_models import StoreInfo
from ashfall_app.api.service import Game
from ashfall_app.engine import AtLeast, CardCount, Condition, SkillLevel, StoreValue, UnlockKind, view
from ashfall_app.engine.index import index
from ashfall_app.engine.viewparts import CardView
from ashfall_app.engine.work import unmet_conditions
from ashfall_app.opening.renames import load_renames
from ashfall_app.opening.schema import Opening
from ashfall_app.saves.ruleset import ruleset
from tests.daytwo.player import DayTwoPlayer
from tests.daytwo.conftest import PLAY_TIMEOUT_S

pytestmark = [pytest.mark.playthrough, pytest.mark.timeout(PLAY_TIMEOUT_S)]


@pytest.fixture(scope="module")
def stores(shipped_opening: Opening) -> dict[str, StoreInfo]:
    content = Game(shipped_opening, ruleset(shipped_opening, load_renames(), "dev", 1)).content()
    return {s.store: s for s in content.store_infos}


def drawn(cond: Condition, card: CardView, seen: set[str], stores: dict[str, StoreInfo]) -> bool:
    if card.blocker is not None and card.blocker.ready_at is not None:
        return True   # the countdown
    if not isinstance(cond, AtLeast):
        return False
    if isinstance(cond.subject, (SkillLevel, CardCount)):
        return True
    if not isinstance(cond.subject, StoreValue):
        return False
    store = cond.subject.store
    return store in seen or getattr(stores[store], "clock", None) is not None


def refused_unshown(p: DayTwoPlayer, stores: dict[str, StoreInfo]) -> list[str]:
    """`card: require` once per card and require left undrawn on any save from B5 on."""
    found: dict[str, None] = {}
    for s, _ in p.history:
        if s.time < p.landed_at["B5"]:
            continue
        v = view(s, p.rules)
        seen = {u.id for u in v.unlocked if u.kind is UnlockKind.STORE}
        for card in v.cards:
            if card.blocker is None:
                continue
            requires = index(p.rules).cards[card.card].requires
            for cond in unmet_conditions(s, p.rules, card.card):
                if cond in requires and not drawn(cond, card, seen, stores):
                    found[f"{card.card}: {cond}"] = None
    return list(found)


@pytest.mark.xfail(strict=True, reason="#59: sit_up_5 waits all day on its night with nothing on its face")
@pytest.mark.parametrize("week_route", ["typical"], indirect=True)
def test_a_refused_card_shows_why_on_its_face(week_route: tuple[str, DayTwoPlayer], stores: dict[str, StoreInfo]):
    _, p = week_route
    found = refused_unshown(p, stores)
    assert not found, "\n".join(found)
