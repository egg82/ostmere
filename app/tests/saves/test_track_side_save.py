"""A save from the release whose track held the hands' side while it ran (captured/f9-track-side.json: the engine's own
encoding, week one's typical route on game day six, the track in the hands' mix and the hunt open, on the rules the
week's plays load, the chapters in writing merged) loads under today's rules: the side entry is gone from the hunt's
strength, the track laid starts empty and in view, the mix is as saved, and a day on fills the track laid by the
track's own runs (decisions/pacing.md, "A sink shows what it buys")."""
import json
from functools import cache
from pathlib import Path
from typing import Any

from ashfall_app.engine import (
    QUANTITY_SCALE as Q, CardId, Rules, Save, SideId, SideStrength, StoreId, Unlock, UnlockKind, advance,
    explain_strength, rebase, segment, view,
)
from tests.daythree.content import rules3

CAPTURED = Path(__file__).resolve().parent / "captured" / "f9-track-side.json"
TRACK, LAID = CardId("field_track"), StoreId("track_laid")
DAY_S = 86_400


def today() -> Rules:
    return rules3()


@cache
def loaded() -> Save:
    return rebase(CAPTURED.read_text().strip(), today())


def completions(save: Save) -> int:
    return next(c.completions for c in view(save, today()).cards if c.card == TRACK)


def laid(save: Save) -> int:
    return segment(save, today(), LAID).start_value


def test_the_captured_save_ran_the_track_with_the_hunt_open():
    raw: dict[str, Any] = json.loads(CAPTURED.read_text())["save"]
    unlocked = {(u["kind"]["v"], u["id"]) for u in raw["unlocked"]}
    assert ("card", "hunt_wolf") in unlocked and ("store", "track_laid") not in unlocked


def test_it_loads_with_the_mix_as_saved_and_the_side_entry_gone():
    raw: dict[str, Any] = json.loads(CAPTURED.read_text())["save"]
    save = loaded()
    assert save.time == raw["time"] and len(save.mixes) == len(raw["mixes"])
    sources = {str(m.source) for m in explain_strength(save, today(), SideStrength(SideId("hands"))).adds}
    assert sources and "held:field_track" not in sources


def test_the_track_laid_starts_empty_and_in_view():
    save = loaded()
    assert laid(save) == 0
    assert Unlock(UnlockKind.STORE, LAID) in advance(save, today(), save.time + 1).unlocked


def test_a_day_on_the_track_laid_is_the_tracks_runs():
    """Only the hands' card is in a mix: the people's track cards arrive with this release, unmixed."""
    save = loaded()
    later = advance(save, today(), save.time + DAY_S)
    runs = completions(later) - completions(save)
    assert runs > 0
    assert abs(laid(later) / Q - runs) < 1   # paid as the work is done: the bar's progress at either end
