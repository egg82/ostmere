"""A route on the chore fixture (chore/chapter.py): the visits it makes, the chapter moves it makes at each visit's start
and end (daythree/moves.move, the chip rule its only work), and the log of every verb it sent, for the 2 AM replay
(dayone/parity.py)."""
from dataclasses import dataclass, field

from ashfall_app.engine import CardId, Save, Verb, advance, decide, new_save, view
from tests.chore.chapter import ASHED, rules
from tests.daythree import moves
from tests.daythree.chapter import ChipRule, Later
from tests.dayone.player.sinks import Chapter, SinkKnobs

Visit = tuple[int, int]
MOVES_PER_VISIT = 10


@dataclass
class Played:
    save: Save
    log: list[tuple[int, Verb]] = field(default_factory=lambda: [])


def later(cure: CardId) -> Later:
    """The chapter as the moves read it: nothing but the chip's rule, its cure on the lane the route chose."""
    return Later("C1", "C2", Chapter(), (), (), (), lambda _s, _r: set(), (), chip_rules=(ChipRule(ASHED, cure),))


def play(visits: tuple[Visit, ...], until: int, cure: CardId, takes_rules: bool) -> Played:
    """The route from a new save through `visits` (start, end), deciding at each one's start and end, then on with
    nobody deciding to `until`."""
    r, chapter = rules(), later(cure)
    p = Played(new_save(r))
    for start, end in visits:
        for at in (start, end):
            p.save = advance(p.save, r, at)
            for _ in range(MOVES_PER_VISIT):
                m = moves.move(view(p.save, r), p.save, r, chapter, SinkKnobs(), takes_rules)
                if m is None:
                    break
                for verb in m[1]:
                    p.save = decide(p.save, r, at, verb)
                    p.log.append((at, verb))
            else:
                raise AssertionError("a visit never settled")
    p.save = advance(p.save, r, until)
    return p
