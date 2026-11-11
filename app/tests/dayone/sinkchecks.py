"""The day-one checks past the sinks (docs/design/banked-time-plan.md, item 7), each a pure function of a save and the
rules, so they read any chapter: a trip tapped lands when the page draws it; a trip paused dry has its supply's maker
in reach; a card showing every need met, a trip or a comfort among them, starts when tapped. Problems name ids and
seconds only (CLAUDE.md, "Never spoil the owner")."""
from collections.abc import Iterable

from ashfall_app.engine import (
    AtLeast, CardCount, CardId, InvalidVerbError, RunBy, RunKind, Rules, Save, SkillLevel, TapCard, View, advance,
    decide, value_at, view,
)
from ashfall_app.engine.work import completions
from ashfall_app.engine.cure_reading import puts_up
from tests.dayone.cures import CURE_S, act


def needs_met_blocked(views: Iterable[View]) -> tuple[int, list[str]]:
    """(cards judged, those showing every need met whose blocker is not a skill level or a card's completions)."""
    checked, broken = 0, set[str]()
    for v in views:
        for c in v.cards:
            if c.cap is not None and c.completions >= c.cap:
                continue
            if all(value_at(n.segment, v.time) >= n.quantity for n in c.needs):
                checked += 1
                shown = c.blocker is not None and isinstance(c.blocker.condition, AtLeast) \
                    and isinstance(c.blocker.condition.subject, SkillLevel | CardCount)
                if c.blocker is not None and not shown:
                    broken.add(f"{c.card} at t={v.time}")
    return checked, sorted(broken)


def tap_fails(save: Save, rules: Rules) -> list[str]:
    """Each card showing every need met and no blocker, on a free lane the player taps (not a ruled one, whose cards
    rules set: engine DESIGN.txt, "Ruled lane"), whose tap does not start it: the verb is refused, or the lane does not
    hold the card with a landing time."""
    v = view(save, rules)
    ruled = {lane.id for lane in rules.lanes if lane.ruled}
    free = {b.lane for b in v.lanes if b.card is None and b.lane not in ruled}
    lanes = {c.id: c.lane for c in rules.cards}
    out: list[str] = []
    for c in v.cards:
        if c.blocker is not None or lanes[c.card] not in free or (c.cap is not None and c.completions >= c.cap):
            continue
        try:
            after = view(decide(save, rules, save.time, TapCard(c.card)), rules)
        except InvalidVerbError:
            out.append(f"{c.card} at t={save.time}: shown ready, its tap is refused")
            continue
        held = next((b for b in after.lanes if b.card == c.card), None)
        if held is None or held.completes_at is None:
            out.append(f"{c.card} at t={save.time}: shown ready, its tap does not start it")
    return out


def landing_kept(save: Save, rules: Rules, card: CardId, at: int) -> bool:
    """A tap of `card` drawn landing at `at` lands then: one more completion at `at`, none a second before."""
    before = completions(save, rules, card)
    early = completions(advance(save, rules, at - 1), rules, card) if at - 1 > save.time else before
    return early == before and completions(advance(save, rules, at), rules, card) == before + 1


def tapped_landings(save: Save, rules: Rules) -> list[str]:
    """Each card a tap runs whose drawn landing (the bar's end) does not come true with nobody deciding."""
    v = view(save, rules)
    return [f"{c.card} drawn landing at t={c.completes_at}, not kept" for c in v.cards
            if c.by is RunBy.TAP and c.completes_at is not None and not landing_kept(save, rules, c.card, c.completes_at)]


def dry_unreached(save: Save, rules: Rules) -> list[str]:
    """Each card paused dry with a supply short whose maker is out of reach: no card on the panel puts that store up,
    or tapping the one that does leaves the store no higher CURE_S on."""
    v = view(save, rules)
    cards = {c.id: c for c in rules.cards}
    out: list[str] = []
    for c in v.cards:
        if c.run is not RunKind.PAUSED:
            continue
        for n in c.needs:
            if value_at(n.segment, v.time) >= n.quantity:
                continue
            makers = [m.card for m in v.cards if m.blocker is None and str(n.store) in puts_up(rules, cards[m.card])]
            if not any(_gains(save, rules, m, str(n.store)) for m in makers):
                out.append(f"{c.card} paused dry at t={save.time}: nothing in reach puts up {n.store}")
    return out


def _gains(save: Save, rules: Rules, maker: CardId, store: str) -> bool:
    """Tapping `maker` leaves `store` higher CURE_S on."""
    def level(s: Save) -> int:
        return next(x.segment.start_value for x in view(s, rules).ledger if str(x.store) == store)

    return level(advance(act(save, rules, maker), rules, save.time + CURE_S)) > level(save)
