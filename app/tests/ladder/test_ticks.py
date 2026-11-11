"""at_time on stand-in saves: a probe runs on from the nearest save below it, whether from the play or an earlier probe,
and a save at an instant the play has is returned as it is."""
from dataclasses import dataclass

from tests.ladder.ticks import at_time


@dataclass(frozen=True)
class Stamp:
    time: int


def test_each_probe_runs_on_from_the_nearest_save_below_it() -> None:
    calls: list[tuple[int, int]] = []

    def run_on(s: Stamp, t: int) -> Stamp:
        calls.append((s.time, t))
        return Stamp(t)

    save_at = at_time([Stamp(0), Stamp(1000)], run_on)
    save_at(600)
    save_at(300)
    save_at(900)
    assert save_at(1000) == Stamp(1000)
    assert save_at(600) == Stamp(600)
    assert calls == [(0, 600), (0, 300), (600, 900)]
