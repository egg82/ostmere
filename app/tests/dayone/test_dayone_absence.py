"""The absence ladder (absence.py): leave a played route's visit and come back after 1 h to 7 days; the return's
arrivals are counted by kind and timed by the page's arrival queue (arrival_rules.py). What it finds is a report
(python -m tests.dayone.report --absence); the checks here are that it counts something, that a longer absence never
holds fewer arrivals than a shorter one from the same point, and the queue's cap arithmetic."""
import json
from dataclasses import replace
from pathlib import Path
from typing import Any

import pytest

from ashfall_app.engine import FeatureId, LedgerLine, Line, LineKey, StoreId, Unlock, UnlockKind, View, new_save, segment, view
from tests.dayone import absence
from tests.dayone import arrival_rules as ar
from tests.dayone.conftest import PLAY_TIMEOUT_S
from tests.opening.playthrough import opening, opening_rules

Run = list[absence.Point]
CASES = Path(__file__).resolve().parents[2] / "client" / "fixtures" / "arrival_cases.json"
"""The page's rules as cases, shared with client/test/arrivalcases.test.ts: either side drifting fails its own test."""


def cases(name: str) -> list[dict[str, Any]]:
    data: dict[str, list[dict[str, Any]]] = json.loads(CASES.read_text())
    found = data[name]
    assert len(found) >= 5
    return found


@pytest.mark.playthrough
@pytest.mark.timeout(PLAY_TIMEOUT_S)
def test_every_leave_point_holds_something_by_kind_and_takes_time_to_reveal(absence_run: Run):
    assert len(absence_run) == 3
    assert all(r.total > 0 and r.reveal_ms > 0 for pt in absence_run for r in pt.returns[1:])
    assert any(r.counts["line"] > 0 for pt in absence_run for r in pt.returns)
    assert any(r.counts[k] > 0 for pt in absence_run for r in pt.returns for k in absence.KINDS if k != "line")


@pytest.mark.playthrough
@pytest.mark.timeout(PLAY_TIMEOUT_S)
def test_a_longer_absence_never_holds_fewer_arrivals(absence_run: Run):
    assert absence.never_fewer(absence_run) == []


@pytest.mark.playthrough
@pytest.mark.timeout(PLAY_TIMEOUT_S)
def test_a_planted_shrinking_ladder_is_found(absence_run: Run):
    pt = absence_run[0]
    swapped = replace(pt, returns=tuple(reversed(pt.returns)))
    assert pt.returns[0].total != pt.returns[-1].total
    assert len(absence.never_fewer([swapped])) >= 1


def test_the_pace_is_read_from_the_page_source():
    p = ar.pace()
    assert 0 < p.min_gap_ms < p.max_gap_ms < p.cap_ms
    assert p.wpm > 0 and p.floor_ms > 0
    assert ar.reading_ms("one two three") == p.floor_ms
    assert ar.reading_ms("word " * 1000) > p.floor_ms


def test_the_cap_squeezes_only_a_batch_too_long_for_it():
    p = ar.pace()
    fits = p.cap_ms // p.min_gap_ms + 1
    assert ar.squeezed(fits) == 0 and ar.squeezed(fits + 1) == 1 and ar.squeezed(fits + 10) == 10
    assert ar.reveal_ms([], fits + 10) == p.cap_ms
    assert ar.reveal_ms([p.floor_ms, p.floor_ms], 0) == 2 * p.floor_ms
    assert ar.reveal_ms([p.floor_ms], 3) == p.floor_ms + round(2 * ar.gap_ms(3))


def test_the_band_placement_matches_the_shared_cases():
    for c in cases("away_lines"):
        chips = {k: (ch["chip"], k == ch["on"]) for ch in c["chips"] for k in (ch["on"], ch["off"]) if k is not None}
        repeats = {x["card"] for x in (*c["cards"], *c["cards_before"]) if x["cap"] is None}
        got = absence.place(chips, [(k, card) for k, card in c["lines"]], set(c["shown"]), repeats)
        assert got == c["expect"], c["name"]


def test_the_reveal_schedule_matches_the_shared_cases():
    for c in cases("schedule"):
        got = ar.reveal_ms(c["holds_ms"], c["rest"], c.get("ledger_ms", []), c.get("behind", 0))
        assert got == c["end_ms"], c["name"]


def _with_line(red: bool) -> tuple[View, View, str]:
    """The opening's start view, then the same with the ledger on and one store's line drawn: the first order card
    offered from the start, its line red or not."""
    card = next(c for c in opening().order_cards if c.chip is None and c.offered_after is None and c.tap_card)
    rules = opening_rules()
    save = new_save(rules)
    before = view(save, rules)
    store = StoreId(card.store)
    line = LedgerLine(store=store, segment=segment(save, rules, store), net_per_hour=-1, contributions=(), empties_at=None,
                      fills_at=None, falling=red, covered=False, starved=False, cap=1)
    unlocked = (*before.unlocked, Unlock(UnlockKind.FEATURE, FeatureId("ledger")), Unlock(UnlockKind.STORE, store))
    return before, replace(before, ledger=(line,), unlocked=unlocked), card.store


def test_a_returning_ledger_line_holds_for_its_reading_and_a_red_one_for_its_offer_too():
    p = ar.pace()
    before, white, _ = _with_line(red=False)
    _, red, _ = _with_line(red=True)
    assert absence.ledger_holds(before, white) == [p.floor_ms]
    assert absence.ledger_holds(before, red)[0] > p.floor_ms
    no_ledger = tuple(u for u in red.unlocked if u.kind is not UnlockKind.FEATURE)
    assert absence.ledger_holds(before, replace(red, unlocked=no_ledger)) == []   # the ledger off: no line drawn


def test_the_strip_kinds_are_read_from_the_page_source():
    kinds = ar.strip_kinds()
    assert "story" in kinds
    assert not kinds & {"find", "level", "fight", "rule", "talk"}


def test_a_return_counts_only_the_lines_the_strip_plays():
    """A find's line placed on the band is the chronicle's alone, so it is no band line and holds no reading time."""
    rules, o = opening_rules(), opening()
    v = view(new_save(rules), rules)
    story = next(k for k, kind in o.line_kinds.items() if kind == "story")
    find = next(k for k, kind in o.line_kinds.items() if kind == "find")
    lines = (Line(0, 0, LineKey(story)), Line(0, 1, LineKey(find)))
    assert [str(ln.key) for ln in absence.band_lines(rules, lines, v, v, o.line_kinds)] == [story]
    counted, holds = absence.counts(rules, v, v, lines)
    assert counted["line"] == 1 and len(holds) == 1
