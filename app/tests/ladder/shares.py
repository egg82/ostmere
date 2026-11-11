"""Each card's share of the running mixes by game day, and the cards whose share went to zero and stayed there (the ladder
readout, tests/ladder/readout.py; docs/decisions.md, "Each new layer reworks the old ones"). Pure: the caller supplies
the samples."""
from collections.abc import Mapping, Sequence

DAY_S = 24 * 3600
BP = 10_000


def day_averages(samples: Sequence[tuple[int, Mapping[str, int]]], days: int) -> list[dict[str, float]]:
    """The mean share in percent of each card over each of `days` calendar days from instant 0, from samples of
    (instant, share in basis points by card). A card a sample omits counts 0 there. A day holding no sample is a
    ValueError: a gap in the probe, not a quiet day."""
    out: list[dict[str, float]] = []
    for day in range(days):
        inside = [shares for t, shares in samples if day * DAY_S <= t < (day + 1) * DAY_S]
        if not inside:
            raise ValueError(f"no sample falls on day {day + 1}")
        cards = {c for shares in inside for c in shares}
        out.append({c: sum(s.get(c, 0) for s in inside) / len(inside) * 100 / BP for c in sorted(cards)})
    return out


def gone_quiet(days: Sequence[Mapping[str, float]]) -> dict[str, int]:
    """Each card that held a share on some day and none on every day after: the 1-based day its run of zeros began.
    A card that never held a share, or still holds one on the last day, is absent."""
    last = {c: i for i, day in enumerate(days) for c, share in day.items() if share > 0}
    return {c: i + 2 for c, i in last.items() if i < len(days) - 1}
