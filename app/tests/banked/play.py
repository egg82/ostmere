"""A route on the fixture chapter: the visits it makes, the moves it makes in each (the gatherer first, then its sinks:
tests/dayone/sinks.py), and the log of every verb it sent, for the 2 AM replay (dayone/parity.py)."""
from dataclasses import dataclass, field
from typing import Unpack

from ashfall_app.engine import BP, CardShare, Mix, MixId, Rules, Save, SaveMix, SwitchMix, Verb, advance, decide, new_save, view
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


def play(visits: tuple[Visit, ...], knobs: sinks.SinkKnobs, until: int, fights: bool = False, **times: Unpack[Times]) -> Played:
    """The route from a new save through `visits` (start, end), then on with nobody deciding to `until`. A visit's moves
    are made at its start and again at its end (what showed while it lasted), each decision after another until the view shows nothing left to do."""
    r = rules(fights=fights, **times)
    p = Played(new_save(r), visits=visits)
    for start, end in (v for v in visits if v[0] <= until):
        for at in (start, min(end, until)):
            p.save = advance(p.save, r, at)
            _settle(p, r, at, knobs, FIGHTING if fights else CHAPTER)
    p.save = advance(p.save, r, until)
    return p


def _settle(p: Played, r: Rules, at: int, knobs: sinks.SinkKnobs, chapter: sinks.Chapter) -> None:
    for _ in range(MOVES_PER_VISIT):
        m = _gather(p.save) or sinks.move(view(p.save, r), r, p.save, chapter, knobs)
        if m is None:
            return
        for verb in m[1]:
            p.save = decide(p.save, r, at, verb)
            p.log.append((at, verb))
    raise AssertionError("a visit never settled")


def _gather(save: Save) -> tuple[str, tuple[Verb, ...]] | None:
    """The first move: the gatherer alone in the mix."""
    if save.active is not None:
        return None
    mix = Mix(MixId("gather_only"), (CardShare(GATHER, BP),))
    return "decision", (SaveMix(mix), SwitchMix(mix.id))


def built(p: Played) -> int:
    """Comfort completions at the end."""
    return completions(p.save, rules(), COMFORT)
