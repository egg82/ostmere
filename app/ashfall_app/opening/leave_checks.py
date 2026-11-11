"""The check on people leaving (week-three-plan item 4; engine DESIGN.txt, "LEAVES", "Content"): only a trigger's or an
answer's outcome has a person leave, each a ruled lane left once across the content, each stop a standing action, and
never a lane the same outcome joins. Raises ValueError naming the entry (refs.fail)."""
from typing import TYPE_CHECKING

from .refs import fail, outcomes

if TYPE_CHECKING:
    from .schema import Opening


def check_leaves(o: "Opening") -> None:
    ruled = {d.id for d in o.lanes if d.ruled}
    standing = {a.id for a in o.standing}
    once = {f"trigger {t.id}" for t in o.triggers} | {f"answer {a.id}" for x in o.offers for a in x.answers}
    left: set[str] = set()
    for where, out in outcomes(o):
        if out.leaves and where not in once:
            fail(where, "only a trigger's or an answer's outcome has a person leave")
        joined = {j.lane for j in out.joins}
        for leave in out.leaves:
            if leave.lane not in ruled:
                fail(where, f"leaves {leave.lane}, which is not a ruled lane")
            if leave.lane in left:
                fail(where, f"leaves {leave.lane}, which another outcome already leaves")
            if leave.lane in joined:
                fail(where, f"joins {leave.lane} in the outcome that leaves it")
            for a in leave.stops:
                if a not in standing:
                    fail(where, f"leaves {leave.lane}, stopping {a}, which is not a standing action")
            left.add(leave.lane)
