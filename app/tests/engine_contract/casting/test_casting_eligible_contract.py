"""Who may be cast (api/contract/casting.txt, "CASTING", "The pick" steps 1 and 2, and the order of an outcome's parts):
a candidate that has joined, has not left and holds no cast feature; a lane that joins in the cast's own outcome is
eligible. Written blind from that part."""
from pathlib import Path

from casting_world import LEAD, at, held, kills, lead_of, rules_of

SCOUT = '{ role = "scout", patterns = ["{lane}_haul"] }'
TWO = f'{LEAD}, {SCOUT}'


@kills(9)
def test_a_lane_that_has_not_joined_is_not_eligible_even_when_it_is_declared_first(tmp_path: Path):
    """Nobody has any, so the tie goes to the earliest declared of the joined: a joins after the cast, so b."""
    assert lead_of(tmp_path, {}, joins={"t_a": 300}) == ["t_b"]


@kills(9)
def test_when_no_candidate_has_joined_no_one_is_cast_and_the_role_stays_open(tmp_path: Path):
    late = {p: 300 for p in ("t_a", "t_b", "t_c", "t_m")}
    r = rules_of(tmp_path, joins=late)
    assert held(at(r, {}), r) == []
    assert held(at(r, {}, 1000), r) == []


@kills(10)
def test_a_lane_that_has_left_is_not_eligible(tmp_path: Path):
    assert lead_of(tmp_path, {}, leaves={"t_a": 100}) == ["t_b"]
    assert lead_of(tmp_path, dict(t_a_chop=4000, t_b_chop=1000), leaves={"t_a": 100}) == ["t_b"]


@kills(11)
def test_a_lane_that_holds_another_role_is_not_eligible_and_the_next_best_is_cast(tmp_path: Path):
    """Two outcomes. b leads on both chop and haul; the second role finds b holding the first and takes a, the next best."""
    by = dict(t_a_chop=1000, t_b_chop=3000, t_a_haul=2000, t_b_haul=3000)
    scout_later = ('[[triggers]]\nid = "t_scout"\nwhen = { test = "after_time", value = 210 }\n'
                   f'outcome = {{ casts = [{SCOUT}] }}\n\n')
    r = rules_of(tmp_path, extra=scout_later)
    s = at(r, by, 230)
    assert held(s, r, "lead") == ["t_b"] and held(s, r, "scout") == ["t_a"]


@kills(11)
def test_casts_in_one_outcome_land_in_list_order_and_a_lane_the_first_takes_is_out_for_the_second(tmp_path: Path):
    by = dict(t_a_chop=1000, t_b_chop=3000, t_a_haul=2000, t_b_haul=3000)
    r = rules_of(tmp_path, casts=TWO)
    s = at(r, by)
    assert held(s, r, "lead") == ["t_b"] and held(s, r, "scout") == ["t_a"]


@kills(11)
def test_a_lane_holds_at_most_one_role_so_the_listed_order_decides_who_gets_the_better_claim(tmp_path: Path):
    """Reversed list: scout is cast first and takes b (most hauls), so lead goes to a."""
    by = dict(t_a_chop=1000, t_b_chop=3000, t_a_haul=2000, t_b_haul=3000)
    r = rules_of(tmp_path, casts=f'{SCOUT}, {LEAD}')
    s = at(r, by)
    assert held(s, r, "scout") == ["t_b"] and held(s, r, "lead") == ["t_a"]


@kills(13)
def test_a_lane_that_joins_in_the_casting_outcome_is_eligible_with_no_completions(tmp_path: Path):
    """Nobody else has joined when the outcome lands; the only person it can name is the one it brings."""
    r = rules_of(tmp_path, joins={"t_a": 900, "t_b": 900, "t_c": 900, "t_m": -1}, casts=LEAD, cast_extra=', joins = ['
              '{ lane = "t_m", mix = "town:main", card = "t_m_chop", own_split = true }], '
              'unlocks = [{ unlock_kind = "card", id = "t_m_chop" }]')
    assert held(at(r, {}), r) == ["t_m"]
