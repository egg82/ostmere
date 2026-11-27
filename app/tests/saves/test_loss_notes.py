"""The journal's loss and fold notes (api/contract/loss-lines.txt, "LOSS LINES", L1-L6), from the composer's public function on
days with no lines of their own, and the lost tallies a step reads at each day's end (saves/journal_tallies.py) on the
engine contract's small fight world."""
from ashfall_app import engine as e
from ashfall_app.saves.journal import DAY_S, ComposedDay, Line, Loss, Note, Source, Subject, compose_day
from ashfall_app.saves.journal_rules import LossRunner
from ashfall_app.saves.journal_tallies import Tallies
from tests.engine_contract.fight_world import LOST, started, world
from tests.saves.journal_fixture import HABITS, WORK

POOL = ("n1", "n2", "n3")
FOLD = "ui.journal.fold"


def day(d: int, lost: int, composed: tuple[ComposedDay, ...] = (), *, ended: bool = True, save: int = 7,
        lines: tuple[Line, ...] = (), subjects: tuple[Subject, ...] = (), pool: tuple[str, ...] = POOL) -> ComposedDay:
    return compose_day(save, d, lines, composed, subjects, HABITS, ended, (Loss("c_hunt", pool, lost),))


def days(tallies: list[int], *, save: int = 7, pool: tuple[str, ...] = POOL,
         first: tuple[ComposedDay, ...] = ()) -> tuple[ComposedDay, ...]:
    """Days composed one after another, day d's tally at its end tallies[d - len(first)]."""
    out = first
    for lost in tallies:
        out = (*out, day(len(out), lost, out, save=save, pool=pool))
    return out


def test_one_lost_fight_writes_one_loss_note_and_more_fold_the_rest():
    (one,) = day(0, 1).notes
    assert (one.subject, one.slot, one.key in POOL, one.count) == ("c_hunt", "loss", True, None)
    many = day(0, 5).notes
    assert [(n.slot, n.count) for n in many] == [("loss", None), ("fold", 4)]
    assert many[1].key == FOLD and many[1].subject == "c_hunt"


def test_nothing_is_written_before_the_day_ends_or_with_nothing_owed():
    assert day(0, 3, ended=False).notes == ()
    assert day(0, 0).notes == ()


def test_the_same_day_composed_again_is_the_same():
    stored = days([1, 2, 0, 4])
    assert days([1, 2, 0, 4]) == stored
    assert day(4, 9, stored) == day(4, 9, stored)


def test_what_earlier_days_told_is_not_told_again():
    told = days([2, 2, 6])
    assert [[(n.slot, n.count) for n in d.notes] for d in told] == [
        [("loss", None), ("fold", 1)], [], [("loss", None), ("fold", 3)]]


def test_a_day_broken_off_carries_its_losses_to_the_next_day_that_ends():
    away = Subject("s_away", "beat", Source("trigger", "t_away"), away_days=2, first=("j.away",))
    lines = (Line("l_away", 100, away.source),)
    broken = day(0, 2, lines=lines, subjects=(away,))
    assert broken.gap == "away" and broken.notes == ()
    gap = day(1, 3, (broken,), lines=lines, subjects=(away,))
    assert gap.gap == "away" and gap.notes == ()
    after = day(2, 4, (broken, gap), lines=lines, subjects=(away,))
    assert [(n.slot, n.count) for n in after.notes] == [("loss", None), ("fold", 3)]


def test_each_round_draws_every_key_once_and_no_key_comes_twice_in_a_row():
    for save in range(1, 30):
        drawn = [n.key for d in days(list(range(1, 25)), save=save) for n in d.notes]
        assert len(drawn) == 24
        assert all(sorted(drawn[i:i + 3]) == sorted(POOL) for i in range(0, 24, 3))
        assert all(a != b for a, b in zip(drawn, drawn[1:]))


def test_the_rounds_differ_between_saves():
    orders = {tuple(n.key for d in days([1, 2, 3], save=s) for n in d.notes) for s in range(1, 30)}
    assert len(orders) > 1


def test_a_trigger_subjects_note_from_the_pool_is_the_first_draw():
    first = (ComposedDay(0, (Note("s_beat", "first", "n1"),), None),)
    for save in range(1, 20):
        drawn = [n.key for d in days([1, 2], save=save, first=first)[1:] for n in d.notes]
        assert sorted(drawn) == ["n2", "n3"]


def test_the_folded_fights_draw_nothing():
    for save in range(1, 30):
        drawn = [n.key for d in days([3, 6, 9], save=save) for n in d.notes if n.slot == "loss"]
        assert sorted(drawn) == sorted(POOL)


def test_the_day_s_own_notes_are_those_it_has_without_losses():
    lines = (Line("l_work", 60, WORK.source),)
    plain = compose_day(7, 0, lines, (), (WORK,), HABITS, True)
    told = day(0, 3, lines=lines, subjects=(WORK,))
    assert told.notes[:len(plain.notes)] == plain.notes and plain.notes
    assert [n.slot for n in told.notes[len(plain.notes):]] == ["loss", "fold"]
    assert told.marks == plain.marks


def test_the_tallies_at_each_day_end_are_the_engine_s_however_the_steps_fell():
    rules = world(1, 1, work_s=3600)
    began = started(rules)
    after = e.advance(began, rules, 3 * DAY_S)
    runner = (LossRunner("hunt", LOST, POOL),)
    whole = Tallies(began, after, rules, runner)
    ends = [DAY_S, 2 * DAY_S, 3 * DAY_S]
    want = [e.value(began, rules, LOST, t) // e.QUANTITY_SCALE for t in ends]
    assert want[0] > 0 and want[0] < want[-1]
    assert [whole.at(t)[0].lost for t in ends] == want
    half = e.advance(began, rules, DAY_S + DAY_S // 2)
    assert Tallies(half, after, rules, runner).at(2 * DAY_S)[0].lost == want[1]
    assert Tallies(half, after, rules, runner).at(DAY_S)[0].lost == e.value(began, rules, LOST, half.time) // e.QUANTITY_SCALE
    assert Tallies(began, after, rules, ()).at(DAY_S) == ()
