"""Day two's engine parts on the wire (api/CONTRACT.txt, "A lane run by rules", "Offers"), on the test chapter
(tests/opening/fixtures/townsfolk.toml): the content's lane and offer infos, the view's lane order and offers, and
answer_offer as a decision and as an order verb, each a plain copy of the engine's."""
from functools import cache

import pytest

from ashfall_app import engine as e
from ashfall_app.api import content_models as cm
from ashfall_app.api import convert
from ashfall_app.api import models as w
from ashfall_app.api.service import Game
from ashfall_app.opening.schema import to_rules
from ashfall_app.saves.ruleset import ruleset
from tests.opening.test_townsfolk_loader import loaded

pytestmark = pytest.mark.usefixtures("townsfolk_opening")

ASK, YES, NO = e.OfferId("t_ask"), e.AnswerId("t_yes"), e.AnswerId("t_no")


@cache
def game() -> Game:
    return Game(loaded(), ruleset(loaded(), [], "test", 1))


def test_the_content_serves_the_ruled_lane_and_the_offer():
    content = game().content()
    lane = next(x for x in content.lane_infos if x.lane == "t_helper")
    assert lane.ruled and lane.later_labels == [
        cm.LaneLabel(after=w.Unlock(category=w.UnlockKind.FEATURE, id="t_named"), label_key="t_l_helper_named")]
    assert next(x for x in content.lane_infos if x.lane == "hands").ruled is False
    asked = [x for x in content.offer_infos if x.offer == "t_ask"]   # beside day two's offer
    assert asked == [cm.OfferInfo(offer="t_ask", text_key="t_o_ask", kind=None, line_keys=["t_l_asked"], answers=[
        cm.AnswerInfo(answer="t_yes", label_key="t_a_yes", cost_key="t_a_yes_cost", role=None, change_bp=[], gains=[]),
        cm.AnswerInfo(answer="t_no", label_key="t_a_no", cost_key="t_a_no_cost", role=None, change_bp=[], gains=[])])]


def test_the_view_serves_the_lane_order_and_the_open_offer():
    r = to_rules(loaded())
    s = e.advance(e.new_save(r), r, 100)
    wire = game().view(s)
    assert w.View.model_validate(wire.model_dump()) == wire
    lane = next(b for b in wire.lanes if b.lane == "t_helper")
    assert (lane.running_card, lane.order) == ("t_help_gather", 0)
    assert [(o.offer, o.answer, [(a.answer, a.card) for a in o.answers]) for o in wire.offers] == [
        ("t_ask", None, [("t_yes", "t_help_fetch"), ("t_no", "t_one_off")])]


def test_answer_offer_converts_as_a_decision_and_as_an_order_verb():
    r = to_rules(loaded())
    assert game().verb(w.AnswerOffer(offer="t_ask", answer="t_yes")) == e.AnswerOffer(ASK, YES)
    order = w.Order(when=w.AfterTime(at=0), then=w.AnswerOffer(offer="t_ask", answer="t_no"))
    verb = convert.verb(w.SetOrders(orders=[order]), r)
    assert verb == e.SetOrders((e.Order(e.AfterTime(0), e.AnswerOffer(ASK, NO)),))
    assert convert.order_verb(e.AnswerOffer(ASK, NO)) == order.then
