"""Every input a card is held back on says where it comes from (docs/decisions.md, "Progress is stated, never hinted"):
on each push route's play from the start through day fifteen, the edge of written content, at every moment the player
saw, each input short on a card waiting on its blocker, not running, and on the card panel (not a ruled lane's task)
has its gate drawn in its place, a maker in play, or is drawn used up: nothing in play can make it again and every
grant of it has fired (View Need.gate, makers and spent, api/sources.py). A store the player never sees
(StoreInfo.hidden) shows as its countdown, so it is not judged. Walked in a fixture's setup; ids only
(CLAUDE.md, "Never spoil the owner")."""
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from functools import cache

import pytest

from ashfall_app.api.sources import Source, StoreSources, sources, store_sources
from ashfall_app.engine import Rules, Save, View, value_at
from ashfall_app.opening.schema import CHAPTERS, IN_WRITING, Opening, load_opening
from tests.daytwo.conftest import PLAY_TIMEOUT_S
from tests.daytwo.player import DayTwoPlayer
from tests.weektwo.routes import FIFTEEN_PUSH_ROUTES

pytestmark = [pytest.mark.playthrough, pytest.mark.timeout(PLAY_TIMEOUT_S)]
Served = Callable[[Save, Rules, View, Mapping[str, StoreSources]], Mapping[tuple[str, str], Source]]


@dataclass(frozen=True)
class Walk:
    judged: int
    """Short inputs judged, counted once per moment."""
    gated: frozenset[str]
    """`card:store` of each judged with a gate served."""
    spent: frozenset[str]
    """`card:store` of each judged served as spent."""
    missed: dict[str, float]
    """`card:store` -> the first hour it was judged with neither a gate nor a maker."""


@cache
def content() -> Opening:
    return load_opening(chapters=CHAPTERS + IN_WRITING)


def served_nothing(save: Save, rules: Rules, v: View, table: Mapping[str, StoreSources]) -> dict[tuple[str, str], Source]:
    """A view that serves no source for any need, as before View Need.gate and makers: the guard's control."""
    return {}


def walk(history: Sequence[tuple[Save, View]], rules: Rules, served: Served = sources) -> Walk:
    hidden = {s.id for s in content().stores if s.hidden}
    ruled = {lane.id for lane in rules.lanes if lane.ruled}
    inputs = {c.id: {a.store for a in c.inputs} for c in rules.cards if c.lane not in ruled}
    table = store_sources(content())
    judged = 0
    gated: set[str] = set()
    spent: set[str] = set()
    missed: dict[str, float] = {}
    for save, v in history:
        src = served(save, rules, v, table)
        for c in v.cards:
            for n in c.needs if c.blocker is not None and c.by is None and c.card in inputs else ():
                if n.store not in inputs[c.card] or n.store in hidden or value_at(n.segment, v.time) >= n.quantity:
                    continue
                judged += 1
                s, key = src.get((c.card, n.store)), f"{c.card}:{n.store}"
                if s is not None and s.gate is not None:
                    gated.add(key)
                if s is not None and s.spent:
                    spent.add(key)
                if s is None or (s.gate is None and not s.makers and not s.spent):
                    missed.setdefault(key, round(v.time / 3600, 2))
    return Walk(judged, frozenset(gated), frozenset(spent), missed)


@pytest.fixture
def walked(fifteen_route: tuple[str, DayTwoPlayer]) -> tuple[Walk, Walk]:
    """The route's walk as served, and the control's."""
    _, p = fifteen_route
    return walk(p.history, p.rules), walk(p.history, p.rules, served_nothing)


@pytest.mark.parametrize("fifteen_route", FIFTEEN_PUSH_ROUTES, indirect=True)
def test_every_short_input_shows_its_gate_a_maker_or_used_up(walked: tuple[Walk, Walk]):
    w, _ = walked
    assert w.judged > 1000 and w.gated, f"judged {w.judged} short inputs, {len(w.gated)} gated: the walk is blind"
    assert w.missed == {}, f"short with no gate, no maker and not spent (card:store -> first hour): {w.missed}"


@pytest.mark.parametrize("fifteen_route", FIFTEEN_PUSH_ROUTES, indirect=True)
def test_the_walk_fails_a_view_that_serves_no_source(walked: tuple[Walk, Walk]):
    """The control: with nothing served, every gated and every spent input and many made ones are missed, the first
    within an hour."""
    w, bare = walked
    assert w.gated | w.spent <= set(bare.missed) and len(bare.missed) > 20
    assert min(bare.missed.values()) < 1
