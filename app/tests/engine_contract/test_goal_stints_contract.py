"""Goal stints (api/CONTRACT.txt "GOAL STINTS", engine DESIGN.txt "Queue mix"), blind: written from those two sections and
the public engine surface alone. A stint is QueueEntry(SwitchMix(m), until) with the until of a goal row: a store at an
amount, or a skill at a level counted across prestige phases ((phase - 1) * (top_level - 1) + level).

World: the player's own mix MO makes S1; the stint mix MS makes S0 at 1000/s from 0, so "S0 >= 100_000" lands at second
100 and the stint pops there. Driven through decide / advance and read through view, segment and the save."""
from dataclasses import replace

import pytest

from ashfall_app.engine import (
    BP, AfterTime, AtLeast, CardCount, CardDef, CardId, CardShare, DeleteMix, Flow, InvalidVerbError, Mix, MixId,
    NodeDef, NodeId, Order, PacingCurve, Prestige, PrestigeDef, QueueEntry, Rules, Save, SaveMix, SetOrders, SetQueue,
    SkillDef, SkillId, SkillLevel, StandingDef, StoreCap, StoreDef, StoreId, StoreValue, SwitchMix, TapCard, ActionId,
    advance, decide, new_save, segment, view,
)

S0, S1, S2, S3 = (StoreId(f"s{i}") for i in range(4))
C_OWN, C_STINT, C_ORDER, C_STINT2, C_OWN2, C_DEAD, C_TAP = (CardId(f"c{i}") for i in range(7))
MO, MS, MR, MS2, MP, MD = (MixId(n) for n in ("own", "stint", "order", "stint2", "player2", "dead"))
K = SkillId("k")
CAP = 10 * 3_600_000
GOAL = 100_000
"""S0 at 1000 units a second: reached at second 100 by MS alone."""


def _rules(*, skill: bool = False) -> Rules:
    cards = (
        CardDef(C_OWN, 60, makes=(Flow(S1, 1000),)), CardDef(C_STINT, 60, makes=(Flow(S0, 1000),)),
        CardDef(C_ORDER, 60, makes=(Flow(S2, 1000),)), CardDef(C_STINT2, 60, makes=(Flow(S3, 1000),)),
        CardDef(C_OWN2, 60, makes=(Flow(S1, 2000),)), CardDef(C_DEAD, 100, cap=1), CardDef(C_TAP, 30),
    )
    extra: dict[str, object] = {}
    if skill:
        extra = dict(
            standing=(StandingDef(ActionId("train"), skill=K, xp_per_hour=1),), skills=(SkillDef(K),),
            prestige=PrestigeDef(top_level=3, carry_window_s=1000, menu_size=2),
            nodes=(NodeDef(NodeId("n"), K, StoreCap(S1), ranks=5, per_rank_bp=100),))
    base = Rules(
        stores=tuple(StoreDef(s, CAP) for s in (S0, S1, S2, S3)), skills=(), standing=(),
        curve=PacingCurve((100, 300, 700)), cards=cards)
    return replace(base, **extra)


def _mix(mix: MixId, card: CardId) -> SaveMix:
    return SaveMix(Mix(mix, (CardShare(card, BP),)))


def _world(*, skill: bool = False) -> tuple[Rules, Save]:
    """Mixes saved, the player's own MO active, nothing queued, at time 0."""
    rules = _rules(skill=skill)
    s = new_save(rules)
    for v in (_mix(MO, C_OWN), _mix(MS, C_STINT), _mix(MR, C_ORDER), _mix(MS2, C_STINT2), _mix(MP, C_OWN2),
              _mix(MD, C_DEAD), SwitchMix(MO)):
        s = decide(s, rules, 0, v)
    return rules, s


def _store(store: StoreId, amount: int) -> AtLeast:
    return AtLeast(StoreValue(store), amount, amount)


def _stint(mix: MixId, store: StoreId = S0, amount: int = GOAL) -> QueueEntry:
    return QueueEntry(SwitchMix(mix), _store(store, amount))


def _queued(s: Save, rules: Rules, *entries: QueueEntry, at: int | None = None) -> Save:
    return decide(s, rules, s.time if at is None else at, SetQueue(entries))


def _running(s: Save, rules: Rules) -> MixId | None:
    return view(s, rules).running_mix


def _met_world() -> tuple[Rules, Save]:
    """S0 holds GOAL (and more) at second 150 with the player back on MO: a goal already met."""
    rules, s = _world()
    s = decide(s, rules, 0, SwitchMix(MS))
    s = decide(advance(s, rules, 120), rules, 120, SwitchMix(MO))
    s = advance(s, rules, 150)
    assert segment(s, rules, S0).rate == 0 and view(s, rules).running_mix == MO
    return rules, s


# ---- which entry controls, the stint's mix and the player's ------------------------------------------------------

def test_a_stint_runs_its_mix_while_the_players_own_stays_active():
    """Controlling: running mix is the stint's, save.active is never written by the queue."""
    rules, s = _world()
    assert _running(s, rules) == MO
    s = _queued(s, rules, _stint(MS))
    assert _running(s, rules) == MS and s.active == MO and view(s, rules).mix_order is None
    assert segment(s, rules, S0).rate == 1000 and segment(s, rules, S1).rate == 0
    mid = advance(s, rules, 60)
    assert _running(mid, rules) == MS and mid.active == MO and mid.queue == s.queue


def test_the_first_live_entry_controls_and_a_dead_one_is_passed_over_and_kept():
    """A stint on a greyed mix (its card completed) is dead: kept in the queue, the entry behind it controls."""
    rules, s = _world()
    s = decide(s, rules, 0, TapCard(C_DEAD))
    s = advance(s, rules, 100)
    assert view(s, rules).greyed_mixes == (MD,)
    dead = _stint(MD, S3, GOAL)
    s = _queued(s, rules, dead, _stint(MS, S0, 500_000))
    assert s.queue[0] == dead and len(s.queue) == 2
    assert _running(s, rules) == MS and s.active == MO
    later = advance(s, rules, 200)
    assert later.queue[0] == dead and _running(later, rules) == MS


def test_the_second_entry_waits_while_the_first_controls():
    rules, s = _world()
    s = _queued(s, rules, _stint(MS), _stint(MS2, S3, 10**6))
    assert _running(s, rules) == MS and segment(s, rules, S3).rate == 0
    assert _running(advance(s, rules, 99), rules) == MS


# ---- popping -----------------------------------------------------------------------------------------------------

def test_a_stint_pops_at_exactly_the_instant_its_goal_lands_and_the_players_mix_returns():
    rules, s = _world()
    s = _queued(s, rules, _stint(MS))
    before = advance(s, rules, 99)
    assert len(before.queue) == 1 and _running(before, rules) == MS
    at = advance(s, rules, 100)
    assert at.queue == () and _running(at, rules) == MO and at.active == MO
    assert segment(at, rules, S0).rate == 0 and segment(at, rules, S1).rate == 1000
    assert advance(s, rules, 5000).queue == ()


def test_a_goal_already_met_pops_in_the_decision_that_sets_it():
    rules, s = _met_world()
    s = _queued(s, rules, _stint(MS))
    assert s.queue == () and _running(s, rules) == MO and s.active == MO


def test_a_met_stint_is_passed_by_and_the_next_entry_controls_at_once():
    rules, s = _met_world()
    s = _queued(s, rules, _stint(MS), _stint(MS2, S3, 50_000))
    assert s.queue == (_stint(MS2, S3, 50_000),)
    assert _running(s, rules) == MS2 and s.active == MO


def test_the_next_stint_controls_after_a_pop_and_the_player_mix_returns_after_the_last():
    rules, s = _world()
    s = _queued(s, rules, _stint(MS), _stint(MS2, S3, 50_000))
    a = advance(s, rules, 100)
    assert a.queue == (_stint(MS2, S3, 50_000),) and _running(a, rules) == MS2 and a.active == MO
    b = advance(s, rules, 149)
    assert _running(b, rules) == MS2
    c = advance(s, rules, 150)
    assert c.queue == () and _running(c, rules) == MO and c.active == MO


def test_after_the_pop_a_tap_entry_behind_it_taps():
    rules, s = _world()
    tap = QueueEntry(TapCard(C_TAP), AtLeast(CardCount(C_TAP), 1, 1))
    s = _queued(s, rules, _stint(MS), tap)

    def lane(save: Save) -> CardId | None:
        return view(save, rules).lanes[0].card

    assert lane(s) is None and lane(advance(s, rules, 99)) is None
    after = advance(s, rules, 100)
    assert after.queue == (tap,) and lane(after) == C_TAP and _running(after, rules) == MO


def test_clearing_the_queue_hands_the_mix_back_before_the_goal_lands():
    rules, s = _world()
    s = _queued(s, rules, _stint(MS))
    mid = _queued(advance(s, rules, 40), rules)
    assert mid.queue == () and _running(mid, rules) == MO and mid.active == MO


# ---- an order's mix over a stint ----------------------------------------------------------------------------------

def _order_over_stint() -> tuple[Rules, Save]:
    rules, s = _world()
    s = decide(s, rules, 0, SetOrders((Order(AfterTime(50), SwitchMix(MR)),)))
    return rules, _queued(s, rules, _stint(MS))


def test_an_orders_mix_takes_the_hands_from_a_stint_and_the_stint_returns_when_it_lets_go():
    rules, s = _order_over_stint()
    assert _running(advance(s, rules, 49), rules) == MS
    on = advance(s, rules, 50)
    v = view(on, rules)
    assert v.running_mix == MR and v.mix_order == 0 and on.active == MO and len(on.queue) == 1
    off = decide(advance(s, rules, 70), rules, 70, SetOrders(()))
    assert _running(off, rules) == MS and off.queue == s.queue and off.active == MO


def test_a_stint_still_pops_at_its_goal_while_an_orders_mix_runs():
    """The queue head pops on its until whoever runs; S0 stays at the value it had at the order's takeover."""
    rules, s = _order_over_stint()
    mid = advance(s, rules, 80)
    assert _running(mid, rules) == MR and len(mid.queue) == 1
    # Under the order S0 is frozen at 50_000; raise it to the goal by a rule change that keeps the order on.
    lifted = decide(mid, rules, 80, SaveMix(Mix(MR, (CardShare(C_ORDER, 5000), CardShare(C_STINT, 5000)))))
    assert _running(lifted, rules) == MR and len(lifted.queue) == 1
    popped = advance(lifted, rules, 400)
    assert popped.queue == () and _running(popped, rules) == MR
    free = decide(popped, rules, 400, SetOrders(()))
    assert _running(free, rules) == MO and free.active == MO


# ---- the player's switch and delete while a stint runs ------------------------------------------------------------

def test_the_players_switch_during_a_stint_changes_only_the_active_mix():
    rules, s = _world()
    s = _queued(s, rules, _stint(MS))
    sw = decide(advance(s, rules, 30), rules, 30, SwitchMix(MP))
    assert sw.active == MP and _running(sw, rules) == MS and sw.queue == s.queue
    assert segment(sw, rules, S0).rate == 1000
    after = advance(sw, rules, 100)
    assert after.queue == () and after.active == MP and _running(after, rules) == MP
    assert segment(after, rules, S1).rate == 2000


def test_deleting_the_active_mix_during_a_stint_leaves_none_active_and_the_stint_running():
    rules, s = _world()
    s = _queued(s, rules, _stint(MS))
    d = decide(advance(s, rules, 30), rules, 30, DeleteMix(MO))
    assert d.active is None and _running(d, rules) == MS and segment(d, rules, S0).rate == 1000
    after = advance(d, rules, 100)
    assert after.queue == () and after.active is None and _running(after, rules) is None


def test_deleting_a_mix_a_queue_entry_names_is_refused_and_changes_nothing():
    rules, s = _world()
    s = _queued(s, rules, _stint(MS))
    with pytest.raises(InvalidVerbError):
        decide(s, rules, 10, DeleteMix(MS))
    assert _running(advance(s, rules, 10), rules) == MS


# ---- an unreachable goal -------------------------------------------------------------------------------------------

@pytest.mark.parametrize("entry", [
    pytest.param(_stint(MS, S0, CAP + 1), id="store-over-cap"),
    pytest.param(_stint(MS, S3, 1), id="store-the-mix-never-moves"),
])
def test_an_unreachable_goal_keeps_running_blocks_the_entries_behind_and_is_never_removed(entry: QueueEntry):
    rules, s = _world()
    behind = _stint(MS2, S3, 10**6)
    s = _queued(s, rules, entry, behind)
    far = advance(s, rules, 10**6)
    assert far.queue == (entry, behind) and _running(far, rules) == MS and far.active == MO
    freed = _queued(far, rules, behind)
    assert _running(freed, rules) == MS2


def test_an_unreachable_stint_pops_once_the_rates_change_and_the_goal_lands():
    rules, s = _world()
    s = _queued(s, rules, _stint(MS, S3, 50_000))
    stuck = advance(s, rules, 200)
    assert len(stuck.queue) == 1 and _running(stuck, rules) == MS and segment(stuck, rules, S3).rate == 0
    changed = decide(stuck, rules, 200, SaveMix(Mix(MS, (CardShare(C_STINT2, BP),))))
    assert _running(changed, rules) == MS and segment(changed, rules, S3).rate == 1000
    assert len(advance(changed, rules, 249).queue) == 1
    done = advance(changed, rules, 250)
    assert done.queue == () and _running(done, rules) == MO


def test_a_falling_store_goal_is_not_an_error_and_does_not_pop():
    rules, s = _world()
    s = decide(s, rules, 0, _mix(MD, C_OWN))
    s = _queued(s, rules, _stint(MS, S1, 1_000))  # S1 sits at 0 under the stint and never rises
    far = advance(s, rules, 10**5)
    assert len(far.queue) == 1 and _running(far, rules) == MS


# ---- a skill goal, counted across prestige phases -------------------------------------------------------------------

def test_a_skill_stint_counts_levels_across_phases_and_pops_when_the_counted_level_lands():
    """top_level 3, XP 1/s, phases of 300 XP: phase 2's level 2 is counted (2 - 1) * 2 + 2 = 4 and lands at XP 400 once
    the skill has prestiged at 300."""
    rules, s = _world(skill=True)
    counted = AtLeast(SkillLevel(K), 4, 4)
    stint = QueueEntry(SwitchMix(MS), counted)
    s = _queued(s, rules, stint)
    mid = advance(s, rules, 299)
    assert mid.queue == (stint,) and _running(mid, rules) == MS
    clicked = decide(advance(s, rules, 300), rules, 300, Prestige(K, NodeId("n")))
    assert view(clicked, rules).skills[0].level == 1 and clicked.queue == (stint,)
    assert _running(advance(clicked, rules, 399), rules) == MS
    done = advance(clicked, rules, 400)
    assert done.queue == () and _running(done, rules) == MO and done.active == MO


def test_a_skill_stint_for_a_later_phase_is_not_met_by_the_same_level_number_in_phase_one():
    """Counted level 4 is not in reach at phase 1's top (level 3) however long the skill trains unclicked: the entry
    keeps controlling, no error."""
    rules, s = _world(skill=True)
    s = _queued(s, rules, QueueEntry(SwitchMix(MS), AtLeast(SkillLevel(K), 4, 4)))
    far = advance(s, rules, 700)
    assert len(far.queue) == 1 and _running(far, rules) == MS


def test_a_skill_stint_set_after_the_click_is_met_at_once_when_the_counted_level_already_holds():
    """After the click at 300 the skill's counted level is 3, so a goal of counted 3 pops in the deciding call."""
    rules, s = _world(skill=True)
    c = decide(advance(s, rules, 300), rules, 300, Prestige(K, NodeId("n")))
    c = _queued(c, rules, QueueEntry(SwitchMix(MS), AtLeast(SkillLevel(K), 3, 3)))
    assert c.queue == () and _running(c, rules) == MO
