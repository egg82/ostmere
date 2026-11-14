"""merge_presentation (accounts/presentation.py): a presentation only grows."""
import json

from ashfall_app.accounts.body_limit import MAX_BODY_BYTES
from ashfall_app.accounts.interface import Json
from ashfall_app.accounts.presentation import merge_presentation

END = {"lesson": "l", "skipped": True, "step": 2, "longest_wait_s": 5}


def test_a_flag_once_set_stays_set_and_a_list_keeps_what_it_had():
    got = merge_presentation({"rule_seen": True, "lessons": ["a"]}, {"rule_seen": False, "lessons": ["b", "a"]}, 512)
    assert got == {"rule_seen": True, "lessons": ["a", "b"]}


def test_an_object_list_names_its_entries_by_lesson_or_by_value():
    got = merge_presentation({"lesson_ends": [END], "switch_offered": [{"chip": "c", "mix_id": "m"}]},
                             {"lesson_ends": [{**END, "skipped": False}], "switch_offered": [{"chip": "c", "mix_id": "m"}]}, 512)
    assert got == {"lesson_ends": [END], "switch_offered": [{"chip": "c", "mix_id": "m"}]}


def test_a_list_stops_at_the_cap_and_the_kept_entries_stay():
    got = merge_presentation({"lessons": ["a", "b"]}, {"lessons": ["c", "d"]}, 3)
    assert got == {"lessons": ["a", "b", "c"]}
    assert merge_presentation({}, {"lessons": [str(n) for n in range(9)]}, 4) == {"lessons": ["0", "1", "2", "3"]}


def test_the_stored_presentation_stops_growing_at_a_byte_budget():
    stored: Json = {"ledger_lines": [f"{n:064}" for n in range(512)], "mix_offered": [f"{n:064}" for n in range(512)],
              "mix_stopped": [f"{n:064}" for n in range(512)], "lessons": ["a"]}
    wide = [{"chip": "c" * 64, "mix_id": (str(n) + "\U0001F600" * 64)[:64]} for n in range(512)]
    got = merge_presentation(stored, {"switch_offered": wide}, 512)
    written = json.dumps(got, separators=(",", ":"), ensure_ascii=False)
    assert len(written.encode()) <= MAX_BODY_BYTES
    assert 0 < len(json.loads(written)["switch_offered"]) < 512
    assert got["lessons"] == ["a"], "nothing is added once the budget is spent"


def test_what_is_stored_stays_when_it_is_over_the_budget():
    stored: Json = {"lessons": [str(n) * 60 for n in range(10)], "ledger_lines": ["x"] * 3}
    got = merge_presentation(stored, {"lessons": ["new"], "ledger_lines": ["y"]}, 512, 100)
    assert got == stored


def chapter(left: int, stores: int = 1) -> Json:
    return {"left": left, "back": left + 1800, "stores": [{"id": "wood", "was": 0, "now": n} for n in range(stores)]}


def test_the_chapter_is_the_latest_return_s_and_a_missing_one_never_replaces_it():
    first = merge_presentation({}, {"chapter": chapter(10)}, 512)
    assert first == {"chapter": chapter(10)}
    assert merge_presentation(first, {"chapter": chapter(20)}, 512) == {"chapter": chapter(20)}
    assert merge_presentation(first, {"chapter": chapter(5)}, 512) == first, "a stale page's older chapter stays out"
    assert merge_presentation(first, {"chapter": chapter(10, 2)}, 512) == first, "the same return is kept as first written"
    assert merge_presentation(first, {"chapter": None, "lessons": ["a"]}, 512) == {**first, "lessons": ["a"]}


def test_a_chapter_past_the_byte_budget_is_not_kept():
    budget = len(json.dumps({"chapter": chapter(10)}, separators=(",", ":")).encode()) + 40
    kept = merge_presentation({}, {"chapter": chapter(10)}, 512, max_bytes=budget)
    assert kept == {"chapter": chapter(10)}   # control: it fits
    assert merge_presentation(kept, {"chapter": chapter(20, 30)}, 512, max_bytes=budget) == kept
