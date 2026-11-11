"""The checks on a find's amount (OutcomeEntry.found_line_key): the slot `{found}` is filled by the page from
Content.find_infos (api/CONTRACT.txt, "Text and numbers"). Raises ValueError naming the entry (refs.fail)."""
from typing import TYPE_CHECKING

from .name_checks import SLOT
from .refs import fail, outcomes

if TYPE_CHECKING:
    from .schema import Opening

SLOT_NAME = "found"


def check_finds(o: "Opening") -> None:
    """A found_line_key sits in a trigger's outcome of one store and names a line holding the slot once; and no text holds
    the slot without one, since the page would leave it unfilled."""
    keyed: set[str] = set()
    for where, out in outcomes(o):
        key = out.found_line_key
        if key is None:
            continue
        if not where.startswith("trigger "):
            fail(where, "has a found_line_key, which only a trigger's outcome may")
        if key not in out.line_keys:
            fail(where, f"found_line_key {key} is not one of its line_keys")
        if len(out.stores) != 1:
            fail(where, "has a found_line_key, so it must put items in exactly one store")
        if SLOT.findall(o.text.get(key, "")).count(SLOT_NAME) != 1:
            fail(where, f"text {key} must hold the slot {{{SLOT_NAME}}} exactly once")
        keyed.add(key)
    for key, text in o.text.items():
        if SLOT_NAME in SLOT.findall(text) and key not in keyed:
            fail(f"text {key}", f"holds the slot {{{SLOT_NAME}}} but is no trigger's found_line_key")
