"""The writer queue's day counts (writer/counts.py DayCounts) in Postgres: one row per day and world. A visit deletes the
rows of earlier days, so the table holds about a day."""

from datetime import date

from sqlalchemy import Connection, Engine, delete, select, update
from sqlalchemy.dialects.postgresql import insert

from .tables import writer_day


def load(conn: Connection, day: date) -> tuple[dict[str, int], dict[str, int]]:
    rows = conn.execute(select(writer_day.c.save_id, writer_day.c.weight, writer_day.c.spent)
                        .where(writer_day.c.day == day)).all()
    return {r.save_id: r.weight for r in rows}, {r.save_id: r.spent for r in rows}


def visit(conn: Connection, day: date, save_id: str, weight: int) -> None:
    conn.execute(delete(writer_day).where(writer_day.c.day < day))
    ins = insert(writer_day).values(day=day, save_id=save_id, weight=weight, spent=0)
    conn.execute(ins.on_conflict_do_update(index_elements=[writer_day.c.day, writer_day.c.save_id],
                                           set_={"weight": ins.excluded.weight}))


def spend(conn: Connection, day: date, save_id: str) -> None:
    conn.execute(update(writer_day).where(writer_day.c.day == day, writer_day.c.save_id == save_id)
                 .values(spent=writer_day.c.spent + 1))


class PgCounts:
    """DayCounts on an engine: each call its own transaction."""

    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def load(self, day: date) -> tuple[dict[str, int], dict[str, int]]:
        with self.engine.connect() as conn:
            return load(conn, day)

    def visit(self, day: date, save_id: str, weight: int) -> None:
        with self.engine.begin() as conn:
            visit(conn, day, save_id, weight)

    def spend(self, day: date, save_id: str) -> None:
        with self.engine.begin() as conn:
            spend(conn, day, save_id)
