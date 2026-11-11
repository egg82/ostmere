"""The scripted player kept going past the end, the way the page teaches the second mix (docs/design/opening-screen.md,
the hands strip and "Dots and the one glow"): the end lines read END_READ_S after the end; then
the strip's rest offer (Nudge 1) shows the first time the tired chip is on with no rule on its store and test, and stays
until used; accepting it is the page's addRule (a saved mix of rest alone, reused if one exists, and a rule running it);
the Mixes list's door glows (Nudge 2) the first time a hands rule comes on by itself after the end while the offer is
not holding the glow. Event by event, so no rule's coming on is stepped over.

The scripted player's hands rules tap a card (playthrough.card_order) where the page's run a one-card mix, so "a hands
rule came on by itself" is read off the latches (any rule that taps a hands card or runs a mix), not view.mix_order.
"""
from dataclasses import dataclass, field

from ashfall_app.engine import (
    BP, HANDS, CardId, CardShare, Condition, Line, Mix, MixId, Order, Rules, Save, SaveMix, SetOrders, SwitchMix,
    TapCard, next_event,
)
from ashfall_app.opening.convert import condition
from ashfall_app.opening.entries import OrderCardEntry
from tests.opening.playthrough import Player, opening

END_READ_S = 20
"""What waits on the end comes this long after it: the end lines' reading time (ui/end.ts, READ_MS)."""


def rest_card() -> OrderCardEntry:
    return next(c for c in opening().order_cards if c.chip is not None)


def rest_when() -> Condition:
    """The rest card's condition, as the engine's: the tired chip's own."""
    return condition(rest_card().when, {c.id for c in opening().cards})


def offer_shows(after_end: bool, ended: bool, read: bool, wanted: bool) -> bool:
    """The page's gate on a chip's card (game/cues.ts, chipCard): one with after_end waits for the end and its lines
    read; `wanted` is the rest of its test (the chip on, no rule on its store and test)."""
    return wanted and (not after_end or (ended and read))


@dataclass
class AfterEnd:
    """What the play past the end saw, in game seconds; None where it never came in the window."""

    end_at: int
    read_at: int
    offer_at: int | None = None
    accepted_at: int | None = None
    door_at: int | None = None
    """Nudge 2: the first hands rule coming on by itself after the end lines are read, while the offer does not hold the glow."""
    came_on: list[tuple[int, int]] = field(default_factory=lambda: [])
    """(time, order index): each hands rule coming on by itself after the end lines are read."""
    rest_taps_after: int = 0
    """Rest tapped by hand after the offer was accepted."""
    effort_at: dict[str, int] = field(default_factory=lambda: {})
    """Actions (taps plus decisions) made by each moment: "offer", "door"."""


@dataclass
class AfterEndPlayer(Player):
    takes_offers: bool = True
    after: AfterEnd | None = None
    wanted_early: list[int] = field(default_factory=lambda: [])
    """Times before the end lines were read when the offer's test short of the end gate held."""
    shown_early: list[int] = field(default_factory=lambda: [])
    """Times before the end lines were read when the offer would show (never: the gate)."""

    # ---------- what the page would show ----------

    def offer_wanted(self, save: Save) -> bool:
        """The chip on and no rule on the rest card's store and test: the offer's test, short of the end gate."""
        return rest_card().chip in self.view().chips and not any(_same_store_test(o.when) for o in save.orders)

    def _took(self, save: Save, lines: tuple[Line, ...]) -> None:
        before = self.save
        super()._took(save, lines)
        a = self.after
        if a is None:
            wanted = self.offer_wanted(save)
            if wanted:
                self.wanted_early.append(save.time)
            if offer_shows(rest_card().after_end, save.ended_at is not None, False, wanted):
                self.shown_early.append(save.time)
            return
        self._observe(a, before, save)

    def _observe(self, a: AfterEnd, before: Save, save: Save) -> None:
        t = save.time
        if t < a.read_at:
            return
        if a.offer_at is None and offer_shows(rest_card().after_end, True, True, self.offer_wanted(save)):
            a.offer_at = t
            a.effort_at["offer"] = len(self.made)
        if before.orders != save.orders or before is save:
            return
        for i, order in enumerate(save.orders):
            on = save.latches[i] and not (i < len(before.latches) and before.latches[i])
            if on and _hands_rule(order, self.rules):
                a.came_on.append((t, i))
                glow_held = a.offer_at is not None and a.accepted_at is None
                if a.door_at is None and not glow_held:
                    a.door_at = t
                    a.effort_at["door"] = len(self.made)

    # ---------- the play ----------

    def play_after_end(self, minutes: int = 20) -> AfterEnd:
        """Play to the end, read its lines, and keep going `minutes` of game time from there."""
        end = self.play()
        a = AfterEnd(end_at=end, read_at=end + END_READ_S)
        self.after = a
        until = a.read_at + minutes * 60
        self._advance_through(min(until, a.read_at))
        self._observe(a, self.save, self.save)
        while self.save.time < until:
            if self.takes_offers and a.offer_at is not None and a.accepted_at is None:
                self._advance_through(self.save.time + self.glance())
                self.decide("decision", self.accept_rest())
                a.accepted_at = self.save.time
                continue
            hands = next(b for b in self.view().lanes if b.lane == HANDS)
            move = self.next_move(self.view()) if hands.card is None else None
            if move is not None:
                self._advance_through(self.save.time + self.glance())
                self.decide(*move)
                if a.accepted_at is not None and move[1] == (TapCard(CardId("rest")),):
                    a.rest_taps_after += 1
                continue
            event = next_event(self.save, self.rules)
            soon = self.save.time + 15
            self.advance(min(until, soon, event.time if event is not None else until))
        return a

    def accept_rest(self) -> tuple[SaveMix | SetOrders, ...]:
        """The page's addRule for the rest card: a mix of rest alone (reused when saved), then a rule running it."""
        card = rest_card()
        assert card.tap_card is not None
        solo = (CardShare(CardId(card.tap_card), BP),)
        found = next((m for m in self.save.mixes if m.components == solo), None)
        name = found.id if found is not None else _free_name(self.save, opening().text["c_rest"])
        rule = Order(rest_when(), SwitchMix(MixId(name)))
        saves = () if found is not None else (SaveMix(Mix(MixId(name), solo)),)
        return (*saves, SetOrders((*self.save.orders, rule)))

    def _advance_through(self, t: int) -> None:
        """To `t`, stopping at every event on the way, so each latch's flip is seen."""
        while True:
            event = next_event(self.save, self.rules)
            if event is None or event.time >= t:
                break
            self.advance(event.time)
        if t > self.save.time:
            self.advance(t)


def _same_store_test(when: Condition) -> bool:
    """The page's ruleFor: a rule on the rest card's store and test, at whatever levels."""
    want = rest_when()
    return type(when) is type(want) and getattr(when, "subject", None) == getattr(want, "subject", None)


def _hands_rule(order: Order, rules: Rules) -> bool:
    """A rule the hands run: a mix, or a tap of a hands card (read off the play's own rules, which may hold chapters
    past the shipped ones)."""
    then = order.then
    return isinstance(then, SwitchMix) or (
        isinstance(then, TapCard) and next(c for c in rules.cards if c.id == then.card).lane == HANDS)


def _free_name(save: Save, base: str) -> str:
    name, n = base, 2
    while any(m.id == name for m in save.mixes):
        name, n = f"{base} {n}", n + 1
    return name
