"""One log line per API request (logs.py): the route's template, the save id, the decision's kind and target id, the
`after` it was sent with, status, ms, error code if any, and, from the page's headers, wall seconds since Begin and since
the player's previous decision; failed=1 when the tap was a failed tap. Ids, counts and durations only: never
a state, a cookie, the client address or any player content."""
import json
import logging
from collections.abc import Mapping
from dataclasses import dataclass
from typing import cast

from .. import logs

_log = logging.getLogger("ashfall.game")
WALL_HEADER = "x-ashfall-wall"   # seconds since Begin
GAP_HEADER = "x-ashfall-gap"   # seconds since this player's previous decision
_TARGET_KEYS = ("card",)   # the content id a decision names, when it names one
_MAX_ID = 64


@dataclass(frozen=True)
class Asked:
    kind: str = "none"
    target: str | None = None
    after: int | None = None


def _as_obj(v: object) -> dict[str, object] | None:
    """v as a JSON object, or None. JSON object keys are always strings."""
    if not isinstance(v, dict):
        return None
    return cast(dict[str, object], v)  # cast -- isinstance leaves dict[Unknown, Unknown]; JSON keys are str


def _obj(raw: bytes) -> dict[str, object]:
    found: object = None
    try:
        if raw:
            found = json.loads(raw)
    except ValueError:
        return {}
    return _as_obj(found) or {}


def describe(body: bytes) -> Asked:
    """What a request body decided: kind is 'none' with no decision in it."""
    req = _obj(body)
    after = req.get("after")
    when = after if isinstance(after, int) and not isinstance(after, bool) else None
    dec = _as_obj(req.get("decision"))
    if dec is None:
        return Asked("none", None, when)
    kind = dec.get("kind")
    target = next((v for k in _TARGET_KEYS if isinstance(v := dec.get(k), str)), None)
    if target is None and isinstance(mix := dec.get("mix_id"), str):
        target = logs.tag(mix)   # a mix id is the player's own text
    return Asked(kind if isinstance(kind, str) else "invalid", target[:_MAX_ID] if target else None, when)


def failed_tap(asked: Asked, response_body: bytes) -> int | None:
    """1 when the answer names the tapped card as a failed tap (Step.failed_tap), 0 when not, None for no tap."""
    if asked.target is None or asked.kind != "tap_card":
        return None
    return 1 if _obj(response_body).get("failed_tap") == asked.target else 0


def seconds(headers: Mapping[str, str], name: str) -> int | None:
    value = headers.get(name, "")
    return int(value) if value.isdecimal() and len(value) <= 8 else None


def record(route: str, save_id: object, body: bytes, status: int, ms: int, error_code: str | None,
           headers: Mapping[str, str], response_body: bytes) -> None:
    asked = describe(body)
    save = save_id if isinstance(save_id, str) and save_id.isdecimal() and len(save_id) <= 18 else None
    logs.info(
        _log, "game.request", route=route, save=save, decision=asked.kind, target=asked.target, after=asked.after,
        status=status, ms=ms, error=error_code, wall_s=seconds(headers, WALL_HEADER),
        gap_s=seconds(headers, GAP_HEADER), failed=failed_tap(asked, response_body) if status == 200 else None)
