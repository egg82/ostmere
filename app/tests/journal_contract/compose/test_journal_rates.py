"""Each rate's observed share over many save ids sits within a binomial bound of the rate: the write roll against
`care * diligence` (11), late additions (16) and misremembering (17). The bound is six standard deviations, so a
correct composer fails one example in about 10**9; a rate applied as `1 - rate`, a roll that ignores the save, or a
non-strict comparison skewed to a constant shows plainly."""
import math
from dataclasses import replace

from hypothesis import given, strategies as st

from ashfall_app.saves.journal import Fade
from journal_gen import examples
from journal_world import PLAIN, QUIET, beat, compose_next, compose_span, note, routine, row, shows, slots_of

SAVES = 300
rates = st.floats(0.05, 0.95)
offsets = st.integers(0, 2**40)


def _within_bound(hits: int, rate: float) -> bool:
    return abs(hits / SAVES - rate) <= 6 * math.sqrt(rate * (1 - rate) / SAVES)


@examples(5)
@given(care=rates, offset=offsets)
def test_the_write_share_is_care_times_diligence(care: float, offset: int):
    """Statement 11: a told routine with care `c` and diligence 1 is written on about `c` of save ids."""
    r = routine("r")
    rows = (row(0, note(r, "first")),)
    habits = replace(PLAIN, routine=Fade(care, 1.0))
    lines = [shows(r, 0), shows(r, 1)]
    hits = sum(bool(compose_next(offset + i, rows, lines, [r], habits).notes) for i in range(SAVES))
    assert _within_bound(hits, care), (hits, care)


@examples(5)
@given(rate=rates, offset=offsets)
def test_the_late_share_is_late_rate(rate: float, offset: int):
    """Statement 16: a subject written on day 0, with day 1 written for another reason, gets its late addition on about
    `late_rate` of save ids."""
    lately, filler = routine("lately", late=1), beat("filler", repeat=1)
    lines = [shows(lately, 0), shows(filler, 0), shows(filler, 1)]
    habits = replace(QUIET, late_rate=rate)
    hits = sum(slots_of(compose_span(offset + i, 2, lines, [lately, filler], habits)[1], lately) == ["late"]
               for i in range(SAVES))
    assert _within_bound(hits, rate), (hits, rate)


@examples(5)
@given(rate=rates, offset=offsets)
def test_the_misremember_share_is_misremember_rate(rate: float, offset: int):
    """Statement 17: a first telling is misremembered on about `misremember_rate` of save ids."""
    wrong = routine("wrong", misremember=1)
    habits = replace(QUIET, misremember_rate=rate)
    hits = sum(slots_of(compose_next(offset + i, (), [shows(wrong, 0)], [wrong], habits), wrong) == ["misremember"]
               for i in range(SAVES))
    assert _within_bound(hits, rate), (hits, rate)
