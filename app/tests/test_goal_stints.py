"""Goal stints (CONTRACT.txt, "Goal stints"): a queue entry switching to a mix until a goal row's `until`. The row's
`until` holds from the instant its lands_at names while the rates hold, and the entry pops there, giving the player's
own mix back (engine DESIGN.txt, "Queue mix")."""
from ashfall_app import engine as e
from ashfall_app.api import decision_models as w
from ashfall_app.api import goal_models as g
from ashfall_app.api.convert import from_condition
from ashfall_app.api.goalrows import goal_rows
from ashfall_app.engine import BP, CardId, CardShare, Mix, MixId, QueueEntry, SaveMix, SetQueue, SwitchMix
from ashfall_app.engine.conditions import is_true
from ashfall_app.engine.plan import running_mix_id
from ashfall_app.engine.units import units
from tests.prestige_contract import prestige_world as pw
from tests.test_goal_rows import plank_goal, running, world

STINT = MixId("stint")


def _row(r: e.Rules, s: e.Save, kind: g.GoalKind, goals: list[g.Goal]) -> g.GoalRow:
    return next(row for row in goal_rows(s, r, e.view(s, r), goals) if row.kind is kind)


def _stint(r: e.Rules, s: e.Save, shares: dict[str, int], kind: g.GoalKind, goals: list[g.Goal]
           ) -> tuple[e.Save, g.GoalRow]:
    """`s` with mix STINT saved and queued until the `kind` row it gets when it runs, read as the editor's dry run
    reads it (the mix run now), and that row."""
    mix = Mix(STINT, tuple(CardShare(CardId(c), bp) for c, bp in shares.items()))
    saved = e.decide(s, r, s.time, SaveMix(mix))
    row = _row(r, e.decide(saved, r, s.time, SwitchMix(STINT)), kind, goals)
    entry = QueueEntry(SwitchMix(STINT), from_condition(row.until, r))
    return e.decide(saved, r, s.time, SetQueue((entry,))), row


def test_a_level_stint_runs_its_mix_until_the_row_lands_then_gives_the_players_mix_back() -> None:
    r, s = world(logs=40)
    s = running(r, s, {"fell": BP})
    queued, row = _stint(r, s, {"chop": BP}, g.GoalKind.LEVEL, [])
    assert row.lands_at is not None and row.until.value == row.target == 2
    before = e.advance(queued, r, row.lands_at - 1)
    assert running_mix_id(before, r) == STINT and len(before.queue) == 1
    at = e.advance(queued, r, row.lands_at)
    assert at.queue == () and running_mix_id(at, r) == MixId("m") and e.view(at, r).skills[0].level == 2


def test_a_store_stint_pops_when_the_store_reaches_the_rows_target() -> None:
    r, s = world(logs=40)
    s = running(r, s, {"chop": BP})
    queued, row = _stint(r, s, {"saw": BP}, g.GoalKind.STORE, [plank_goal(units(12))])
    assert row.lands_at is not None and (row.until.watched, row.until.value) == (w.StoreValue(store="plank"), units(12))
    assert len(e.advance(queued, r, row.lands_at - 1).queue) == 1
    at = e.advance(queued, r, row.lands_at)
    assert at.queue == () and running_mix_id(at, r) == MixId("m")


def test_a_stint_whose_goal_never_lands_keeps_its_mix_running() -> None:
    r, s = world(logs=40)
    s = running(r, s, {"chop": BP})
    queued, row = _stint(r, s, {"fell": BP}, g.GoalKind.LEVEL, [])
    assert row.lands_at is None and row.per_hour == 0
    later = e.advance(queued, r, s.time + 30 * 86_400)
    assert len(later.queue) == 1 and running_mix_id(later, r) == STINT


def test_a_level_rows_until_is_the_counted_level_past_the_first_phase() -> None:
    """In phase 2 the shown level counts from 1 again; SkillLevel reads levels counted across phases, so the row's
    target is shown and its until counted, and the until comes true at lands_at."""
    r = pw.rules()
    s = pw.click(pw.at_second(r, pw.SPAN), r, pw.N1)
    bar = e.view(s, r).skills[0]
    [row] = [x for x in goal_rows(s, r, e.view(s, r), []) if x.skill == str(pw.K)]
    assert row.target == bar.level + 1
    assert row.until.value == pw.TOP_LEVEL - 1 + row.target, "phase 2 counts on from phase 1's top"
    assert row.lands_at is not None
    cond = from_condition(row.until, r)
    assert not is_true(e.advance(s, r, row.lands_at - 1), r, cond)
    assert is_true(e.advance(s, r, row.lands_at), r, cond)


def test_a_dead_stint_pops_once_its_goal_settles_and_is_kept_while_its_goal_could_fall() -> None:
    """Engine DESIGN.txt, "Greyed mix": the stint's mix greys when nap reaches its cap of 5 (3000 s), so the entry is
    dead and the player's mix runs. A dead entry whose until holds and cannot fall (a level) pops; one whose until
    could fall (a store) is kept although it holds."""
    r, s = world(logs=40)
    s = running(r, s, {"chop": BP // 2, "fell": BP // 2})
    s = e.decide(s, r, 0, SaveMix(Mix(STINT, (CardShare(CardId("nap"), BP),))))
    level = e.AtLeast(e.SkillLevel(e.SkillId("k")), 2, 2)
    store = e.AtLeast(e.StoreValue(e.StoreId("log")), units(42), units(42))
    for until, kept in ((level, 0), (store, 1)):
        q = e.decide(s, r, 0, SetQueue((QueueEntry(SwitchMix(STINT), until),)))
        dead = e.advance(q, r, 3000)
        assert STINT in e.view(dead, r).greyed_mixes and running_mix_id(dead, r) == MixId("m"), "control: dead"
        assert len(dead.queue) == 1 and not is_true(dead, r, until), "control: kept while its goal is unmet"
        later = e.advance(dead, r, 12_000)
        assert is_true(later, r, until), "control: the goal holds"
        assert len(later.queue) == kept


def test_a_stint_reports_when_it_began_to_run_and_when_its_goal_landed_and_a_removal_reports_nothing() -> None:
    r, s = world(logs=40)
    s = running(r, s, {"fell": BP})
    queued, row = _stint(r, s, {"chop": BP}, g.GoalKind.LEVEL, [])
    assert row.lands_at is not None
    order = e.Order(queued.queue[0].until, queued.queue[0].verb)
    ran = e.advance_logged(queued, r, row.lands_at + 60).rule_changes
    assert ran == (e.RuleChange(row.lands_at, order, False, None, e.Ended.STINT),)
    unqueued = e.decide(queued, r, queued.time, SetQueue(()))
    began = e.decide_logged(unqueued, r, unqueued.time, SetQueue(queued.queue)).rule_changes
    assert began == (e.RuleChange(unqueued.time, order, True, None),)
    removed = e.decide_logged(queued, r, queued.time, SetQueue(())).rule_changes
    assert removed == (), "control: a removal before the goal holds is not a landing"
