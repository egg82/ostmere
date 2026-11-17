"""The hands-free answer a save keeps (docs/design/reminders.md, "The hands-free notice"): the forecast's hands_free_at
(engine DESIGN.txt, "Forecast"), kept only when the player gave the hands that work at least `min_busy_s` before it,
with how far the forecast reached. The reminders job forecasts each save whose kept answer a decision dropped or time
ran out (`refresh`); the forecast route keeps nothing, so it stays one checkout and writes nothing. Whether a notice is
due and sending it is reminders/notices.py's."""

import logging
from collections.abc import Callable, Sequence
from dataclasses import dataclass

from sqlalchemy import Engine

from .. import engine as e
from .. import logs
from ..db import handsfree as rows
from ..db import saves as save_rows
from ..db import unit
from ..db.saves import DecisionRecord
from .interface import Ruleset, Unavailable
from .load import load
from .repeats import hands_cards

HORIZON_S = 6 * 3600
"""How far ahead a forecast looks, the forecast route's (api/CONTRACT.txt, "Forecast": past it the page draws no time)
and the job's alike."""
_log = logging.getLogger("ashfall.saves")


@dataclass(frozen=True)
class Kept:
    at: int | None
    until: int


def kept(f: e.Forecast, given_at: int | None, min_busy_s: int) -> Kept:
    """The forecast's hands-free instant, unless the player gave the hands that work less than `min_busy_s` before it
    (or no decision that gave it is on the log)."""
    at = f.hands_free_at
    if at is not None and (given_at is None or at - given_at < min_busy_s):
        at = None
    return Kept(at, f.until)


def given_at(logged: Sequence[DecisionRecord], hands: frozenset[e.CardId]) -> int | None:
    """When the player last gave the hands work, from the log newest first: a tap of a hands card, or a queue set with
    an entry in it. A tap that failed is logged as one too, and counts."""
    for d in logged:
        verb = e.verb_from_json(d.verb)
        if isinstance(verb, e.TapCard) and verb.card in hands or isinstance(verb, e.SetQueue) and verb.entries:
            return d.at
    return None


def keep_answer(engine: Engine, rs: Ruleset, f: e.Forecast, ids: tuple[int, int, int], min_busy_s: int) -> bool:
    """Keeps `f`, the forecast of the save `ids` names (save, account, the decision count it was made at); False when
    a decision was written since."""
    save_id, account_id, decisions = ids
    with unit.begin(engine) as conn:
        k = kept(f, given_at(rows.giving(conn, save_id), hands_cards(rs.rules)), min_busy_s)
        return rows.keep(conn, save_id, account_id, decisions, k.at, k.until)


def refresh(engine: Engine, rs: Ruleset, latest: rows.Latest, min_busy_s: int, stop: Callable[[], bool]) -> bool:
    """Forecasts the save afresh and keeps the answer: from where the kept forecast reached, or, with none kept since
    the last decision, from the save as written. False when the save cannot be read or advanced within `stop`, or a
    decision was written meanwhile; each is logged."""
    with unit.read(engine) as conn:
        row = save_rows.save(conn, latest.save_id, latest.account_id)
    unit.release()
    if row is None or row.decisions != latest.decisions:
        return False
    try:
        save = load(row, rs).save
    except Unavailable as ex:
        logs.warning(_log, "hands_free.refresh_failed", save=latest.save_id, why=ex.reason)
        return False
    if latest.until is not None and latest.until > save.time:
        moved = e.advance_logged(save, rs.rules, latest.until, stop)
        if moved.stopped_short:
            logs.warning(_log, "hands_free.refresh_failed", save=latest.save_id, why="advance_cut")
            return False
        save = moved.save
    f = e.forecast(save, rs.rules, save.time + HORIZON_S, (), stop)
    return keep_answer(engine, rs, f, (latest.save_id, latest.account_id, latest.decisions), min_busy_s)
