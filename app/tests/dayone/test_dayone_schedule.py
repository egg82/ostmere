"""The scheduler reads each subject once for all the triggers on it (engine schedule.trigger_events): many levels and
counts pay, and rise_time looked the subject up and solved it once per trigger per instant. The events are the same as
rise_time gives them, trigger by trigger, on the saves real day-one plays saw. The caches the speed of an instant rests
on (the unlocked standing actions, the stack's inputs) follow the save they are asked of, in any order of asking."""
import pytest

from ashfall_app.engine import Event, EventKind, Rules, Save, schedule
from ashfall_app.engine.conditions import all_true, rise_time
from ashfall_app.engine.gates import is_unlocked, stack_inputs
from ashfall_app.engine.heldentries import held_part, holders
from ashfall_app.engine.odds import kept_speeds
from ashfall_app.engine.pickentries import pick_entries
from ashfall_app.engine.rates import unlocked_standing
from ashfall_app.engine.rules import StandingDef
from ashfall_app.engine.unlocks import Unlock, UnlockKind
from tests.dayone.conftest import PLAY_TIMEOUT_S
from tests.dayone.routes import day

pytestmark = [pytest.mark.playthrough, pytest.mark.timeout(PLAY_TIMEOUT_S)]


def naive_trigger_events(save: Save, rules: Rules) -> list[Event]:
    """The scheduler's trigger events as conditions.rise_time gives them, one trigger at a time."""
    out: list[Event] = []
    for i, (t, fired) in enumerate(zip(rules.triggers, save.fired)):
        at = rise_time(save, rules, t.when) if not fired and all_true(save, rules, t.requires) else None
        if at is not None:
            out.append(Event(at, EventKind.TRIGGER, i, t.id))
    return out


@pytest.fixture(scope="module")
def trigger_diffs() -> tuple[int, int]:
    """(saves compared, saves where the fast path differs from rise_time), over two plays, in setup."""
    n = bad = 0
    for name in ("typical", "babysitter"):
        p = day(name)
        for save, _ in p.history[::9]:
            n += 1
            bad += schedule.trigger_events(save, p.rules) != naive_trigger_events(save, p.rules)
    return n, bad


def test_the_schedulers_level_fast_path_is_rise_time(trigger_diffs: tuple[int, int]):
    n, bad = trigger_diffs
    assert n > 50 and bad == 0


def test_the_unlocked_standing_actions_follow_each_save_asked_in_any_order():
    p = day("typical")
    saves = [save for save, _ in p.history[::9]]
    seen: set[tuple[StandingDef, ...]] = set()
    for save in [*saves, *reversed(saves)]:
        fresh = tuple(a for a in p.rules.standing if is_unlocked(save, p.rules, Unlock(UnlockKind.ACTION, a.id)))
        assert unlocked_standing(save, p.rules) == fresh
        seen.add(fresh)
    assert len(seen) > 1   # control: the set grew over the play, so a cache that ignored the save would fail


def test_the_stack_inputs_follow_each_save_asked_in_any_order():
    p = day("typical")
    saves = [save for save, _ in p.history[::9]]
    different = {(s.modifiers, s.unlocked) for s in saves}
    for save in [*saves, *reversed(saves)]:
        held = (held_part(save, p.rules),) if holders(p.rules) else ()
        picked = (pick_entries(save, p.rules),) if p.rules.prestige is not None else ()
        fresh = (p.rules, save.modifiers, save.unlocked, *kept_speeds(save, p.rules), *held, *picked)
        found = stack_inputs(save, p.rules)
        assert len(found) == len(fresh) and all(a is b for a, b in zip(found, fresh))
    assert len(different) > 1   # control: the stack changed over the play
