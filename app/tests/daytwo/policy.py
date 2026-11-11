"""What a day-two player does when it looks at the screen, before day one's moves (tests/dayone/policy.py): answer the
offer (and set the kind's rule once one of its offers is answered), the one-off steps (A15, A16, the builds in the knob's order, When ready on an
unready build), her task changed to what the next build is short of, her first rule when its line goes red. Each is
one decision of a kind, as day one's: "tap" or "decision" (a rule, her task, the queue, the answer, the choice between
builds). Read off the view the way the page shows it; ids only."""
from dataclasses import dataclass

from ashfall_app.engine import (
    AfterTime, AnswerId, AtMost, CardId, OfferId, Order, Rules, SetOrders, StoreId, StoreValue, TapCard, View, units,
)
from tests.daytwo import content as c
from tests.dayone import sinks
from tests.dayone.policy import Move, cards, lane_free

ONE_OFFS = ("give_stool", "make_room")
"""The day's one-off story steps, tapped the moment they are ready."""
HER_RULE = Order(AtMost(StoreValue(StoreId("damp_wood")), units(5), units(11)), TapCard(CardId(c.CUT)))
"""Her first rule, as the damp wood line's order card fills it in (day_two.toml, order_cards)."""


@dataclass(frozen=True)
class Knobs2:
    first_build: str = "build_shelter"
    answer: str = c.GO
    answer_order: bool = False
    """Sets the kind's answer rule in the Rules tab once an offer of the kind is answered, so its later offers are
    answered the instant they show, present or away. An offer of no kind gets none: the page builds no per-offer rule."""
    other_answers: tuple[tuple[str, str], ...] = ()
    """Further offers (a later kind), as (offer, answer), answered the way the day's own is: by order or when shown."""
    her_task: str = "need"
    """"need": her task switched to what the next build is short of, and back to foraging once both are built;
    "keep": her default task all day."""
    her_rule: bool = True
    """Takes her first rule when the damp wood line it answers goes red."""
    tries_early: bool = True
    """Taps make_room and each build once while unready, as a newcomer does (their failed lines)."""
    stays: bool = False
    """Never leaves a visit early (the babysitter); every other route leaves once nothing is left to act on and no tap
    of theirs lands within the dead gap (player.py)."""


def answer(v: View, rules: Rules, orders: tuple[Order, ...], knobs: Knobs2) -> Move | None:
    """The first answer whose offer is shown and open; then, when the route sets the kind's rule, the rule of a kind an
    answered offer belongs to (sinks.answer_offers)."""
    offers = ((c.OFFER, AnswerId(knobs.answer)), *((OfferId(o), AnswerId(a)) for o, a in knobs.other_answers))
    return sinks.answer_offers(v, rules, orders, offers, knobs.answer_order)


def one_off(v: View, knobs: Knobs2, tried: set[str], bed_by_hand: bool = True) -> Move | None:
    """A ready step, the first build by the knob (a choice while both show), or one early try of an unready one. The
    comfort is tapped here only by a route that does not queue it, and never while A16 or a build waits."""
    if not lane_free(v, "hands"):
        return None
    cs = cards(v)
    bed = (c.BED,) if bed_by_hand and not builds_wait(v) else ()
    order = [*ONE_OFFS, knobs.first_build, *(b for b in c.BUILDS if b != knobs.first_build), *bed]
    ready = next((x for x in order if x in cs and cs[x].blocker is None), None)
    if ready is not None:
        both = all(b in cs for b in c.BUILDS)
        return ("decision" if ready in c.BUILDS and both else "tap"), (TapCard(CardId(ready)),)
    early = next((x for x in order if x in cs and x not in tried), None) if knobs.tries_early else None
    if early is not None:
        tried.add(early)
        return "tap", (TapCard(CardId(early)),)
    return None


def builds_wait(v: View) -> bool:
    """A16 or a build is in view and not yet done: the comfort waits behind them, so it never holds the hands B4's way
    needs."""
    done = {x.card for x in v.completed}
    return any(b in cards(v) and b not in done for b in ("make_room", *c.BUILDS))


def her_rule_index(orders: tuple[Order, ...]) -> int | None:
    """Where her default (always) rule stands in the orders: the rule her row's `Change` edits."""
    return next((i for i, o in enumerate(orders) if isinstance(o.when, AfterTime) and isinstance(o.then, TapCard)
                 and o.then.card in c.TASKS), None)


def wanted_task(v: View, first_build: str) -> str:
    """The task that feeds the first unbuilt build's shortest store; foraging when nothing is short or both are
    built."""
    cs = cards(v)
    for b in (first_build, *(x for x in c.BUILDS if x != first_build)):
        card = cs.get(b)
        if card is None:
            continue
        short = [n.store for n in card.needs if n.store in c.TASK_FOR and n.segment.start_value < n.quantity]
        if short:
            return c.TASK_FOR[short[0]]
    return c.FORAGE


def her_task(v: View, orders: tuple[Order, ...], knobs: Knobs2) -> Move | None:
    """`Change` on her row: her default rule's task edited in place, once the builds are in view."""
    i = her_rule_index(orders)
    if knobs.her_task != "need" or i is None or not any(b in cards(v) for b in c.BUILDS):
        return None
    want = wanted_task(v, knobs.first_build)
    current = orders[i].then
    if isinstance(current, TapCard) and current.card == want:
        return None
    edited = Order(orders[i].when, TapCard(CardId(want)))
    return "decision", (SetOrders((*orders[:i], edited, *orders[i + 1:])),)


def her_first_rule(v: View, orders: tuple[Order, ...], knobs: Knobs2) -> Move | None:
    """The damp wood line's order card, taken while the line is red (falling or starved, uncovered), whatever draws it
    down, as the page offers it (client ui/ledger.ts, offerFor; game/shown.ts drawnDown decides only when a line with no
    offer joins): above her default rule, since a rule below an always rule acts only while that one cannot (engine
    DESIGN.txt, "Ruled lane")."""
    line = next((ln for ln in v.ledger if ln.store == "damp_wood"), None)
    i = her_rule_index(orders)
    if not knobs.her_rule or line is None or i is None or HER_RULE in orders:
        return None
    if not ((line.falling or line.starved) and not line.covered):
        return None
    return "decision", (SetOrders((*orders[:i], HER_RULE, *orders[i:])),)
