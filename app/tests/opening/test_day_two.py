"""Day two's chapter (day_two.toml) ships in CHAPTERS, and none of its unwritten lines ships: no text of the content a
release is built from (load_opening's CHAPTERS, what the server, the API and the release lock read) is UNWRITTEN. A
chapter whose lines are still to write waits in IN_WRITING and moves into CHAPTERS once they are written."""
from functools import cache

import pytest

from ashfall_app.engine import CardId, RuleInstall
from ashfall_app.opening.schema import CHAPTERS, IN_WRITING, OPENING, UNWRITTEN, Opening, load_opening, to_rules


@cache
def with_day_two() -> Opening:
    return load_opening(OPENING, (*CHAPTERS, *IN_WRITING))


@pytest.fixture(scope="module")
def in_writing() -> Opening:
    """The content with every chapter in writing merged, loaded once for the module: each chapter adds to its load."""
    return with_day_two()


def unwritten(o: Opening) -> list[str]:
    """The text keys whose line is still to write."""
    return sorted(k for k, text in o.text.items() if UNWRITTEN in text)


def test_no_shipping_release_holds_an_unwritten_line():
    assert unwritten(load_opening()) == []


def test_the_guard_sees_an_unwritten_line(shipped_opening: Opening, in_writing: Opening):
    """The check above can fail: of all-written text, one line planted as unwritten is found alone, in the
    shipped text and in an in-writing chapter's. The shipped content is the session's, loaded once."""
    o = shipped_opening
    written = {k: "a line" for k in o.text}
    key = next(iter(written))
    assert unwritten(o.model_copy(update={"text": written})) == []
    assert unwritten(o.model_copy(update={"text": {**written, key: UNWRITTEN}})) == [key]
    planted = {**in_writing.text, key: UNWRITTEN}
    assert unwritten(in_writing.model_copy(update={"text": planted})) == [key]


def test_no_chapter_is_both_shipping_and_in_writing():
    assert not set(CHAPTERS) & set(IN_WRITING)


def test_day_two_loads_after_the_shipped_chapters():
    to_rules(with_day_two())


def test_her_lane_starts_on_the_rule_her_arrival_installs():
    r = to_rules(with_day_two())
    arrive = next(t for t in r.triggers if t.id == "t_n1_works")
    assert arrive.outcome.orders == (RuleInstall(CardId("n1_forage")),)


def test_each_answer_sets_its_walk_as_a_one_off_never_a_start():
    """Engine DESIGN.txt, "Content": a start on a busy lane changes nothing, so the story would wait on a step no one
    takes. The hands' walk is queued, hers is a rule above her task."""
    offer = next(x for x in to_rules(with_day_two()).offers if x.id == "o_cart")
    go, she_goes = offer.answers
    assert go.outcome.queues == (CardId("walk_ridge"),) and not go.outcome.starts
    assert she_goes.outcome.orders == (RuleInstall(CardId("n1_walk_ridge"), first=True),) and not she_goes.outcome.starts
