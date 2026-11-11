"""Offer kinds through the loader and the release lock, on a test chapter (fixtures/askkinds.toml; engine DESIGN.txt,
part "OFFER KINDS"): the content's kind and roles reach the rules, a kind whose offers differ in roles fails the load,
a rule for the kind answers both offers as each shows, and each release-lock class has a planted release."""
from pathlib import Path

import pytest

from ashfall_app.engine import (
    AfterTime, AnswerId, AnswerKind, AnswerOffer, KindId, OfferId, Order, RoleId, Rules, Save, SetOrders, UnlockKind,
    advance, decide, new_save,
)
from ashfall_app.opening.lock import Lock, snapshot
from ashfall_app.opening.lock_checks import Problem, problems
from ashfall_app.opening.renames import load_renames
from ashfall_app.opening.schema import Opening, merge_chapters, to_rules

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "askkinds.toml"
RULE = Order(AfterTime(0), AnswerKind(KindId("q_ask"), RoleId("yes")))
FIRST, SECOND = OfferId("q_first"), OfferId("q_second")


def given(s: Save) -> set[str]:
    return {u.id for u in s.unlocked if u.kind is UnlockKind.ANSWER}


def variant(tmp_path: Path, *edits: tuple[str, str]) -> Path:
    """The fixture with each (old, new) text replaced once, written beside the test's other temporary files."""
    text = FIXTURE.read_text()
    for old, new in edits:
        assert text.count(old) >= 1, old
        text = text.replace(old, new)
    path = tmp_path / "askkinds.toml"
    path.write_text(text)
    return path


def lock_of(base: Opening, path: Path) -> Lock:
    """The lock of `base` (the shipped content, loaded once per session) with the chapter at `path` merged on."""
    o = merge_chapters(base, (path,))
    return snapshot(o, to_rules(o), load_renames())


def forbidden(was: Lock, now: Lock) -> list[Problem]:
    return [p for p in problems(was, now, load_renames()) if p.cls == "forbidden"]


@pytest.fixture(scope="module")
def released(shipped_opening: Opening) -> Lock:
    """The lock of the unedited fixture chapter, built once in setup."""
    return lock_of(shipped_opening, FIXTURE)


@pytest.fixture(scope="module")
def rules(shipped_opening: Opening) -> Rules:
    return to_rules(merge_chapters(shipped_opening, (FIXTURE,)))


def test_the_kind_and_roles_reach_the_rules(rules: Rules):
    offers = {o.id: o for o in rules.offers}
    assert offers[FIRST].kind == offers[SECOND].kind == "q_ask"
    assert [(str(a.id), a.role) for a in offers[SECOND].answers] == [("q_second_no", "no"), ("q_second_yes", "yes")]


def test_the_rule_set_while_the_first_is_open_answers_it_and_the_second_as_it_shows(rules: Rules):
    r = rules
    s = decide(advance(new_save(r), r, 150), r, 150, SetOrders((RULE,)))
    assert given(s) == {"q_first_yes"}
    done = advance(s, r, 250)
    by_hand = decide(advance(new_save(r), r, 150), r, 150, AnswerOffer(FIRST, AnswerId("q_first_yes")))
    by_hand = decide(advance(by_hand, r, 200), r, 200, AnswerOffer(SECOND, AnswerId("q_second_yes")))
    by_hand = advance(by_hand, r, 250)
    for part in ("stores", "cards", "lanes", "unlocked", "modifiers", "fired"):
        assert getattr(done, part) == getattr(by_hand, part), part
    assert given(done) == {"q_first_yes", "q_second_yes"}


ROLE_NO = 'role = "no"\nlabel_key = "q_a_no"\ncost_key = "q_a_cost"\n[offers.answers.outcome]\nline_keys = ["q_l_second_no"]'
ROLE_YES = 'role = "yes"\nlabel_key = "q_a_yes"\ncost_key = "q_a_cost"\n[offers.answers.outcome]\nline_keys = ["q_l_second_yes"]'
PLANTS = [
    ((ROLE_NO, ROLE_NO.replace('role = "no"\n', "")), "needs a role"),
    ((ROLE_NO, ROLE_NO.replace('"no"', '"maybe"')), "differ from the other offers"),
    ((ROLE_YES, ROLE_YES.replace('"yes"', '"no"')), "share a role"),
    (('kind = "q_ask"\ngate = { test = "after_time", value = 200 }', 'gate = { test = "after_time", value = 200 }'),
     "has a role but the offer has no kind"),
]


@pytest.mark.parametrize("edit,message", PLANTS, ids=["second offer lacks a role", "second offer has other roles",
                                                    "second offer repeats a role", "roles without a kind"])
def test_a_kind_whose_offers_differ_in_roles_fails_the_loader(shipped_opening: Opening, tmp_path: Path, edit: tuple[str, str], message: str):
    with pytest.raises(ValueError, match=f"offer q_second: .*{message}"):
        merge_chapters(shipped_opening, (variant(tmp_path, edit),))


def unkinded(tmp_path: Path) -> Path:
    return variant(tmp_path, ("kind = \"q_ask\"\n", ""), ("role = \"yes\"\n", ""), ("role = \"no\"\n", ""))


def test_giving_a_kind_to_released_offers_that_had_none_is_safe(shipped_opening: Opening, released: Lock, tmp_path: Path):
    assert forbidden(lock_of(shipped_opening, unkinded(tmp_path)), released) == []


def test_a_released_offers_kind_changed_is_forbidden(shipped_opening: Opening, released: Lock, tmp_path: Path):
    found = forbidden(released, lock_of(shipped_opening, variant(tmp_path, ('kind = "q_ask"', 'kind = "q_other"'))))
    assert any("offer q_first's kind changed or went" in p.message for p in found), found


def test_a_released_offers_kind_removed_is_forbidden(shipped_opening: Opening, released: Lock, tmp_path: Path):
    found = forbidden(released, lock_of(shipped_opening, unkinded(tmp_path)))
    assert any("offer q_first's kind changed or went" in p.message for p in found), found
    assert any("answer q_first_yes's role changed or went" in p.message for p in found), found


def test_a_released_answers_role_changed_is_forbidden(shipped_opening: Opening, released: Lock, tmp_path: Path):
    both = variant(tmp_path, ('role = "yes"', 'role = "ja"'))
    found = forbidden(released, lock_of(shipped_opening, both))
    assert any("answer q_first_yes's role changed or went" in p.message for p in found), found
    assert not any("kind changed" in p.message for p in found)
