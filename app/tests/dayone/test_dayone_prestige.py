"""The simulated player clicks a skill at its top at its next visit (policy.prestige_click), and the carry makes that
click level with one at the top (docs/design/prestige-phases.md, "The idle math"): a top landing inside an absence
shorter than the carry window ends with the same XP and shown level as an instant clicker. Today's content has no
[prestige] table, so the day-one player's own visit loop runs on the prestige fixture's rules (prestige_world), with
the opening's moves left out."""
from dataclasses import dataclass

from ashfall_app.engine import Rules, Save, advance, decide, new_save, view
from ashfall_app.engine.phases import level_shown, phase_state
from tests.dayone import policy
from tests.dayone.player import DayOnePlayer
from tests.dayone.schedules import Schedule, Visit
from tests.prestige_contract import prestige_world as world

TOP_S = 300
"""K reaches phase 1's top at second 300 (prestige_world)."""
BACK_S = 400
"""The return: 100 s after the top, inside an absence from second 100."""
END_S = 500


@dataclass
class FixturePlayer(DayOnePlayer):
    """The day-one player with only the visit's own moves: the opening's and the day's read content the fixture lacks."""

    def day_move(self, v: object) -> policy.Move | None:
        return None


def visit_clicker(r: Rules) -> Save:
    p = FixturePlayer(r, schedule=Schedule("prestige", (Visit(0, 100), Visit(BACK_S, 20))))
    p.play_visits(0, 0)
    assert any(isinstance(verb, world.Prestige) for _, _, verb in p.decisions)
    return advance(p.save, r, END_S)


def instant_clicker(r: Rules) -> Save:
    at_top = advance(new_save(r), r, TOP_S)
    move = policy.prestige_click(view(at_top, r))
    assert move is not None
    return advance(decide(at_top, r, TOP_S, move[1][0]), r, END_S)


def xp_and_shown(s: Save, r: Rules) -> tuple[int, int, tuple[str, ...]]:
    ps = phase_state(s, r, world.K)
    assert r.prestige is not None
    x = world.xp_now(s, r)
    return x, level_shown(r.curve, r.prestige, ps.phase, x), tuple(ps.picks)


def test_the_click_waits_for_the_visit_and_picks_the_first_menu_node():
    r = world.rules(window=200)
    s = advance(new_save(r), r, BACK_S - 1)
    assert phase_state(s, r, world.K).phase == 1
    assert xp_and_shown(visit_clicker(r), r)[2] == (world.N1,)


def test_inside_the_carry_window_the_visit_clicker_ends_level_with_an_instant_clicker():
    r = world.rules(window=200)
    assert xp_and_shown(visit_clicker(r), r) == xp_and_shown(instant_clicker(r), r)


def test_past_the_carry_window_the_check_sees_the_gap():
    """Control: with a window shorter than the time away, the visit clicker's XP stopped for at least the time from
    the carry's end to the return, and it ends behind."""
    r = world.rules(window=50)
    late, prompt = xp_and_shown(visit_clicker(r), r), xp_and_shown(instant_clicker(r), r)
    assert late[0] <= prompt[0] - (BACK_S - TOP_S - 50)
