"""The whenever player on the fixture outpost: the banked route (tests/banked/play.py) with one move of the chapter's
own, queueing every stage of the build at once, since the sinks queue a comfort for its next completion only."""
from typing import Unpack

from ashfall_app.engine import AtLeast, CardCount, QueueEntry, Save, SetQueue, TapCard, Verb, View
from tests.banked.play import Played, Visit, route
from tests.dayone import sinks
from tests.supply.chapter import BUILD, CHAPTER, GATHER, STAGES, Knobs, rules

__all__ = ["Played", "play"]


def play(visits: tuple[Visit, ...], knobs: sinks.SinkKnobs, until: int, **kw: Unpack[Knobs]) -> Played:
    return route(rules(**kw), visits, knobs, until, CHAPTER, GATHER, _stages)


def _stages(v: View, save: Save) -> tuple[str, tuple[Verb, ...]] | None:
    """Once the build shows, every stage queued at once, When ready (the queue carries them across the night)."""
    if save.queue or all(c.card != BUILD for c in v.cards):
        return None
    queue = tuple(QueueEntry(TapCard(BUILD), AtLeast(CardCount(BUILD), n, n)) for n in range(1, STAGES + 1))
    return "decision", (SetQueue(queue),)
