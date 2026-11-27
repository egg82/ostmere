"""An offer whose second answer leaves the one-off on the Tasks list (docs/design/week-four-plan.md, item 3), on
fixtures/unqueued.toml merged onto the opening alone: one answer queues the capped hands card and unlocks it, the other
only unlocks it; tapped later, its finish lands the feature as the queued one does. `gates_read_feature` names the
feature later gates read: a gate reading the offer's answers instead, or a feature the card's finish does not unlock,
fails the load by name."""
from pathlib import Path

import pytest

from ashfall_app.engine import (
    QUANTITY_SCALE as Q, AnswerId, AnswerOffer, CardId, OfferId, Rules, Save, StoreId, TapCard, Unlock, UnlockKind, advance,
    decide, new_save, view,
)
from ashfall_app.rules.schema import OPENING, Opening, load_opening, to_rules

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "unqueued.toml"
OFFER, JOB, HEAP = OfferId("t_help"), CardId("t_job"), StoreId("t_heap")
FEATURE = Unlock(UnlockKind.FEATURE, "t_job_done")
NOW, LATER = AnswerId("t_help_now"), AnswerId("t_help_later")
TRIGGER = ('[[triggers]]\nid = "t_after_job"\nwhen = { test = "at_least", subject_kind = "unlocked", unlock_kind = "feature", '
           'id = "t_job_done", value = 1 }')
BY_ANSWER = ('[[triggers]]\nid = "t_after_job"\nwhen = { test = "at_least", subject_kind = "unlocked", unlock_kind = "%s", '
             'id = "%s", value = 1 }')

PLANTS = (
    ("a later gate reading an answer", "trigger t_after_job: reads offer t_help's answer; read t_job_done instead",
     ((TRIGGER, BY_ANSWER % ("answer", "t_help_later")),)),
    ("a later gate reading that the offer was answered", "trigger t_after_job: reads offer t_help's answer",
     ((TRIGGER, BY_ANSWER % ("answered", "t_help")),)),
    ("a feature the card's finish does not unlock", "offer t_help: feature t_other is not unlocked by the finish",
     (('gates_read_feature = ["t_job_done"]', 'gates_read_feature = ["t_other"]'),
      ('[[features]]\nid = "t_job_done"', '[[features]]\nid = "t_job_done"\n\n[[features]]\nid = "t_other"'))),
    ("a card only one answer unlocks", "offer t_help: feature t_job_done is not unlocked by the finish",
     (('[offers.answers.outcome]\nunlocks = [{ unlock_kind = "card", id = "t_job" }]\n\n[[cards]]',
       '[offers.answers.outcome]\n\n[[cards]]'),)),
)


def edited(tmp_path: Path, *edits: tuple[str, str]) -> Path:
    text = FIXTURE.read_text()
    for old, new in edits:
        assert text.count(old) == 1, f"anchor is not unique: {old!r}"
        text = text.replace(old, new)
    path = tmp_path / FIXTURE.name
    path.write_text(text)
    return path


def load_with(path: Path) -> Opening:
    return load_opening(OPENING, (path,))


@pytest.fixture(scope="module")
def rules() -> Rules:
    return to_rules(load_with(FIXTURE))


def heap(s: Save) -> int:
    return next(st.segment.start_value // Q for st in s.stores if st.store == HEAP)


def answered(r: Rules, answer: AnswerId, at: int = 100) -> Save:
    return decide(advance(new_save(r), r, at), r, at, AnswerOffer(OFFER, answer))


def test_either_answer_ends_with_the_card_unlocked_and_on_the_tasks(rules: Rules):
    for answer in (NOW, LATER):
        s = answered(rules, answer)
        assert Unlock(UnlockKind.CARD, JOB) in s.unlocked
        assert JOB in [c.card for c in view(s, rules).cards]


def test_only_the_first_answer_queues_it(rules: Rules):
    assert len(answered(rules, NOW).queue) == 1 and answered(rules, LATER).queue == ()


def test_tapped_later_the_feature_lands_as_the_queued_one_does(rules: Rules):
    queued = advance(answered(rules, NOW), rules, 400)
    later = answered(rules, LATER)
    assert FEATURE not in advance(later, rules, 400).unlocked and heap(advance(later, rules, 400)) == 0
    later = advance(decide(advance(later, rules, 300), rules, 300, TapCard(JOB)), rules, 400)
    assert heap(queued) == heap(later) == 1
    assert FEATURE in later.unlocked and FEATURE in queued.unlocked and JOB not in [c.card for c in view(later, rules).cards]


@pytest.mark.parametrize(("message", "edits"), [(m, e) for _, m, e in PLANTS], ids=[n for n, _, _ in PLANTS])
def test_the_loader_refuses(tmp_path: Path, message: str, edits: tuple[tuple[str, str], ...]):
    with pytest.raises(ValueError, match=message):
        load_with(edited(tmp_path, *edits))


def test_the_shipped_book_offer_is_one():
    """O-book (day_twenty_three.toml): both answers unlock bind_book, only the first queues it, and what reads the book
    reads its finish (D-162)."""
    from tests.rules.play.playthrough import opening
    book = next(x for x in opening().offers if x.id == "o_book")
    assert book.gates_read_feature == ["book_given"]
    assert [[u.id for u in a.outcome.unlocks] for a in book.answers] == [["bind_book"], ["bind_book"]]
    assert [a.outcome.queues for a in book.answers] == [["bind_book"], []]
