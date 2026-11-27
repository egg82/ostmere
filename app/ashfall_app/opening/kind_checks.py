"""An offer's kind and its answers' roles (engine design/offer-kinds.txt, "OFFER KINDS"): a role exactly where there is a kind,
distinct within an offer, and the same set across the offers of a kind; and a label per role for each kind
(`offer_kinds`), the words of the rule that answers the kind."""
from typing import TYPE_CHECKING

from .refs import fail

if TYPE_CHECKING:
    from .schema import Opening


def check_kinds(o: "Opening") -> None:
    """Fails, naming the offer, for a role on an unkinded offer, a kinded offer's answer with no role, two answers of
    one offer with one role, and two offers of one kind whose role sets differ."""
    roles: dict[str, frozenset[str | None]] = {}
    for x in o.offers:
        have = [a.role for a in x.answers]
        where = f"offer {x.id}"
        if x.kind is None:
            if any(r is not None for r in have):
                fail(where, "an answer has a role but the offer has no kind")
            continue
        if None in have:
            fail(where, "every answer of a kinded offer needs a role")
        if len(set(have)) != len(have):
            fail(where, "two answers share a role")
        if roles.setdefault(x.kind, frozenset(have)) != frozenset(have):
            fail(where, f"its roles differ from the other offers of kind {x.kind}")
    _check_kind_labels(o, roles)


def _check_kind_labels(o: "Opening", roles: dict[str, frozenset[str | None]]) -> None:
    """Fails, naming the kind, for a kind declared twice, declared with no offer, or declared with roles other than its
    offers', and for an offer kind with no declaration: an AnswerKind rule is worded by these labels."""
    declared: dict[str, frozenset[str]] = {}
    for k in o.offer_kinds:
        where = f"offer kind {k.kind}"
        if k.kind in declared:
            fail(where, "is declared twice")
        if k.kind not in roles:
            fail(where, "no offer has this kind")
        have = [r.role for r in k.roles]
        if len(set(have)) != len(have):
            fail(where, "two labels share a role")
        declared[k.kind] = frozenset(have)
    for kind, want in roles.items():
        if kind not in declared:
            fail(f"offer kind {kind}", "has no label per role: declare it under offer_kinds")
        if declared[kind] != want:
            fail(f"offer kind {kind}", "its labelled roles differ from the roles of its offers' answers")
