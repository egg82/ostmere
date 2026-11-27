"""When B3 may land, as docs/decisions.md implies it rather than as fixed hours per route.

"Length" says minutes spent never change how long the game takes, and the 2 AM test says a babysitter ends no
further ahead than a player who comes back whenever they like. So a route's B3 is held to the babysitter's, not to a
band of its own: it may lag only by being away when a step that needs the player came due, at most one of the
route's visit gaps for each such step in B3's chain (relative). Those steps are read off the content
(presence_steps), never counted by hand. Only the players who use the tools are held to it (routes.TOOL_USERS); when
B3 lands is otherwise the readout's (report.py)."""
from collections.abc import Callable
from functools import cache

from ashfall_app.engine import Rules, Unlock, UnlockKind
from ashfall_app.engine.orders import AfterTime, CardCount, SkillLevel, StoreValue, Subject, Unlocked
from ashfall_app.opening.schema import load_opening

B3_CARD = "take_stock"


@cache
def _opening_ids() -> frozenset[str]:
    o = load_opening(chapters=())
    return frozenset([*(c.id for c in o.cards), *(t.id for t in o.triggers)])


def presence_steps(rules: Rules, target: str = B3_CARD, opening: frozenset[str] | None = None) -> list[str]:
    """The triggers `target` cannot land without, each opening one of the cards on its way: a trigger can open a card
    while the player is away, so that step waits for a return (a card opened by another card's completion opens in
    front of the player). Walked back from `target` through what opens each card, what each card and trigger waits on
    and what makes the stores those wait on; where a store has several makers only the triggers on every way count
    (another way around one is no wait). Stops at the opening's own content, skill levels and the clock."""
    return sorted(_Chain(rules, _opening_ids() if opening is None else opening).card(target))


class _Chain:
    """presence_steps' walk: each method returns the triggers its node cannot do without. A node met again on its
    own way back (a loop) needs nothing more."""

    def __init__(self, rules: Rules, stop: frozenset[str]) -> None:
        self.rules, self.stop = rules, stop
        self.done: dict[tuple[str, str], frozenset[str]] = {}

    def _memo(self, key: tuple[str, str], walk: Callable[[], frozenset[str]]) -> frozenset[str]:
        if key not in self.done:
            self.done[key] = frozenset()
            self.done[key] = walk()
        return self.done[key]

    def card(self, c: str) -> frozenset[str]:
        if c in self.stop:
            return frozenset()
        d = next(x for x in self.rules.cards if x.id == c)
        return self._memo(("card", c), lambda: frozenset[str]().union(
            self.opened(Unlock(UnlockKind.CARD, c), counts=True),
            *(self.subject(r.subject) for r in d.requires if not isinstance(r, AfterTime)),
            *(self.store(a.store) for a in d.inputs)))

    def opened(self, u: Unlock, counts: bool) -> frozenset[str]:
        ways = [frozenset[str]({t.id} if counts else ()) | self.trigger(t.id) for t in self.rules.triggers
                if u in t.outcome.unlocks and t.id not in self.stop]
        ways += [self.card(d.id) for d in self.rules.cards if u in d.outcome.unlocks or u in d.finished.unlocks]
        return _every(ways)

    def trigger(self, t: str) -> frozenset[str]:
        when = next(x for x in self.rules.triggers if x.id == t).when
        if isinstance(when, AfterTime):
            return frozenset()
        subject = when.subject
        return self._memo(("trigger", t), lambda: self.subject(subject))

    def subject(self, s: Subject) -> frozenset[str]:
        if isinstance(s, StoreValue):
            return self.store(s.store)
        if isinstance(s, CardCount):
            return self.card(s.card)
        if isinstance(s, Unlocked):
            return self.opened(s.unlock, counts=s.unlock.kind is UnlockKind.CARD)
        assert isinstance(s, SkillLevel), s   # a level is the mix's own pace: nobody needs to be there
        return frozenset()

    def store(self, s: str) -> frozenset[str]:
        def walk() -> frozenset[str]:
            r = self.rules
            ways = [self.opened(Unlock(UnlockKind.ACTION, a.id), counts=False) for a in r.standing
                    if any(f.store == s for f in a.makes)]
            ways += [self.card(d.id) for d in r.cards
                     if any(f.store == s for f in d.makes) or any(x.store == s for x in d.outcome.stores)]
            ways += [self.trigger(t.id) for t in r.triggers
                     if any(x.store == s for x in t.outcome.stores) and t.id not in self.stop]
            return _every(ways)
        return self._memo(("store", s), walk)


def _every(ways: list[frozenset[str]]) -> frozenset[str]:
    """What every way needs: nothing when there is no way (the opening's content or a save's start)."""
    if not ways:
        return frozenset()
    found = ways[0]
    for w in ways[1:]:
        found &= w
    return found


def b3_relative(hours: float | None, babysitter: float | None, gaps_h: list[float], steps: int) -> list[str]:
    """B3 no later than the babysitter's plus the route's `steps` largest gaps (each presence step costs at most the
    absence it came due in)."""
    if hours is None or babysitter is None:
        return [f"B3 at {hours} h, babysitter's at {babysitter} h"]
    bound = babysitter + sum(sorted(gaps_h, reverse=True)[:steps])
    return [] if hours <= bound + 1e-9 else [f"B3 at {hours} h, past the babysitter's {babysitter} h plus "
                                            f"{steps} gaps ({bound:.1f} h)"]
