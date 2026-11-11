"""A scripted player of day two: day one's player (tests/dayone/player.py) on the rules with day two merged, kept going
past B3 to the visit B4 is seen in, or on through a later chapter (daythree/chapter.Later) to the visit its last beat
is seen in, making that chapter's moves first (daythree/moves.py) once its first beat has landed. Inside a visit it makes day two's moves first (policy.py), then day one's; away, time
runs event by event as day one's. What it adds to day one's records: day two's story ids as they land and are seen
(content.py), and the beats among them as News. Past B3 it leaves a visit as the human-paced player does (leaves());
a babysitter, whose one visit never ends, leaves LINGER_S after B4."""
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import ClassVar

from ashfall_app.engine import Line, Save, View
from tests.daythree import moves as m3
from tests.daythree.chapter import Later
from tests.daytwo import content as c
from tests.daytwo import policy as p2
from tests.dayone import policy, sinks
from tests.dayone.human import lands_within, thresholds
from tests.dayone.player import DayOnePlayer, VisitRecord
from tests.opening.playthrough import News

LINGER_S = 10 * 60
QUEUEABLE = (*policy.QUEUEABLE, *c.BUILDS)
"""Day one's queueable steps and the two builds (A16 is not: look_out's shape, day_two.toml)."""


@dataclass
class DayTwoPlayer(DayOnePlayer):
    STOP_BEAT: ClassVar[str] = "B4"
    knobs2: p2.Knobs2 = field(default_factory=p2.Knobs2)
    tried: set[str] = field(default_factory=lambda: set())
    sink_knobs: sinks.SinkKnobs = field(default_factory=sinks.SinkKnobs)
    """What the route does about the sinks (dayone/sinks.py): day two's is the comfort, queued once both builds are in."""
    laters: tuple[Later, ...] = ()
    """The chapters past B4 in order, each starting at the beat the one before stops at (daythree/chapter.Later)."""
    kept_lines: set[str] = field(default_factory=lambda: set())
    """The ledger lines the page keeps: each store whose line has joined at a view this player looked at, since a line
    drawn once stays drawn (sinks.line_drawn)."""
    trip_marks: sinks.Marks = field(default_factory=lambda: {})
    """Which retune last set each trip's share (sinks.retune_trip): the player's memory that keeps a hands rule's
    turn-down and the raise-back from undoing each other within one cycle of the rule."""

    @property
    def later(self) -> Later | None:
        """The chapter being played: the last whose first beat has landed (the first, before any has)."""
        started = [x for x in self.laters if x.start in self.landed_at]
        return started[-1] if started else (self.laters[0] if self.laters else None)

    def stop_beat(self) -> str:
        return self.laters[-1].stop if self.laters else self.STOP_BEAT

    def b3_visit(self) -> int | None:
        """The index (1-based) of the visit B3 was seen in: day two's V1."""
        return visit_seen(self.visits, self.seen_at.get("B3"))

    def leaves(self) -> bool:
        """Past B3, by the human player's rule: nothing to act on and no tap of the player's landing within the dead
        gap ends the visit, and the rest of the schedule's window is absence (human.lands_within). A route that
        stays leaves LINGER_S after B4 is seen."""
        seen = self.seen_at.get(self.stop_beat())
        if seen is not None and self.save.time >= seen + LINGER_S:
            return True
        return ("B3" in self.seen_at and not self.knobs2.stays
                and not lands_within(self.view(), self.rules, self.save.time, thresholds().dead_gap_s()))

    def _landings(self, save: Save) -> None:
        super()._landings(save)
        found = c.landed(save, self.rules).union(*(x.landed(save, self.rules) for x in self.laters))
        for b in found - set(self.landed_at):
            self.landed_at[b] = save.time

    def _took(self, save: Save, lines: tuple[Line, ...]) -> None:
        before = set(self.seen_at)
        super()._took(save, lines)
        taps, decisions = self.effort()
        new = set(self.seen_at) - before
        later = [b for x in self.laters for b in x.news if b in new]
        for beat in (*c.new_beats(new), *later):
            self.news.append(News(save.time, f"beat:{beat}", taps, decisions))

    def day_move(self, v: View) -> policy.Move | None:
        self.kept_lines |= {str(ln.store) for ln in v.ledger if sinks.line_drawn(v, ln)}
        if "B3" not in self.landed_at:
            return super().day_move(v)
        orders, k = self.save.orders, self.knobs2
        later = self.later
        if later is not None and later.start in self.landed_at:
            mine = m3.move(v, self.save, self.rules, later, self.sink_knobs, k.her_rule, frozenset(self.kept_lines),
                           self.trip_marks)
            if mine is not None:
                return mine
        return (p2.answer(v, self.rules, orders, k) or self._sink(v) or p2.one_off(v, k, self.tried, not self.sink_knobs.queue_comforts) or p2.her_first_rule(v, orders, k)
                or p2.her_task(v, orders, k) or self._queue_build(v) or super().day_move(v))

    def _sink(self, v: View) -> policy.Move | None:
        """The comfort queued When ready once it shows, never while A16 or a build waits (policy.builds_wait)."""
        if p2.builds_wait(v):
            return None
        return sinks.move(v, self.rules, self.save, c.CHAPTER, self.sink_knobs, kept=frozenset(self.kept_lines))

    def _queue_build(self, v: View) -> policy.Move | None:
        if not self.knobs.queue:
            return None
        completions = {str(x.card): x.completions for x in v.cards}
        return policy.queued(v, self.save.queue, completions, QUEUEABLE, c.BUILDS)


def visit_seen(visits: Sequence[VisitRecord], seen: int | None) -> int | None:
    """The index (1-based) of the visit a thing seen at `seen` was seen in, or None."""
    return next((v.index for v in visits if seen is not None and v.start <= seen <= v.end), None)
