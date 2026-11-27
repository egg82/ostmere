"""The check on a line-only trigger: one marked `line_only` exists to say its line once and gates nothing. Raises
ValueError naming the entry (refs.fail)."""
from typing import TYPE_CHECKING

from ...refs import conditions, fail

if TYPE_CHECKING:
    from ...schema import Opening


def check_line_only(o: "Opening") -> None:
    """A line-only trigger's outcome holds lines and nothing else, and no condition names it."""
    marked = {t.id for t in o.triggers if t.line_only}
    for t in o.triggers:
        if t.line_only and t.outcome.model_dump(exclude_defaults=True).keys() - {"line_keys"}:
            fail(f"trigger {t.id}", "is line_only but its outcome does more than tell lines")
    for where, c, _ in conditions(o):
        if c.id in marked:
            fail(where, f"waits on the line_only trigger {c.id}, which gates nothing")
