"""Manifests (engine DESIGN.txt, "Manifest") stored once per rules digest, and a save's text with or without its own.

A save's or snapshot's state is the engine's canonical text, either whole or `stripped` of its manifest; a stripped one
is read `whole` again with its digest's manifest from save_manifests. A canonical envelope's keys sort format,
manifest, rules, save, so the manifest always comes straight after the format, and both directions are exact on any
canonical envelope."""

import json
import re
from typing import Any

from sqlalchemy import ColumnElement, Connection, ScalarSelect, not_, select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from .tables import save_manifests

_HEAD = re.compile(r'\{"format":[0-9]+,')
_KEY = '"manifest":'
_WHOLE_SQL = r'^\{"format":[0-9]+,"manifest":'


def whole(state: str, manifest: str | None) -> str:
    """`state` with `manifest` put back, when `state` is a stripped envelope and `manifest` is given; else `state`."""
    head = _HEAD.match(state)
    if manifest is None or head is None or state.startswith(_KEY, head.end()):
        return state
    return f"{state[:head.end()]}{_KEY}{manifest},{state[head.end():]}"


def without(state: str, manifest: str) -> str:
    """`state` without its manifest when it is a whole envelope carrying exactly `manifest`; else `state`:
    whole(without(t, m), m) == t."""
    head = _HEAD.match(state)
    own = f"{_KEY}{manifest},"
    if head is None or not state.startswith(own, head.end()):
        return state
    return f"{state[:head.end()]}{state[head.end() + len(own):]}"


def stripped(state: str) -> tuple[str, str]:
    """A whole canonical envelope without its manifest, and that manifest's canonical text: whole(*stripped(t)) == t."""
    envelope = json.loads(state)
    manifest = envelope.pop("manifest")
    return _canonical(envelope), _canonical(manifest)


def held_for(state: ColumnElement[str], digest: ColumnElement[str]) -> ScalarSelect[Any]:
    """`digest`'s stored manifest when `state` is stripped of its own, else NULL: a whole state reads nothing more."""
    return select(save_manifests.c.manifest).where(
        save_manifests.c.rules_digest == digest, not_(carries_own(state))).scalar_subquery()


def carries_own(state: ColumnElement[str]) -> ColumnElement[bool]:
    """Whether `state` is a whole envelope, carrying its own manifest."""
    return state.op("~")(_WHOLE_SQL)


def held(conn: Connection, digest: str) -> str | None:
    """The manifest held for `digest`, if any."""
    return conn.execute(select(save_manifests.c.manifest).where(save_manifests.c.rules_digest == digest)
                        ).scalar_one_or_none()


def put(conn: Connection, digest: str, manifest: str) -> str:
    """Stores `manifest` as `digest`'s unless one is held already; the one held for `digest` after."""
    conn.execute(pg_insert(save_manifests).values(rules_digest=digest, manifest=manifest).on_conflict_do_nothing())
    return conn.execute(select(save_manifests.c.manifest).where(save_manifests.c.rules_digest == digest)).scalar_one()


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))
