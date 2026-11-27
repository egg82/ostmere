"""Who a role is cast to (api/contract/casting.txt, "CASTING", "The pick"): the lane whose own count is highest on the
first pattern, ties going to the next pattern, then to the earliest declared. Written blind from that part; each test
states its premise from the control (the same play with no cast), so a numbers slip shows there, not as a wrong winner."""
from pathlib import Path

from casting_world import LEAD, counts, kills, lead_of

BOTH = '{ role = "lead", patterns = ["{lane}_chop", "{lane}_haul"] }'


@kills(3)
def test_the_lane_with_the_most_completions_of_the_card_holds_the_role(tmp_path: Path):
    by = dict(t_a_chop=1000, t_b_chop=3000, t_c_chop=2000, t_m_chop=1000)
    n = counts(tmp_path, by)
    assert [n[f"t_{x}_chop"] for x in "abcm"] == [2, 6, 4, 2]
    assert lead_of(tmp_path, by) == ["t_b"]


@kills(3)
def test_a_lane_that_led_alone_early_and_trails_by_the_instant_does_not_hold_it(tmp_path: Path):
    """Counts are read at the instant, not along the way: c has the most at the instant."""
    by = dict(t_a_chop=1000, t_b_chop=1000, t_c_chop=4000, t_m_chop=1000)
    assert lead_of(tmp_path, by) == ["t_c"]


@kills(6)
def test_the_first_pattern_decides_whatever_the_later_ones_hold(tmp_path: Path):
    """a leads on chop (2 against 1); b has far more hauls. Counting the two patterns together would make b the lead."""
    by = dict(t_a_chop=1000, t_b_chop=500, t_a_haul=0, t_b_haul=6000)
    n = counts(tmp_path, by, casts=BOTH)
    assert (n["t_a_chop"], n["t_b_chop"], n["t_b_haul"]) == (2, 1, 12)
    assert lead_of(tmp_path, by, casts=BOTH) == ["t_a"]


@kills(6, 7)
def test_a_tie_on_the_first_pattern_goes_to_the_second_among_the_tied_only(tmp_path: Path):
    """a and b tie on chop (3), c trails (1) but has the most hauls: c is out for good, so b (2 hauls) beats a (1)."""
    by = dict(t_a_chop=1500, t_b_chop=1500, t_c_chop=500, t_a_haul=500, t_b_haul=1000, t_c_haul=4000)
    n = counts(tmp_path, by, casts=BOTH)
    assert [n[f"t_{x}_chop"] for x in "abc"] == [3, 3, 1] and [n[f"t_{x}_haul"] for x in "abc"] == [1, 2, 8]
    assert lead_of(tmp_path, by, casts=BOTH) == ["t_b"]


@kills(2)
def test_a_tie_through_every_pattern_goes_to_the_earliest_declared_not_the_latest_joined(tmp_path: Path):
    """t_c joins first and t_m last; a and b tie on both patterns and a is declared first."""
    by = dict(t_a_chop=2000, t_b_chop=2000, t_c_chop=500, t_a_haul=1000, t_b_haul=1000)
    n = counts(tmp_path, by, casts=BOTH)
    assert (n["t_a_chop"], n["t_b_chop"], n["t_a_haul"], n["t_b_haul"]) == (4, 4, 2, 2)
    assert lead_of(tmp_path, by, casts=BOTH) == ["t_a"]


@kills(2)
def test_a_tie_among_the_last_declared_still_goes_to_the_earliest_of_them(tmp_path: Path):
    by = dict(t_a_chop=500, t_b_chop=2000, t_c_chop=2000, t_m_chop=2000)
    assert lead_of(tmp_path, by) == ["t_b"]


@kills(2)
def test_nobody_having_any_is_a_tie_at_none_and_goes_to_the_earliest_declared(tmp_path: Path):
    assert all(v == 0 for k, v in counts(tmp_path, {}).items() if k.endswith(("chop", "haul")))
    assert lead_of(tmp_path, {}) == ["t_a"]
    assert lead_of(tmp_path, {}, casts=BOTH) == ["t_a"]


@kills(1)
def test_a_pooled_lanes_cards_are_never_counted_for_its_members(tmp_path: Path):
    """m is in t_p's crew and t_p's chop completes 8 times; m's own count is 0, a's is 2: a holds it."""
    by = dict(t_a_chop=1000, t_p_chop=4000)
    n = counts(tmp_path, by, crew=True)
    assert (n["t_p_chop"], n["t_m_chop"], n["t_a_chop"]) == (8, 0, 2)
    assert lead_of(tmp_path, by, crew=True) == ["t_a"]


@kills(1)
def test_the_pooled_lane_is_never_the_one_cast(tmp_path: Path):
    by = dict(t_p_chop=9000)
    assert counts(tmp_path, by, crew=True)["t_p_chop"] > 0
    assert lead_of(tmp_path, by, crew=True) == ["t_a"]


def test_the_cast_reads_only_which_lane_so_the_lead_is_one_lane(tmp_path: Path):
    assert len(lead_of(tmp_path, dict(t_a_chop=1000, t_b_chop=3000), casts=LEAD)) == 1
