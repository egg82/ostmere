"""Week five's readings (reads.py) on the engine contract suites' fixture worlds, each shown able to fail: the cast lane,
the chain's length per cast, the preparation gap, the decide counter's refusal of a queued stage, and the unlock-order
check on a planted fixture whose card opens before its outcome's beat."""
from pathlib import Path

import pytest

from ashfall_app.engine import (
    HANDS, AfterTime, AnswerId, AnswerOffer, CardDef, OfferId, QueueEntry, SetQueue, TapCard, Unlock, UnlockKind, decide,
    new_save,
)
from tests.daythree import counters as c3
from tests.daythree.counters import Counts, Step, Visit
from tests.weekfive import fixtures, reads
from tests.weekone import fights

casting = fixtures.world("casting_world", "casting")
spells = fixtures.world("spells_world", "spells")


def test_the_cast_lane_is_read_from_the_save_and_none_before_the_cast(tmp_path: Path):
    r = casting.rules_of(tmp_path)
    by = dict(t_a_chop=1000, t_b_chop=3000, t_c_chop=1000, t_m_chop=1000)
    before, after = casting.at(r, by, casting.CAST_AT - 5), casting.at(r, by, casting.CAST_AT + 5)
    assert reads.cast_lane(before, r, "lead") is None and reads.cast_lane(after, r, "lead") == "t_b"
    assert reads.cast_lane(after, r, "other") is None
    assert reads.cast_line("typical", after, r, ("lead",)) == "typical: lead -> t_b"


@pytest.mark.parametrize(("members", "reach"), [(3, 2), (2, 5), (4, 1)])
def test_a_chains_length_per_cast_is_the_links_it_resolved(members: int, reach: int):
    r = spells.world(members, reach, per=3600)
    taps = (11, 40, 80, 120)
    _, lines = spells.play(r, taps)
    want = [k for _, k in spells.model_links(r, tuple(t + 10 for t in taps), reach, members)]
    got = reads.chain_lengths(lines, r)[str(spells.SPELL)]
    assert got == want and want, "the fixture chains"
    assert max(got) <= min(reach, members)
    assert reads.chain_text("typical", {"spell": got})[0].startswith("typical spell: ")


def test_a_cards_own_line_is_not_a_link():
    r = spells.world(3, 2, per=3600, own=(spells.OWN,))
    _, lines = spells.play(r, (11,))
    assert any(x.key == spells.OWN for x in lines), "the card writes its own line too"
    assert reads.chain_lengths(lines, r)[str(spells.SPELL)] == [k for _, k in spells.per_instant(lines)]


def test_a_card_without_a_chain_has_no_chain_readout():
    plain = CardDef(spells.PLAIN, 10, lane=HANDS)
    r = spells.world(3, 2, per=3600, cards=(spells.spell(), plain))
    _, lines = spells.play(r, (11,))
    assert set(reads.chain_lengths(lines, r)) == {str(spells.SPELL)}


def test_a_visit_whose_only_change_is_a_queued_stage_has_no_decision():
    """Two staged builds: queuing a stage of one moves which lands first, which day three's counter counts."""
    r = spells.world(3, 2, per=3600, cards=(spells.spell(cap=3, work_s=100), spells.spell(card_id=spells.SPELL2, cap=3, work_s=100)))
    queue = SetQueue((QueueEntry(TapCard(spells.SPELL2), AfterTime(10**9)),))
    s0 = new_save(r)
    step = Step(0, queue, s0, decide(s0, r, 0, queue), 7200)
    assert c3.decides(step, r), "the planted visit is one day three's counter counts"
    got = reads.count(Visit("V1", 3600, s0, (step,)), r)
    assert got.decide == 0 and reads.undecided_visits([got]) == ["V1"]


def test_a_visit_that_answers_an_offer_decides():
    r = spells.world(3, 2, per=3600)
    s = new_save(r)
    answer = AnswerOffer(OfferId("o"), AnswerId("a"))
    got = reads.count(Visit("V2", 3600, s, (Step(0, answer, s, s, 100),)), r)
    assert got.decide == 1 and reads.undecided_visits([got]) == []


def test_the_decision_ratio_counts_visits_with_a_decision():
    counts = [Counts("V1", 0, 0, 2), Counts("V2", 0, 0, 0), Counts("V3", 0, 0, 1), Counts("V4", 0, 0, 3)]
    assert reads.decision_ratio(counts) == (3, 4) and reads.undecided_visits(counts) == ["V2"]


def test_a_card_that_opens_before_its_outcomes_beat_fails_the_unlock_order(tmp_path: Path):
    """In the casting world the lead is cast at CAST_AT and `t_a_chop` is unlocked at 0 by the join: pairing it with the
    cast's beat is the planted defect; the cast feature itself opens at the beat, the control."""
    r = casting.rules_of(tmp_path)
    saves = [casting.at(r, dict(t_a_chop=1000), t) for t in (0, 100, casting.CAST_AT - 5, casting.CAST_AT + 5)]
    card, cast = Unlock(UnlockKind.CARD, "t_a_chop"), Unlock(UnlockKind.FEATURE, "lead_t_a")
    opened = reads.first_held(saves, (card, cast))
    landed = {"t_cast": casting.CAST_AT}
    assert card in opened and opened[card] < casting.CAST_AT
    assert reads.unlock_order(opened, landed, [(card, "t_cast")]) != []
    assert reads.unlock_order(opened, landed, [(cast, "t_cast")]) == []
    assert reads.unlock_order(opened, {}, [(card, "t_cast")]) != [], "a beat that never landed opens nothing"
    assert reads.unlock_order({}, landed, [(card, "t_cast")]) == [], "an unlock never held is no violation"


def test_the_preparation_gap_is_the_measure_with_the_card_built_against_without():
    r = spells.world(3, 2, per=3600)
    week = fights.Week(new_save(r), [(11, TapCard(spells.SPELL))], 100, r)
    with_card, bare = reads.prepared_gap(week, {spells.SPELL}, lambda s: spells.chained(r, s))
    assert with_card > 0 and bare == 0
    assert reads.prepared_gap(week, set(), lambda s: spells.chained(r, s)) == (with_card, with_card), "no card named, no gap"


def test_a_queue_loses_only_the_entries_of_the_cards_taken_out():
    keep, drop = QueueEntry(TapCard(spells.PLAIN), AfterTime(5)), QueueEntry(TapCard(spells.SPELL), AfterTime(5))
    assert reads.strip_cards(SetQueue((keep, drop)), {spells.SPELL}) == SetQueue((keep,))
    assert reads.strip_cards(TapCard(spells.SPELL), {spells.SPELL}) is None
