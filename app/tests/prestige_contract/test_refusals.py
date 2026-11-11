"""Every refusal reason of Prestige and UndoPick is reachable, comes back in the documented order, and is the same
from the read (prestige.refusal), the application (prestige.applied) and decide(). BY_HAND_ONLY: test_by_hand.py."""
from collections.abc import Callable
from dataclasses import replace

import pytest

from ashfall_app.engine import (
    NodeId, Prestige, PrestigeRefusal, PrestigeRefused, Rules, Save, SkillId, Unlock, UnlockKind, UndoPick, advance, decide, new_save,
)
from ashfall_app.engine.prestige import applied, refusal
from prestige_world import J, J1, K, N1, N2, N3, N4, at_second, click, rules, undo, without_prestige

R = rules()
GHOST = SkillId("ghost")
Scenario = Callable[[], tuple[Rules, Save]]
Verb = Prestige | UndoPick


def fresh() -> tuple[Rules, Save]:
    return R, new_save(R)


def no_prestige() -> tuple[Rules, Save]:
    bare = without_prestige(R)
    return bare, new_save(bare)


def locked() -> tuple[Rules, Save]:
    """Opening set and K not in it: K is not unlocked."""
    r = replace(R, opening=(Unlock(UnlockKind.STORE, "wood"),))
    return r, new_save(r)


def at_top() -> tuple[Rules, Save]:
    return R, at_second(R, 300)


def second_top_after_n2() -> tuple[Rules, Save]:
    """K clicked n2 at its first top (n2 is finished) and stands at the second top."""
    return R, advance(click(at_second(R, 300), R, N2), R, 600)


def track_done() -> tuple[Rules, Save]:
    """A one-rank track, taken: K stands at its second top with nothing left to pick."""
    short = replace(R, nodes=(replace(R.nodes[0], ranks=1),))
    return short, advance(click(at_second(short, 300), short, N1), short, 600)


def pick_owed() -> tuple[Rules, Save]:
    clicked = click(at_second(R, 300), R, N1)
    return R, undo(advance(clicked, R, 310), R)


def undo_window_closed() -> tuple[Rules, Save]:
    return R, advance(click(at_second(R, 300), R, N1), R, 400)


def undo_window_open() -> tuple[Rules, Save]:
    return R, advance(click(at_second(R, 300), R, N1), R, 399)


P = PrestigeRefusal
CASES: list[tuple[str, Scenario, Verb, PrestigeRefusal | None]] = [
    ("prestige-no-prestige", no_prestige, Prestige(K, N1), P.NO_PRESTIGE),
    ("undo-no-prestige", no_prestige, UndoPick(K), P.NO_PRESTIGE),
    ("no-prestige-before-unknown-skill", no_prestige, Prestige(GHOST, N1), P.NO_PRESTIGE),
    ("prestige-unknown-skill", fresh, Prestige(GHOST, N1), P.UNKNOWN_SKILL),
    ("undo-unknown-skill", fresh, UndoPick(GHOST), P.UNKNOWN_SKILL),
    ("prestige-locked-skill", locked, Prestige(K, N1), P.LOCKED_SKILL),
    ("undo-locked-skill", locked, UndoPick(K), P.LOCKED_SKILL),
    ("locked-before-not-at-top", locked, Prestige(K, N3), P.LOCKED_SKILL),
    ("prestige-not-at-top", fresh, Prestige(K, N1), P.NOT_AT_TOP),
    ("not-at-top-before-not-on-menu", fresh, Prestige(K, N3), P.NOT_AT_TOP),
    ("not-at-top-below-the-top", lambda: (R, at_second(R, 299)), Prestige(K, N1), P.NOT_AT_TOP),
    ("track-done", track_done, Prestige(K, N1), P.TRACK_DONE),
    ("track-done-before-not-on-menu", track_done, Prestige(K, N4), P.TRACK_DONE),
    ("node-beyond-the-menu", at_top, Prestige(K, N3), P.NOT_ON_MENU),
    ("node-unknown", at_top, Prestige(K, NodeId("ghost")), P.NOT_ON_MENU),
    ("node-of-another-skills-track", at_top, Prestige(K, J1), P.NOT_ON_MENU),
    ("node-finished", second_top_after_n2, Prestige(K, N2), P.NOT_ON_MENU),
    ("node-on-the-menu-after-a-finished-one", second_top_after_n2, Prestige(K, N3), None),
    ("click", at_top, Prestige(K, N1), None),
    ("click-second-menu-node", at_top, Prestige(K, N2), None),
    ("click-with-a-pick-owed-below-the-top", pick_owed, Prestige(K, N2), None),
    ("pick-owed-node-not-on-menu", pick_owed, Prestige(K, N3), P.NOT_ON_MENU),
    ("nothing-to-undo-in-phase-one", at_top, UndoPick(K), P.NOTHING_TO_UNDO),
    ("nothing-to-undo-twice", pick_owed, UndoPick(K), P.NOTHING_TO_UNDO),
    ("undo-closed", undo_window_closed, UndoPick(K), P.UNDO_CLOSED),
    ("undo-open", undo_window_open, UndoPick(K), None),
]
IDS = [c[0] for c in CASES]


@pytest.mark.parametrize("make, verb, reason", [c[1:] for c in CASES], ids=IDS)
def test_the_read_names_the_first_reason_that_applies(make: Scenario, verb: Verb, reason: PrestigeRefusal | None):
    r, save = make()
    assert refusal(save, r, verb) is reason


@pytest.mark.parametrize("make, verb, reason", [c[1:] for c in CASES], ids=IDS)
def test_decide_and_applied_refuse_with_that_reason_and_otherwise_act(
        make: Scenario, verb: Verb, reason: PrestigeRefusal | None):
    r, save = make()
    for apply in (lambda: decide(save, r, save.time, verb), lambda: applied(save, r, verb)):
        if reason is None:
            assert apply() != save
        else:
            with pytest.raises(PrestigeRefused) as found:
                apply()
            assert found.value.reason is reason


def test_every_reason_but_by_hand_only_is_reached_by_a_case_here():
    reached = {c[3] for c in CASES if c[3] is not None}
    assert reached == set(PrestigeRefusal) - {P.BY_HAND_ONLY, P.PICK_OWED, P.NOT_PICKED}   # MovePick's: test_move_pick.py


def test_a_click_at_the_top_acts():
    r, save = at_top()
    assert refusal(save, r, Prestige(K, N1)) is None
    assert applied(save, r, Prestige(K, N1)) != save


def test_another_skills_track_is_a_pick_for_that_skill():
    """J has no XP of its own, so J is below its top: the control that J1 is a real node of the real J."""
    r, save = at_top()
    assert refusal(save, r, Prestige(J, J1)) is P.NOT_AT_TOP
