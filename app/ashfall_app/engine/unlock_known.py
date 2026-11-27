"""Which unlock ids the rules know (validate_rules asks per unlock; design/core.txt, "Unlocks"), built once per rules object."""
from typing import TYPE_CHECKING

from .derived import derived
from .unlocks import Unlock, UnlockKind

if TYPE_CHECKING:
    from .rules import Rules


def mentioned(rules: "Rules", kind: UnlockKind) -> set[str]:
    """The ids of `kind` the rules mention (the opening, an outcome or a finished): a feature, an entry and a note have
    no declaration, so they are known where they are written."""
    return derived(rules, "_mentioned", _all_mentioned)[kind]


def _all_mentioned(rules: "Rules") -> dict[UnlockKind, set[str]]:
    outcomes = [o for c in rules.cards for o in (c.outcome, c.finished)] + [t.outcome for t in rules.triggers]
    outcomes += [a.outcome for o in rules.offers for a in o.answers]
    found: dict[UnlockKind, set[str]] = {k: set() for k in UnlockKind}
    for u in (*(rules.opening or ()), *(u for o in outcomes for u in o.unlocks)):
        found[u.kind].add(u.id)
    return found


def features(rules: "Rules") -> set[str]:
    return mentioned(rules, UnlockKind.FEATURE)


def unlock_known(rules: "Rules", u: Unlock) -> bool:
    if u.kind in (UnlockKind.FEATURE, UnlockKind.ENTRY, UnlockKind.NOTE):
        return u.id in mentioned(rules, u.kind)
    return u.id in derived(rules, "_unlock_ids", _unlock_ids)[u.kind]


def _unlock_ids(rules: "Rules") -> dict[UnlockKind, set[str]]:
    return {
        UnlockKind.ACTION: {a.id for a in rules.standing}, UnlockKind.CARD: {c.id for c in rules.cards},
        UnlockKind.SKILL: {s.id for s in rules.skills}, UnlockKind.STORE: {s.id for s in rules.stores},
        UnlockKind.CHIP: {c.id for c in rules.chips}, UnlockKind.RETIRED: {c.id for c in rules.cards},
        UnlockKind.OFFER: {o.id for o in rules.offers}, UnlockKind.ANSWERED: {o.id for o in rules.offers},
        UnlockKind.ANSWER: {a.id for o in rules.offers for a in o.answers},
        UnlockKind.JOINED: {d.id for d in rules.lanes if d.ruled}, UnlockKind.LEFT: {d.id for d in rules.lanes if d.ruled},
    }
