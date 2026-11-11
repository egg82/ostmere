"""The content checks on fights (combat-plan item 6, engine DESIGN.txt "FIGHTS"), on the built Rules: ids and fields
only, never text. Each refusal names the failing id (refs.fail). `check_fight_content` runs the four; they read
nothing when the content declares no fight."""
from collections.abc import Iterator

from ..engine import AtLeast, AtMost, CardDef, FightDef, Outcome, Rules, StandingDef, StoreValue, ThreatStrength, UnlockKind
from ..engine.cure_reading import feeds, puts_up
from .refs import fail

COMBAT = "combat"


def check_fight_content(rules: Rules) -> None:
    runners = _runners(rules)
    if not runners:
        return
    _check_ramp_clocks(rules, runners)
    _check_combat_first(rules, set(runners))
    _check_cures(rules, runners)
    _check_tallies(rules, runners)


def _runners(rules: Rules) -> dict[str, tuple[str, CardDef | StandingDef]]:
    """Every fight runner by its unlock id: ("card" | "action", its def)."""
    return {**{str(c.id): ("card", c) for c in rules.cards if c.fight is not None},
            **{str(a.id): ("action", a) for a in rules.standing if a.fight is not None}}


def _outcomes(rules: Rules) -> Iterator[tuple[str, Outcome]]:
    for c in rules.cards:
        yield f"card {c.id}", c.outcome
        yield f"card {c.id} finished", c.finished
    for t in rules.triggers:
        yield f"trigger {t.id}", t.outcome
    for x in rules.offers:
        for a in x.answers:
            yield f"answer {a.id}", a.outcome


def _unlocked_with(out: Outcome, kind: UnlockKind) -> set[str]:
    return {u.id for u in out.unlocks if u.kind is kind}


def _start(rules: Rules, kind: UnlockKind) -> set[str] | None:
    """What a new save starts unlocked of `kind`; None when nothing is gated."""
    return None if rules.opening is None else {u.id for u in rules.opening if u.kind is kind}


def _check_ramp_clocks(rules: Rules, runners: dict[str, tuple[str, CardDef | StandingDef]]) -> None:
    """A trigger aiming at a threat's strength reads a clock store: made by a fight-free standing action, and made or
    costed by nothing else."""
    for t in rules.triggers:
        if not any(isinstance(m.target, ThreatStrength) for m in t.outcome.modifiers):
            continue
        subject = t.when.subject if isinstance(t.when, (AtLeast, AtMost)) else None
        if not isinstance(subject, StoreValue) or not _is_clock(rules, str(subject.store)):
            fail(f"trigger {t.id}", "aims at a threat's strength but its when is not a clock store (made only by "
                 "fight-free standing actions, costed by nothing)")


def _is_clock(rules: Rules, store: str) -> bool:
    made = [a for a in rules.standing if any(str(f.store) == store for f in a.makes)]
    if not made or any(a.fight is not None for a in made):
        return False
    if any(str(f.store) == store for a in rules.standing for f in a.costs):
        return False
    return not any(store in _card_stores(rules, c) for c in rules.cards) and not any(
        store in _fight_stores(c.fight) for c in (*rules.cards, *rules.standing) if c.fight is not None)


def _card_stores(rules: Rules, c: CardDef) -> set[str]:
    return {*(str(f.store) for f in (*c.makes, *c.costs)), *(str(a.store) for a in c.inputs),
            *(str(a.store) for o in (c.outcome, c.finished) for a in o.stores), *feeds(rules, c)}


def _fight_stores(f: FightDef) -> set[str]:
    return {str(f.lost), *([] if f.fought is None else [str(f.fought)]), *(str(a.store) for a in (*f.loses, *f.wounds))}


def _check_combat_first(rules: Rules, runners: set[str]) -> None:
    """A fight runner is unlocked by an outcome that unlocks `combat` too, or after a start that has it."""
    start = _start(rules, UnlockKind.FEATURE)
    if start is None or COMBAT in start:
        return
    for u in rules.opening or ():
        if u.id in runners and u.kind in (UnlockKind.CARD, UnlockKind.ACTION):
            fail(u.id, f"is a fight runner unlocked at the start without {COMBAT}")
    for where, out in _outcomes(rules):
        landed = (_unlocked_with(out, UnlockKind.CARD) | _unlocked_with(out, UnlockKind.ACTION)) & runners
        if landed and COMBAT not in _unlocked_with(out, UnlockKind.FEATURE):
            fail(sorted(landed)[0], f"is a fight runner unlocked by {where} without {COMBAT}")


def _check_cures(rules: Rules, runners: dict[str, tuple[str, CardDef | StandingDef]]) -> None:
    """A lost fight's loses store has something that puts it up, its wounds store something that takes it, each
    unlocked at the start or by an outcome that unlocks the runner: in reach the moment it shows."""
    for rid, (_, r) in runners.items():
        assert r.fight is not None
        reach = _reach(rules, rid)
        for a in r.fight.loses:
            if not any(str(a.store) in _raised(rules, k) for k in reach):
                fail(str(a.store), f"is lost by fight {rid} with nothing in reach that puts it up")
        for a in r.fight.wounds:
            if not any(str(a.store) in _taken(k) for k in reach):
                fail(str(a.store), f"is a wound of fight {rid} with nothing in reach that takes it")


def _reach(rules: Rules, runner: str) -> list[CardDef | StandingDef]:
    """What can be unlocked by the time the runner is: the unlock graph from the start set without the outcomes that
    unlock the runner, plus what those outcomes unlock with it."""
    gate = [o for _, o in _outcomes(rules) if runner in {u.id for u in o.unlocks}]
    ids = _closure(rules, {u.id for u in rules.opening or ()}, gate)
    for o in gate:
        ids |= {u.id for u in o.unlocks}
    ids = _closure(rules, ids, gate)
    return [k for k in (*rules.cards, *rules.standing) if rules.opening is None or str(k.id) in ids]


def _closure(rules: Rules, ids: set[str], skip: list[Outcome]) -> set[str]:
    """`ids` plus everything their outcomes unlock, repeatedly: a trigger always lands, a card's outcome once the card
    is unlocked, an answer once its offer is."""
    sources = [(None, t.outcome) for t in rules.triggers] + [(str(c.id), o) for c in rules.cards for o in (c.outcome, c.finished)] \
        + [(str(x.id), a.outcome) for x in rules.offers for a in x.answers]
    ids = set(ids)
    while True:
        more = {u.id for owner, o in sources if (owner is None or owner in ids) and not any(o is g for g in skip) for u in o.unlocks} - ids
        if not more:
            return ids
        ids |= more


def _raised(rules: Rules, k: CardDef | StandingDef) -> set[str]:
    return puts_up(rules, k) if isinstance(k, CardDef) else {str(f.store) for f in k.makes}


def _taken(k: CardDef | StandingDef) -> set[str]:
    own = {str(f.store) for f in k.costs}
    return own | {str(a.store) for a in k.inputs} if isinstance(k, CardDef) else own


def _check_tallies(rules: Rules, runners: dict[str, tuple[str, CardDef | StandingDef]]) -> None:
    """A tally (a fight's lost or fought store) is made by its fight alone: no outcome or start unlocks it."""
    tallies = {s for _, r in runners.values() if r.fight is not None
               for s in (str(r.fight.lost), *([] if r.fight.fought is None else [str(r.fight.fought)]))}
    for where, out in _outcomes(rules):
        for s in sorted(_unlocked_with(out, UnlockKind.STORE) & tallies):
            fail(s, f"is a tally of a fight, and {where} unlocks it")
    for s in sorted((_start(rules, UnlockKind.STORE) or set()) & tallies):
        fail(s, "is a tally of a fight, and the start unlocks it")
