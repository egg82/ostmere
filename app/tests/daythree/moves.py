"""What a route does in a chapter past B4 (chapter.Later), before day two's moves, most pressing first, read off the view
the way the page shows it: an offer answered when it shows, a one-off step the moment it is ready or queued When ready
where the chapter asks (Later.queued) (before a comfort
is queued: a ready glowing step is tapped first, cutting in on the queue's or a rule's task: Card.cuts_in), the sink moves its knobs ask for (dayone/sinks.py), an order card
set once offered (a route that takes rules), a card kept up by
hand, and, for a route that does not use the queue or the trip's hold, a comfort tapped once ready and the trip tapped
until its first run lands. Ids come from the chapter (CLAUDE.md, "Never spoil the owner")."""
from ashfall_app.engine import (
    BP, AtLeast, CardShare, Mix, MixId, Rules, Save, SaveMix, SetOrders, StoreId, StoreValue, SwitchMix, TapCard, View, units,
    value_at,
)
from tests.daythree.chapter import Later
from tests.dayone import sinks
from tests.dayone.policy import Move, cards, lane_free, queued


def step(v: View, later: Later) -> Move | None:
    cs = cards(v)
    ready = next((s for s in later.steps if s in cs and cs[s].blocker is None), None)
    if ready is None:
        return None
    return ("tap", (TapCard(ready),)) if lane_free(v, "hands") or cs[ready].cuts_in else None


def queue_step(v: View, save: Save, later: Later) -> Move | None:
    if not later.queued:
        return None
    done = {str(c.card): c.completions for c in v.cards}
    return queued(v, save.queue, done, tuple(str(c) for c in later.queued))


def order_card(save: Save, later: Later) -> Move | None:
    held = set(save.unlocked)
    for after, order in later.order_cards:
        if after in held and order not in save.orders:
            return "decision", (SetOrders((order, *save.orders)),)
    return None


def keep(v: View, save: Save, later: Later) -> Move | None:
    if not lane_free(v, "hands"):
        return None
    cs = cards(v)
    for k in later.keeps:
        line = next((ln for ln in v.ledger if ln.store == k.store), None)
        low = line is None or value_at(line.segment, save.time) < units(k.below)
        if k.card in cs and cs[k.card].blocker is None and low:
            return "tap", (TapCard(k.card),)
    return None


def waiting(v: View, rules: Rules, later: Later) -> frozenset[StoreId]:
    """The supplies of the trips that take a store (takes) a chapter's one-off step, or the comfort the story waits on
    (Chapter.first), is blocked on: the trip draws the store down while the card waits for it to rise, and holding it
    flat leaves the card no ready time, so When ready is not on offer."""
    cs = cards(v)
    out = set[StoreId]()
    for card in (*later.steps, *later.sinks.first):
        b = cs[card].blocker if card in cs else None
        if b is not None and isinstance(b.condition, AtLeast) and isinstance(b.condition.subject, StoreValue):
            store = b.condition.subject.store
            out |= {t.supply for t in later.sinks.trips if store in takes(rules, t)}
    return frozenset(out)


def takes(rules: Rules, trip: sinks.Trip) -> frozenset[StoreId]:
    """The stores a trip draws down: its supply and its card's other inputs."""
    return frozenset({trip.supply, *(a.store for c in rules.cards if c.id == trip.card for a in c.inputs)})


def release(v: View, save: Save, rules: Rules, later: Later) -> Move | None:
    """The trips' mix put aside while a one-off step or the comfort the story waits on is blocked on a store they take:
    the active mix without the trips' cards, kept shares scaled up, so the store can rise to the ask (the page's Mix
    tab)."""
    held = waiting(v, rules, later)
    base = next((m for m in save.mixes if m.id == save.active), None)
    if not held or base is None:
        return None
    mixed = {c.card for c in base.components if isinstance(c, CardShare)}
    if not any(t.supply in held and t.card in mixed for t in later.sinks.trips):
        return None
    trips = {t.card for t in later.sinks.trips}
    kept = [c for c in base.components if isinstance(c, CardShare) and c.card not in trips]
    total = sum(c.share_bp for c in kept) or 1
    mix = Mix(MixId("w1_free"), tuple(CardShare(c.card, c.share_bp * BP // total) for c in kept))
    return "decision", (SaveMix(mix), SwitchMix(mix.id))


def share(v: View, save: Save, later: Later) -> Move | None:
    """A chapter's share card added to the active mix once shown; taken out again once its `until` holds."""
    base = next((m for m in save.mixes if m.id == save.active), None)
    shown = {c.card for c in v.cards}
    for sh in later.shares:
        shares = [c for c in (base.components if base else ()) if isinstance(c, CardShare)]
        held, done = any(c.card == sh.card for c in shares), sh.until is not None and sh.until(save)
        if held and done:
            kept = [c for c in shares if c.card != sh.card]
            total = sum(c.share_bp for c in kept) or 1
            mix = Mix(MixId(f"{sh.card}_out"), tuple(CardShare(c.card, c.share_bp * BP // total) for c in kept))
            return "decision", (SaveMix(mix), SwitchMix(mix.id))
        if sh.card in shown and not held and not done:
            scaled = tuple(CardShare(c.card, c.share_bp * (BP - sh.share_bp) // BP) for c in shares)
            mix = Mix(MixId(f"{sh.card}_in"), (*scaled, CardShare(sh.card, sh.share_bp)))
            return "decision", (SaveMix(mix), SwitchMix(mix.id))
    return None


def cure(v: View, save: Save, later: Later) -> Move | None:
    """A cure card tapped the moment it is ready while its bad state is held."""
    if not lane_free(v, "hands"):
        return None
    cs = cards(v)
    for c in later.cures:
        line = next((ln for ln in v.ledger if ln.store == c.store), None)
        if line is not None and value_at(line.segment, save.time) >= units(1) and c.card in cs and cs[c.card].blocker is None:
            return "tap", (TapCard(c.card),)
    return None


def by_hand(v: View, save: Save, later: Later, knobs: sinks.SinkKnobs) -> Move | None:
    """A comfort tapped once ready by a route that does not queue them; the trip tapped until its first run lands by
    one that does not mix it."""
    if not lane_free(v, "hands"):
        return None
    cs = cards(v)
    if not knobs.queue_comforts:
        ready = next((c for c in later.sinks.comforts if c in cs and cs[c].blocker is None), None)
        if ready is not None:
            return "tap", (TapCard(ready),)
    if not knobs.mix_trips:
        trip = next((t.card for t in later.sinks.trips if t.card in cs and cs[t.card].blocker is None
                     and cs[t.card].completions == 0), None)
        if trip is not None:
            return "tap", (TapCard(trip),)
    return None


def move(v: View, save: Save, rules: Rules, later: Later, knobs: sinks.SinkKnobs, takes_rules: bool,
         kept: frozenset[str] = frozenset(), marks: sinks.Marks | None = None) -> Move | None:
    """The chapter's next move; a mix edit carries the trips' shares as the running ledger shows them holding
    (sinks.ride_along)."""
    held = waiting(v, rules, later)
    if later.own is not None and (mine := later.own(v, save, rules)) is not None:
        return mine
    found = (sinks.answer_offers(v, rules, save.orders, (*later.sinks.arrivals, *later.answers), False)
             or release(v, save, rules, later) or step(v, later) or queue_step(v, save, later)
             or sinks.move(v, rules, save, later.sinks, knobs, held, kept, marks)
             or (share(v, save, later) if knobs.mix_trips else None) or cure(v, save, later)
             or (order_card(save, later) if takes_rules else None) or keep(v, save, later) or by_hand(v, save, later, knobs))
    return (found[0], sinks.ride_along(v, rules, save, found[1], later.sinks.trips)) if found else None

