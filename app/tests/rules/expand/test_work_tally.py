"""The work kind's roles are counted (offer_kinds' tally, rules/expand/tally_convert.py): each answer of a work offer adds one
to its role's store, a save that answered before counts at rebase, the pattern of three answers to a role lands, and an
offer of the kind added later is counted by its own data alone."""
from dataclasses import replace
from pathlib import Path

import pytest

from ashfall_app.engine import QUANTITY_SCALE as Q, Rules, Save, StoreId, Unlock, UnlockKind, encode, new_save, rebase
from ashfall_app.rules.expand.convert import build_rules
from ashfall_app.rules.schema import CHAPTERS, DAY_EIGHTEEN, DAY_TWENTY_THREE, IN_WRITING, OPENING, Opening, load_opening, to_rules
from ashfall_app.rules.expand.tally_convert import tally_triggers

TALLY = {"food": "work_food", "build": "work_build"}


@pytest.fixture(scope="module")
def content() -> Opening:
    return load_opening(chapters=(*CHAPTERS, *IN_WRITING))


@pytest.fixture(scope="module")
def new(content: Opening) -> Rules:
    return to_rules(content)


def work_answers(o: Opening) -> dict[str, str]:
    return {a.id: TALLY[a.role or ""] for x in o.offers if x.kind == "work" for a in x.answers}


def value(s: Save, store: str) -> int:
    return next(st.segment.start_value for st in s.stores if st.store == StoreId(store)) // Q


def fired(s: Save, r: Rules, trigger: str) -> bool:
    return next(f for t, f in zip(r.triggers, s.fired) if str(t.id) == trigger)


def before_the_tally(r: Rules, answers: dict[str, str]) -> Rules:
    gone = {f"tally_{a}" for a in answers} | {"t_pattern_work_food", "t_pattern_work_build"}
    return replace(r, triggers=tuple(t for t in r.triggers if str(t.id) not in gone),
                   stores=tuple(s for s in r.stores if str(s.id) not in set(TALLY.values())))


def answered(r: Rules, *ids: str) -> Save:
    s = new_save(r)
    return replace(s, unlocked=(*s.unlocked, *(Unlock(UnlockKind.ANSWER, a) for a in ids)))


def test_every_work_answer_adds_one_to_its_roles_store(content: Opening, new: Rules):
    answers = work_answers(content)
    assert len(answers) >= 10 and set(answers.values()) == set(TALLY.values()), "counted almost no answers: the check is blind"
    assert {str(t.id) for t in new.triggers if str(t.id).startswith("tally_") and str(t.id)[6:] in answers} == {f"tally_{a}" for a in answers}


def test_a_save_that_answered_before_counts_at_rebase_and_one_that_answered_nothing_reads_zero(content: Opening, new: Rules):
    old = before_the_tally(new, work_answers(content))
    s = answered(old, "o_choir_beds", "o_cutter_road", "o_fiddle_food")
    rebased = rebase(encode(s, old), new)
    assert (value(rebased, "work_food"), value(rebased, "work_build")) == (2, 1)
    assert not fired(rebased, new, "t_pattern_work_food") and not fired(rebased, new, "t_pattern_work_build")
    none = rebase(encode(new_save(old), old), new)
    assert (value(none, "work_food"), value(none, "work_build")) == (0, 0)


def test_three_answers_to_a_role_land_that_roles_pattern_and_not_the_others(content: Opening, new: Rules):
    old = before_the_tally(new, work_answers(content))
    rebased = rebase(encode(answered(old, "o_choir_road", "o_fiddle_build", "o_walkers_build", "o_widowers_food", "o_cutter_beds"), old), new)
    assert fired(rebased, new, "t_pattern_work_build") and not fired(rebased, new, "t_pattern_work_food")


def test_a_new_offer_of_the_kind_is_counted_with_no_other_edit(content: Opening):
    src = next(x for x in content.offers if x.id == "o_choir")
    answers = [a.model_copy(update={"id": f"o_next_{a.role}"}) for a in src.answers]
    grown = content.model_copy(update={"offers": [*content.offers, src.model_copy(update={"id": "o_next", "answers": answers})]})
    added = {str(t.id) for t in tally_triggers(grown)} - {str(t.id) for t in tally_triggers(content)}
    assert added == {"tally_o_next_food", "tally_o_next_build"}


@pytest.mark.parametrize("last", [DAY_EIGHTEEN, DAY_TWENTY_THREE])
def test_the_rules_load_with_only_the_chapters_through_each_boundary(last: Path):
    """The pattern needs three answers to a role, so it lives in the first chapter whose offers can give them (the
    loader's finite check refuses a threshold the loaded offers cannot reach)."""
    build_rules(load_opening(OPENING, CHAPTERS[: CHAPTERS.index(last) + 1]))
