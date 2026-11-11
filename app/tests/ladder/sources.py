"""Which sources a skill's XP comes from, by band of game days (the ladder readout, tests/ladder/readout.py). Pure: the
caller supplies the samples."""
from collections import defaultdict
from collections.abc import Mapping, Sequence

from tests.ladder.shares import DAY_S

BANDS: tuple[tuple[int, int | None], ...] = ((1, 2), (3, 5), (6, 9), (10, None))
"""Inclusive 1-based game days; the last band has no end."""


def band_label(band: tuple[int, int | None]) -> str:
    first, last = band
    return f"{first}+" if last is None else f"{first}" if first == last else f"{first}-{last}"


def band_shares(samples: Sequence[tuple[int, Mapping[str, Mapping[str, int]]]]
                ) -> dict[str, dict[tuple[int, int | None], dict[str, float]]]:
    """Each skill's XP split by source, in percent, over each band holding a sample of it: the sum of a source's XP rate
    over the band's samples (instant, XP per hour by skill then source) against the skill's. A band where the skill
    earned nothing is absent."""
    sums: dict[str, dict[tuple[int, int | None], dict[str, int]]] = defaultdict(lambda: defaultdict(dict))
    for t, by_skill in samples:
        day = t // DAY_S + 1
        band = next(b for b in BANDS if day >= b[0] and (b[1] is None or day <= b[1]))
        for skill, sources in by_skill.items():
            into = sums[skill][band]
            for source, rate in sources.items():
                into[source] = into.get(source, 0) + rate
    return {skill: {band: {src: 100 * v / total for src, v in sorted(got.items()) if v > 0}
                    for band, got in bands.items() if (total := sum(got.values())) > 0}
            for skill, bands in sums.items()}
