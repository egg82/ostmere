"""Properties over generated histories for the day-to-day statements: the budget (12), away and busy gaps (13, 14),
late additions (16), misremembering and corrections (17), the page's order (18) and the slots' rounds (19)."""
from hypothesis import given

from ashfall_app.saves.journal import ComposedDay, Note
from journal_check import budget, musts_on, showing
from journal_gen import History, histories
from journal_world import OWN_SLOTS, compose_span, ref_roll


def _compose(h: History) -> tuple[ComposedDay, ...]:
    return compose_span(h.save_id, h.days, h.lines, h.subjects, h.habits)


def _away_days(h: History) -> set[int]:
    return {d + i for s in h.subjects if s.away_days for d in range(h.days)
            if s in showing(h.lines, h.subjects, d) for i in range(s.away_days)}


@given(history=histories())
def test_non_musts_stay_within_what_musts_leave_of_the_budget(history: History):
    """Statement 12: a day's non-must own notes number at most the budget less its must notes, never below 0."""
    rows = _compose(history)
    for d, r in enumerate(rows):
        musts = musts_on(rows, d, history.lines, history.subjects)
        must_notes = sum(1 for n in r.notes if n.slot in ("catchup", "correction")
                         or (n.slot in OWN_SLOTS and n.subject in musts))
        non_musts = sum(1 for n in r.notes if n.slot in OWN_SLOTS and n.subject not in musts)
        assert non_musts <= max(0, budget(rows[:d], history.subjects, history.habits) - must_notes), d


@given(history=histories())
def test_away_gaps_are_exactly_the_away_subjects_days(history: History):
    """Statement 13: a day is an away gap exactly when an away subject showed within its `away_days` before it."""
    rows = _compose(history)
    away = _away_days(history)
    assert {r.day for r in rows if r.gap == "away"} == away & set(range(history.days))


@given(history=histories())
def test_busy_is_the_days_own_subjects_over_the_budget(history: History):
    """Statement 14: a day not away is busy exactly when its subjects showing exceed `busy_ratio * budget`."""
    rows = _compose(history)
    away = _away_days(history)
    for d, r in enumerate(rows):
        if d in away:
            continue
        crowded = len(showing(history.lines, history.subjects, d)) > history.habits.busy_ratio * budget(
            rows[:d], history.subjects, history.habits)
        assert (r.gap == "busy") == crowded, d


def _wrote(r: ComposedDay, sid: str) -> bool:
    return any(n.subject == sid and n.slot not in ("late", "correction") for n in r.notes)


@given(history=histories())
def test_a_late_note_is_exactly_the_roll_on_the_day_after(history: History):
    """Statement 16: subject S has a late note on day d + 1 exactly when it has a late slot, was written on day d by a
    slot other than late or correction, `roll(save, d, S, "late") < late_rate`, and day d + 1 has another note."""
    rows = _compose(history)
    for d in range(1, len(rows)):
        for s in history.subjects:
            others = [n for n in rows[d].notes if n.slot != "late"]
            due = bool(s.late) and _wrote(rows[d - 1], s.id) and bool(others)
            due = due and ref_roll(history.save_id, d - 1, s.id, "late") < history.habits.late_rate
            assert any(n.subject == s.id and n.slot == "late" for n in rows[d].notes) == due, (d, s.id)
    assert all(n.slot != "late" for n in rows[0].notes)


@given(history=histories())
def test_each_misremembering_has_one_correction_after_the_wait(history: History):
    """Statement 17: each misremembering on day d is followed by exactly one correction, on the first written day at
    least `correct_after_days` later (or none if the history ends first), and a correction follows nothing else."""
    rows = _compose(history)
    expected: list[tuple[int, str]] = []
    for r in rows:
        for n in r.notes:
            if n.slot == "misremember":
                due = [x.day for x in rows[r.day + history.habits.correct_after_days:] if x.notes]
                expected += [(due[0], n.subject)] if due else []
    got = [(r.day, n.subject) for r in rows for n in r.notes if n.slot == "correction"]
    assert sorted(got) == sorted(expected)


@given(history=histories())
def test_misremembering_is_exactly_the_roll_on_a_first_own_telling(history: History):
    """Statement 17: a subject with both slots, told for the first time on its own day, is written by `misremember`
    exactly when its roll passes, and no note is ever by `misremember` otherwise."""
    rows = _compose(history)
    rate = history.habits.misremember_rate
    for r in rows:
        for n in r.notes:
            if n.slot not in ("first", "misremember"):
                continue
            s = next(x for x in history.subjects if x.id == n.subject)
            passes = ref_roll(history.save_id, r.day, s.id, "misremember") < rate
            wrong = bool(s.misremember and s.correction) and passes
            assert (n.slot == "misremember") == wrong, (r.day, n)


def _group(n: Note, musts: set[str]) -> int:
    return {"catchup": 0, "late": 3, "correction": 4}.get(n.slot, 1 if n.subject in musts else 2)


@given(history=histories())
def test_the_page_runs_in_its_five_groups(history: History):
    """Statement 18: catch-ups, own musts, own non-musts, late additions, corrections; late additions and corrections
    each by subject id."""
    rows = _compose(history)
    for d, r in enumerate(rows):
        musts = musts_on(rows, d, history.lines, history.subjects)
        groups = [_group(n, musts) for n in r.notes]
        assert groups == sorted(groups), (d, r.notes)
        for slot in ("late", "correction"):
            ids = [n.subject for n in r.notes if n.slot == slot]
            assert ids == sorted(ids), (d, slot)


@given(history=histories())
def test_every_slot_and_band_draws_in_rounds(history: History):
    """Statement 19: for every subject and slot (a crowd's mention, every band), notes with equal `n // len(keys)` are
    different keys, n counted over the history."""
    rows = _compose(history)
    for s in history.subjects:
        slots = [("first", s.first), ("repeat", s.repeat), ("catchup", s.catchup), ("late", s.late),
                 ("misremember", s.misremember), ("correction", s.correction)]
        slots += [("mention", b.keys) for b in s.mention]
        for slot, keys in slots:
            drawn = [n.key for r in rows for n in r.notes if n.subject == s.id and n.slot == slot and n.key in keys]
            for i in range(0, len(drawn), max(len(keys), 1)):
                chunk = drawn[i:i + len(keys)]
                assert len(set(chunk)) == len(chunk), (s.id, slot, drawn)
