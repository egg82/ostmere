"""Repeats counted from the decision log (CONTRACT.txt, "Repeats"; saves/repeats.py): what counts, the window and the
count, and that a log rebuilt by replaying its decisions counts the same. Rules: the opening's, everything unlocked,
so hands cards are tappable and chips show from the start."""
from dataclasses import replace

import pytest
from hypothesis import given, settings, strategies as st

from ashfall_app import engine as e
from ashfall_app.engine.codec import Json
from ashfall_app.opening.schema import DAY_ONE, load_opening, to_rules
from ashfall_app.saves.repeats import Logged, RepeatRules, Repeats, count, hands_cards

RULES = replace(to_rules(load_opening(chapters=(DAY_ONE,))), opening=None)
HANDS = hands_cards(RULES)
A, B, C = e.CardId("gather_wood"), e.CardId("scavenge"), e.CardId("forage")
M0, M1 = e.MixId("m0"), e.MixId("m1")
MIXES = (e.SaveMix(e.Mix(M0, (e.CardShare(A, e.BP),))), e.SaveMix(e.Mix(M1, (e.CardShare(B, e.BP),))))
R = RepeatRules(hand_taps=3, hand_taps_within_s=900, switches=2, switches_within_s=3600)


def played(verbs: list[tuple[int, e.Verb]]) -> tuple[e.Save, list[Logged]]:
    """The verbs decided live (decide_logged), each `dt` after the last; a verb the engine refuses is left out, as the
    log never holds one. The log as the server keeps it: the context through its JSON form."""
    s, log = e.new_save(RULES), list[Logged]()
    for dt, verb in verbs:
        try:
            step = e.decide_logged(s, RULES, s.time + dt, verb)
        except e.InvalidVerbError:
            continue
        assert step.context is not None
        log.append(Logged(step.save.time, verb, e.context_from_json(e.context_to_json(step.context))))
        s = step.save
    return s, log


def replayed(log: list[Logged]) -> list[Logged]:
    """The log rebuilt by replaying its decisions with decide() from a new save, each context read off the replay."""
    s, out = e.new_save(RULES), list[Logged]()
    for d in log:
        before = e.advance(s, RULES, d.at)
        out.append(Logged(d.at, d.verb, e.decision_context(before, RULES, d.verb)))
        s = e.decide(s, RULES, d.at, d.verb)
    return out


def test_taps_count_only_while_a_mix_runs_without_the_card_and_only_from_the_count():
    _, log = played([(0, MIXES[0]), (0, e.SwitchMix(M0)), *[(30, e.TapCard(B)) for _ in range(3)],
                     *[(30, e.TapCard(A)) for _ in range(3)]])
    assert [type(d.verb) for d in log].count(e.TapCard) == 6   # control: every tap was taken
    now = log[-1].at
    assert count(log, now, HANDS, R).taps == ((B, 3),)   # A is in the running mix
    assert count(log, now, HANDS, replace(R, hand_taps=4)).taps == ()


def test_taps_with_no_mix_running_count_nothing():
    _, log = played([(30, e.TapCard(B)) for _ in range(4)])
    assert len(log) == 4 and all(d.context is not None and d.context.mix is None for d in log)
    assert count(log, log[-1].at, HANDS, R) == Repeats()


def test_the_window_drops_taps_older_than_it():
    _, log = played([(0, MIXES[0]), (0, e.SwitchMix(M0)), *[(30, e.TapCard(B)) for _ in range(3)]])
    first_tap = log[2].at
    assert count(log, first_tap + R.hand_taps_within_s, HANDS, R).taps == ((B, 3),)
    assert count(log, first_tap + R.hand_taps_within_s + 1, HANDS, R).taps == ()


def test_switches_count_per_chip_shown_and_not_to_the_mix_already_running():
    _, log = played([*[(0, m) for m in MIXES], (0, e.SwitchMix(M0)), (5, e.SwitchMix(M1)), (5, e.SwitchMix(M1)),
                     (5, e.SwitchMix(M0)), (5, e.SwitchMix(M1))])
    chips = log[-1].context.chips if log[-1].context else ()
    assert chips   # control: a chip shows, so a switch can count
    got = count(log, log[-1].at, HANDS, R).switches
    # m0: the first switch (from no mix) and the last but one; m1: three, but the second ran m1 already
    assert set(got) == {(chip, mix, 2) for chip in chips for mix in (M0, M1)}


def test_a_row_without_a_context_counts_for_nothing():
    _, log = played([(0, MIXES[0]), (0, e.SwitchMix(M0)), *[(30, e.TapCard(B)) for _ in range(3)]])
    assert count([replace(d, context=None) for d in log], log[-1].at, HANDS, R) == Repeats()


_verb = st.one_of(st.sampled_from(MIXES), st.sampled_from([e.SwitchMix(M0), e.SwitchMix(M1)]),
                  st.sampled_from([e.TapCard(A), e.TapCard(B), e.TapCard(C)]))
_dt = st.one_of(st.integers(0, 12), st.integers(13, 400), st.integers(401, 2400))


@settings(max_examples=6)
@given(steps=st.lists(st.tuples(_dt, _verb), min_size=4, max_size=10), later=st.integers(0, 2000))
def test_a_replayed_log_counts_the_same(steps: list[tuple[int, e.Verb]], later: int):
    """Each logged context equals the one a replay of the log reads at that decision, so the counts agree at any
    time; the live save and the replay's end equal too (the replay is a real one)."""
    end, log = played(steps)
    again = replayed(log)
    assert again == log
    for now in {end.time, end.time + later}:
        assert count(again, now, HANDS, R) == count(log, now, HANDS, R)


def test_the_property_can_see_a_count():
    """Control for the property above: a log of its shape does reach a count, so agreeing is not agreeing on empty."""
    _, log = played([(0, MIXES[0]), (0, e.SwitchMix(M0)), *[(13, e.TapCard(B)) for _ in range(3)]])
    assert count(replayed(log), log[-1].at, HANDS, R).taps == ((B, 3),)


@pytest.mark.parametrize("bad", [{"mix": 3, "in_mix": False, "chips": []}, {"mix": None, "chips": []}, [], None])
def test_a_context_not_of_its_shape_reads_as_none(bad: Json):
    assert e.context_from_json(bad) is None
