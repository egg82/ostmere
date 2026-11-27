"""The Mixes list's numbers (contract/mix-rows.txt, "Mix rows"): each of the player's saved mixes as if it ran from now, on
separate numbers (when each open goal lands, each store's net per hour, when the mix runs out), never one score, and the
player's own earlier best per goal from saves/mixbest.py."""
from collections.abc import Mapping

from .. import engine as e
from ..opening.goals import GoalDef
from ..saves.interface import Played
from ..saves.mixbest import Best
from . import goal_models as g
from . import mixrow_models as m
from . import setrates as sr
from .goalrows import goal_rows
from .goals import goals


def goal_key(r: g.GoalRow) -> str:
    return f"{r.kind.value}|{r.store or ''}|{r.skill or ''}|{r.target}"


def mix_row(save: e.Save, rules: e.Rules, defs: Mapping[str, GoalDef], mix: e.MixId) -> m.MixRow | None:
    """None when the mix cannot be switched to (greyed, retired or a town mix)."""
    try:
        after = e.decide(save, rules, save.time, e.SwitchMix(mix))
    except e.InvalidVerbError:
        return None
    v = e.view(after, rules)
    now = sr.as_set(after, rules)
    nets = [m.StoreNet(store=str(ln.store), per_hour=sr.net_per_hour(after, rules, now, ln.store)) for ln in v.ledger]
    return m.MixRow(id=str(mix), goals=goal_rows(after, rules, v, goals(after, rules, v, defs)), nets=nets,
                    runs_out_at=v.runs_out_at)


def marks(save: e.Save, rules: e.Rules, defs: Mapping[str, GoalDef], mix: e.MixId) -> tuple[tuple[str, int], ...]:
    """Each open goal the mix lands, as its key and when: the saves layer's input to keep the best."""
    row = mix_row(save, rules, defs, mix)
    if row is None:
        return ()
    return tuple((goal_key(r), r.lands_at) for r in row.goals if r.lands_at is not None and r.lands_at > save.time)


def best_rows(kept: tuple[Best, ...]) -> list[m.MixBest]:
    return [m.MixBest(goal=b.goal, mix_id=b.mix, lands_at=b.lands_at, saved_at=b.at) for b in kept]


class MixNumbers:
    """The Mixes list's numbers under one game's rules and goal definitions."""

    def __init__(self, rules: e.Rules, defs: Mapping[str, GoalDef]) -> None:
        self._rules = rules
        self._defs = defs

    def marks(self, save: e.Save, mix: e.MixId) -> tuple[tuple[str, int], ...]:
        """Ruleset.mix_marks: the open goals `mix` lands, as its saves keep them."""
        return marks(save, self._rules, self._defs, mix)

    def rows(self, played: Played, kept: tuple[Best, ...]) -> m.MixRows:
        """Each of the player's own saved mixes as if it ran from now, and the kept earlier best."""
        save = played.save
        rows = [r for x in save.mixes if not str(x.id).startswith(e.TOWN_PREFIX)
                and (r := mix_row(save, self._rules, self._defs, x.id)) is not None]
        return m.MixRows(at=save.time, rows=rows, best=best_rows(kept))
