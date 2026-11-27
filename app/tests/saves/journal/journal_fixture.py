"""A small journal for the writer's tests (saves/journal_write.py): two subjects on line keys no content writes and one
on a line the opening writes by itself early on day 0 (so only a step's own lines show it), the lines a test stores for
them, and the days the composer makes of a save's stored lines at a save time, composed one at a time from its own public
function, as the reference the stored rows must equal."""
from dataclasses import replace

import psycopg

from sqlalchemy import Engine, select

from ashfall_app.db import saves as rows
from ashfall_app.db.tables import save_journal
from ashfall_app.rules.schema import Opening
from ashfall_app.saves.interface import Ruleset
from ashfall_app.saves.journal import DAY_S, ComposedDay, Fade, Habits, Line, Note, Press, Source, Subject, compose_day
from ashfall_app.saves.journal_rules import JournalRules, journal_rules

BEAT = Subject("s_beat", "beat", Source("trigger", "t_beat"), first=("j.beat",), repeat=("j.beat_again",),
               catchup=("j.beat_caught",))
WORK = Subject("s_work", "routine", Source("card", "c_work"), first=("j.work",), repeat=("j.work_a", "j.work_b"),
               catchup=("j.work_caught",))
HABITS = Habits(routine=Fade(0.9, 0.7), worry=Press(0.5, 0.5), crowd=Fade(0.5, 0.5), floor=0.4, halflife=6,
                beat_refresh=1, lines_start=4, lines_floor=2, lines_halflife=6, busy_ratio=10, late_rate=0,
                misremember_rate=0, correct_after_days=1)
TIRED = Subject("s_tired", "beat", Source("trigger", "t_tired"), first=("j.tired",), catchup=("j.tired_caught",))
SOURCES = {"l_beat": (BEAT.source,), "l_work": (WORK.source,), "l_both": (BEAT.source, WORK.source),
           "l_tired": (TIRED.source,)}
JOURNAL = JournalRules(subjects=(BEAT, WORK, TIRED), habits=HABITS, sources=SOURCES, looks={})

LINES: tuple[tuple[int, str], ...] = (
    (100, "l_beat"), (300, "l_noise"),
    (DAY_S + 50, "l_work"), (DAY_S + 60, "l_work"),
    (2 * DAY_S + 10, "l_beat"), (2 * DAY_S + 20, "l_work"),
    (3 * DAY_S + 5, "l_both"),
    (4 * DAY_S + 7, "l_work"), (5 * DAY_S + 9, "l_work"), (6 * DAY_S + 1, "l_beat"),
)
"""(game second, key) for days 0 to 6; l_noise feeds no subject, l_both feeds both."""


def a_beat_line(opening: Opening) -> tuple[str, str]:
    """A line key of a shipped beat subject that has a first slot, and the subject's id."""
    j = journal_rules(opening)
    told = {s.source: s.id for s in j.subjects if s.kind == "beat" and s.first}
    return next((key, told[src[0]]) for key, src in sorted(j.sources.items()) if len(src) == 1 and src[0] in told)


def journaled(rs: Ruleset, journal: JournalRules = JOURNAL) -> Ruleset:
    return replace(rs, journal=journal)


def store_lines(engine: Engine, save_id: int, lines: tuple[tuple[int, str], ...] = LINES) -> None:
    with engine.begin() as conn:
        rows.append_lines(conn, save_id, list(lines))


def lines_of(engine: Engine, save_id: int) -> list[tuple[int, str]]:
    """The save's stored lines, (game second, key), in order."""
    with engine.begin() as conn:
        return [(ln.at, ln.key) for ln in rows.last_lines(conn, save_id, 100_000)]


def reference(engine: Engine, save_id: int, time: int, journal: JournalRules = JOURNAL,
              start: tuple[ComposedDay, ...] = ()) -> list[ComposedDay]:
    """The days as compose_day makes them at save time `time` from the save's stored lines: each day after `start`
    through `time`'s day, from the lines up to `time` before its end and the days before it, ended unless it is
    `time`'s own day."""
    fed = [Line(key, at, src) for at, key in lines_of(engine, save_id) if at <= time
           for src in journal.sources.get(key, ())]
    out = list(start)
    for d in range(len(out), time // DAY_S + 1):
        end = (d + 1) * DAY_S
        out.append(compose_day(save_id, d, tuple(ln for ln in fed if ln.at < end), tuple(out), journal.subjects,
                               journal.habits, ended=time >= end))
    return out


def stored(engine: Engine, save_id: int) -> list[ComposedDay]:
    """The save's save_journal rows, read straight from the table, oldest first."""
    j = save_journal.c
    with engine.begin() as conn:
        found = conn.execute(select(j.day, j.notes, j.gap).where(j.save_id == save_id).order_by(j.day)).all()
    return [ComposedDay(r.day, tuple(Note(n["subject"], n["slot"], n["key"]) for n in r.notes), r.gap) for r in found]


def lock_waiters(url: str) -> int:
    """How many sessions on the test's database are waiting on a lock."""
    with psycopg.connect(url, autocommit=True) as c:
        row = c.execute("SELECT count(*) FROM pg_stat_activity WHERE wait_event_type = 'Lock'"
                        " AND datname = current_database()").fetchone()
    return int(row[0]) if row else 0
