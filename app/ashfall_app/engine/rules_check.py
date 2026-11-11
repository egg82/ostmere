"""What makes the rules' lanes, cards, chips, triggers and opening valid (DESIGN.txt, "Validation of cards"), and the
vocabulary check conditions share with the player's verbs. validate_rules (rules.py) calls it.
"""
from typing import TYPE_CHECKING

from .cards import Amount, CardDef, Join, Outcome
from .errors import InvalidRulesError
from .ids import HANDS, TOWN_PREFIX, CardId, TriggerId
from .modifiers import (
    LaneSpeed, Modifier, ModifierKind, RateRef, SideStrength, StoreCap, ThreatStrength, WorkRef, lowers_cap,
    lowers_threat,
)
from .orders import (
    AfterTime, AtLeast, CardCount, Condition, LaneRules, Running, SkillLevel, StoreValue, Subject, Unlocked,
)
from .cardsides import card_costs, card_makes
from .drains import check_drains
from .fightcheck import check_fight, check_no_odds_source, check_tallies, check_while_running, standing_stores
from .planchecks import check_leaves, check_one_leave_each, check_retire
from .unlocks import PRESENT_ONLY, Unlock, UnlockKind

if TYPE_CHECKING:
    from .rules import Rules


def condition_problem(rules: "Rules", cond: Condition) -> str | None:
    """Why `cond` cannot be used under `rules` (an unknown id, a release on the wrong side), or None."""
    if isinstance(cond, AfterTime):
        return None
    problem = subject_problem(rules, cond.subject)
    if problem is not None:
        return problem
    ok = cond.release <= cond.value if isinstance(cond, AtLeast) else cond.release >= cond.value
    return None if ok else "condition release is on the wrong side of its value"


def is_lane_rules(cond: Condition) -> bool:
    """Whether `cond` reads LaneRules, which only a trigger's `when` may (DESIGN.txt, "Lane rules")."""
    return not isinstance(cond, AfterTime) and isinstance(cond.subject, LaneRules)


def subject_problem(rules: "Rules", subject: Subject) -> str | None:
    """A StoreValue's store, a SkillLevel's skill, a CardCount's card, a Running's runner, a LaneRules' ruled lane, an
    Unlocked's id: known."""
    if isinstance(subject, StoreValue):
        known = subject.store in {s.id for s in rules.stores}
    elif isinstance(subject, SkillLevel):
        known = subject.skill in {s.id for s in rules.skills}
    elif isinstance(subject, CardCount):
        known = subject.card in {c.id for c in rules.cards}
    elif isinstance(subject, Running):
        known = subject.runner in _runners(rules)
    elif isinstance(subject, LaneRules):
        known = subject.lane in {d.id for d in rules.lanes if d.ruled}
    else:
        known = _unlock_known(rules, subject.unlock)
    return None if known else f"condition on an unknown {type(subject).__name__} subject"


def check_parts(rules: "Rules") -> None:
    """Raise InvalidRulesError for any constraint on lanes, cards, chips, triggers and the opening (DESIGN.txt,
    "Validation of cards")."""
    _check_ids(rules)
    for card in rules.cards:
        _check_card(rules, card)
    for a in rules.standing:
        if a.fight is not None:
            check_fight(rules, f"action {a.id}", a.fight, [f.store for f in a.makes + a.costs], None)
        check_while_running(rules, f"action {a.id}", a.while_running)
    check_tallies(rules)
    for c in rules.chips:
        _require(condition_problem(rules, c.when) is None, f"chip {c.id}: bad condition")
        _require(not is_lane_rules(c.when), f"chip {c.id}: a chip cannot read LaneRules")
        _require(all(m.source == c.id for m in c.effects), f"chip {c.id}: an effect is not sourced by the chip")
        _check_modifiers(rules, c.effects, f"chip {c.id}")
        _require(not any(isinstance(m.target, StoreCap) for m in c.effects), f"chip {c.id}: a chip cannot aim at a cap")
    for t in rules.triggers:
        _require(condition_problem(rules, t.when) is None, f"trigger {t.id}: bad condition")
        for r in t.requires:
            _require(condition_problem(rules, r) is None, f"trigger {t.id}: bad requirement")
            _require(not isinstance(r, AfterTime) and isinstance(r.subject, (Unlocked, Running)),
                     f"trigger {t.id}: a requirement must be on an unlock or a runner")
        _check_outcome(rules, t.outcome, f"trigger {t.id}", installs=True, trigger=t.id)
    for u in rules.opening or ():
        _require(_unlock_known(rules, u), f"opening: unknown {u.kind.value} {u.id}")
        _require(u.kind not in PRESENT_ONLY, f"opening: only an answer, a join or a leave adds a {u.kind.value} unlock")
    _require(rules.end is None or rules.end in features(rules), f"end: unknown feature {rules.end}")
    _check_offers(rules)
    check_one_leave_each(rules)


def _check_offers(rules: "Rules") -> None:
    """Offer ids unique, answer ids unique across every offer, two or more answers each, and each answer's outcome
    valid as one that may install rules and queue one-offs (DESIGN.txt, "Offers")."""
    offers = [o.id for o in rules.offers]
    answers = [a.id for o in rules.offers for a in o.answers]
    _require(len(set(offers)) == len(offers), "duplicate offer id")
    _require(len(set(answers)) == len(answers), "duplicate answer id (answer ids are unique across offers)")
    for o in rules.offers:
        _require(len(o.answers) >= 2, f"offer {o.id}: needs two or more answers")
        for a in o.answers:
            _check_outcome(rules, a.outcome, f"answer {a.id}", installs=True, queues=True)
    _check_kinds(rules)


def _check_kinds(rules: "Rules") -> None:
    """A kinded offer has a distinct role on every answer, an unkinded one none, and every offer of a kind has the same
    set of roles (DESIGN.txt, "OFFER KINDS")."""
    roles: dict[str, frozenset[str]] = {}
    for o in rules.offers:
        have = [a.role for a in o.answers]
        if o.kind is None:
            _require(all(r is None for r in have), f"offer {o.id}: an answer has a role but the offer has no kind")
            continue
        _require(None not in have, f"offer {o.id}: every answer of a kinded offer needs a role")
        _require(len(set(have)) == len(have), f"offer {o.id}: two answers share a role")
        found = frozenset(str(r) for r in have)
        _require(roles.setdefault(o.kind, found) == found, f"offer {o.id}: its roles differ from the kind {o.kind}'s")


def mentioned(rules: "Rules", kind: UnlockKind) -> set[str]:
    """The ids of `kind` the rules mention (the opening, an outcome or a finished): a feature, an entry and a note have
    no declaration, so they are known where they are written."""
    outcomes = [o for c in rules.cards for o in (c.outcome, c.finished)] + [t.outcome for t in rules.triggers]
    outcomes += [a.outcome for o in rules.offers for a in o.answers]
    unlocks = [u for u in (*(rules.opening or ()), *(u for o in outcomes for u in o.unlocks))]
    return {u.id for u in unlocks if u.kind is kind}


def features(rules: "Rules") -> set[str]:
    return mentioned(rules, UnlockKind.FEATURE)


def _require(ok: bool, message: str) -> None:
    if not ok:
        raise InvalidRulesError(message)


def _runners(rules: "Rules") -> set[str]:
    return {str(a.id) for a in rules.standing} | {str(c.id) for c in rules.cards}


def _check_ids(rules: "Rules") -> None:
    for kind, ids in (("lane", [d.id for d in rules.lanes]), ("chip", [c.id for c in rules.chips]),
                      ("trigger", [t.id for t in rules.triggers])):
        _require(len(set(ids)) == len(ids), f"duplicate {kind} id")
    _require(all(d.id != HANDS for d in rules.lanes), "HANDS always exists and is never declared")
    for kind, ids in (("side", [s.id for s in rules.sides]), ("threat", [t.id for t in rules.threats])):
        _require(len(set(ids)) == len(ids), f"duplicate {kind} id")
    _require(all(s.base >= 0 for s in rules.sides), "side: base must be >= 0")
    _require(all(t.base > 0 for t in rules.threats), "threat: base must be > 0")


def _check_card(rules: "Rules", c: CardDef) -> None:
    where = f"card {c.id}"
    _require(c.lane == HANDS or c.lane in {d.id for d in rules.lanes}, f"{where}: unknown lane")
    _require(c.work_s >= 1, f"{where}: work_s must be >= 1")
    _require(c.cap is None or c.cap >= 1, f"{where}: cap must be >= 1")
    _require(c.skill in {s.id for s in rules.skills} if c.skill is not None else c.xp_per_hour == 0,
             f"{where}: unknown skill")
    _require(c.xp_per_hour >= 0, f"{where}: negative xp")
    _require(c.lane not in {d.id for d in rules.lanes if d.ruled} or (c.skill is None and c.xp_per_hour == 0),
             f"{where}: a card on a ruled lane trains no skill")
    stores = {s.id for s in rules.stores}
    _require(all(f.per_hour >= 0 and f.store in stores for f in c.makes + c.costs), f"{where}: bad flow")
    _check_amounts(rules, c.inputs, where)
    listed = [f.store for f in c.makes + c.costs] + [a.store for a in c.inputs + c.outcome.stores]
    _require(len(set(listed)) == len(listed), f"{where}: a store is listed twice across makes, costs, inputs and outcome stores")
    if c.fight is not None:
        check_fight(rules, where, c.fight, listed, c)
    check_while_running(rules, where, c.while_running)
    check_drains(rules, where, c, listed)
    for cond in c.requires:
        _require(condition_problem(rules, cond) is None, f"{where}: bad requires condition")
        _require(isinstance(cond, AfterTime) or cond.release == cond.value,
                 f"{where}: a requires is a plain threshold (release == value)")
        _require(isinstance(cond, AfterTime) or not isinstance(cond.subject, Running),
                 f"{where}: a requires may not read Running (it would define itself)")
        _require(not is_lane_rules(cond), f"{where}: a requires cannot read LaneRules")
    _check_outcome(rules, c.outcome, where)
    _check_outcome(rules, c.finished, f"{where} finished")
    _check_cap_shape(c, where)
    _check_hands_chain(rules, c, where)


def _check_cap_shape(c: CardDef, where: str) -> None:
    if c.cap is None:
        _require(c.finished == Outcome(), f"{where}: finished needs a cap")
        _require(len(c.lines) <= 1, f"{where}: at most one line without a cap")
        o = c.outcome
        _require(not (o.unlocks or o.modifiers or o.raises or o.starts or o.lines),
                 f"{where}: without a cap the outcome holds stores only")
    else:
        _require(not c.lines or len(c.lines) == c.cap, f"{where}: lines must be empty or one per completion")


def _check_hands_chain(rules: "Rules", c: CardDef, where: str) -> None:
    started = {s for o in (c.outcome, c.finished) for s in o.starts}
    hands = {x.id for x in rules.cards if x.lane == HANDS}
    _require(not (c.lane == HANDS and started & hands), f"{where}: its completion taps a HANDS card on HANDS")


def _check_amounts(rules: "Rules", amounts: tuple[Amount, ...], where: str) -> None:
    stores = {s.id for s in rules.stores}
    _require(all(a.quantity > 0 and a.store in stores for a in amounts), f"{where}: bad amount (>0, known store)")


def _check_outcome(
    rules: "Rules", o: Outcome, where: str, installs: bool = False, queues: bool = False, trigger: TriggerId | None = None,
) -> None:
    """`installs`: a trigger's or an answer's outcome, which may install rules; `queues`: an answer's, which may also
    queue hands one-offs (DESIGN.txt, "Installs land once"); `trigger`: the trigger whose outcome it is, the only source
    that may raise a ThreatStrength (DESIGN.txt, "FIGHTS")."""
    capped = {c.id for c in rules.cards if c.cap is not None}
    ruled = {d.id for d in rules.lanes if d.ruled}
    lanes = {c.id: c.lane for c in rules.cards}
    _require(installs or not o.orders, f"{where}: only a trigger's or an answer's outcome installs a rule")
    _require(all(lanes.get(i.card) in ruled for i in o.orders), f"{where}: an installed rule taps a card on a ruled lane")
    _require(installs or not o.joins, f"{where}: only a trigger's or an answer's outcome joins a person")
    _require(all(_join_problem(rules, j, capped) is None for j in o.joins), f"{where}: a join is not valid")
    _require(queues or not o.queues, f"{where}: only an answer's outcome queues a one-off")
    _require(all(lanes.get(q) == HANDS and q in capped for q in o.queues),
             f"{where}: a queued one-off is a hands card with a cap")
    _check_amounts(rules, o.stores, where)
    _require(all(_unlock_known(rules, u) for u in o.unlocks), f"{where}: outcome unlocks an unknown id")
    _require(not any(u.kind in PRESENT_ONLY for u in o.unlocks),
             f"{where}: only an answer, a join or a leave adds an answered, answer, joined or left unlock")
    _check_modifiers(rules, o.modifiers, where, trigger)
    _require(all(r.card in capped and r.by > 0 for r in o.raises), f"{where}: a raise needs a capped card and by > 0")
    _require(all(q in {c.id for c in rules.cards} for q in o.starts), f"{where}: outcome starts an unknown card")
    check_retire(rules, o, where, trigger is not None)
    check_leaves(rules, o, where, installs)


def _join_problem(rules: "Rules", j: Join, capped: set[CardId]) -> str | None:
    """Why `j` cannot be a join, or None: its lane is a declared ruled lane, its mix id a town one, its card (if any)
    an uncapped card on that lane (DESIGN.txt, "THE TOWN'S MIX", invariant 96)."""
    if j.lane not in {d.id for d in rules.lanes if d.ruled}:
        return "lane is not a declared ruled lane"
    if not j.mix.startswith(TOWN_PREFIX):
        return f"mix does not begin {TOWN_PREFIX!r}"
    on_lane = {c.id for c in rules.cards if c.lane == j.lane}
    return None if j.card is None or (j.card in on_lane and j.card not in capped) else "card is not an uncapped card on the lane"


def _check_modifiers(
    rules: "Rules", modifiers: tuple[Modifier, ...], where: str, trigger: TriggerId | None = None,
) -> None:
    _require(all(m.kind is not ModifierKind.MUL_BP or m.amount_bp >= 0 for m in modifiers),
             f"{where}: negative multiplier")
    _require(all(_target_known(rules, m) for m in modifiers), f"{where}: a modifier aims at an unknown id")
    check_no_odds_source(modifiers, where)
    _require(not any(lowers_cap(m) for m in modifiers), f"{where}: a store cap modifier may only raise the cap")
    threat = [m for m in modifiers if isinstance(m.target, ThreatStrength)]
    _require(not any(lowers_threat(m) for m in threat), f"{where}: a threat's strength only rises")
    _require(all(m.source == trigger for m in threat), f"{where}: only a trigger's outcome aims at a threat, sourced by that trigger")


def _target_known(rules: "Rules", m: Modifier) -> bool:
    t = m.target
    if isinstance(t, WorkRef):
        return t.card in {c.id for c in rules.cards}
    if isinstance(t, StoreCap):
        return t.store in {s.id for s in rules.stores}
    if isinstance(t, SideStrength):
        return t.side in {s.id for s in rules.sides}
    if isinstance(t, ThreatStrength):
        return t.threat in {s.id for s in rules.threats}
    if isinstance(t, LaneSpeed):
        return t.lane == HANDS or t.lane in {d.id for d in rules.lanes}
    return _rate_known(rules, t)


def _rate_known(rules: "Rules", t: RateRef) -> bool:
    card = next((c for c in rules.cards if c.id == t.runner), None)
    if card is not None:
        flows = card_makes(card) | card_costs(card)
    else:
        standing = next((a for a in rules.standing if a.id == t.runner), None)
        if standing is None:
            return False
        flows = set(standing_stores(standing))
    return t.store is None if t.kind.value == "xp" else t.store in flows


def _unlock_known(rules: "Rules", u: Unlock) -> bool:
    ids = {
        UnlockKind.ACTION: [a.id for a in rules.standing], UnlockKind.CARD: [c.id for c in rules.cards],
        UnlockKind.SKILL: [s.id for s in rules.skills], UnlockKind.STORE: [s.id for s in rules.stores],
        UnlockKind.CHIP: [c.id for c in rules.chips], UnlockKind.RETIRED: [c.id for c in rules.cards],
        UnlockKind.OFFER: [o.id for o in rules.offers], UnlockKind.ANSWERED: [o.id for o in rules.offers],
        UnlockKind.ANSWER: [a.id for o in rules.offers for a in o.answers],
        UnlockKind.JOINED: [d.id for d in rules.lanes if d.ruled], UnlockKind.LEFT: [d.id for d in rules.lanes if d.ruled],
    }
    if u.kind in (UnlockKind.FEATURE, UnlockKind.ENTRY, UnlockKind.NOTE):
        return u.id in mentioned(rules, u.kind)
    return u.id in ids[u.kind]
