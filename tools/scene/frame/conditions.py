"""A composite's State of facts and store levels, and the page's rule for whether a layer's condition holds in one,
with the kinds of condition it knows."""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass


@dataclass(frozen=True)
class State:
    """A moment to composite: the facts that hold (project:, pushes:, running:, chip:, feature:) and store levels."""
    facts: frozenset[str] = frozenset()
    stores: tuple[tuple[str, int], ...] = ()

    def then(self, add: Iterable[str] = (), drop: Iterable[str] = (), **stores: int) -> State:
        return State((self.facts - frozenset(drop)) | frozenset(add), tuple({**dict(self.stores), **stores}.items()))


def holds(cond: str | None, state: State) -> bool:
    """The page's rule (app/client/src/scene/conditions.ts) over a composite's State."""
    if cond is None or cond == "always":
        return True
    if "|" in cond:
        return any(holds(c, state) for c in cond.split("|"))
    if "&" in cond:
        return all(holds(c, state) for c in cond.split("&"))
    if cond in ("dark", "day"):
        from frame.grades import GRADES, pick
        return bool(GRADES[pick(lambda when: holds(when, state))].get("dark")) == (cond == "dark")
    if cond.startswith("store:"):
        store, _, n = cond[len("store:"):].partition("@")
        lo, _, hi = (n or "1").partition("..")
        held = dict(state.stores).get(store, 0)
        return held >= int(lo) and (not hi or held < int(hi))
    return cond in state.facts


def in_dark(cond: str) -> str:
    """`cond` while it is dusk or night: each of its alternatives and the dark."""
    return "|".join(f"{term}&dark" for term in cond.split("|"))


CONDITIONS = {
    "always": "shown from the start",
    "project:<id>": "the project has completed at least once",
    "pushes:<id>@<n>": "the project has had at least n of its pushes",
    "running:<id>": "the project is running now (a lane is working on it)",
    "mix:<id>": "the card runs in the active mix (a share above 0, not paused or yielded) and it is its turn at the figure: the mix's cards take turns, each for its share of a 30 s round",
    "store:<id>": "the store holds at least one item",
    "store:<id>@<n>": "the store holds at least n items",
    "store:<id>@<a>..<b>": "the store holds at least a items and fewer than b: a window of a count-up clock",
    "chip:<id>": "the chip is showing",
    "feature:<id>": "the feature is unlocked",
    "action:<id>": "the standing action is unlocked (it runs by itself from then on)",
    "answered:<offer>": "the offer has been answered, by any answer",
    "answer:<answer>": "that answer was the one given",
    "joined:<lane>": "the lane's person has joined the town",
    "left:<lane>": "the lane's person has left the town for good",
    "end:showing": "the end has happened: the end feature was unlocked with every ledger line covered (it never clears)",
    "dark": "the grade the page shows is a dusk or a night one (the manifest's grades say which, `dark`): the light going, or gone",
    "day": "the grade the page shows is not a dusk or night one: `dark`'s opposite, for a layer that gives way by day only",
    "<a>|<b>|...": "any of the conditions holds",
    "<a>&<b>&...": "all of the conditions hold; binds tighter than |, so a&b|c is (a and b) or c",
}


KINDS = {"always", "project", "pushes", "running", "mix", "store", "end", "chip", "feature", "action", "answered", "answer", "joined", "left", "dark", "day"}
"""The condition kinds the page knows (app/client/src/scene/conditions.ts)."""
