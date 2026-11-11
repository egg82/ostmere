"""The scripted plays every opening test reads, each played once per pytest session (docs/engineering.md, "Fast from
the start"). A push plays the representative routes at seed 0: typical, by_hand, fireback_first, the eager forager, and
one run kept going past the end. The nightly deep run (tests-deep, which sets HYPOTHESIS_PROFILE=ci) plays every route
at seeds 0-2 and both kinds of player past the end. Tests take a route through the fixtures in conftest.py, so the play
happens in a fixture's setup, never in a test's own time; a test that needs a moment of a play reads it (`Player.at`)."""
import os
from collections.abc import Callable
from functools import cache

from ashfall_app.engine import View
from tests.opening.afterend import AfterEnd, AfterEndPlayer
from tests.opening.playthrough import Player, opening_rules

DEEP = os.environ.get("HYPOTHESIS_PROFILE") == "ci"
"""The nightly deep run: every route and seed, not just the representative ones."""

ROUTES: dict[str, Callable[[int], AfterEndPlayer]] = {
    "typical": lambda seed: AfterEndPlayer(opening_rules(), seed=seed),
    "by_hand": lambda seed: AfterEndPlayer(opening_rules(), seed=seed, mixes_needs=False),
    "fireback_first": lambda seed: AfterEndPlayer(opening_rules(), seed=seed, first_craft="build_fireback"),
    "slow": lambda seed: AfterEndPlayer(opening_rules(), seed=seed, reaction=(6, 12)),
}
"""Each kind of player: typical mixes its needs; by_hand taps them; fireback_first builds the other craft first; slow
reacts in 6-12 s. The page's two after-the-end kinds are typical (it mixed rest) and by_hand."""
PUSH_ROUTES = ("typical", "by_hand", "fireback_first")
SEEDS = (0, 1, 2) if DEEP else (0,)
AFTER_END_MINUTES = 20


def plays() -> list[tuple[str, int]]:
    """(route, seed) for the routes this run plays."""
    return [(name, seed) for name in (ROUTES if DEEP else PUSH_ROUTES) for seed in SEEDS]


@cache
def route(name: str, seed: int = 0) -> AfterEndPlayer:
    """The route played to its end moment, once per session. Read it; to play on from it, fork it."""
    p = ROUTES[name](seed)
    p.play()
    return p


def after_end_plays() -> list[tuple[str, int]]:
    """(route, seed) kept going past the end: by_hand on a push (it meets the offer); typical too in the deep run (it
    mixed rest, so never tired)."""
    return [(name, seed) for name in (("by_hand", "typical") if DEEP else ("by_hand",)) for seed in SEEDS]


@cache
def after_end(name: str, seed: int = 0) -> tuple[AfterEnd, AfterEndPlayer]:
    """The route kept going AFTER_END_MINUTES past the end lines, on a fork of its opening."""
    p = route(name, seed).fork()
    return p.play_after_end(AFTER_END_MINUTES), p


class EagerForager(Player):
    """Forages by hand to a full store whenever foraging is open: more forages, earlier, than anything could count."""

    def pick(self, v: View) -> str | None:
        cards = {c.card for c in v.cards}
        if "forage" in cards and self.items("roots") < 8:
            return "forage"
        return super().pick(v)


@cache
def eager() -> EagerForager:
    p = EagerForager(opening_rules())
    p.play()
    return p
