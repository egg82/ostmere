"""Who makes each store, by band of game days (the makers readout, tests/makers/readout.py). Pure: the caller supplies
the samples."""
from collections import defaultdict
from collections.abc import Mapping, Sequence

from tests.ladder.sources import BANDS
from tests.ladder.shares import DAY_S

Band = tuple[int, int | None]
Made = Mapping[str, Mapping[str, float]]
"""Items per hour by store, then by the runner making it."""


def band_of(t: int) -> Band:
    day = t // DAY_S + 1
    return next(b for b in BANDS if day >= b[0] and (b[1] is None or day <= b[1]))


def made_by_band(samples: Sequence[tuple[int, Made]], step_h: int) -> dict[str, dict[Band, dict[str, float]]]:
    """Items made per store over each band holding a sample of it, by maker: each sample's rate held for `step_h` game
    hours. A band where a store was made in nothing is absent."""
    sums: dict[str, dict[Band, dict[str, float]]] = defaultdict(lambda: defaultdict(dict))
    for t, by_store in samples:
        band = band_of(t)
        for store, makers in by_store.items():
            into = sums[store][band]
            for maker, rate in makers.items():
                into[maker] = into.get(maker, 0.0) + rate * step_h
    return {store: {band: {m: v for m, v in sorted(got.items()) if v > 0}
                    for band, got in bands.items() if sum(got.values()) > 0}
            for store, bands in sums.items()}


def at_cap_share(samples: Sequence[tuple[int, Mapping[str, bool]]]) -> dict[str, dict[Band, float]]:
    """The percent of each band's samples a store stood at its cap in."""
    count: dict[str, dict[Band, list[int]]] = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    for t, full in samples:
        band = band_of(t)
        for store, at in full.items():
            c = count[store][band]
            c[0] += at
            c[1] += 1
    return {store: {band: 100 * c[0] / c[1] for band, c in bands.items()} for store, bands in count.items()}


def merged(*parts: Mapping[str, Mapping[Band, Mapping[str, float]]]) -> dict[str, dict[Band, dict[str, float]]]:
    """Items made by store, band and maker from several readings of different makers, summed where they share one."""
    out: dict[str, dict[Band, dict[str, float]]] = defaultdict(lambda: defaultdict(dict))
    for part in parts:
        for store, bands in part.items():
            for band, makers in bands.items():
                into = out[store][band]
                for maker, v in makers.items():
                    into[maker] = into.get(maker, 0.0) + v
    return {store: {band: dict(sorted(m.items())) for band, m in bands.items()} for store, bands in out.items()}


def band_spans(end: int) -> list[tuple[Band, int, int]]:
    """Each band with a game day before `end` (seconds) and its span in seconds, the last cut at `end`."""
    return [(b, (b[0] - 1) * DAY_S, end if b[1] is None else min(end, b[1] * DAY_S))
            for b in BANDS if (b[0] - 1) * DAY_S < end]
