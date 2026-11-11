"""View.goal_rows: each open goal a mix can move, with when it lands at the rates as set and the line that binds it
(CONTRACT.txt, "Goal rows"). The goals are the stores and levels the story waits on (View.goals) and each skill's next
level; the rates are setrates.py's."""
from collections.abc import Sequence

from .. import engine as e
from ..engine.phases import counted_xp, level_counted, phase_state
from ..engine.rates import Running
from ..engine.segments import value_at
from . import decision_models as w
from . import goal_models as g
from . import setrates as sr


def goal_rows(save: e.Save, rules: e.Rules, v: e.View, goals: Sequence[g.Goal]) -> list[g.GoalRow]:
    """The story's store and level goals in View.goals order, then each skill's next level in skill order, once each."""
    now = sr.as_set(save, rules)
    caps = {str(ln.store): ln.cap for ln in v.ledger}
    shown = frozenset(ln.store for ln in v.ledger)
    out: list[g.GoalRow] = []
    for goal in goals:
        if goal.kind is g.GoalKind.STORE and goal.store is not None:
            out.append(_store(save, rules, now, goal.store, goal.target, caps.get(goal.store), shown))
        elif goal.kind is g.GoalKind.LEVEL and goal.skill is not None:
            row = _story_level(save, rules, now, goal.skill, goal.target, shown)
            out += [] if row is None else [row]
    seen = {(r.skill, r.target) for r in out}
    for bar in v.skills:
        if bar.next_level_xp is not None and (str(bar.skill), bar.level + 1) not in seen:
            out.append(_level(save, rules, now, str(bar.skill), bar.level + 1, bar.next_level_xp, shown))
    return out


def _store(save: e.Save, rules: e.Rules, now: Running, store: str, target: int, cap: int | None,
           shown: frozenset[e.StoreId]) -> g.GoalRow:
    sid = e.StoreId(store)
    net = sr.net_per_hour(save, rules, now, sid)
    left = target - e.segment(save, rules, sid).start_value
    reachable = cap is None or target <= cap
    return g.GoalRow(kind=g.GoalKind.STORE, store=store, skill=None, target=target,
                     lands_at=_lands(save.time, left, net) if reachable else None, per_hour=net,
                     limit=None if left <= 0 else limit(save, rules, now, sr.movers(rules, now, sid, None), shown),
                     until=w.AtLeast(watched=w.StoreValue(store=store), value=target, release=target))


def _story_level(save: e.Save, rules: e.Rules, now: Running, skill: str, target: int, shown: frozenset[e.StoreId]
                 ) -> g.GoalRow | None:
    """None when no XP in the skill's phase reaches `target` (past its top, which only a click lifts)."""
    xp = counted_xp(rules.curve, rules.prestige, phase_state(save, rules, e.SkillId(skill)).phase, target)
    return None if xp is None else _level(save, rules, now, skill, target, xp, shown)


def _level(save: e.Save, rules: e.Rules, now: Running, skill: str, target: int, xp: int, shown: frozenset[e.StoreId]
           ) -> g.GoalRow:
    sid = e.SkillId(skill)
    rate = sr.xp_per_hour(save, rules, now, sid)
    st = next(s for s in save.skills if s.skill == sid)
    left = xp - value_at(st.xp, save.time)
    counted = level_counted(rules.curve, rules.prestige, phase_state(save, rules, sid).phase, xp)
    return g.GoalRow(kind=g.GoalKind.LEVEL, store=None, skill=skill, target=target,
                     lands_at=_lands(save.time, left, rate), per_hour=rate,
                     limit=None if left <= 0 else limit(save, rules, now, sr.movers(rules, now, None, sid), shown),
                     until=w.AtLeast(watched=w.SkillLevel(skill=skill), value=counted, release=counted))


def _lands(t: int, left: int, per_hour: int) -> int | None:
    """A rate in rate units moves a quantity by that many units a second (engine/units.py)."""
    if left <= 0:
        return t
    return None if per_hour <= 0 else t + e.ceil_div(left, per_hour)


def limit(save: e.Save, rules: e.Rules, now: Running, runners: list[e.Runner], shown: frozenset[e.StoreId]
           ) -> g.GoalLimit | None:
    dry = sr.dry_input(now, runners, shown)
    return None if dry is None else g.GoalLimit(store=str(dry), in_per_hour=sr.in_per_hour(save, rules, now, dry))
