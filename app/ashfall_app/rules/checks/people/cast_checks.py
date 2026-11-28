"""The checks on a role's cast (api/contract/casting.txt, "CASTING", "Loader refusals"): where a cast may sit, what a role
is called, that its patterns are town cards, and that a text naming the role can only show once it is cast. Raises
ValueError naming the entry (refs.fail)."""
import re
from collections.abc import Iterable
from typing import TYPE_CHECKING

from ....engine import HANDS
from ...casts import cast_outcomes, casts, role_features
from ...entries.entries import ConditionEntry, UnlockEntry
from ...refs import fail, outcomes
from ..text.name_checks import SLOT
from ..text.slot_checks import fixed_slots

if TYPE_CHECKING:
    from ...schema import Opening

ROLE = re.compile(r"[A-Za-z][A-Za-z0-9_]*")


def check_casts(o: "Opening") -> None:
    once = {where for where, _ in cast_outcomes(o)}
    for where, out in outcomes(o):
        if out.casts and where not in once:
            fail(where, "only a trigger's or an answer's outcome casts a role")
    lanes = {HANDS, *(x.id for x in o.lanes)}
    town = {tc.id for tc in o.town_cards}
    named: set[str] = set()
    for where, c in casts(o):
        if ROLE.fullmatch(c.role) is None:
            fail(where, f"casts {c.role}, which is not a word of letters, digits and underscores")
        if c.role in lanes or c.role in fixed_slots():
            fail(where, f"casts {c.role}, which names a lane or a slot the page fills elsewhere")
        if c.role in named:
            fail(where, f"casts {c.role}, which another outcome already casts")
        named.add(c.role)
        if not o.text.get(c.label_key, "").strip():
            fail(where, f"casts {c.role}, which has no display name (text key {c.label_key!r} is missing or empty)")
        for i, pattern in enumerate(c.patterns):
            if pattern not in town:
                fail(where, f"casts {c.role} by {pattern}, which is no town card's id pattern")
            if pattern in c.patterns[:i]:
                fail(where, f"casts {c.role} by {pattern} twice")
    features = [f for fs in role_features(o).values() for f in fs]
    if len(features) != len(set(features)):
        fail("casts", "two roles unlock the same feature")


def check_cast_text(o: "Opening", key_fields: Iterable[tuple[str, str]]) -> None:
    """A text holding `{<role>}` belongs only to what a cast of the role comes before: the lines of the outcome that
    casts it, a later label or an owner gated on one of the role's features."""
    roles = role_features(o)
    if not roles:
        return
    fields = list(key_fields)
    allowed = {r: _allowed(o, r, fs, fields) for r, fs in roles.items()}
    for where, key in fields:
        for slot in SLOT.findall(o.text.get(key, "")):
            if slot in roles and (where, key) not in allowed[slot]:
                fail(f"text {key}", f"holds the slot {{{slot}}}, which can show before {slot} is cast (in {where})")


def _reads(c: ConditionEntry, features: set[str]) -> bool:
    return (c.subject_kind == "unlocked" and c.unlock_kind == "feature" and c.id in features
            and c.test == "at_least" and c.value >= 1)


def _names(u: UnlockEntry, features: set[str]) -> bool:
    return u.unlock_kind == "feature" and u.id in features


def _allowed(o: "Opening", role: str, features: set[str], fields: list[tuple[str, str]]) -> set[tuple[str, str]]:
    """The (owner, text key) pairs where the role's slot may be held."""
    out: set[tuple[str, str]] = set()
    for where, outcome in outcomes(o):
        if any(c.role == role for c in outcome.casts):
            out |= {(where, k) for k in outcome.line_keys}
    for x in o.lanes:
        out |= {(f"lane {x.id}", lb.label_key) for lb in x.later_labels if _names(lb.after, features)}
    out |= {("town title", lb.label_key) for lb in o.town_later_labels if _names(lb.after, features)}
    return out | _gated(o, features, fields)


def _gated(o: "Opening", features: set[str], fields: list[tuple[str, str]]) -> set[tuple[str, str]]:
    """Every text of an owner that holds only once one of `features` is unlocked, as the owners' texts are named."""
    owners: set[str] = {f"card {c.id}" for c in o.cards if any(_reads(x, features) for x in c.requires)}
    owners |= {f"trigger {t.id}" for t in o.triggers if any(_reads(x, features) for x in (t.when, *t.requires))}
    owners |= {f"aim {a.id}" for a in o.aims if a.after is not None and _names(a.after, features)}
    for x in o.offers:
        if any(_reads(c, features) for c in (x.gate, *x.requires)):
            owners |= {f"offer {x.id}", *(f"answer {a.id}" for a in x.answers)}
    return {(w, k) for w, k in fields if w in owners}
