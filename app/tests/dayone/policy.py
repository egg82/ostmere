"""What a day-one player does when it looks at the screen: the moves, most pressing first, read off the view the way
the page shows it. The opening's moves come first (playthrough.Player), then day one's: the rising-line rule under a
full catch line, a rule re-tuned to what Take stock asks, When ready on an unready step (kept in order of when each
turns ready), then taps (the one-off steps, the wood a build is short of, a smoke by hand when no rule smokes).

A player is set by its knobs (Knobs): which build first, whether it takes the rule and the queue, whether it sits up.
Every move is one decision of a kind: "tap", or "decision" (a rule, a mix, the queue, or the choice between builds)."""
from dataclasses import dataclass

from ashfall_app.engine import (
    AtLeast, AtMost, CardCount, CardId, CardView, Order, Prestige, QueueEntry, SetOrders, SetQueue, StoreId, StoreValue,
    TapCard, Verb, View, units,
)
from tests.opening.playthrough import Kind

Move = tuple[Kind, tuple[Verb, ...]]
BUILDS = ("build_lean_to", "build_larder")
STEPS = ("look_out", "set_snare", "look_over_camp", "build_smoke_rack", "take_stock")
"""The one-off steps a player taps the moment they are ready (the builds go by the knob's order)."""
QUEUEABLE = ("set_snare", *BUILDS, "build_smoke_rack", "take_stock")
"""Steps the queue's When ready can wait on: the day's rate- and cap-raising steps."""
SMOKE, SMOKE_ROOTS, CATCH, ROOTS, TAKE_STOCK = "smoke_catch", "smoke_roots", "catch", "roots", "take_stock"
HUNGRY, COOK = "hungry", "cook_roots"
WEAVE, SCREEN = "weave_wattle", "screen_fire"
"""Day one's sink: the weave, held against damp wood in the mix (sinks.Trip), and the comfort it feeds."""


@dataclass(frozen=True)
class Knobs:
    first_build: str = "build_lean_to"
    rising_rule: bool = True
    """Takes the rule offered under a full catch line; False smokes by hand."""
    queue: bool = True
    """Uses When ready on an unready step whose ready time is known; False taps it once present and ready."""
    sits_up: bool = True
    hunger_rule: bool = True
    """Sets hunger's rule up once cooking opens (the rule the strip's card would add, written ahead in the Rules tab);
    False cooks by hand each time the chip shows."""
    mix_weave: bool = True
    """Adds the weave to the mix once damp wood's line shows (sinks.mix_trip); False leaves it out."""
    screen_rule: bool = True
    """Takes the screen's order card once it shows; False builds each stage by hand when ready (only with mix_weave)."""


def prestige_click(v: View) -> Move | None:
    """The first skill waiting at its top, clicked into the first node of its menu: a visit's first act, since the
    click is by hand only and the carry keeps a click at the next visit level with one at the top."""
    for b in v.skills:
        p = b.prestige
        if p is not None and p.at_top and p.menu:
            return "decision", (Prestige(b.skill, p.menu[0].node),)
    return None


def cards(v: View) -> dict[str, CardView]:
    return {c.card: c for c in v.cards}


def lane_free(v: View, lane: str) -> bool:
    return any(b.lane == lane and b.card is None for b in v.lanes)


def items(v: View, store: str) -> float:
    line = next((ln for ln in v.ledger if ln.store == store), None)
    return 0.0 if line is None else line.segment.start_value / units(1)


def rising_rule(v: View, orders: tuple[Order, ...], rising: Order | None) -> Move | None:
    """The catch line's card, offered while the line is full or rising and the smoke lane idle (day-one.md)."""
    line = next((ln for ln in v.ledger if ln.store == CATCH), None)
    if rising is None or line is None or SMOKE not in cards(v) or not lane_free(v, "smoke"):
        return None
    if any(getattr(o.when, "subject", None) == StoreValue(StoreId(CATCH)) for o in orders):
        return None
    if line.segment.rate > 0 or line.segment.start_value >= line.cap:
        return "decision", (SetOrders((*orders, rising)),)
    return None


def retuned_roots(v: View, orders: tuple[Order, ...], offered: Order | None) -> Move | None:
    """Take stock asks for more roots than the roots rule keeps: once the content offers the rule re-tuned to it
    (`offered`: its order card, offered when the larder can hold it), the player takes it in the old rule's place.
    Before the offer the rule is left alone: raised past the roots cap it would never let go, and its forage would hold
    the hands for good (an always-true order starves the mix: engine DESIGN.txt, "Orders")."""
    stock = cards(v).get(TAKE_STOCK)
    need = next((n.quantity for n in stock.needs if n.store == ROOTS), None) if stock is not None else None
    if offered is None or need is None or offered in orders:
        return None
    i = next((i for i, o in enumerate(orders)
              if isinstance(o.when, AtMost) and o.when.subject == StoreValue(StoreId(ROOTS))), len(orders))
    return "decision", (SetOrders((*orders[:i], offered, *orders[i + 1:])),)


def queued(v: View, queue: tuple[QueueEntry, ...], completions: dict[str, int],
           queueable: tuple[str, ...] = QUEUEABLE, behind_hands: tuple[str, ...] = ()) -> Move | None:
    """When ready on the first unready queueable step with a known ready time not already waiting; the queue kept in
    order of ready time, since its head waits (DESIGN.txt, "Orders": the queue is the plan). `behind_hands`: steps
    also queued when ready but for the hands tapping another card, to start when that tap ends."""
    have = {e.verb.card for e in queue if isinstance(e.verb, TapCard)}
    ready: dict[str, int] = {c.card: v.time if c.blocker is None else c.blocker.ready_at or v.time for c in v.cards}
    hands = next((b for b in v.lanes if b.lane == "hands" and b.card is not None), None)
    behind = {c.card for c in v.cards if hands is not None and c.card in behind_hands and c.card != hands.card
              and c.blocker is None}
    if hands is not None:
        ready |= {card: hands.completes_at or v.time for card in behind}
    for c in v.cards:
        waits = c.blocker is not None and c.blocker.ready_at is not None
        if c.card in queueable and c.card not in have and (waits or c.card in behind):
            n = completions[c.card] + 1
            entry = QueueEntry(TapCard(c.card), AtLeast(CardCount(c.card), n, n))
            order = sorted([*queue, entry], key=lambda e: ready.get(_card_of(e), v.time))
            return "decision", (SetQueue(tuple(order)),)
    return None


def _card_of(entry: QueueEntry) -> str:
    return entry.verb.card if isinstance(entry.verb, TapCard) else ""


def screen_rule(v: View, orders: tuple[Order, ...], offered: Order | None) -> Move | None:
    """The screen's rule, taken as soon as its card shows: it taps a stage whenever a stage's wattle is in."""
    if offered is None or SCREEN not in cards(v) or offered in orders:
        return None
    return "decision", (SetOrders((*orders, offered)),)


def hunger(v: View, knobs: Knobs, accept: tuple[Verb, ...] | None) -> Move | None:
    """Hunger's rule set up once cooking is open, before the chip needs it (`accept`: the rule the strip's chip card
    would add, None before cooking opens or once a rule is on its condition); without the knob, roots cooked by hand
    while hungry, once ready with the hands free."""
    if accept is None:
        return None
    if knobs.hunger_rule:
        return "decision", accept
    if HUNGRY not in v.chips:
        return None
    cook = cards(v).get(COOK)
    return ("tap", (TapCard(CardId(COOK)),)) if cook is not None and cook.blocker is None and lane_free(v, "hands") \
        else None


def tap(v: View, knobs: Knobs, rising_taken: bool, tried_roots: bool) -> Move | None:
    """A tap: a ready step, the first build by the knob (a choice while both show), wood a build is short of, a smoke
    by hand when no rule smokes, one smoke of roots to see the tradeoff."""
    cs = cards(v)
    ready = {k for k, c in cs.items() if c.blocker is None}
    hands = lane_free(v, "hands")
    builds = [knobs.first_build, *(b for b in BUILDS if b != knobs.first_build)]
    order = [*(["sit_up"] if knobs.sits_up else []), "look_out", "set_snare", "look_over_camp", *builds,
             "build_smoke_rack", TAKE_STOCK, *([] if knobs.screen_rule or not knobs.mix_weave else [SCREEN])]
    step = next((c for c in order if c in ready), None)
    if hands and step is not None:
        return ("decision" if step in BUILDS and all(b in cs for b in BUILDS) else "tap"), (TapCard(CardId(step)),)
    short = [n for c in (*BUILDS, "build_smoke_rack") if c in cs and c not in ready for n in cs[c].needs
             if n.store == "dry_wood" and n.segment.start_value < n.quantity]
    if short and "lay_to_dry" in ready and lane_free(v, "rack"):
        return "tap", (TapCard(CardId("lay_to_dry")),)
    if lane_free(v, "smoke"):
        if not rising_taken and SMOKE in ready:
            return "tap", (TapCard(CardId(SMOKE)),)
        if not tried_roots and SMOKE_ROOTS in ready and SMOKE not in ready:
            return "decision", (TapCard(CardId(SMOKE_ROOTS)),)
    return None
