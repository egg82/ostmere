"""Every save and snapshot row still carrying its own manifest written without it, and the manifests no row names then
deleted (`python -m ashfall_app.saves strip [--dry-run]`).

Per row: its own manifest is stored under the digest its row names unless one is held, and the row is stripped only
when the held one is exactly its own, the envelope names the same digest as its row, and the row still holds the text
read (a compare-and-set), so a row a player's write changed meanwhile is left to that write. Rows are read a batch at
a time and each row's write commits on its own, so the run never holds one row's lock while it waits for another's
and never deadlocks a step's write. The prune keeps this build's manifest, which its writes leave out of the rows
from its first one: run it once the deploy has rolled out, as a build still serving under another digest whose
manifest no row names yet would have its manifest pruned (it stores it again at its next start). A dry run counts
what would be done and writes nothing."""

import json
import logging
import time
from dataclasses import dataclass

from sqlalchemy import Engine

from .. import logs
from ..db import manifests
from ..db.strip import KINDS, Kind, Stored, prune, swap, unnamed, whole_rows
from ..engine.codec import canonical
from .interface import Ruleset

_log = logging.getLogger("ashfall.saves")


@dataclass
class Stripped:
    """What a run did (or, dry, would do): rows stripped, kept whole, changed meanwhile, and manifests pruned."""

    stripped: int = 0
    whole: int = 0
    changed: int = 0
    pruned: int = 0


def strip(engine: Engine, rs: Ruleset, dry_run: bool = False, batch: int = 100) -> Stripped:
    t0 = time.perf_counter()
    logs.info(_log, "saves.strip.start", dry_run=dry_run, rules=rs.digest[:12], batch=batch)
    done, held = Stripped(), dict[str, str]()
    for kind in KINDS:
        after: tuple[int, ...] | None = None
        while True:
            with engine.connect() as conn:
                found = whole_rows(conn, kind, after, batch)
            for row in found:
                _one(engine, kind, row, _held(engine, row, held, dry_run), dry_run, done)
            if len(found) < batch:
                break
            after = found[-1].key
    with engine.begin() as conn:
        done.pruned = unnamed(conn, rs.digest) if dry_run else prune(conn, rs.digest)
    logs.info(_log, "saves.strip.finish", dry_run=dry_run, stripped=done.stripped, whole=done.whole,
              changed=done.changed, pruned=done.pruned, ms=int((time.perf_counter() - t0) * 1000))
    return done


def _held(engine: Engine, row: Stored, held: dict[str, str], dry_run: bool) -> str | None:
    """The manifest held for the row's digest once its own is stored unless one was (on a dry run, the one that would
    be); None when the row's text is unreadable."""
    own = _own(row)
    if own is None:
        return None
    if row.rules_digest not in held:
        with engine.begin() as conn:
            found = manifests.held(conn, row.rules_digest) if dry_run else manifests.put(conn, row.rules_digest, own)
        held[row.rules_digest] = own if found is None else found
    return held[row.rules_digest]


def _own(row: Stored) -> str | None:
    """The row's own manifest, when its envelope names the digest its row does; else None."""
    try:
        envelope = json.loads(row.state)
        rules, manifest = envelope["rules"], envelope["manifest"]
    except (ValueError, KeyError, TypeError):
        return None
    return canonical(manifest) if rules == row.rules_digest else None


def _one(engine: Engine, kind: Kind, row: Stored, held: str | None, dry_run: bool, done: Stripped) -> None:
    bare = row.state if held is None else manifests.without(row.state, held)
    if bare == row.state:
        done.whole += 1
        logs.warning(_log, "saves.strip.whole", table=kind, key="/".join(map(str, row.key)),
                     reason="no_own_manifest" if held is None else "manifest_differs")
    elif dry_run:
        done.stripped += 1
    else:
        with engine.begin() as conn:
            if swap(conn, kind, row, bare):
                done.stripped += 1
            else:
                done.changed += 1
