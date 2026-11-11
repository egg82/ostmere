"""Two kinds of offer on a test chapter (fixtures/offerkinds.toml) merged after the shipped ones: one whose answers
start a card, one whose answers start nothing and install a modifier. The loader carries each answer's modifier, an
answer lands it in its target's explain() with the answer as source, and the simulator's policy answers both kinds by hand
(day two's own offer, a card kind, and a modifier kind; docs/design/day-three-plan.md, item 5; engine DESIGN.txt, "Offers")."""
from functools import cache
from pathlib import Path

import pytest

from ashfall_app.engine import (
    AnswerId, AnswerOffer, CardId, FlowKind, OfferId, Rules, Save, SourceId, StoreId, RateRef, advance, decide, explain,
    new_save, view,
)
from ashfall_app.opening.schema import CHAPTERS, OPENING, load_opening, to_rules
from tests.daytwo.content import GO, OFFER
from tests.daytwo.policy import Knobs2, answer

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "offerkinds.toml"
HEARTH = RateRef(CardId("k_hearth"), FlowKind.MAKE, StoreId("damp_wood"))


@cache
def rules() -> Rules:
    return to_rules(load_opening(OPENING, (*CHAPTERS, FIXTURE)))


@pytest.fixture(scope="module", autouse=True)
def built() -> Rules:
    """The fixture chapter's rules, built in setup so no test's timed call pays for loading them."""
    return rules()


def sources(save: Save) -> list[str]:
    return [str(m.source) for m in explain(save, rules(), HEARTH).muls]


def test_an_answers_modifier_is_in_its_targets_explain_with_the_answer_as_source():
    r = rules()
    shown = advance(new_save(r), r, 200)
    assert sources(shown) == []
    hers = decide(shown, r, 200, AnswerOffer(OfferId("k_bank"), AnswerId("k_hers")))
    assert sources(hers) == ["k_hers"]
    assert [m.amount_bp for m in explain(hers, r, HEARTH).muls] == [11000]
    his = decide(shown, r, 200, AnswerOffer(OfferId("k_bank"), AnswerId("k_his")))
    assert sources(his) == ["k_his"]


def test_the_card_kind_leaves_the_modifier_unset():
    r = rules()
    asked = decide(advance(new_save(r), r, 200), r, 200, AnswerOffer(OfferId("k_ask"), AnswerId("k_ask_no")))
    assert sources(asked) == []


def test_the_policy_answers_both_kinds_by_hand_when_shown_and_sets_no_order_ahead():
    r = rules()
    knobs = Knobs2(answer=GO, answer_order=True, other_answers=(("k_ask", "k_ask_yes"), ("k_bank", "k_his")))
    save = advance(new_save(r), r, 10)
    assert answer(view(save, r), r, save.orders, knobs) is None   # nothing shown yet: nothing set ahead
    save = advance(save, r, 300)
    while (move := answer(view(save, r), r, save.orders, knobs)) is not None:
        assert move[0] == "decision" and len(move[1]) == 1 and isinstance(move[1][0], AnswerOffer)
        save = decide(save, r, save.time, move[1][0])
    v = view(save, r)
    assert {o.offer: o.answer for o in v.offers if o.offer != OFFER} == {OfferId("k_ask"): AnswerId("k_ask_yes"), OfferId("k_bank"): AnswerId("k_his")}
    assert AnswerOffer(OFFER, AnswerId(GO)) not in [o.then for o in save.orders]
    assert SourceId("k_his") in [m.source for m in explain(save, r, HEARTH).muls]
