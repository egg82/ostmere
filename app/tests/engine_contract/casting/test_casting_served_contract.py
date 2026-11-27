"""What the content serves of a cast (api/contract/casting.txt, "CASTING", "Served"): Content.cast_infos, one CastInfo per
role cast by any outcome in content order, its lanes the role's candidates in declared order with the feature each cast
unlocks. Written blind from that part."""
from pathlib import Path

from casting_world import LEAD, PEOPLE, at, feature, game, held, kills, rules_of

SCOUT = '{ role = "scout", patterns = ["{lane}_haul"] }'
LATER = ('[[triggers]]\nid = "t_scout"\nwhen = { test = "after_time", value = 210 }\n'
         f'outcome = {{ casts = [{SCOUT}] }}\n\n')


def infos(tmp_path: Path, **kw):
    return game(tmp_path, **kw).content().cast_infos


@kills(21)
def test_one_cast_info_per_role_lists_the_single_person_lanes_in_declared_order_with_their_features(tmp_path: Path):
    [lead] = infos(tmp_path)
    assert lead.role == "lead"
    assert [(x.lane, x.feature) for x in lead.lanes] == [(p, f"lead_{p}") for p in PEOPLE]


@kills(21)
def test_the_pooled_lane_the_station_and_the_hands_are_no_candidates(tmp_path: Path):
    [lead] = infos(tmp_path)
    assert {"t_p", "t_pot", "hands"}.isdisjoint(x.lane for x in lead.lanes)


@kills(21)
def test_roles_are_served_in_content_order(tmp_path: Path):
    assert [i.role for i in infos(tmp_path, extra=LATER)] == ["lead", "scout"]
    assert [i.role for i in infos(tmp_path, casts=SCOUT, extra=LATER.replace("scout", "lead").replace(SCOUT, LEAD))] == ["scout", "lead"]


def test_a_content_that_casts_nothing_serves_no_cast_info(tmp_path: Path):
    assert infos(tmp_path, casts=None) == []


@kills(21)
def test_the_feature_the_view_holds_after_the_cast_is_one_of_the_served_features(tmp_path: Path):
    r = rules_of(tmp_path)
    [lead] = infos(tmp_path)
    s = at(r, dict(t_a_chop=1000, t_b_chop=3000))
    held_now = [x.lane for x in lead.lanes if feature("lead", x.lane) in s.unlocked]
    assert held_now == held(s, r) == ["t_b"]
