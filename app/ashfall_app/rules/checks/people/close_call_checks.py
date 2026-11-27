"""The checks on close calls (close_call_entries.py): structure only, never a count or a spacing. The person is a
notable's lane, `at` is a trigger or answer, `change` (when given) is a trigger, an answer or a text key, and only a
person's lane is marked notable. Raises ValueError naming the entry (refs.fail)."""
from typing import TYPE_CHECKING

from ...refs import fail, ids_by_kind

if TYPE_CHECKING:
    from ...schema import Opening


def check_close_calls(o: "Opening") -> None:
    ids = ids_by_kind(o)
    for x in o.lanes:
        if x.notable and (not x.ruled or x.pooled or x.station):
            fail(f"lane {x.id}", "is notable but is not a person")
    notables = {x.id for x in o.lanes if x.notable}
    outcomes = {*(t.id for t in o.triggers), *ids["answer"]}
    seen: set[str] = set()
    for c in o.close_calls:
        where = f"close call {c.id}"
        if c.id in seen:
            fail(where, "duplicate id")
        seen.add(c.id)
        if c.person not in notables:
            fail(where, f"{c.person} is not a notable's lane")
        if c.at not in outcomes:
            fail(where, f"at {c.at} is not a trigger or an answer")
        if c.change is not None and c.change not in outcomes and c.change not in o.text:
            fail(where, f"change {c.change} is not a trigger, an answer or a text key")
