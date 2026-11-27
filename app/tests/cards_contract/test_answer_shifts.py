"""What an open offer's answers do to the lasting changes they make (engine DESIGN.txt, "Answer shifts"; api
contract/offers.txt, "OFFERS"). Each AnswerView.shifts has one entry per distinct change of the answer's modifiers, in authored
order: the target's total change now and with the answer's entries added, additions summing and multipliers compounding
as modified_rate combines them; None where entries of one change aim at targets standing differently; empty once given."""
from dataclasses import replace

from ashfall_app.engine import AnswerShift, LaneSpeed, Outcome, Rules, Save, WorkRef, advance, new_save, view
from cards_world import add, mul
from town_world import HC, SHOW_AT, TC, TOWN, YES, answer, town

A, B = WorkRef(HC), WorkRef(TC)


def shifts(r: Rules, save: Save | None = None) -> tuple[AnswerShift | None, ...]:
    s = advance(new_save(r), r, SHOW_AT) if save is None else save
    return view(s, r).offers[0].answers[0].shifts


def test_an_answer_shows_the_total_before_and_after_for_each_change():
    """A held +5% addition and a held x1.1 read +15.5% (1.05 x 1.1); the answer's +10% makes the addition +15%, so
    +26.5% (1.15 x 1.1). Its x0.5 aimed at a target with nothing on it is a change of its own."""
    r = town(yes=Outcome(modifiers=(add(A, 1_000, "y"), mul(B, 5_000, "y"))))
    s = replace(advance(new_save(r), r, SHOW_AT), modifiers=(add(A, 500, "held"), mul(A, 11_000, "held")))
    assert shifts(r, s) == (AnswerShift(1_550, 2_650), AnswerShift(0, -5_000))


def test_a_target_with_nothing_on_it_starts_at_zero():
    r = town(yes=Outcome(modifiers=(add(A, 500, "y"),)))
    assert shifts(r) == (AnswerShift(0, 500),)


def test_one_change_aimed_at_targets_standing_differently_has_no_shift():
    r = town(yes=Outcome(modifiers=(add(A, 500, "y"), add(B, 500, "y"))))
    s = replace(advance(new_save(r), r, SHOW_AT), modifiers=(add(A, 1_000, "held"),))
    assert shifts(r, s) == (None,)


def test_the_same_change_on_targets_standing_alike_is_one_shift():
    r = town(yes=Outcome(modifiers=(add(A, 500, "y"), add(LaneSpeed(TOWN), 500, "y"))))
    assert shifts(r) == (AnswerShift(0, 500),)


def test_an_answered_offer_has_none():
    r = town(yes=Outcome(modifiers=(add(A, 500, "y"),)))
    s = answer(advance(new_save(r), r, SHOW_AT), r, SHOW_AT, YES)
    assert view(s, r).offers[0].answers[0].shifts == ()
