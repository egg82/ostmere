"""This build's manifest stored under its rules digest (db/manifests.py) before it writes a save, so every save it
writes can be read by any build with the manifest kept apart from the row."""

import logging
from dataclasses import replace

from sqlalchemy import Engine

from .. import logs
from ..db import manifests
from ..engine.codec import canonical, manifest
from .interface import Ruleset

_log = logging.getLogger("ashfall.saves")


def register(engine: Engine, rs: Ruleset) -> bool:
    """Stores the manifest of `rs`'s rules as its digest's unless one is held already; whether the one held is this
    build's (a different one is logged as an error)."""
    mine = canonical(manifest(rs.rules))
    with engine.begin() as conn:
        held = manifests.put(conn, rs.digest, mine)
    agrees = held == mine
    logs.emit(_log, logging.INFO if agrees else logging.ERROR, "saves.manifest", rules=rs.digest[:12],
              agrees=agrees, bytes=len(mine))
    return agrees


def registered(engine: Engine, rs: Ruleset) -> Ruleset:
    """`rs` after `register`: writing saves without their manifest when the one held is this build's, whole
    otherwise."""
    return replace(rs, held_manifest=canonical(manifest(rs.rules)) if register(engine, rs) else None)
