"""What the Asks list reads of an offer (api/CONTRACT.txt, "OFFERS"): who asks, what led to it, and the three texts an
offer has only where it differs from the usual. Served as authored, its cause shared with its lines, and the content
refuses an asker that is no person and an expiry the engine cannot keep."""
import pytest

from ashfall_app.api.content_models import Content, OfferInfo
from ashfall_app.api.line_causes import line_infos
from ashfall_app.api.line_models import AnswerCause, WhenCause
from ashfall_app.api.service import Game
from ashfall_app.opening.ask_checks import check_asks
from ashfall_app.opening.offer_entries import OfferEntry
from ashfall_app.opening.renames import load_renames
from ashfall_app.opening.schema import Opening
from ashfall_app.saves.ruleset import ruleset


@pytest.fixture(scope="module")
def served(shipped_opening: Opening) -> dict[str, OfferInfo]:
    content: Content = Game(shipped_opening, ruleset(shipped_opening, load_renames(), "dev", 1)).content()
    return {x.offer: x for x in content.offer_infos}


def hidden_gated(o: Opening) -> OfferEntry:
    hidden = {s.id for s in o.stores if s.hidden}
    return next(x for x in o.offers if x.gate.subject_kind == "store" and x.gate.id in hidden)


def test_the_fields_are_served_as_authored(shipped_opening: Opening, served: dict[str, OfferInfo]) -> None:
    assert any(x.askers for x in shipped_opening.offers) and any(x.permanence_key for x in shipped_opening.offers), \
        "control: the content fills the fields"
    for x in shipped_opening.offers:
        got = served[x.id]
        assert (got.askers, got.waiting_key, got.expiry_key, got.permanence_key) == (
            x.askers, x.waiting_key, x.expiry_key, x.permanence_key), x.id


def test_a_gate_the_page_can_word_is_the_cause(shipped_opening: Opening, served: dict[str, OfferInfo]) -> None:
    x = next(x for x in shipped_opening.offers if x.gate.subject_kind == "card_count")
    got = served[x.id].cause
    assert isinstance(got, WhenCause) and got.when.kind == "at_least"
    assert got.when.watched.kind == "card_count" and got.when.watched.card == x.gate.id


def test_a_hidden_gate_names_the_answer_it_follows(shipped_opening: Opening, served: dict[str, OfferInfo]) -> None:
    x = hidden_gated(shipped_opening)
    after = next(c.id for c in x.requires if c.unlock_kind == "answered")
    assert served[x.id].cause == AnswerCause(offer=after or "")


def test_an_offers_lines_carry_the_offers_cause(shipped_opening: Opening, served: dict[str, OfferInfo]) -> None:
    """A line moved from the offer that writes it onto a hidden-gated one takes that offer's cause."""
    x = hidden_gated(shipped_opening)
    giver = next(g for g in shipped_opening.offers if g.line_keys)
    moved = {giver.id: giver.model_copy(update={"line_keys": []}), x.id: x.model_copy(update={"line_keys": giver.line_keys})}
    o = shipped_opening.model_copy(update={"offers": [moved.get(g.id, g) for g in shipped_opening.offers]})
    causes = {i.key: i.cause for i in line_infos(o)}
    assert all(causes[k] == served[x.id].cause for k in giver.line_keys)


def planted(o: Opening, **fields: object) -> Opening:
    x = o.offers[0]
    return o.model_copy(update={"offers": [x.model_copy(update=fields), *o.offers[1:]]})


def test_the_shipped_asks_pass(shipped_opening: Opening) -> None:
    check_asks(shipped_opening)


@pytest.mark.parametrize(("fields", "says"), [
    ({"askers": ["hands"]}, "not a ruled lane"),
    ({"askers": ["no_such_lane"]}, "not a ruled lane"),
    ({"expiry_key": "anything"}, "never goes"),
])
def test_a_bad_ask_fails_naming_the_offer(shipped_opening: Opening, fields: dict[str, object], says: str) -> None:
    with pytest.raises(ValueError, match=says) as got:
        check_asks(planted(shipped_opening, **fields))
    assert shipped_opening.offers[0].id in str(got.value)


def test_an_asker_named_twice_fails(shipped_opening: Opening) -> None:
    lane = next(lane.id for lane in shipped_opening.lanes if lane.ruled)
    with pytest.raises(ValueError, match="twice"):
        check_asks(planted(shipped_opening, askers=[lane, lane]))
