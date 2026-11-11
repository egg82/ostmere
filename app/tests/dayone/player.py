"""A scripted player of day one, on the real engine: the opening played as playthrough.Player plays it, then a route's
visits (schedules.py). Inside a visit it looks and acts as the page lets it (policy.py), a glance of seconds before
each decision. Between visits it is away: time runs event by event with nobody deciding, and what landed is shown on
return, all of it at the return (a planned moment plays in full then: docs/decisions.md, "Day and night run on the
story's clock").

What it keeps, for the checks (checks.py): each visit's window, every decision with its time and kind, every new thing
on screen (News, stamped when seen), when each story id landed and when it was seen, the save at each visit's exit."""
from collections.abc import Callable
from dataclasses import dataclass, field
from functools import cache, cached_property
from typing import ClassVar

from ashfall_app.engine import (
    AtLeast, AtMost, CardId, Line, Order, Save, SetOrders, StoreId, StoreValue, TapCard, Unlock, UnlockKind, Verb, View,
    advance_logged, next_event, units,
)
from ashfall_app.engine.work import completions
from ashfall_app.opening.convert import condition
from ashfall_app.opening.schema import load_opening
from tests.dayone import policy, sinks
from tests.dayone.beats import STORY, landed
from tests.dayone.schedules import Schedule
from tests.opening.afterend import END_READ_S, AfterEnd, AfterEndPlayer
from tests.opening.playthrough import Kind, News, opening, opening_rules

LOOK_S = 15
WEAVE_TRIP = sinks.Trip(CardId(policy.WEAVE), StoreId("damp_wood"))
"""With nothing to do, the player looks back at least this often."""


@dataclass(frozen=True)
class VisitRecord:
    index: int
    start: int
    end: int
    gap: int
    """Seconds away before it (0 for V1)."""
    exit: Save | None = None
    came: Save | None = None
    """The save the visit began on: at `start` when the player was away until then or had just left at that time."""


Stage = tuple[CardId, int]
"""A card and the number of the completion that finished one of its stages."""


@dataclass
class DayOnePlayer(AfterEndPlayer):
    STOP_BEAT: ClassVar[str] = "B3"
    """The day ends with the visit this beat is seen in."""
    schedule: Schedule = field(default_factory=lambda: Schedule("none", ()))
    knobs: policy.Knobs = field(default_factory=policy.Knobs)
    visits: list[VisitRecord] = field(default_factory=lambda: [])
    acts: list[tuple[int, Kind, str]] = field(default_factory=lambda: [])
    """(time, kind, what) per decision: a card id for a tap, else the verb's kind."""
    landed_at: dict[str, int] = field(default_factory=lambda: {})
    seen_at: dict[str, int] = field(default_factory=lambda: {})
    tried_roots: bool = False
    accept_rest_before: tuple[Verb, ...] = ()
    extras: set[str] = field(default_factory=lambda: set())
    """Things on screen the opening's player does not record: When ready's first showing, the rising-line card."""
    look_s: int = LOOK_S
    unlocked_at: dict[Unlock, int] = field(default_factory=lambda: {})
    """When each unlock first showed in the save, event by event while away."""
    stage_at: dict[Stage, int] = field(default_factory=lambda: {})
    """When each stage first showed: a completion of a card with a cap above one, the last being the card's finish."""
    end_save: Save | None = None
    """The save at the opening's end moment, where day one's replays start (parity.py)."""
    opening_decisions: int = 0
    """How many of `decisions` the opening made."""

    @cached_property
    def _staged(self) -> list[tuple[CardId, int]]:
        return [(c.id, c.cap) for c in self.rules.cards if c.cap is not None and c.cap > 1]

    def stop_beat(self) -> str:
        return self.STOP_BEAT

    def day_log(self) -> list[tuple[int, Verb]]:
        """Every verb sent after the opening's end moment, with its time."""
        return [(t, verb) for t, _, verb in self.decisions[self.opening_decisions:]]

    # ---------- the day ----------

    def play_day(self, make_schedule: Callable[[int], Schedule] | None = None) -> None:
        """The opening to its end, then each visit in turn until the visit stop_beat() is seen in has ended. `make_schedule`,
        given the end's time, sets the visits (a schedule that keeps to the clock needs it)."""
        end = self.play()
        if make_schedule is not None:
            self.schedule = make_schedule(end)
        self.end_save, self.opening_decisions = self.save, len(self.decisions)
        self.after = AfterEnd(end_at=end, read_at=end + END_READ_S)
        self.play_visits(end, 0)

    def play_visits(self, end: int, first: int) -> None:
        """The schedule's visits from index `first` (0-based) in turn, `end` being the opening's end, until the visit
        stop_beat() is seen in has ended."""
        for i, v in enumerate(self.schedule.visits[first:], start=first):
            start, stop = end + v.start, end + v.start + v.length
            gap = start - self.save.time if i else 0
            if gap > 0:
                self._away(start)
            came = self.save
            self._visit(stop)
            self.visits.append(VisitRecord(i + 1, start, self.save.time, gap, self.save, came))
            if self.stop_beat() in self.seen_at:
                return

    def _visit(self, stop: int) -> None:
        while self.save.time < stop:
            move = self.visit_move(self.view())
            if move is None:
                if self.leaves():
                    return
                self._look(stop)
                continue
            self._advance_through(min(stop, self.save.time + self.glance()))
            if self.save.time >= stop:
                return
            again = self.visit_move(self.view())   # what shows after the glance is what the player acts on
            if again is not None:
                offer = self._offer_open()
                self.decide(*again)
                if offer is not None and again[1] == self.accept_rest_before:
                    offer.accepted_at = self.save.time

    def play_on(self) -> None:
        """The last visit re-entered at the moment it was left, then the schedule's later visits in turn, until the visit
        stop_beat() is seen in has ended: a copy given more content plays on from where the play stopped."""
        assert self.after is not None
        end, left = self.after.end_at, self.visits.pop()
        v = self.schedule.visits[left.index - 1]
        self._visit(end + v.start + v.length)
        self.visits.append(VisitRecord(left.index, left.start, self.save.time, left.gap, self.save, left.came))
        if self.stop_beat() not in self.seen_at:
            self.play_visits(end, left.index)

    def leaves(self) -> bool:
        """With nothing to act on, whether the player leaves now; a route stays to the end of its visit."""
        return False

    def _look(self, stop: int) -> None:
        v = self.view()
        event = next_event(self.save, self.rules)
        soon = [self.save.time + self.look_s, stop, *(c.blocker.ready_at for c in v.cards
                                                 if c.blocker is not None and c.blocker.ready_at is not None)]
        if event is not None:
            soon.append(event.time)
        self.advance(min(t for t in soon if t > self.save.time))

    def _away(self, until: int) -> None:
        """Nobody deciding: event by event to `until`, every line kept; what landed is seen at the return."""
        save, lines = self.save, list[Line]()
        while True:
            event = next_event(save, self.rules)
            t = until if event is None or event.time >= until else event.time
            step = advance_logged(save, self.rules, t)
            save, lines = step.save, lines + list(step.lines)
            self._landings(save)
            if t >= until:
                break
        self._took(save, tuple(lines))

    # ---------- recording ----------

    def _landings(self, save: Save) -> None:
        for u in save.unlocked:
            self.unlocked_at.setdefault(u, save.time)
        for card, cap in self._staged:
            for n in range(1, min(completions(save, self.rules, card), cap) + 1):
                self.stage_at.setdefault((card, n), save.time)
        for beat in landed(save, self.rules) - set(self.landed_at):
            self.landed_at[beat] = save.time

    def _took(self, save: Save, lines: tuple[Line, ...]) -> None:
        super()._took(save, lines)
        self._landings(save)
        taps, decisions = self.effort()
        for beat in sorted(set(self.landed_at) - set(self.seen_at)):
            self.seen_at[beat] = save.time
            if beat in STORY:
                self.news.append(News(save.time, f"beat:{beat}", taps, decisions))
        v = self.view()
        extra = {"control:when_ready" for c in v.cards if c.card in policy.QUEUEABLE and c.blocker is not None
                 and c.blocker.ready_at is not None}
        rising = self._rising_order()
        if rising is not None and policy.rising_rule(v, (), rising) is not None:
            extra.add(f"order_card:{policy.CATCH}")
        for thing in sorted(extra - self.extras):
            self.news.append(News(save.time, thing, taps, decisions))
        self.extras |= extra

    def decide(self, kind: Kind, verbs: tuple[Verb, ...]) -> None:
        first = verbs[0]
        self.acts.append((self.save.time, kind, first.card if isinstance(first, TapCard) else type(first).__name__))
        if isinstance(first, TapCard) and first.card == policy.SMOKE_ROOTS:
            self.tried_roots = True
        super().decide(kind, verbs)

    # ---------- the moves ----------

    def _offer_open(self) -> AfterEnd | None:
        a = self.after
        return a if self.takes_offers and a is not None and a.offer_at is not None and a.accepted_at is None else None

    def visit_move(self, v: View) -> policy.Move | None:
        """A skill at its top is clicked before anything else; then the day's moves."""
        return policy.prestige_click(v) or self.day_move(v)

    def day_move(self, v: View) -> policy.Move | None:
        if self._offer_open() is not None:
            self.accept_rest_before = self.accept_rest()
            return "decision", self.accept_rest_before
        fed = policy.hunger(v, self.knobs, self._hunger_offer())
        if fed is not None:
            return fed
        hands_free = any(b.lane == "hands" and b.card is None for b in v.lanes)
        opening = self.next_move(v) if hands_free else None
        if opening is not None and not (opening[0] == "tap" and self._day_card(opening[1])):
            return opening
        orders, queue = self.save.orders, self.save.queue
        completions = {str(c.card): c.completions for c in v.cards}
        rising = self._rising_order() if self.knobs.rising_rule else None
        return (policy.rising_rule(v, orders, rising) or policy.retuned_roots(v, orders, self._stock_order())
                or (policy.queued(v, queue, completions) if self.knobs.queue else None)
                or self._sink_move(v)
                or policy.tap(v, self.knobs, any(o == rising for o in orders) if rising else False, self.tried_roots)
                or self._drop_weave(v))

    def _sink_move(self, v: View) -> policy.Move | None:
        """The weave added to the mix until the screen stands, then the screen's rule, as the knobs ask. A later
        chapter's trip on damp wood keeps the store: the weave gives way rather than take it back."""
        built = policy.SCREEN in {c.card for c in v.completed}
        if (self.knobs.mix_weave and not built and not sinks.fed_by_another(self.save, self.rules, WEAVE_TRIP)
                and (m := sinks.mix_trip(v, self.rules, self.save, WEAVE_TRIP))):
            return m
        return policy.screen_rule(v, self.save.orders, self._screen_order()) if self.knobs.screen_rule else None

    def _drop_weave(self, v: View) -> policy.Move | None:
        """The weave out of the mix once the screen stands, when nothing else is left to do."""
        return sinks.drop_trip(v, self.save, WEAVE_TRIP, CardId(policy.SCREEN)) if self.knobs.mix_weave else None

    def _screen_order(self) -> Order | None:
        """The screen's order card as the page fills it in, or None before it is offered."""
        card = next((c for c in opening().order_cards if c.tap_card == policy.SCREEN), None)
        after = None if card is None else card.offered_after
        if card is None or (after is not None and not self.has(UnlockKind(after.unlock_kind), after.id)):
            return None
        release = card.when.release if card.when.release is not None else card.when.value
        return Order(AtLeast(StoreValue(StoreId(card.store)), units(card.when.value), units(release)),
                     TapCard(CardId(policy.SCREEN)))

    def _hunger_offer(self) -> tuple[Verb, ...] | None:
        """Accepting hunger's chip card, or None before its offered_after or once a rule is on its condition (the page's
        chipCard and ruleFor)."""
        card = next(c for c in opening().order_cards if c.chip == policy.HUNGRY)
        after = card.offered_after
        if after is not None and not self.has(UnlockKind(after.unlock_kind), after.id):
            return None
        assert card.tap_card is not None
        rule = Order(condition(card.when, set(opening_cards()) | {card.tap_card}), TapCard(CardId(card.tap_card)))
        return None if any(o.when == rule.when for o in self.save.orders) else (SetOrders((*self.save.orders, rule)),)

    def _day_card(self, verbs: tuple[Verb, ...]) -> bool:
        """The opening's pick would tap a day-one card: day one's own rules decide those."""
        return any(isinstance(x, TapCard) and x.card not in opening_cards() for x in verbs)

    def _stock_order(self) -> Order | None:
        """The roots rule re-tuned to Take stock's need, once its order card is offered (its offered_after unlocked)."""
        card = next((c for c in opening().order_cards if c.store == policy.ROOTS and c.when.test == "at_most"
                     and c.offered_after is not None and c.offered_after.unlock_kind == "feature"), None)
        if card is None or card.tap_card is None or card.offered_after is None \
                or not self.has(UnlockKind.FEATURE, card.offered_after.id):
            return None
        release = card.when.release if card.when.release is not None else card.when.value
        return Order(AtMost(StoreValue(StoreId(card.store)), units(card.when.value), units(release)),
                     TapCard(CardId(card.tap_card)))

    def _rising_order(self) -> Order | None:
        card = next((c for c in opening().order_cards if c.when.test == "at_least"), None)
        if card is None or card.tap_card is None:
            return None
        n, m = units(card.when.value), units(card.when.release if card.when.release is not None else card.when.value)
        return Order(AtLeast(StoreValue(StoreId(card.store)), n, m), TapCard(CardId(card.tap_card)))


@cache
def opening_cards() -> frozenset[str]:
    """The opening's own cards, whose taps the opening's player decides."""
    return frozenset(c.id for c in load_opening(chapters=()).cards)


def route_player(schedule: Schedule, knobs: policy.Knobs, seed: int = 0) -> DayOnePlayer:
    return DayOnePlayer(opening_rules(), seed=seed, schedule=schedule, knobs=knobs)
