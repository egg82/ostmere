"""What a page keeps about the player (api/CONTRACT.txt, AccountPresentation) only grows: a flag once set stays set and
a list only gains entries. A page's copy can be older than the stored one (a second tab, a second device), so a write
is merged into what is stored: flags OR together, lists are the stored entries then the new ones. What is stored
weighs at most MAX_BODY_BYTES of JSON, as much as one request may carry: past that, nothing more is added."""

import json
from typing import TypeGuard

from .body_limit import MAX_BODY_BYTES
from .interface import Json

NEWEST = {"visits": 200}
"""For a list that keeps its newest entries, how many: past that the oldest go, where any other list stops gaining. The
page's game/loggroups.ts MAX_VISITS and the API's MAX_VISITS are the same number."""

_KEYS = {"lesson_ends": "lesson", "visits": "left"}
"""For a list of objects, the field that names an entry: a second entry for one name is the same entry."""


def _is_list(value: object) -> TypeGuard[list[object]]:
    return isinstance(value, list)


def _is_object(value: object) -> TypeGuard[dict[str, object]]:
    return isinstance(value, dict)


def _name(field: str, item: object) -> object:
    key = _KEYS.get(field)
    if key is not None and _is_object(item):
        return item.get(key)
    return repr(item)


def _weight(value: object) -> int:
    """The bytes `value` adds to the stored JSON, with its separator."""
    return len(json.dumps(value, separators=(",", ":"), ensure_ascii=False).encode()) + 1


def _grown(field: str, stored: list[object], sent: list[object], cap: int, room: int) -> list[object]:
    seen = {_name(field, i) for i in stored}
    grown = list(stored)
    for item in sent:
        if len(grown) >= cap or (cost := _weight(item)) > room:
            break
        if (name := _name(field, item)) not in seen:
            seen.add(name)
            grown.append(item)
            room -= cost
    return grown


def merge_presentation(stored: Json, sent: Json, cap: int, max_bytes: int = MAX_BODY_BYTES) -> Json:
    """`stored` with `sent` added; a list stops growing at `cap` entries (one in NEWEST keeps its newest instead), and
    nothing is added past `max_bytes` of JSON (the stored ones always stay, but for a NEWEST list's oldest)."""
    merged: Json = dict(stored)
    room = max_bytes - _weight(stored)
    for field, value in sent.items():
        have = merged.get(field)
        if isinstance(value, bool):
            merged[field] = value or have is True
        elif _is_list(value):
            kept = have if _is_list(have) else []
            newest = NEWEST.get(field)
            grown = _grown(field, kept, value, len(kept) + len(value) if newest else cap, room)
            room -= sum(_weight(i) for i in grown[len(kept):])
            merged[field] = grown[-newest:] if newest else grown
        else:
            merged[field] = value
    return merged
