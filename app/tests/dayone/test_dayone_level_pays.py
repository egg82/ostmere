"""On every route a run plays, no skill pays speed alone more than two levels running among the levels day one reaches
(levelpays.py; docs/decisions.md, "A level is a thing, not only a number", an authoring rule), read off what the play
reached. Which leave points name only a speed level is the readout's (report.py); the reader is proven able to see one
by the named pays planted away."""
from dataclasses import replace

import pytest

from ashfall_app.engine import Outcome, UnlockKind
from ashfall_app.engine.orders import AtLeast, SkillLevel
from tests.dayone.conftest import PLAY_TIMEOUT_S
from tests.dayone.levelpays import LeavePoint, reached, runs, speed_only_leaves
from tests.dayone.player import DayOnePlayer
from tests.dayone.routes import plays

pytestmark = [pytest.mark.playthrough, pytest.mark.timeout(PLAY_TIMEOUT_S)]


@pytest.mark.parametrize("day_route", plays(), indirect=True, ids=lambda r: f"{r[0]}-{r[1]}")
def test_no_skill_pays_speed_alone_three_levels_running(day_route: DayOnePlayer):
    top = reached(day_route)
    at_b3 = [s for s, _ in day_route.history if s.time <= day_route.seen_at["B3"]][-1]
    opened = {u.id for u in at_b3.unlocked if u.kind is UnlockKind.CARD}   # a later chapter's trainer is not day one's
    trained = {str(c.skill) for c in day_route.rules.cards
               if c.skill is not None and str(c.lane) == "hands" and c.id in opened}
    assert trained and all(top.get(s, 0) >= 2 for s in trained), top   # the play reached levels in every mixed skill
    assert runs(day_route.rules, top) == []


@pytest.mark.parametrize("day_route", [("typical", 0)], indirect=True)
def test_a_skill_with_its_named_pays_taken_away_is_caught(day_route: DayOnePlayer):
    """Woodcutting's levels past its builds keep only their numbers: the run the typical day reaches goes red."""
    rules, top = day_route.rules, reached(day_route)
    assert runs(rules, top) == []

    def numbers_only(o: Outcome) -> Outcome:
        return Outcome(modifiers=o.modifiers, raises=o.raises)

    stripped = tuple(replace(t, outcome=numbers_only(t.outcome))
                     if isinstance(t.when, AtLeast) and isinstance(t.when.subject, SkillLevel)
                     and t.when.subject.skill == "woodcutting" and t.when.value > 3 else t
                     for t in rules.triggers)
    found = runs(replace(rules, triggers=stripped), top)
    assert any(f.startswith("woodcutting") for f in found), found



Leaves = tuple[DayOnePlayer, list[LeavePoint]]


@pytest.mark.parametrize("day_leaves", [("typical", 0)], indirect=True)
def test_a_leave_with_its_named_levels_taken_away_is_caught(day_leaves: Leaves):
    """Every skill-level trigger keeps only its numbers: the leave whose named levels were finds goes red."""
    p, points = day_leaves
    stripped = tuple(replace(t, outcome=Outcome(modifiers=t.outcome.modifiers, raises=t.outcome.raises))
                     if isinstance(t.when, AtLeast) and isinstance(t.when.subject, SkillLevel) else t
                     for t in p.rules.triggers)
    assert speed_only_leaves(points, p.rules) == []
    found = speed_only_leaves(points, replace(p.rules, triggers=stripped))
    assert any(f.startswith("V1:") for f in found), found
