"""Properties over generated histories for the day-to-day statements: the budget (12), away and busy gaps (13, 14),
late additions (16), misremembering and corrections (17), the page's order (18) and the slots' rounds (19)."""
from hypothesis import given

from ashfall_app.saves.journal import DAY_S, ComposedDay, Line, Note, Subject
from journal_check import budget, first_at, gap_runs, musts_on, showing
from journal_gen import History, histories
from journal_world import OWN_SLOTS, compose_span, ref_roll


def _compose(h: History) -> tuple[ComposedDay, ...]:
    return compose_span(h.save_id, h.days, h.lines, h.subjects, h.habits)


def _away_days(h: History) -> set[int]:
    return {d + i for s in h.subjects if s.away_days for d in range(h.days)
            if s in showing(h.lines, h.subjects, d) for i in range(s.away_days)}


def _covered(h: History) -> set[int]:
    """The days an away gap covers from their start: the days after an away subject's day, within its `away_days`."""
    return {d + i for s in h.subjects if s.away_days for d in range(h.days)
            if s in showing(h.lines, h.subjects, d) for i in range(1, s.away_days)}


@given(history=histories())
def test_a_non_must_is_written_only_while_the_page_has_room(history: History):
    """Statement 12: fewer notes than the budget stand before each non-must own note on its day."""
    rows = _compose(history)
    for d, r in enumerate(rows):
        musts = musts_on(rows, d, history.lines, history.subjects)
        room = budget(rows[:d], history.subjects, history.habits)
        for i, n in enumerate(r.notes):
            if n.slot in OWN_SLOTS and n.subject not in musts:
                assert i < room, (d, i, room, r.notes)


@given(history=histories())
def test_away_gaps_fall_on_the_away_subjects_days(history: History):
    """Statement 13: a day an away gap covers from its start is an away gap with no notes; a day an away subject shows
    on breaks off (away, or busy if that came first); no other day is an away gap."""
    rows = _compose(history)
    covered = _covered(history)
    showed = {d for s in history.subjects if s.away_days for d in range(history.days)
              if s in showing(history.lines, history.subjects, d)}
    for r in rows:
        if r.day in covered:
            assert r.gap == "away" and r.notes == (), r
        elif r.day in showed:
            assert r.gap in ("away", "busy"), r
        else:
            assert r.gap != "away", r


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
    slot other than late or correction, `roll(save, d, S, "late") < late_rate`, and day d + 1 did not break off and has
    another note."""
    rows = _compose(history)
    for d in range(1, len(rows)):
        for s in history.subjects:
            others = [n for n in rows[d].notes if n.slot != "late"]
            due = bool(s.late) and _wrote(rows[d - 1], s.id) and bool(others) and rows[d].gap is None
            due = due and ref_roll(history.save_id, d - 1, s.id, "late") < history.habits.late_rate
            assert any(n.subject == s.id and n.slot == "late" for n in rows[d].notes) == due, (d, s.id)
    assert all(n.slot != "late" for n in rows[0].notes)


@given(history=histories())
def test_each_misremembering_has_one_correction_after_the_wait(history: History):
    """Statement 17: each misremembering on day d is followed by exactly one correction, on the first day at least
    `correct_after_days` later that did not break off (or none if the history ends first), and a correction follows
    nothing else."""
    rows = _compose(history)
    expected: list[tuple[int, str]] = []
    for r in rows:
        for n in r.notes:
            if n.slot == "misremember":
                due = [x.day for x in rows[r.day + history.habits.correct_after_days:] if x.gap is None]
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


def _group(n: Note, crowds: set[str]) -> int:
    if n.slot in ("catchup", "late", "correction"):
        return {"catchup": 0, "late": 3, "correction": 4}[n.slot]
    return 2 if n.subject in crowds else 1


def _moments(lines: tuple[Line, ...], s: Subject, d: int) -> list[int]:
    """The seconds of `s`'s moments on day `d` ("Terms"): its first line that day and each with a key it never held."""
    held: set[str] = set()
    out: list[int] = []
    for line in sorted((ln for ln in lines if ln.source == s.source and ln.at < (d + 1) * DAY_S), key=lambda ln: ln.at):
        if line.at >= d * DAY_S and (not out or line.key not in held):
            out.append(line.at)
        held.add(line.key)
    return out


def _placeable(ats: list[list[int]]) -> bool:
    """Whether each note can take one of its moments so that the seconds never fall."""
    last = -1
    for options in ats:
        fits = [a for a in options if a >= last]
        if not fits:
            return False
        last = min(fits)
    return True


@given(history=histories())
def test_the_page_runs_in_its_five_groups(history: History):
    """Statement 18: catch-ups by their earliest line on the run days they are caught up from, then own notes each at a
    moment of its subject, then crowds by their first line, then late additions and corrections, each by subject id."""
    rows = _compose(history)
    by_id = {s.id: s for s in history.subjects}
    crowds = {s.id for s in history.subjects if s.kind == "crowd"}
    runs = {last: first for first, last in gap_runs(rows)}
    for d, r in enumerate(rows):
        groups = [_group(n, crowds) for n in r.notes]
        assert groups == sorted(groups), (d, r.notes)
        caught = [n.subject for n in r.notes if n.slot == "catchup"]
        run = range(runs.get(d - 1, d), d)
        places = [min(a for dd in run if all(n.subject != i for n in rows[dd].notes)
                      and (a := first_at(history.lines, by_id[i], dd, dd)) is not None) for i in caught]
        assert places == sorted(places), (d, caught, places)
        crowded = [first_at(history.lines, by_id[n.subject], d, d) or 0 for n in r.notes if _group(n, crowds) == 2]
        assert crowded == sorted(crowded), (d, r.notes)
        for group in (3, 4):
            ids = [n.subject for n in r.notes if _group(n, crowds) == group]
            assert ids == sorted(ids), (d, group)
        own = [_moments(history.lines, by_id[n.subject], d) for n in r.notes if _group(n, crowds) == 1]
        assert _placeable(own), (d, r.notes)


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
