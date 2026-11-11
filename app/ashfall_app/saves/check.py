"""Every kept save (live, or deleted and still held, so a restore never strands one) dry-rebased under a build's
rules, writing nothing (`python -m ashfall_app.saves check`). The app
runs it at start, so a build that would strand a save never turns ready and the build before it keeps serving. A save
already under these rules is fine as it is; one a later build wrote is not this build's to read (a rollback), and is
counted apart."""

import logging
import time
from dataclasses import dataclass

from sqlalchemy import Engine

from .. import engine as e
from .. import logs
from ..db import saves as rows
from .interface import Ruleset
from .load import exact, newer

_log = logging.getLogger("ashfall.saves")


@dataclass(frozen=True)
class Checked:
    total: int
    ok: int
    failed: int
    newer: int


def check(engine: Engine, rs: Ruleset) -> Checked:
    t0 = time.perf_counter()
    total = ok = failed = later = 0
    with engine.connect() as conn:
        for row in rows.kept_saves(conn):
            total += 1
            if exact(row, rs):
                ok += 1
            elif newer(row, rs):
                later += 1
            elif _rebases(row, rs):
                ok += 1
            else:
                failed += 1
    done = Checked(total=total, ok=ok, failed=failed, newer=later)
    logs.emit(_log, logging.ERROR if failed else logging.INFO, "saves.check", total=total, ok=ok, failed=failed,
              newer=later, ms=int((time.perf_counter() - t0) * 1000))
    return done


def _rebases(row: rows.SaveRecord, rs: Ruleset) -> bool:
    try:
        e.rebase(row.state, rs.rules, rs.renames)
    except e.RebaseError as ex:
        logs.error(_log, "save.rebase_failed", save=row.id, kind=ex.kind.value, id=ex.id)
        return False
    except e.StateFormatError:
        logs.error(_log, "save.rebase_failed", save=row.id, kind="format", id=None)
        return False
    return True
