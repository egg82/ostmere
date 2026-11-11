"""A scripted newcomer-ish player of the opening, driving the engine directly in simulated time, the way the page would.

It does what the screen asks as each card shows, one tap per decision, `reaction` seconds (drawn from a seeded range)
after the hands free up or after a glance finds nothing to do: the story steps; wood by hand for the warm wall and the
ruin for its find; laying wood to dry while the order isn't there yet; the fire plan, trying the ring and the strike
once too early; the first mix from the page's offer; each red line's order card, as the page shows it inline; forage
and rest into the mix when hunger and tiredness come; the roast; the edge; the greyed mix edited (woodcutting where
gathering was); the two crafts in the order `first_craft` picks; reading by the fire. Once the mix runs it taps no
mixed card, since a tap only stands in for its share. Every decision is recorded with its kind (a tap or another
decision), and every new thing on screen with the effort spent since the one before. It stops at the end moment:
the end feature unlocked (api/CONTRACT.txt, "The end").
"""
import copy
import random
from collections.abc import Callable
from dataclasses import dataclass, field
from functools import cache
from typing import Literal, Self, cast

from ashfall_app.engine import (
    BP, HANDS, CardId, CardShare, CardView, Line, Mix, MixId, Order, Rules, Save, SaveMix, SetOrders, StoreId,
    SwitchMix, TapCard, Unlock, UnlockKind, Verb, View, advance_logged, decide_logged, new_save, next_event, segment,
    units, view,
)
from ashfall_app.opening.convert import camp_lands, camp_trigger_id, condition
from ashfall_app.opening.schema import DAY_ONE, Opening, load_opening, to_rules

QUANTITY = units(1)
STUCK = "the player has nothing to do and nothing is coming"
STORY = ("stand_up", "look_around", "search_coat")
TOO_EARLY = ("ring_it", "strike_fire")
"""Tapped once as soon as they show, before they can be done, as a newcomer would: the bar lands its failed line."""
CRAFTS = ("make_stool", "build_fireback")
DRY_WANTED = 9
"""Dry wood the player lays for by hand before the order keeps it: the strike, both crafts and some fuel."""

IDLE_LOOK_S = 15
"""With nothing to do, the player looks back at least this often."""

Kind = Literal["tap", "decision"]


@cache
def opening() -> Opening:
    return load_opening()


@cache
def day_one() -> Opening:
    """The opening and day one alone: the order cards this player and day one's take. Day two's player takes day two's
    by its own policy (tests/daytwo/policy.py)."""
    return load_opening(chapters=(DAY_ONE,))


@cache
def camp_triggers() -> frozenset[str]:
    camp = opening().camp
    return frozenset() if camp is None else frozenset(
        camp_trigger_id(n) for n, lv in enumerate(camp.levels, start=1) if camp_lands(lv))


@cache
def opening_rules() -> Rules:
    """One Rules object for every run: the engine caches by the rules' identity."""
    return to_rules(opening())


def card_order(store: str) -> Order:
    """The order the content's order card fills in for `store`'s red line."""
    card = next(c for c in day_one().order_cards if c.store == store)
    assert card.tap_card is not None
    return Order(condition(card.when, {c.id for c in opening().cards}), TapCard(CardId(card.tap_card)))


def even(cards: list[str]) -> tuple[CardShare, ...]:
    """An even split of BP, the remainder to the first (the page's rule for the first mix and a card joining)."""
    each = BP // len(cards)
    return tuple(CardShare(CardId(c), BP - each * (len(cards) - 1) if i == 0 else each) for i, c in enumerate(cards))


@dataclass(frozen=True)
class News:
    """A new thing on screen: when, what, and the player's effort (taps, decisions) up to then."""

    at: int
    thing: str
    taps: int
    decisions: int


@dataclass
class Player:
    rules: Rules
    seed: int = 0
    reaction: tuple[int, int] = (2, 4)
    first_craft: str = "make_stool"
    drops_forage: bool = True
    mixes_needs: bool = True
    """Adds forage and rest to the mix when hunger and tiredness come; False taps them by hand instead."""
    """Takes forage out of the mix once the roast has answered hunger (the need gone); False keeps it running."""
    save: Save = field(init=False)
    lines: list[Line] = field(default_factory=lambda: [])
    decisions: list[tuple[int, Kind, Verb]] = field(default_factory=lambda: [])
    """Every verb sent, with its time and the kind of decision it belongs to (one control may send two verbs)."""
    made: list[Kind] = field(default_factory=lambda: [])
    """One entry per decision the player made: the effort."""
    news: list[News] = field(default_factory=lambda: [])
    end_at: int | None = None
    tried: set[str] = field(default_factory=lambda: set())
    history: list[tuple[Save, View]] = field(default_factory=lambda: [])
    """Every save the play passed through, with its view: a test reads a moment of a shared play (`at`) rather than
    playing its own copy to it."""
    decided: list[Save] = field(default_factory=lambda: [])
    """decided[i]: the save just after decisions[i] (`replay`)."""
    undecided: list[Save] = field(default_factory=lambda: [])
    """undecided[i]: the save decisions[i] was made on (daythree/visits.py reads a step's save before it here)."""

    def __post_init__(self) -> None:
        self.save = new_save(self.rules)
        self._rng = random.Random(self.seed)
        self._seen: set[str] = set()
        self._viewed: tuple[Save, View] | None = None
        self._took(self.save, ())

    # ---------- reading ----------

    def items(self, store: str) -> float:
        return segment(self.save, self.rules, StoreId(store)).start_value / QUANTITY

    def view(self) -> View:
        """The view of the current save, read once per save (a view costs milliseconds)."""
        if self._viewed is None or self._viewed[0] is not self.save:
            self._viewed = (self.save, view(self.save, self.rules))
        return self._viewed[1]

    def has(self, kind: UnlockKind, id_: str) -> bool:
        return Unlock(kind, id_) in self.save.unlocked

    def mix(self) -> Mix | None:
        return next((m for m in self.save.mixes if m.id == self.save.active), None)

    def mixed(self) -> list[str]:
        mix = self.mix()
        return [] if mix is None else [c.card for c in mix.components if isinstance(c, CardShare)]

    def resting(self) -> bool:
        """The mix the hands run now holds rest (a rule's, after the end): tired, the player leaves it to that."""
        running = next((m for m in self.save.mixes if m.id == self.view().running_mix), None)
        return running is not None and any(isinstance(c, CardShare) and c.card == "rest" for c in running.components)

    def card(self, card: str) -> CardView | None:
        return next((c for c in self.view().cards if c.card == card), None)

    def completed(self, card: str) -> bool:
        return any(c.card == card for c in self.view().completed)

    def taps(self) -> list[str]:
        return [v.card for _, kind, v in self.decisions if kind == "tap" and isinstance(v, TapCard)]

    def effort(self) -> tuple[int, int]:
        """(taps, other decisions) so far."""
        taps = self.made.count("tap")
        return taps, len(self.made) - taps

    def at_end(self, v: View) -> bool:
        """The engine recorded the end (View.ended_at)."""
        return v.ended_at is not None

    # ---------- recording ----------

    def _took(self, save: Save, lines: tuple[Line, ...]) -> None:
        self.save = save
        self.lines.extend(lines)
        v = self.view()
        self.history.append((save, v))
        shown = {f"{u.kind.value}:{u.id}" for u in save.unlocked if u.kind is not UnlockKind.STORE}
        shown |= {f"chip:{c}" for c in v.chips}
        shown |= {f"level:{s.skill}:{s.level}" for s in v.skills if s.level > 1}
        shown |= {f"level:{t.id}" for i, t in enumerate(self.rules.triggers) if save.fired[i] and t.id in camp_triggers()}
        if all(b.card is None for b in v.lanes if b.lane == HANDS):   # a tap's own draw is no reason for an order
            shown |= {f"order_card:{s}" for s in self._red_lines(v)}
        if self.at_end(v):
            shown.add("end")
            self.end_at = v.ended_at
        taps, decisions = self.effort()
        for thing in sorted(shown - self._seen):
            self.news.append(News(save.time, thing, taps, decisions))
        self._seen |= shown

    # ---------- sharing one play ----------

    def fork(self) -> Self:
        """A copy that plays on by itself: its records and its seeded randomness are its own (the rules are shared, as
        the engine caches by their identity)."""
        other = copy.copy(self)
        for name, value in vars(self).items():
            held: object = value
            if isinstance(held, (list, set, dict)):
                setattr(other, name, copy.copy(cast(object, held)))  # cast -- isinstance leaves list[Unknown] | set | dict
        other._rng = random.Random()
        other._rng.setstate(self._rng.getstate())
        return other

    def at(self, moment: Callable[["Player"], bool]) -> Self:
        """A fork standing at the first save of this play where `moment` holds (read off its history)."""
        q = self.fork()
        for save, v in self.history:
            q.save, q._viewed = save, (save, v)
            if moment(q):
                return q
        raise AssertionError("the play never reached that moment")

    def replay(self, decisions: int) -> Self:
        """A fork standing just after its first `decisions` decisions, as a fresh player given them would be."""
        q = self.fork()
        q.save, q._viewed = self.decided[decisions - 1], None
        return q

    # ---------- acting ----------

    def advance(self, t: int) -> None:
        step = advance_logged(self.save, self.rules, t)
        self._took(step.save, step.lines)

    def decide(self, kind: Kind, verbs: tuple[Verb, ...]) -> None:
        """One decision of the player's: a tap, or one control that may send more than one verb (the first mix)."""
        self.made.append(kind)
        for verb in verbs:
            self.decisions.append((self.save.time, kind, verb))
            self.undecided.append(self.save)
            step = decide_logged(self.save, self.rules, self.save.time, verb)
            self._took(step.save, step.lines)
            self.decided.append(step.save)

    def glance(self) -> int:
        return self._rng.randint(*self.reaction)

    def _free_hands(self) -> None:
        """Advance until the hands are free (an order may start the next bar the instant one lands)."""
        while True:
            hands = next(b for b in self.view().lanes if b.lane == HANDS)
            if hands.card is None:
                return
            if hands.completes_at is None:
                event = next_event(self.save, self.rules)
                assert event is not None, STUCK
                self.advance(event.time)
            else:
                self.advance(hands.completes_at)

    def wait(self) -> None:
        """Nothing to do: look again at the next event, when a card on screen turns ready, or after IDLE_LOOK_S,
        whichever comes first (the reaction to what then shows is added before acting)."""
        event = next_event(self.save, self.rules)
        soon = [self.save.time + IDLE_LOOK_S, *(c.blocker.ready_at for c in self.view().cards
                                                 if c.blocker is not None and c.blocker.ready_at is not None)]
        self.advance(min(t for t in (*soon, event.time if event else None) if t is not None and t > self.save.time))

    # ---------- the play ----------

    def play(self, limit_s: int = 40 * 60) -> int:
        """Play to the end moment; returns its engine time in seconds."""
        self.play_until(lambda: self.end_at is not None, limit_s)
        assert self.end_at is not None, f"no end by {limit_s}s: {self.news[-3:]}"
        return self.end_at

    def play_until(self, stop: Callable[[], bool], limit_s: int = 40 * 60) -> None:
        while not stop() and self.save.time < limit_s:
            self._free_hands()
            if stop():
                return
            move = self.next_move(self.view())
            if move is None:
                self.wait()
                continue
            self.advance(self.save.time + self.glance())
            self.decide(*move)

    def next_move(self, v: View) -> tuple[Kind, tuple[Verb, ...]] | None:
        """The next decision, most pressing first; None when only waiting helps."""
        red = next(iter(self._red_lines(v)), None)
        if red is not None:
            return "decision", (SetOrders((*self.save.orders, card_order(red))),)
        mix = self._mix_change(v)
        if mix is not None:
            return "decision", mix
        tap = self.pick(v)
        return None if tap is None else ("tap", (TapCard(CardId(tap)),))

    def _red_lines(self, v: View) -> list[str]:
        """Red and uncovered (falling or starved) lines that have an order card: shown inline, so always seen."""
        cards = {c.store for c in day_one().order_cards   # a chip's card is the strip's; an at_least one a rising line's
                 if c.chip is None and c.when.test == "at_most"}
        return [ln.store for ln in v.ledger if (ln.falling or ln.starved) and not ln.covered and ln.store in cards]

    def _mix_change(self, v: View) -> tuple[Verb, ...] | None:
        """The first mix from the offer; the greyed mix edited; a card joining for a need; forage leaving once the
        roast has answered hunger."""
        if self.has(UnlockKind.FEATURE, opening().first_mix.feature) and not self.save.mixes:
            ready = {c.card for c in v.cards}
            mix = Mix(MixId(opening().text["ui.mix.default"]),
                      even([c for c in opening().first_mix.cards if c in ready]))
            return SaveMix(mix), SwitchMix(mix.id)
        current = self.mix()
        if current is None:
            return None
        if current.id in v.greyed_mixes:
            return (SaveMix(self._edited(current, v)),)
        open_cards = {c.card for c in v.cards}
        for need, card in (("hungry", "forage"), ("tired", "rest")):
            if self.mixes_needs and need in v.chips and card in open_cards and card not in self.mixed():
                return (SaveMix(Mix(current.id, even([*self.mixed(), card]))),)
        if self.drops_forage and "forage" in self.mixed() and self.completed("roast_roots") and "hungry" not in v.chips:
            return (SaveMix(Mix(current.id, even([c for c in self.mixed() if c != "forage"]))),)
        return None

    def _edited(self, current: Mix, v: View) -> Mix:
        """The editor's first use: the retired card struck out and the card that replaced it dragged into its place."""
        out = {c.card for c in v.completed}
        waiting = [c.card for c in v.cards if c.card == "woodcutting" and c.card not in self.mixed()]
        parts: list[CardShare] = []
        for c in current.components:
            assert isinstance(c, CardShare)
            if c.card not in out:
                parts.append(c)
            elif waiting:
                parts.append(CardShare(CardId(waiting.pop()), c.share_bp))
        return Mix(current.id, tuple(parts))

    def pick(self, v: View) -> str | None:
        """The next card to tap, most pressing first; None when only waiting helps."""
        cards: dict[str, CardView] = {c.card: c for c in v.cards}
        ready = {k for k, c in cards.items() if c.blocker is None}
        story = next((c for c in STORY if c in cards), None)
        if story is not None:
            return story
        early = next((c for c in TOO_EARLY if c in cards and c not in ready and c not in self.tried), None)
        if early is not None:
            self.tried.add(early)
            return early
        crafts = (self.first_craft, *(c for c in CRAFTS if c != self.first_craft))
        one_off = next((c for c in ("clear_spot", "ring_it", "strike_fire", "roast_roots", "knap_edge",
                                    crafts[0], "read_by_fire", crafts[1]) if c in ready), None)
        if one_off is not None:
            return one_off
        rack_free = any(b.lane == "rack" and b.card is None for b in v.lanes)
        if "lay_to_dry" in ready and rack_free and not self.save.orders and self.items("dry_wood") < DRY_WANTED:
            return "lay_to_dry"
        return self._by_hand(cards)

    def _by_hand(self, cards: dict[str, CardView]) -> str | None:
        """A need by hand when it is not mixed (roots for the roast, rest while tired). Before the mix: wood for the
        wall's next batch, the ruin for its find, then stones once the ring asks for them; once the mix runs nothing
        else (a tap only stands in for its share)."""
        chips = self.view().chips
        if not self.mixes_needs or not self.save.mixes:
            if "hungry" in chips and "forage" in cards and self.items("roots") < 3:
                return "forage"
            if "tired" in chips and "rest" in cards and not self.resting():
                return "rest"
        if self.save.mixes:
            return None
        lay = cards.get("lay_to_dry")
        batch = lay.needs[0].quantity / QUANTITY if lay is not None and lay.needs else 3
        if "gather_wood" in cards and self.items("damp_wood") < batch:
            return "gather_wood"
        if "scavenge" in cards and (not self.has(UnlockKind.STORE, "nails")
                                    or ("ring_it" in cards and self.items("stones") < 5)):
            return "scavenge"
        return None
