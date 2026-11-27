"""A route on the fixture chapter: the visits it makes, the moves it makes in each (the gatherer first, then its sinks:
tests/dayone/sinks.py), and the log of every verb it sent, for the 2 AM replay (dayone/parity.py)."""
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Unpack

from ashfall_app.engine import (
    BP, CardId, CardShare, Mix, MixId, Rules, Save, SaveMix, SwitchMix, Verb, View, advance, decide, new_save, view,
)
from ashfall_app.engine.work import completions
from tests.banked.chapter import CHAPTER, COMFORT, FIGHTING, GATHER, Times, rules
from tests.dayone import sinks

Visit = tuple[int, int]
MOVES_PER_VISIT = 20


@dataclass
class Played:
    save: Save
    log: list[tuple[int, Verb]] = field(default_factory=lambda: [])
    visits: tuple[Visit, ...] = ()


def play(visits: tuple[Visit, ...], knobs: sinks.SinkKnobs, until: int, fights: bool = False, finds: int = 0, **times: Unpack[Times]) -> Played:
    r = rules(fights=fights, finds=finds, **times)
    return route(r, visits, knobs, until, FIGHTING if fights else CHAPTER, GATHER)


Extra = Callable[[View, Save], tuple[str, tuple[Verb, ...]] | None]


def route(r: Rules, visits: tuple[Visit, ...], knobs: sinks.SinkKnobs, until: int, chapter: sinks.Chapter, gatherer: CardId,
          extra: Extra | None = None) -> Played:
    """The route from a new save through `visits` (start, end), then on with nobody deciding to `until`. A visit's moves
    are made at its start and again at its end (what showed while it lasted), each decision after another until the view shows nothing left to do.
    `gatherer`: the card the first move runs alone. `extra`: a move of the chapter's own, tried after the gatherer's."""
    p = Played(new_save(r), visits=visits)
    for start, end in (v for v in visits if v[0] <= until):
        for at in (start, min(end, until)):
            p.save = advance(p.save, r, at)
            _settle(p, r, at, knobs, chapter, gatherer, extra)
    p.save = advance(p.save, r, until)
    return p


def _settle(p: Played, r: Rules, at: int, knobs: sinks.SinkKnobs, chapter: sinks.Chapter, gatherer: CardId,
            extra: Extra | None) -> None:
    for _ in range(MOVES_PER_VISIT):
        v = view(p.save, r)
        m = _gather(p.save, gatherer) or (extra(v, p.save) if extra else None) or sinks.move(v, r, p.save, chapter, knobs)
        if m is None:
            return
        for verb in m[1]:
            p.save = decide(p.save, r, at, verb)
            p.log.append((at, verb))
    raise AssertionError("a visit never settled")


def _gather(save: Save, gatherer: CardId) -> tuple[str, tuple[Verb, ...]] | None:
    """The first move: the gatherer alone in the mix."""
    if save.active is not None:
        return None
    mix = Mix(MixId("gather_only"), (CardShare(gatherer, BP),))
    return "decision", (SaveMix(mix), SwitchMix(mix.id))


def built(p: Played) -> int:
    """Comfort completions at the end."""
    return completions(p.save, rules(), COMFORT)
