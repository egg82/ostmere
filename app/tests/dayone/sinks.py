"""What a player does about a chapter's sinks (docs/design/banked-time-plan.md, item 4), read off the view the way the
page shows it. A trip joins the mix at the visit its supply store's line shows, at the share its inputs' lines hold at,
with a reserve rule where a second consumer needs the store kept; a comfort is queued with
When ready the visit it shows, built or not; an arrival offer is answered by hand while the player is there, and once
an offer of a kind is answered the kind's rule is set, so the kind's later offers are taken the instant they show,
present or away (an offer of no kind has no rule: the page builds none, CONTRACT.txt, "Offers"). The sinks are named by id in a Chapter, so the policies hold for any chapter; a
route's knobs say which of the three it does. Ids only (CLAUDE.md, "Never spoil the owner")."""
from dataclasses import dataclass

from ashfall_app.engine import (
    BP, QUANTITY_SCALE, AfterTime, AnswerId, AnswerKind, AnswerOffer, AtLeast, AtMost, CardCount, CardId, CardShare,
    CardView, LedgerLine, Mix, MixId, OfferId, Order, QueueEntry, Rules, Save, SaveMix, SetOrders, SetQueue, StoreId,
    HANDS, TOWN_PREFIX, RunBy, RunKind, StoreValue, SwitchMix, TapCard, Verb, View, advance, decide, value_at, view,
)
from tests.dayone.policy import Move, lane_free


@dataclass(frozen=True)
class Trip:
    card: CardId
    supply: StoreId
    share_bp: int = BP // 2
    """The trip's share of the mix; the mix's other cards are scaled to leave it. Run dry, it pauses and its share
    goes to the rest of the mix until the supply refills (DESIGN.txt, "SPENT")."""
    reserve_for: tuple[CardId, ...] = ()
    """The cards the player keeps a reserve of the supply for (reserve_move): ones whose take the dry store's handover
    does not leave room for, such as a long tap that would run dry while the trip drinks beside it."""


@dataclass(frozen=True)
class Chapter:
    trips: tuple[Trip, ...] = ()
    comforts: tuple[CardId, ...] = ()
    arrivals: tuple[tuple[OfferId, AnswerId], ...] = ()
    """Each arrival offer and the answer a route that lets newcomers stay gives."""
    first: tuple[CardId, ...] = ()
    """Comforts whose next course the player queues ahead of the other comforts: a staged one the story waits on, which
    soonest-ready order would leave behind every comfort that is ready sooner."""


@dataclass(frozen=True)
class SinkKnobs:
    mix_trips: bool = False
    queue_comforts: bool = False
    answer_arrivals: bool = False


SINKS: dict[str, SinkKnobs] = {
    "typical": SinkKnobs(True, True),
    "sharp": SinkKnobs(True, True),
    "lazy": SinkKnobs(),
    "by_hand": SinkKnobs(mix_trips=True),
    "larder_first": SinkKnobs(True, True),
    "evenings": SinkKnobs(True, True),
    "lunch": SinkKnobs(True, True),
    "return_22h": SinkKnobs(True, True),
    "babysitter": SinkKnobs(mix_trips=True),
    "whenever": SinkKnobs(True, True, True),
}
"""Day-two route names to what each does about a chapter's sinks. sharp and typical mix the trip and queue the comfort;
lazy does neither; whenever also answers arrival offers (by hand, then the kind's rule). Routes the plan does not name follow typical, except
by_hand and the babysitter, which do nothing a rule or the queue would: they mix the trip (a mix, not a rule) and build
the comforts by hand."""


def kind_rule(rules: Rules, orders: tuple[Order, ...], offer: OfferId, answer: AnswerId) -> Order | None:
    """The answer rule the page offers once `offer` is answered with `answer` (always true, the answer's role in the
    offer's kind), or None: the offer has no kind, or the kind has its rule."""
    found = next((o for o in rules.offers if o.id == offer), None)
    role = next((a.role for a in found.answers if a.id == answer), None) if found else None
    if found is None or found.kind is None or role is None:
        return None
    verb = AnswerKind(found.kind, role)
    return None if any(isinstance(x.then, AnswerKind) and x.then.kind == found.kind for x in orders) else Order(AfterTime(0), verb)


def answer_offers(v: View, rules: Rules, orders: tuple[Order, ...], answers: tuple[tuple[OfferId, AnswerId], ...],
                  rule: bool) -> Move | None:
    """What the page lets a player do about offers: answer, by hand, the first of `answers` that is shown and open; and,
    when `rule` and an offer of a kind has been answered as given, set the kind's rule (its answer's role). Nothing
    is set ahead of an answer, and an offer of no kind has no rule."""
    open_ = {o.offer for o in v.offers if o.answer is None}
    verb = next((AnswerOffer(o, a) for o, a in answers if o in open_), None)
    if verb is not None:
        return "decision", (verb,)
    if not rule:
        return None
    given = {o.offer: o.answer for o in v.offers}
    for offer, answer in answers:
        if given.get(offer) == answer and (new := kind_rule(rules, orders, offer, answer)) is not None:
            return "decision", (SetOrders((*orders, new)),)
    return None


def fed_by_another(save: Save, rules: Rules, trip: Trip) -> bool:
    """Whether another uncapped card of the active mix takes the trip's supply as an input."""
    takes = {c.id for c in rules.cards if c.cap is None and c.id != trip.card and any(a.store == trip.supply for a in c.inputs)}
    return any(isinstance(c, CardShare) and c.card in takes for m in save.mixes if m.id == save.active for c in m.components)


def in_mix(save: Save, trip: Trip) -> bool:
    return any(isinstance(c, CardShare) and c.card == trip.card
               for m in save.mixes if m.id == save.active for c in m.components)


def line_drawn(v: View, line: LedgerLine, kept: frozenset[str] = frozenset()) -> bool:
    """Whether the page draws the store's ledger line at this view: one it has kept (`kept`: a line drawn once stays,
    kept for the account, client ui/ledger.ts), or one joining now (client game/shown.ts, lineJoins): starved, drawn
    down by something other than the hands' tap, full while fed, or covered. A line joining by an order card's offer
    is not modelled, so this errs toward refusing."""
    if str(line.store) in kept:
        return True
    tapped = next((ln.card for ln in v.lanes if ln.lane == "hands"), None)
    drawn_down = line.falling and any(c.per_hour < 0 and c.runner != tapped for c in line.contributions)
    full_and_fed = line.cap > 0 and value_at(line.segment, v.time) >= line.cap and sum(c.per_hour for c in line.contributions) > 0
    return line.starved or drawn_down or full_and_fed or line.covered


def mix_trip(v: View, rules: Rules, save: Save, trip: Trip, kept: frozenset[str] = frozenset()) -> Move | None:
    """The trip, once shown, added to the active mix, the mix's other cards scaled to leave it: at the share the
    ledger shows its inputs holding at (tuned_share; its own share for a supply that arrives in bursts, bursty), or, while a tap holds the hands and the mix's rates do not show,
    at its own share until they do (retune_trip). It waits while the supply's line is not drawn (`kept`: the lines the
    page already keeps), since the page offers the trip on that line."""
    line = next((ln for ln in v.ledger if ln.store == trip.supply), None)
    if trip.card not in {c.card for c in v.cards} or line is None or not line_drawn(v, line, kept) or in_mix(save, trip):
        return None   # waits: the page draws no line to offer the trip on yet
    if lane_free(v, "hands"):
        share = trip.share_bp if bursty(rules, save, trip) else tuned_share(rules, save, trip)
        mixed = trip_mix(save, trip, share, MixId(f"{trip.card}_{trip.supply}_mixed"))
    else:
        mixed = trip_mix(save, trip, trip.share_bp, untuned_id(trip))
    return "decision", (SaveMix(mixed), SwitchMix(mixed.id))


def untuned_id(trip: Trip) -> MixId:
    return MixId(f"{trip.card}_{trip.supply}_untuned")


Marks = dict[CardId, str]
"""What the player remembers set each trip's share last: RULE_LOW (a hands rule's fight turned it down) or RAISED (the
raise-back turned it up again), so the two turns undo each other once a rule cycle at most (retune_trip)."""
RULE_LOW, RAISED = "rule_low", "raised"


def retune_trip(v: View, rules: Rules, save: Save, trip: Trip, marks: Marks) -> Move | None:
    """With the hands free, the trip's share set again from the page's preview (tuned_share): once its rates show,
    when it was mixed under a tap, once it has paused or starved its supply's line (its own share, for a supply that
    arrives in bursts: bursty), or once it runs down a store one of the player's hands rules keeps (fights_a_rule),
    which stops the mix to refill it. A share that rule turned down is turned back up, by RETUNE_BP or more, once the
    rule has let go (rule_let_go); a share raised so is not turned down again until the rule has come on once more, a
    hysteresis kept in `marks`. Any other turn of the share rides on a mix edit the player makes anyway (ride_along)."""
    card = next((c for c in v.cards if c.card == trip.card), None)
    line = next((ln for ln in v.ledger if ln.store == trip.supply), None)
    now = next((c.share_bp for m in save.mixes if m.id == save.active for c in m.components
                if isinstance(c, CardShare) and c.card == trip.card), None)
    if card is None or line is None or save.active is None or now is None or not lane_free(v, "hands"):
        return None
    if marks.get(trip.card) == RAISED and rule_on(rules, save, trip):
        del marks[trip.card]   # the rule has come on again: a new cycle
    raised = read_share(v, rules, save, trip, now) if marks.get(trip.card) == RULE_LOW and card.by is RunBy.MIX \
        and now <= trip.share_bp - RETUNE_BP and rule_let_go(v, rules, save, trip) else 0
    if raised >= now + RETUNE_BP:
        share, marks[trip.card] = raised, RAISED   # the running ledger's read: the mix runs the trip, so it shows the room
    else:
        if marks.get(trip.card) == RAISED:
            return None
        fight = fights_a_rule(v, rules, save, trip)
        if save.active != untuned_id(trip) and card.run is not RunKind.PAUSED and not line.starved and not fight:
            return None
        share = trip.share_bp if not fight and bursty(rules, save, trip) else tuned_share(rules, save, trip)
        if save.active != untuned_id(trip) and abs(share - now) < TUNE_STEP_BP:
            return None   # already there, give or take what scaling the mix for another card left
        if fight:
            marks[trip.card] = RULE_LOW
    mix_id = MixId(f"{trip.card}_{trip.supply}_mixed") if save.active == untuned_id(trip) else save.active
    mixed = trip_mix(save, trip, share, mix_id)
    return "decision", ((SaveMix(mixed),) if mix_id == save.active else (SaveMix(mixed), SwitchMix(mix_id)))


def rule_on(rules: Rules, save: Save, trip: Trip) -> bool:
    """A hands "Under" rule on a store the trip is kept from running down (watched, past its supply) is on."""
    ruled = watched(rules, save, trip) - {trip.supply}
    return any(on and isinstance(o.when, AtMost) and isinstance(o.when.subject, StoreValue) and o.when.subject.store in ruled
               for o, on in zip(save.orders, save.latches))


def bursty(rules: Rules, save: Save, trip: Trip) -> bool:
    """The trip's supply comes only from cards a store rule taps (a reaping by its rule): no maker of it runs in the
    active mix or by an always rule, so between taps the ledger shows it only falling, and the player keeps the trip
    at its own share."""
    makers = {c.id for c in rules.cards
              if any(f.store == trip.supply for f in c.makes) or any(a.store == trip.supply for a in c.outcome.stores)}
    mixed = {c.card for m in save.mixes if m.id == save.active for c in m.components if isinstance(c, CardShare)}
    tapped = [(o.when, o.then.card) for o in save.orders if isinstance(o.then, TapCard) and o.then.card in makers]
    return (not makers & mixed and any(not isinstance(w, AfterTime) for w, _ in tapped)
            and all(not isinstance(w, AfterTime) for w, _ in tapped))


def shared(rules: Rules, trip: Trip, trips: tuple[Trip, ...]) -> bool:
    """Another of the chapter's trips takes the trip's supply: turning this one up to drink the full store would take
    it from the other."""
    others = {t.card for t in trips if t.card != trip.card}
    return any(a.store == trip.supply for c in rules.cards if c.id in others for a in c.inputs)


def spilling(v: View, rules: Rules, save: Save, trip: Trip) -> bool:
    """The trip's supply is full and the supply is all it is kept from running down (watched): its maker fills it in
    bursts the running ledger cannot show (a rule's reaping), so a mix edit leaves it at its own share (ride_along)."""
    line = next((ln for ln in v.ledger if ln.store == trip.supply), None)
    return (line is not None and line.cap > 0 and value_at(line.segment, v.time) >= line.cap
            and watched(rules, save, trip) == frozenset({trip.supply}))


def fights_a_rule(v: View, rules: Rules, save: Save, trip: Trip) -> bool:
    """The mix runs the trip and the ledger shows it running down a store an "Under" rule of the player's keeps by a
    tap on the hands (watched, past its supply): the rule will stop the mix to refill it, and the trip drink it again,
    each time round."""
    card = next((c for c in v.cards if c.card == trip.card), None)
    ruled = watched(rules, save, trip) - {trip.supply}
    return card is not None and card.by is RunBy.MIX and any(
        ln.net_per_hour < 0 and any(str(c.runner) == str(trip.card) and c.per_hour < 0 for c in ln.contributions)
        for ln in v.ledger if ln.store in ruled)


def rule_let_go(v: View, rules: Rules, save: Save, trip: Trip) -> bool:
    """A hands "Under" rule on a store the trip is kept from running down (watched, past its supply) has let go: off,
    with the store over its "until". A player who sees the store recovered turns a trip the rule's fight had them turn
    down back up (retune_trip, by RETUNE_BP or more); the typical player, away when the rule lets go, sees it at its
    next look.""" 
    ruled = watched(rules, save, trip) - {trip.supply}
    lines = {ln.store: ln for ln in v.ledger}
    for o, on in zip(save.orders, save.latches):
        if on or not isinstance(o.when, AtMost) or not isinstance(o.when.subject, StoreValue):
            continue
        store = o.when.subject.store
        if store in ruled and store in lines and value_at(lines[store].segment, v.time) > o.when.release:
            return True
    return False


def retune_trips(v: View, rules: Rules, save: Save, trips: list[Trip], marks: Marks) -> Move | None:
    """Every trip retune_trip would turn, in one edit of the mix: a player turning two shares in the editor saves once."""
    now, verbs = save, list[Verb]()
    for _ in trips:   # a turn of one share can move another's: until none turns, at most once a trip
        turned = False
        for trip in trips:
            m = retune_trip(v if now is save else view(now, rules), rules, now, trip, marks)
            for verb in (m[1] if m else ()):
                now, turned = decide(now, rules, now.time, verb), True
                verbs.append(verb)
        if not turned:
            break
    if not verbs:
        return None
    final = next(m for m in now.mixes if m.id == now.active)
    return "decision", ((SaveMix(final),) if now.active == save.active else (SaveMix(final), SwitchMix(final.id)))


TUNE_STEP_BP = 100
"""The finest share step a player sets the trip at while reading its inputs' lines."""
RETUNE_BP = 500
"""How far from the trip's share the running ledger must put the share that holds before a player editing the mix
turns it too: a smaller band would follow every rule that starts and stops beside it."""


def ride_along(v: View, rules: Rules, save: Save, verbs: tuple[Verb, ...], trips: tuple[Trip, ...]) -> tuple[Verb, ...]:
    """`verbs` with each SaveMix of a hands mix holding a trip given that trip at the share the running ledger shows
    holding while the mix runs it (read_share), or its own share while its supply is full or arrives in bursts and no
    other trip takes it (spilling, bursty, shared), when that is
    RETUNE_BP or more from its share, the mix's other cards scaled to leave it: a player editing the mix turns the
    trip's share in the same save."""
    cards = {c.card: c for c in v.cards}
    out = list[Verb]()
    for verb in verbs:
        if isinstance(verb, SaveMix) and not str(verb.mix.id).startswith(("town:", "reserve_", "cap_")):
            for trip in trips:
                card = cards.get(trip.card)
                now = next((c.share_bp for c in verb.mix.components if isinstance(c, CardShare) and c.card == trip.card), None)
                if card is None or now is None or not 0 < now < BP:
                    continue
                if (spilling(v, rules, save, trip) or bursty(rules, save, trip)) and not shared(rules, trip, trips):
                    share = trip.share_bp
                elif card.by is RunBy.MIX:
                    share = read_share(v, rules, save, trip, now)
                else:
                    continue
                if abs(share - now) >= RETUNE_BP:
                    verb = SaveMix(with_share(verb.mix, trip.card, share))
        out.append(verb)
    return tuple(out)


def with_share(mix: Mix, card: CardId, share: int) -> Mix:
    """`mix` with `card` at `share`, the other cards scaled to leave it."""
    rest = without(mix, frozenset({card}), mix.id)
    scaled = tuple(CardShare(c.card, c.share_bp * (BP - share) // BP) for c in (rest.components if rest else ())
                   if isinstance(c, CardShare))
    return Mix(mix.id, (*scaled, CardShare(card, share)), mix.layer)



def watched(rules: Rules, save: Save, trip: Trip) -> frozenset[StoreId]:
    """The trip's inputs whose lines the player keeps from falling when setting its share: its supply, and any the
    player keeps with an "Under" rule of their own, which the trip running it down would set fighting the trip. Its
    other inputs are left to the dry store's handover."""
    ruled = {o.when.subject.store for o in save.orders if isinstance(o.when, AtMost)
             and isinstance(o.when.subject, StoreValue) and not isinstance(o.then, SwitchMix)}
    inputs = {a.store for c in rules.cards if c.id == trip.card for a in c.inputs}
    return frozenset({trip.supply} | (ruled & inputs))


def read_share(v: View, rules: Rules, save: Save, trip: Trip, now: int) -> int:
    """The share the running ledger shows the trip's watched inputs holding at, in TUNE_STEP_BP steps up to its own:
    on each, the trip's draw grows with its share and the mix's other cards' parts shrink to leave it, the rest
    standing, so the line's net is linear in the share and the share where it crosses zero is read off this view."""
    mixed = {str(c.card) for m in save.mixes if m.id == save.active for c in m.components
             if isinstance(c, CardShare) and c.card != trip.card}
    best = float(trip.share_bp)
    for ln in (ln for ln in v.ledger if ln.store in watched(rules, save, trip)):
        draw = -sum(c.per_hour for c in ln.contributions if str(c.runner) == str(trip.card))
        made = sum(c.per_hour for c in ln.contributions if str(c.runner) in mixed)
        if draw <= 0:
            continue
        rest = ln.net_per_hour + draw - made
        per_mix, per_trip = made / (BP - now), draw / now
        best = min(best, (rest + per_mix * BP) / (per_mix + per_trip))
    return max(TUNE_STEP_BP, int(best) // TUNE_STEP_BP * TUNE_STEP_BP)


def trip_mix(save: Save, trip: Trip, share: int, mix_id: MixId) -> Mix:
    """The active mix with the trip at `share`, the other cards scaled to leave it."""
    base = next((m for m in save.mixes if m.id == save.active), None)
    rest = without(base, frozenset({trip.card}), MixId("rest")) if base else None
    scaled = tuple(CardShare(c.card, c.share_bp * (BP - share) // BP) for c in (rest.components if rest else ())
                   if isinstance(c, CardShare))
    return Mix(mix_id, (*scaled, CardShare(trip.card, share)))


def tuned_share(rules: Rules, save: Save, trip: Trip) -> int:
    """The largest share, up to the trip's own and in TUNE_STEP_BP steps, at which the page's preview of the mix shows
    none of its watched inputs falling: a player dragging the trip's share while reading the lines' rates. A share past
    that drinks a store dry and pauses, the dry store's handover giving the share back until it has refilled, which a
    player reads as a red line; one under it lets the store fill and spill. The preview is of the mix itself beside
    the other lanes and the town's mix, with no hands mix rule running over it, no rule or queue entry tapping on the
    hands, and from when a tap holding the hands lands; the floor is one step."""
    hands = {c.id for c in rules.cards if c.lane == HANDS}
    town = {m.id for m in save.mixes if str(m.id).startswith(TOWN_PREFIX)}
    own = tuple(o for o in save.orders if not (isinstance(o.then, SwitchMix) and o.then.mix not in town)
                and not (isinstance(o.then, TapCard) and o.then.card in hands))
    bare = decide(decide(save, rules, save.time, SetOrders(own)), rules, save.time, SetQueue(()))
    held = next((b.completes_at for b in view(bare, rules).lanes if b.lane == HANDS and b.card is not None), None)
    if held is not None:   # the mix's rates show once the tap holding the hands lands
        bare = advance(bare, rules, held)
    kept = watched(rules, save, trip)
    def holds(share: int) -> bool:
        m = trip_mix(save, trip, share, MixId("preview"))
        shown = view(decide(decide(bare, rules, bare.time, SaveMix(m)), rules, bare.time, SwitchMix(m.id)), rules)
        return all(ln.net_per_hour >= 0 for ln in shown.ledger if ln.store in kept)
    if holds(trip.share_bp):
        return trip.share_bp
    lo, hi = 0, trip.share_bp // TUNE_STEP_BP   # hi does not hold; lo holds, or is the floor
    while hi - lo > 1:
        mid = (lo + hi) // 2
        lo, hi = (mid, hi) if holds(mid * TUNE_STEP_BP) else (lo, mid)
    return max(lo, 1) * TUNE_STEP_BP


def without(base: Mix, cards: frozenset[CardId], mix_id: MixId) -> Mix | None:
    """`base` less `cards`, the other cards scaled back to the whole mix, or None when nothing else is in it."""
    rest = [c for c in base.components if isinstance(c, CardShare) and c.card not in cards]
    total = sum(c.share_bp for c in rest)
    return Mix(mix_id, tuple(CardShare(c.card, c.share_bp * BP // total) for c in rest)) if total else None


def drop_trip(v: View, save: Save, trip: Trip, done: CardId) -> Move | None:
    """Once `done` (the comfort the trip feeds) is completed, the trip taken out of the active mix, the other cards scaled back to the whole mix: what it made has no use left."""
    base = next((m for m in save.mixes if m.id == save.active), None)
    if base is None or done not in {c.card for c in v.completed} or not in_mix(save, trip):
        return None
    kept = without(base, frozenset({trip.card}), MixId(f"without_{trip.card}"))
    return None if kept is None else ("decision", (SaveMix(kept), SwitchMix(kept.id)))


def reserve_mix_id(trip: Trip) -> MixId:
    return MixId(f"reserve_{trip.supply}")


def reserve_rule(v: View, rules: Rules, save: Save, trip: Trip) -> Order | None:
    """The rule the page builds for "Under n {supply}, until m" (client game/storerule.ts, buildRule), running the
    trip's reserve mix. n is the most one of `reserve_for` takes of the supply a completion, in whole items rounded up,
    or an item over the highest level another rule of the player's comes on under the store, if higher: the reserve
    keeps the store above it, so the two never fight over the store. m is the page's default, halfway from n to the
    line's cap. None while the line is too small for a band above n."""
    line = next((ln for ln in v.ledger if ln.store == trip.supply), None)
    asks = [a.quantity for c in rules.cards if c.id in trip.reserve_for for a in c.inputs if a.store == trip.supply]
    if line is None or not asks:
        return None
    others = [o.when.value // QUANTITY_SCALE + 1 for o in save.orders
              if isinstance(o.when, AtMost) and o.when.subject == StoreValue(trip.supply) and o.then != SwitchMix(reserve_mix_id(trip))]
    n, cap = max([-(-max(asks) // QUANTITY_SCALE), *others]), line.cap // QUANTITY_SCALE
    if cap <= n:
        return None
    m = -(-(n + cap) // 2)
    q = QUANTITY_SCALE
    return Order(AtMost(StoreValue(trip.supply), n * q - 1, m * q - 1), SwitchMix(reserve_mix_id(trip)))


def reserve_move(v: View, rules: Rules, save: Save, trip: Trip) -> Move | None:
    """The reserve a player paying attention keeps for a second consumer of a trip's supply (decisions.md, "No hold on
    a line"): while the trip is in the active mix, a rule switches to the active mix less every card of it that takes
    the supply while the supply is low, and lets go once it has refilled (reserve_rule). The reserve mix is saved once,
    as the active mix was then: a player does not edit it again with every change to the mix it stands in for, which
    it runs over only while the store refills. The rule goes once the trip leaves the mix."""
    mine = [o for o in save.orders if isinstance(o.then, SwitchMix) and o.then.mix == reserve_mix_id(trip)]
    base = next((m for m in save.mixes if m.id == save.active), None)
    if not trip.reserve_for or base is None:
        return None
    if not in_mix(save, trip):
        return ("decision", (SetOrders(tuple(o for o in save.orders if o not in mine)),)) if mine else None
    takes = frozenset(c.id for c in rules.cards if any(a.store == trip.supply for a in c.inputs))
    want = without(base, takes, reserve_mix_id(trip))
    rule = reserve_rule(v, rules, save, trip)
    if want is None or rule is None:
        return None
    verbs: list[Verb] = []
    if all(m.id != want.id for m in save.mixes):
        verbs.append(SaveMix(want))
    if mine != [rule]:
        verbs.append(SetOrders((*(o for o in save.orders if o not in mine), rule)))
    return ("decision", tuple(verbs)) if verbs else None


def queue_comforts(v: View, save: Save, chapter: Chapter) -> Move | None:
    """When ready on each comfort that shows, whether or not its inputs are in yet: the queue carries it across an
    absence (DESIGN.txt, "BANKED TIME", "Comfort"). The queue's head is never passed over, so its comfort entries are
    kept soonest ready first (ready now, then by ready time), and one showing no ready time is not queued (the page
    offers When ready only with one, client game/queue.ts) and goes last if it already is: either would hold back a
    comfort that is ready. The order is set as each new comfort is queued (one SetQueue), never re-sorted on its own,
    so a visit's ready times shifting do not churn the queue."""
    order = by_readiness(v, chapter)
    mine = {e.verb.card: e for e in save.queue if isinstance(e.verb, TapCard) and e.verb.card in chapter.comforts}
    cs = {c.card: c for c in v.cards}
    new = [x for x in order if x not in mine and offered(cs[x])]
    if not new:
        return None
    for comfort in new:
        n = cs[comfort].completions + 1
        mine[comfort] = QueueEntry(TapCard(comfort), AtLeast(CardCount(comfort), n, n))
    rank = {c: i for i, c in enumerate(order)}
    sorted_mine = sorted(mine.values(), key=lambda e: rank.get(_card(e), len(rank)))
    queue = (*(e for e in save.queue if e not in mine.values()), *sorted_mine)
    return "decision", (SetQueue(queue),)


def offered(c: CardView) -> bool:
    """When ready is on offer: the card is ready, or shows when it will be."""
    return c.blocker is None or c.blocker.ready_at is not None


def _card(e: QueueEntry) -> CardId:
    assert isinstance(e.verb, TapCard)
    return e.verb.card


def move(v: View, rules: Rules, save: Save, chapter: Chapter, knobs: SinkKnobs,
         waiting: frozenset[StoreId] = frozenset(), kept: frozenset[str] = frozenset(),
         marks: Marks | None = None) -> Move | None:
    """The first sink move the knobs ask for, most pressing first: an arrival answered, a trip mixed (and its reserve
    kept), a comfort queued.
    `waiting`: supplies a step waits on, whose trips stay out; `kept`: the ledger lines the page already keeps
    (line_drawn); `marks`: the player's memory of its trips' last retunes (retune_trip), none kept when not given."""
    if knobs.answer_arrivals and (m := answer_offers(v, rules, save.orders, chapter.arrivals, True)) is not None:
        return m
    if knobs.mix_trips:
        trips = [t for t in chapter.trips if t.supply not in waiting]
        mixed = next((m for t in trips if (m := mix_trip(v, rules, save, t, kept)) is not None), None)
        reserved = None if mixed else next((m for t in trips if (m := reserve_move(v, rules, save, t)) is not None), None)
        if (m := mixed or retune_trips(v, rules, save, trips, {} if marks is None else marks) or reserved) is not None:
            return m
    return queue_comforts(v, save, chapter) if knobs.queue_comforts else None


def by_readiness(v: View, chapter: Chapter) -> list[CardId]:
    """The chapter's comforts in view and not under way: those of `first`, then the rest soonest ready first (ready now,
    then by ready time, then those with none known)."""
    running = {b.card for b in v.lanes if b.card is not None}
    shown = [c for c in v.cards if c.card in chapter.comforts and c.card not in running]
    def soon(c: CardView) -> float:
        if c.blocker is None:
            return 0
        return c.blocker.ready_at if c.blocker.ready_at is not None else float("inf")
    return [c.card for c in sorted(shown, key=lambda c: (c.card not in chapter.first, soon(c)))]
