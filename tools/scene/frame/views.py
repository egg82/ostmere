"""How much of the art the page shows, as authored data: the camp's frame and each widening, keyed on an unlock.

The first view is the default; a later one whose `when` holds replaces it (the page's pickView, as grades are picked),
so the frame only ever grows. Every view is the art's top-left corner at its size, so a layer keeps its place when the
frame widens, and the art itself (`EXTENT`) is as big as the biggest."""
from __future__ import annotations

from dataclasses import dataclass

from draw.kit import T
from frame.stages import State, holds


@dataclass(frozen=True)
class View:
    id: str
    size: tuple[int, int]
    when: str | None


VIEWS = (View("camp", (15 * T, 9 * T), None),
         View("room_for_two", (18 * T, 11 * T), "project:make_room"),
         View("rack_roof", (20 * T, 12 * T), "pushes:rack_roof@1"),
         View("make_bay2", (22 * T, 13 * T), "project:make_bay2"),
         View("drift", (24 * T, 14 * T), "feature:drift"))
EXTENT = (max(v.size[0] for v in VIEWS), max(v.size[1] for v in VIEWS))
"""The art's own size: the canvas every layer is drawn on."""


def pick(state: State) -> View:
    """The view the page shows in `state`: the last whose `when` holds, else the first."""
    chosen = VIEWS[0]
    for view in VIEWS[1:]:
        if holds(view.when, state):
            chosen = view
    return chosen


def problems(views: tuple[View, ...]) -> list[str]:
    """What is wrong with a list of views: the first must be unconditional, the rest conditional, and each at least as
    big as the one before (the frame only grows)."""
    out = [f"{v.id}: only the first view is unconditional" for v in views[1:] if v.when is None]
    if views[0].when is not None:
        out.append(f"{views[0].id}: the first view is the default, so it has no `when`")
    out += [f"{b.id}: smaller than {a.id}" for a, b in zip(views, views[1:]) if b.size[0] < a.size[0] or b.size[1] < a.size[1]]
    return out


def manifest() -> list[dict[str, object]]:
    return [{"id": v.id, "size": list(v.size), "when": v.when} for v in VIEWS]
