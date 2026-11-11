"""The simulator's offer policy on a kinded test chapter (fixtures/askkinds.toml; tests/dayone/sinks.py, answer_offers):
it answers the kind's first offer by hand, and only then sets the kind's rule, with the role of the answer it gave; the
rule answers the second offer; before the first offer is answered nothing is set ahead."""
from functools import cache
from pathlib import Path

import pytest

from ashfall_app.engine import (
    AfterTime, AnswerId, AnswerKind, AnswerOffer, KindId, OfferId, Order, RoleId, Rules, Save, SetOrders, advance,
    decide, new_save, view,
)
from ashfall_app.opening.schema import CHAPTERS, OPENING, load_opening, to_rules
from tests.dayone.sinks import answer_offers

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "askkinds.toml"
ANSWERS = ((OfferId("q_first"), AnswerId("q_first_no")), (OfferId("q_second"), AnswerId("q_second_no")))


@cache
def rules() -> Rules:
    return to_rules(load_opening(OPENING, (*CHAPTERS, FIXTURE)))


@pytest.fixture(scope="module", autouse=True)
def built() -> Rules:
    """The fixture chapter's rules, built in setup so no test's timed call pays for loading them."""
    return rules()


def step(save: Save, rule: bool = True):
    r = rules()
    return answer_offers(view(save, r), r, save.orders, ANSWERS, rule)


def test_nothing_is_set_before_the_kinds_first_offer_is_answered():
    save = advance(new_save(rules()), rules(), 50)
    assert step(save) is None


def test_the_first_offer_is_answered_by_hand_and_then_the_rule_is_set_with_the_answers_role():
    r = rules()
    save = advance(new_save(r), r, 150)
    assert step(save) == ("decision", (AnswerOffer(OfferId("q_first"), AnswerId("q_first_no")),))
    save = decide(save, r, 150, AnswerOffer(OfferId("q_first"), AnswerId("q_first_no")))
    rule = Order(AfterTime(0), AnswerKind(KindId("q_ask"), RoleId("no")))
    assert step(save) == ("decision", (SetOrders((*save.orders, rule)),))
    assert step(save, rule=False) is None   # a route that sets no rule leaves it
    save = decide(save, r, 150, SetOrders((*save.orders, rule)))
    assert step(save) is None
    later = advance(save, r, 250)
    assert {o.offer: o.answer for o in view(later, r).offers} == {OfferId("q_first"): AnswerId("q_first_no"), OfferId("q_second"): AnswerId("q_second_no")}
