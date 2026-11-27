"""Arrivals that join as a pooled group (docs/design/week-four-plan.md, item 6), on fixtures/group_arrivals.toml merged
onto the opening alone: an offer of a two-role kind whose either answer joins four people, told by a mention, into one
pooled lane's split, the answer picking the group's card; the kind's rule answers it with either role. A join whose card
is on another group than the lane's fails the group checks, naming the answer."""
from pathlib import Path

import pytest

from ashfall_app.engine import (
    AfterTime, AnswerId, AnswerKind, AnswerOffer, CardId, KindId, LaneId, OfferId, Order, RoleId, Rules, Save,
    SetOrders, StoreId, QUANTITY_SCALE as Q, UnlockKind, advance, decide, decide_logged, new_save, view,
)
from ashfall_app.rules.people import mention_key
from ashfall_app.rules.schema import OPENING, Opening, load_opening, to_rules

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "group_arrivals.toml"
OFFER, KIND = OfferId("t_arrive"), KindId("t_work")
MEMBERS = tuple(LaneId(f"t_m{i}") for i in range(1, 5))
BP = 10_000
ANSWERS = {"food": ("t_arrive_food", "t_crew_food", StoreId("t_food"), 30),
           "build": ("t_arrive_build", "t_crew_build", StoreId("t_stone"), 60)}


def edited(tmp_path: Path, *edits: tuple[str, str]) -> Path:
    text = FIXTURE.read_text()
    for old, new in edits:
        assert text.count(old) >= 1, f"anchor is not found: {old!r}"
        text = text.replace(old, new)
    path = tmp_path / FIXTURE.name
    path.write_text(text)
    return path


def load_with(path: Path) -> Opening:
    return load_opening(OPENING, (path,))


@pytest.fixture(scope="module")
def rules() -> Rules:
    return to_rules(load_with(FIXTURE))


def held(s: Save, store: StoreId) -> int:
    return next(st.segment.start_value for st in s.stores if st.store == store) // Q


def joined(s: Save) -> set[str]:
    return {u.id for u in s.unlocked if u.kind is UnlockKind.JOINED}


@pytest.mark.parametrize("role", ANSWERS)
def test_either_answer_joins_the_four_into_the_group_at_the_answers_share(rules: Rules, role: str):
    answer, card, store, per_hour = ANSWERS[role]
    s = decide(advance(new_save(rules), rules, 100), rules, 100, AnswerOffer(OFFER, AnswerId(answer)))
    assert joined(s) == set(MEMBERS)
    shown = {c.card: c for c in view(s, rules).cards}
    group = shown[CardId(card)]
    assert [c for c in shown if c.startswith("t_")] == [card] and group.crew == 4 and group.share_bp == 4 * BP
    assert held(advance(s, rules, 100 + 3600), store) == 4 * per_hour


def test_each_arrival_is_a_mention_line_whichever_answer(rules: Rules):
    for answer, *_ in ANSWERS.values():
        step = decide_logged(advance(new_save(rules), rules, 100), rules, 100, AnswerOffer(OFFER, AnswerId(answer)))
        assert {ln.key for ln in step.lines} >= {mention_key("joined", m) for m in MEMBERS}


@pytest.mark.parametrize("role", ANSWERS)
def test_the_kinds_rule_answers_it_while_away_with_the_same_outcome(rules: Rules, role: str):
    answer, _, store, _ = ANSWERS[role]
    ruled = decide(new_save(rules), rules, 0, SetOrders((Order(AfterTime(0), AnswerKind(KIND, RoleId(role))),)))
    by_hand = decide(advance(new_save(rules), rules, 100), rules, 100, AnswerOffer(OFFER, AnswerId(answer)))
    away = advance(ruled, rules, 500)
    assert joined(away) == set(MEMBERS) and held(advance(away, rules, 4000), store) == held(advance(by_hand, rules, 4000), store) > 0


PLANTS = (
    ("a join handing a lane to a card of another group",
     "answer t_arrive_food: joins t_m1 without its own split, and card t_other_work is not an uncapped card on its group",
     (('card = "t_crew_food", own_split', 'card = "t_other_work", own_split'),)),
    ("a lane already in another group",
     "answer t_arrive_food: joins t_m4 without its own split, and card t_crew_food is not an uncapped card on its group",
     (('id = "t_m4"\nlabel_key = "t_l_m4"\nruled = true\ntold = "mention"\ngroup = "t_crew"',
       'id = "t_m4"\nlabel_key = "t_l_m4"\nruled = true\ntold = "mention"\ngroup = "t_other"'),)),
)


@pytest.mark.parametrize(("message", "edits"), [(m, e) for _, m, e in PLANTS], ids=[n for n, _, _ in PLANTS])
def test_the_group_checks_refuse(tmp_path: Path, message: str, edits: tuple[tuple[str, str], ...]):
    with pytest.raises(ValueError, match=message):
        load_with(edited(tmp_path, *edits))
