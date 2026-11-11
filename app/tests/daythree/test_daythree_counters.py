"""The spend and decide counters (counters.py), each with a planted fixture visit that reads zero: a return with
nothing affordable at a full store, and a visit with no choice. The fixtures are the banked-time chapter (banked/chapter.py,
whose wood store fills in two hours) and the two builds of choicefix.py."""
from typing import Unpack

from ashfall_app.engine import (
    BP, AnswerOffer, CardShare, Mix, MixId, Rules, Save, SaveMix, SetQueue, SwitchMix, TapCard, Verb, advance, decide,
    new_save, view,
)
from tests.banked import chapter
from tests.banked.chapter import COMFORT, GATHER, HOUR as H, NEWCOMER, STAY, TRIP
from tests.daythree import choicefix, counters, shifts
from tests.daythree.counters import Step, Visit
from tests.daythree.choicefix import A, B

GATHER_ONLY = Mix(MixId("gather_only"), (CardShare(GATHER, BP),))


def returned(t: int, **times: Unpack[chapter.Times]) -> tuple[Rules, Save]:
    """The chapter's rules and the save at `t` with the gatherer alone running from the start."""
    r = chapter.rules(**times)
    s = new_save(r)
    for verb in (SaveMix(GATHER_ONLY), SwitchMix(GATHER_ONLY.id)):
        s = decide(s, r, 0, verb)
    return r, advance(s, r, t)


def test_a_return_at_a_full_store_with_an_affordable_card_has_something_to_spend_on():
    r, s = returned(3 * H)
    assert counters.spendable(s, r) == (str(COMFORT),)


def test_a_return_with_nothing_shown_at_a_full_store_has_nothing_to_spend_on():
    """The planted visit: wood is full at 3 h, and the comfort and the trip show only at 10 h."""
    r, s = returned(3 * H, trip_at=10 * H, comfort_at=10 * H)
    full = counters.full_stores(s, r, view(s, r))
    assert str(chapter.WOOD) in full and counters.spendable(s, r) == ()
    c = counters.count(Visit("V2", 3 * H, s, ()), r)
    assert (c.spend, c.decide) == (0, 0) and counters.line(c) == "spend  0  decide  0"


def test_an_affordable_card_at_a_store_under_the_level_is_not_spend():
    """The comfort takes 3 of the wood store's 4: affordable from 75%, counted from 80%."""
    r, early = returned(int(1.55 * H))
    _, later = returned(int(1.7 * H))
    assert counters.spendable(early, r) == () and counters.spendable(later, r) == (str(COMFORT),)
    assert str(TRIP) not in counters.spendable(later, r)


def step(s: Save, verb: Verb, r: Rules, at: int = 0) -> Step:
    return Step(at, verb, s, decide(s, r, at, verb))


def test_reordering_the_queue_moves_which_goal_lands_first_and_is_a_decision():
    r, s = choicefix.rules(), choicefix.planned(A, B)
    moved = step(s, SetQueue((choicefix.entry(B), choicefix.entry(A))), r)
    assert counters.decides(moved, r)


def test_saving_the_same_queue_again_is_no_decision():
    """The planted visit with no choice: the same plan set again, and the mix saved as it was."""
    r, s = choicefix.rules(), choicefix.planned(A, B)
    same = [step(s, SetQueue(s.queue), r), step(s, SaveMix(choicefix.MIX), r)]
    assert not any(counters.decides(x, r) for x in same)
    c = counters.count(Visit("V3", 9 * H, s, tuple(same)), r)
    assert c.decide == 0


def test_a_tap_of_a_build_while_the_other_is_ready_is_a_choice_and_alone_is_not():
    r = choicefix.rules()
    both = choicefix.planned(A, B, 3 * H, queued=False)
    assert counters.chooses(step(both, TapCard(A), r, 3 * H), r)
    only_b = choicefix.planned(A, B, 2 * H, queued=False)   # the second store's build is ready, the first's is not
    assert not counters.chooses(step(only_b, TapCard(B), r, 2 * H), r)


def test_an_answer_is_a_decision():
    r, s = returned(5 * H)
    assert counters.decides(step(s, AnswerOffer(NEWCOMER, STAY), r, 5 * H), r)


def switch_to(g1_share: int) -> Step:
    """The quarter mix switched for one giving the first store `g1_share` of the hands' time, three hours before the return."""
    r, s = choicefix.rules(), choicefix.planned(A, B, 0, queued=False)
    mix = Mix(MixId("other"), (CardShare(choicefix.G1, g1_share), CardShare(choicefix.G2, BP - g1_share)))
    after = decide(decide(s, r, 0, SaveMix(mix)), r, 0, SwitchMix(mix.id))
    return Step(0, SwitchMix(mix.id), s, after, 3 * H)


def test_a_mix_change_that_moves_a_store_a_quarter_of_its_cap_by_the_return_is_a_decision():
    """Half the time to each store, not a quarter and three quarters: the first store ends 30% of its cap higher and
    the second lower, though no goal's landing order moves (there is no queue)."""
    r, step = choicefix.rules(), switch_to(BP // 2)
    assert shifts.shift(step.before, step.after, r, 3 * H).level_bp == 3000 >= counters.LEVEL_MIN_BP
    assert not counters.moves_the_order(step, r)
    assert counters.decides(step, r)


def test_a_mix_change_that_moves_a_store_a_few_percent_of_its_cap_is_no_decision():
    r, step = choicefix.rules(), switch_to(BP // 4 + BP // 100)
    assert 0 < shifts.shift(step.before, step.after, r, 3 * H).level_bp < counters.LEVEL_MIN_BP
    assert not counters.decides(step, r)
