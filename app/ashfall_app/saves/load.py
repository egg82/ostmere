"""A stored save read under a pod's rules (api/CONTRACT.txt, "Saves across releases and pods"): decoded exactly when
it is under them already, else rebased forward (engine DESIGN.txt, "Rebase"). A save last written under a later
content release is not rebased at all: this pod is the older one mid-deploy, and a rebase back to its rules (which can
succeed when the change was only numbers) must not overwrite the newer release's. A save that
cannot be read is Unavailable, so nothing is written and the page asks again."""

import logging
import time
from dataclasses import dataclass

from .. import engine as e
from .. import logs
from ..db.saves import SaveRecord
from .interface import Ruleset, Unavailable

_log = logging.getLogger("ashfall.saves")


@dataclass(frozen=True)
class Loaded:
    save: e.Save
    lines: tuple[e.Line, ...]
    """What the rebase emitted (new content landing at the save's own time); none for an exact read."""
    rebased: bool
    rule_changes: tuple[e.RuleChange, ...] = ()
    """The rebase instant's rule changes (a rule new content installed comes on); none for an exact read."""


def exact(row: SaveRecord, rs: Ruleset) -> bool:
    return row.format == e.FORMAT and row.rules_digest == rs.digest


def newer(row: SaveRecord, rs: Ruleset) -> bool:
    """Last written under a content release later than this pod's (a save of no release yet is of none)."""
    return (row.release or 0) > rs.release


def load(row: SaveRecord, rs: Ruleset) -> Loaded:
    if exact(row, rs):
        try:
            return Loaded(e.decode(row.state, rs.rules), (), False)
        except e.StateFormatError as ex:
            logs.error(_log, "save.rebase_failed", save=row.id, kind="format", id=None)
            raise Unavailable("unreadable") from ex
    if newer(row, rs):
        logs.warning(_log, "save.newer", save=row.id, build=row.build, release=row.release)
        raise Unavailable("a later release")
    t0 = time.perf_counter()
    try:
        done = e.rebase_logged(row.state, rs.rules, rs.renames)
    except e.RebaseError as ex:
        logs.error(_log, "save.rebase_failed", save=row.id, kind=ex.kind.value, id=ex.id)
        raise Unavailable("rebase failed") from ex
    except e.StateFormatError as ex:
        logs.error(_log, "save.rebase_failed", save=row.id, kind="format", id=None)
        raise Unavailable("rebase failed") from ex
    logs.info(_log, "save.rebased", save=row.id, **{"from": row.rules_digest[:12]}, to=rs.digest[:12],
              format_from=row.format, lines=len(done.lines), ms=int((time.perf_counter() - t0) * 1000))
    return Loaded(done.save, done.lines, True, done.rule_changes)
