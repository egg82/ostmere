"""Blind contract tests of View.goal_rows (api/CONTRACT.txt, "Goal rows"; api/goalrows.py and setrates.py public
surface only). Written from the contract, never the implementation, and checked against real engine saves: a row's
`lands_at` is judged by advancing the engine itself, its `per_hour` by the engine's own ledger line.

Worlds are tests/engine_contract/spent_world.py's: every card runs one item a second at a full share, a store is
Q units to an item, and `standard()` is an eating card (costs pool p, makes y) beside makers of z and w."""
from dataclasses import replace

from ashfall_app.api import goal_models as g
from ashfall_app.api.goalrows import goal_rows
from ashfall_app.engine import (
    QUANTITY_SCALE as Q, CardId, PacingCurve, Rules, Save, SkillId, StoreId, TapCard, View, advance, decide, new_save,
    value, view, xp,
)
from tests.engine_contract.spent_world import (
    BIG, EAT, P, P2, PS, R1, R2, Y, Z, eater, maker, mixed, plain, standard, world,
)

K = SkillId("k")
EAT2, MK = CardId("eat2"), CardId("mk")


def store_goal(store: StoreId, target: int) -> g.Goal:
    return g.Goal(kind=g.GoalKind.STORE, store=str(store), card=None, skill=None, target=target, value=None, at=None,
                  feeds=[])


def level_goal(skill: SkillId, target: int) -> g.Goal:
    return g.Goal(kind=g.GoalKind.LEVEL, store=None, card=None, skill=str(skill), target=target, value=None, at=None,
                  feeds=[])


def rows_at(save: Save, rules: Rules, t: int, goals: list[g.Goal]) -> tuple[View, list[g.GoalRow]]:
    s = advance(save, rules, t)
    v = view(s, rules)
    return v, goal_rows(s, rules, v, goals)


def only_store_row(rows: list[g.GoalRow], store: StoreId) -> g.GoalRow:
    found = [r for r in rows if r.kind == g.GoalKind.STORE and r.store == str(store)]
    assert len(found) == 1
    return found[0]


def net(v: View, store: StoreId) -> int:
    return next(line.net_per_hour for line in v.ledger if line.store == store)


def skill_world() -> tuple[Rules, Save]:
    """R1 makes z at 25% and trains k; level 2 at 3 xp-items, level 3 at 6."""
    cards = (replace(maker(R1, Z), skill=K, xp_per_hour=PS), *plain(R2))
    r = replace(world(*cards), curve=PacingCurve((3 * Q, 6 * Q)))
    return r, mixed(r, [(R1, 2500), (R2, 1500)])


# ---- lands_at and per_hour ----

def test_store_row_lands_when_the_engine_reaches_the_target():
    r, s = standard()
    target = 1000 * Q
    v, rows = rows_at(s, r, 200, [store_goal(Z, target)])
    row = only_store_row(rows, Z)
    assert row.target == target
    assert row.lands_at is not None and row.lands_at > v.time
    assert value(s, r, Z, row.lands_at) >= target
    assert value(s, r, Z, row.lands_at - 1) < target


def test_store_row_per_hour_is_the_ledger_net_without_a_tap():
    r, s = standard()
    v, rows = rows_at(s, r, 200, [store_goal(Z, 1000 * Q)])
    assert only_store_row(rows, Z).per_hour == net(v, Z) > 0


def test_a_falling_store_never_lands_and_reports_its_negative_net():
    r, s = standard()
    v, rows = rows_at(s, r, 50, [store_goal(P, 100 * Q)])
    row = only_store_row(rows, P)
    assert row.per_hour == net(v, P) < 0
    assert row.lands_at is None


def test_a_zero_rate_never_lands():
    r, s = standard()
    v, rows = rows_at(s, r, 200, [store_goal(Y, 1000 * Q)])
    row = only_store_row(rows, Y)
    assert net(v, Y) == 0
    assert row.per_hour == 0
    assert row.lands_at is None


def test_a_goal_already_met_lands_now():
    r, s = standard()
    v, rows = rows_at(s, r, 200, [store_goal(Z, 1)])
    assert only_store_row(rows, Z).lands_at == v.time == 200


def test_a_met_goal_lands_now_even_at_a_zero_rate():
    r, s = standard()
    v, rows = rows_at(s, r, 200, [store_goal(Y, 1)])
    assert only_store_row(rows, Y).lands_at == v.time


def test_a_target_over_the_cap_never_lands():
    r, s = standard()
    _, rows = rows_at(s, r, 200, [store_goal(Z, BIG + 1)])
    row = only_store_row(rows, Z)
    assert row.per_hour > 0
    assert row.lands_at is None


def test_a_target_at_the_cap_lands():
    r, s = standard()
    _, rows = rows_at(s, r, 200, [store_goal(Z, BIG)])
    row = only_store_row(rows, Z)
    assert row.lands_at is not None
    assert value(s, r, Z, row.lands_at) >= BIG
    assert value(s, r, Z, row.lands_at - 1) < BIG


def test_lands_at_rounds_up_to_the_second():
    """One item short of z at 1 item per 4 s: it lands on the 4th second, not the 3rd."""
    r, s = standard()
    base = advance(s, r, 200)
    have = value(s, r, Z, 200)
    _, rows = rows_at(s, r, 200, [store_goal(Z, have + 1)])
    lands = only_store_row(rows, Z).lands_at
    assert lands is not None and lands >= 200 + 1
    assert value(base, r, Z, lands) >= have + 1
    assert value(base, r, Z, lands - 1) < have + 1


# ---- which goals are rows ----

def test_card_and_clock_goals_are_never_rows():
    r, s = standard()
    card = g.Goal(kind=g.GoalKind.CARD, store=None, card=str(R1), skill=None, target=3, value=None, at=None, feeds=[])
    clock = g.Goal(kind=g.GoalKind.CLOCK, store=None, card=None, skill=None, target=0, value=None, at=900, feeds=[])
    _, rows = rows_at(s, r, 200, [card, clock, store_goal(Z, 1000 * Q)])
    assert [(x.kind, x.store) for x in rows if x.kind != g.GoalKind.LEVEL] == [(g.GoalKind.STORE, str(Z))]


def test_store_and_level_goals_keep_their_order_then_each_skills_next_level():
    r, s = skill_world()
    goals = [store_goal(StoreId("w"), 50 * Q), level_goal(K, 3), store_goal(Z, 50 * Q)]
    _, rows = rows_at(s, r, 10, goals)
    keys = [(x.kind, x.store, x.skill, x.target) for x in rows]
    assert keys[:3] == [(g.GoalKind.STORE, "w", None, 50 * Q), (g.GoalKind.LEVEL, None, "k", 3),
                        (g.GoalKind.STORE, "z", None, 50 * Q)]
    assert keys[3:] == [(g.GoalKind.LEVEL, None, "k", 2)]


def test_a_skill_with_a_story_level_goal_on_its_next_level_gets_one_row():
    r, s = skill_world()
    _, rows = rows_at(s, r, 10, [level_goal(K, 2)])
    assert [(x.kind, x.skill, x.target) for x in rows] == [(g.GoalKind.LEVEL, "k", 2)]


def test_a_skill_row_lands_when_the_engine_gains_the_xp():
    r, s = skill_world()
    v, rows = rows_at(s, r, 10, [])
    (row,) = rows
    assert (row.kind, row.skill, row.store, row.target) == (g.GoalKind.LEVEL, "k", None, 2)
    assert row.per_hour > 0
    assert row.lands_at is not None and row.lands_at > v.time
    need = 3 * Q
    assert xp(s, r, K, row.lands_at) >= need
    assert xp(s, r, K, row.lands_at - 1) < need


def test_a_skill_that_gains_nothing_still_has_a_row_that_never_lands():
    r, s = standard()
    _, rows = rows_at(s, r, 200, [])
    (row,) = rows
    assert (row.kind, row.skill, row.target) == (g.GoalKind.LEVEL, "k", 2)
    assert row.per_hour == 0 and row.lands_at is None


def test_no_goals_and_no_skills_gives_no_rows():
    r = replace(world(*plain(R1)), skills=())
    s = mixed(r, [(R1, 2500)])
    assert goal_rows(s, r, view(s, r), []) == []


# ---- limit ----

def test_limit_is_absent_when_nothing_binds():
    r, s = standard()
    _, rows = rows_at(s, r, 200, [store_goal(Z, 1000 * Q)])
    assert only_store_row(rows, Z).limit is None


def test_limit_is_absent_before_the_pool_runs_dry():
    r, s = standard()
    _, rows = rows_at(s, r, 50, [store_goal(Y, 1000 * Q)])
    assert only_store_row(rows, Y).limit is None


def test_a_dry_store_binds_the_goal_it_starves_with_nothing_coming_in():
    r, s = standard()
    _, rows = rows_at(s, r, 200, [store_goal(Y, 1000 * Q)])
    row = only_store_row(rows, Y)
    assert row.limit == g.GoalLimit(store="p", in_per_hour=0)


def test_limit_reports_the_makers_inflow_of_the_dry_store():
    """A maker of p at 5% trickles in less than the eater (40%) spends: p is dry and its in-rate is the maker's line."""
    r = world(eater(), maker(MK, P), *plain(R1))
    s = mixed(r, [(EAT, 4000), (MK, 500), (R1, 1500)])
    v, rows = rows_at(s, r, 200, [store_goal(Y, 1000 * Q)])
    row = only_store_row(rows, Y)
    assert row.limit is not None and row.limit.store == "p"
    assert row.limit.in_per_hour == net(v, P) > 0


def test_a_goal_the_dry_store_does_not_feed_is_not_bound_by_it():
    r = world(eater(), maker(MK, P), *plain(R1))
    s = mixed(r, [(EAT, 4000), (MK, 500), (R1, 1500)])
    _, rows = rows_at(s, r, 200, [store_goal(Z, 1000 * Q)])
    assert only_store_row(rows, Z).limit is None


def test_of_two_dry_stores_the_first_in_running_order_binds():
    r = world(eater(), eater(EAT2, P2), *plain(R1))
    s = mixed(r, [(EAT, 3000), (EAT2, 3000), (R1, 2000)])
    _, rows = rows_at(s, r, 200, [store_goal(Y, 1000 * Q)])
    assert only_store_row(rows, Y).limit == g.GoalLimit(store="p", in_per_hour=0)


def test_with_the_first_store_stocked_the_second_dry_store_binds():
    r = world(eater(), eater(EAT2, P2), *plain(R1), initial={P: BIG})
    s = mixed(r, [(EAT, 3000), (EAT2, 3000), (R1, 2000)])
    _, rows = rows_at(s, r, 200, [store_goal(Y, 1000 * Q)])
    assert only_store_row(rows, Y).limit == g.GoalLimit(store="p2", in_per_hour=0)


# ---- a tap of the hands is set aside ----

def test_a_tap_running_does_not_change_the_rows():
    r, s = standard()
    goals = [store_goal(Z, 1000 * Q), store_goal(Y, 1000 * Q), level_goal(K, 2)]
    _, plain_rows = rows_at(s, r, 200, goals)
    s2 = advance(s, r, 200)
    tapped = decide(s2, r, 200, TapCard(R1))
    v = view(tapped, r)
    assert net(v, Z) != net(view(s2, r), Z), "control: the tap must move the ledger or this proves nothing"
    assert goal_rows(tapped, r, v, goals) == plain_rows


def test_rows_of_a_save_with_no_running_mix_never_land_what_nothing_makes():
    r = world(eater(), *plain(R1))
    s = new_save(r)
    v = view(s, r)
    rows = goal_rows(s, r, v, [store_goal(Z, Q)])
    row = only_store_row(rows, Z)
    assert row.per_hour == 0 and row.lands_at is None
