"""The statement that writes the save (db/saves.py's rows): built once with bound parameters (`writing`), so SQLAlchemy
keys and compiles it once, not on every write."""

from datetime import datetime
from typing import Any

from sqlalchemy import Connection, Update, bindparam, case, func, update
from sqlalchemy.dialects.postgresql import JSONB

from ..saves import LISTED, Listed, Written, as_listed, next_number
from ..tables import saves

WRITING: Update = update(saves).where(saves.c.id == bindparam("w_save_id", type_=saves.c.id.type)).values(
    {c.name: bindparam(f"w_{c.name}", type_=c.type) for c in (
        saves.c.updated_at, saves.c.state, saves.c.format, saves.c.rules_digest, saves.c.decisions, saves.c.game_time,
        saves.c.ended_at, saves.c.build, saves.c.release, saves.c.camp_level, saves.c.rule_runs)}
    | {"mix_best": func.coalesce(bindparam("w_mix_best", type_=JSONB(none_as_null=True)), saves.c.mix_best)}
    | {"number": func.coalesce(saves.c.number, next_number(saves.c.account_id))}
    | {c.name: case((saves.c.decisions == bindparam("w_decisions", type_=saves.c.decisions.type), c), else_=None)
       for c in (saves.c.hands_free_at, saves.c.hands_free_wall, saves.c.hands_free_until)})
"""The statement that writes the save, built once with bound parameters (`writing`), so SQLAlchemy keys and compiles
it once, not on every write; one begun by a build before numbers takes the next number now. A write with a decision
drops the kept hands-free answer (db/handsfree.py): the decision changed the save's future."""

_WRITE = WRITING.returning(*LISTED)


def writing(save_id: int, now: datetime, w: Written) -> dict[str, Any]:
    """`WRITING`'s parameters."""
    return {"w_save_id": save_id, "w_updated_at": now, "w_state": w.state, "w_format": w.format,
            "w_rules_digest": w.rules_digest, "w_decisions": w.decisions, "w_game_time": w.game_time,
            "w_ended_at": w.ended_at, "w_build": w.build, "w_release": w.release, "w_camp_level": w.camp_level,
            "w_rule_runs": w.rule_runs, "w_mix_best": w.mix_best}


def write(conn: Connection, save_id: int, now: datetime, w: Written) -> Listed:
    """Writes the save, alone (a step's write is db/step.py). The row as written."""
    return as_listed(conn.execute(_WRITE, writing(save_id, now, w)).one())
