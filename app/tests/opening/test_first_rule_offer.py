"""Every route meets the rule's lesson in the opening (docs/design/opening-screen.md, "Lessons"): a rule offer shows
before the end, after the first mix and before any rule, which is when the lesson may start. The ledger's inline
offers carry it, so the strip's rest offer, which a player who mixed rest never meets, is not the only way in."""
import pytest

from ashfall_app.engine import SaveMix, SetOrders
from tests.opening.afterend import AfterEndPlayer
from tests.opening.routes import plays

pytestmark = pytest.mark.playthrough


@pytest.mark.parametrize("a_route", plays(), indirect=True)
def test_a_rule_offer_shows_in_the_opening_while_the_rule_lesson_may_start(a_route: AfterEndPlayer):
    p = a_route
    offer = next((n.at for n in p.news if n.thing.startswith("order_card:")), None)
    mix = next((t for t, _, v in p.decisions if isinstance(v, SaveMix)), None)
    rule = next((t for t, _, v in p.decisions if isinstance(v, SetOrders)), None)
    print(f"seed {p.seed}: first mix {mix}s, first rule offer {offer}s, first rule {rule}s, end {p.end_at}s")
    assert offer is not None and p.end_at is not None and offer < p.end_at
    assert mix is not None and mix < offer
    assert rule is None or rule >= offer
