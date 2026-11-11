"""tools/tester_sheet.py on rows captured from the prod database (ids anonymised): `a` is a whole log with contexts and a long
idle gap, `b` a log cut to its first 20 and last 4 decisions. Prod accounts hold no lesson_ends yet, so the presentation
with them is authored here from the LessonEnd model."""
import json
from pathlib import Path
from typing import Any

from tools.tester_sheet import NOT_RECORDED, sheet

FIXTURES = Path(__file__).parent / "fixtures"


def _doc(name: str) -> dict[str, Any]:
    return json.loads((FIXTURES / name).read_text())


def test_whole_log_gives_first_tap_idle_gap_and_its_screen_proxy():
    text = sheet(_doc("tester_sheet_a.json"))
    assert "time to first tap: 5s after the game began (decision 1, game time 4)" in text
    assert "first built mix (by the player or an accepted offer, not told apart): none yet" in text
    assert "first idle gap over 60s: 24h58m, after decision 4 (game time 21)" in text
    assert "last recorded action: tap_card (decision 15, game time 90014)" in text


def test_cut_log_that_starts_at_one_reads_its_firsts_and_unrecorded_rows_say_so():
    text = sheet(_doc("tester_sheet_b.json"))
    assert "older ones deleted" in text and "time to first tap: 5s" in text   # it starts at decision 1, so its firsts are real
    assert "first built mix (by the player or an accepted offer, not told apart): 3m57s after the game began (decision 18" in text
    assert "first built rule: 57m46s after the game began (decision 93" in text
    assert f"offers answered: {NOT_RECORDED}" in text and f"lessons ended: {NOT_RECORDED}" in text


def test_recorded_presentation_prints_counts_and_lesson_ends_not_zero():
    doc = _doc("tester_sheet_a.json")
    doc["presentation"] = {
        "mix_offered": ["gather"], "switch_offered": [], "mix_stopped": [], "lessons": ["mix", "rule"],
        "lesson_ends": [{"lesson": "mix", "skipped": True, "step": 2, "longest_wait_s": 41}]}
    text = sheet(doc)
    assert "mix_offered 1, switch_offered 0, mix_stopped 0" in text
    assert "lesson mix: skipped at step 2, longest wait 41s" in text
    assert f"lesson rule: ended, step and wait {NOT_RECORDED}" in text


def test_log_whose_start_was_deleted_claims_no_first():
    doc = _doc("tester_sheet_b.json")
    doc["decisions"] = [d for d in doc["decisions"] if d["n"] > 1]
    assert f"time to first tap: {NOT_RECORDED}" in sheet(doc)


def test_idle_gap_names_the_context_of_the_decision_before_it():
    doc = _doc("tester_sheet_a.json")
    doc["decisions"][3].update(mix="wood", chips=["hungry"])   # authored: prod rows before decision 5 predate contexts
    assert "on screen (PROXY: the context of that last decision, not a screen capture): the mix running wood, chips shown hungry" in sheet(doc)
