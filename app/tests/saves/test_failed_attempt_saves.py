"""Saves written while a timed failed attempt ran (format 5; captured/ holds the engine's own encodings from then, one
on the rack, one on the hands with a mix yielded to it) load under today's engine: the attempt is gone, its lane free
and the mix running again; every other lane, store, skill and card is as the save had it (engine DESIGN.txt,
"Rebase", UPGRADES[5])."""
import json
from functools import cache
from pathlib import Path
from typing import Any

import pytest

from ashfall_app.engine import Rules, RunBy, advance, rebase, view
from ashfall_app.opening.renames import engine_renames, load_renames
from ashfall_app.opening.schema import DAY_ONE, load_opening, to_rules

CAPTURED = sorted((Path(__file__).resolve().parent / "captured").glob("f5-*.json"))
DAY_S = 86_400


@cache
def today() -> Rules:
    return to_rules(load_opening(chapters=(DAY_ONE,)))


def test_the_captured_saves_are_there_and_each_holds_a_failed_attempt():
    assert len(CAPTURED) == 2
    for path in CAPTURED:
        envelope: dict[str, Any] = json.loads(path.read_text())
        assert envelope["format"] == 5 and any(ls["failed"] for ls in envelope["save"]["lanes"])


@pytest.mark.parametrize("path", CAPTURED, ids=lambda p: p.stem)
def test_a_save_mid_failed_attempt_loads_with_that_lane_free_and_nothing_else_changed(path: Path):
    text = path.read_text().strip()
    raw: dict[str, Any] = json.loads(text)["save"]
    save = rebase(text, today(), engine_renames(load_renames()))
    was = {ls["lane"]: ls for ls in raw["lanes"]}
    for ls in save.lanes:
        assert ls.card == (None if was[ls.lane]["failed"] else was[ls.lane]["card"]), ls.lane
    assert save.time == raw["time"]
    saved = {st["store"]: st["segment"]["start_value"] for st in raw["stores"]}
    assert {d.id: saved.get(d.id, d.initial) for d in today().stores} == {
        st.store: st.segment.start_value for st in save.stores}
    assert {sk.skill: sk.xp.start_value for sk in save.skills} == {
        sk["skill"]: sk["xp"]["start_value"] for sk in raw["skills"]}
    assert [cs.card for cs in save.cards] == [cs["card"] for cs in raw["cards"]]
    assert save.active == raw["active"] and len(save.mixes) == len(raw["mixes"])
    if save.active is not None and was["hands"]["failed"]:
        assert any(cv.by is RunBy.MIX for cv in view(save, today()).cards)
    advance(save, today(), save.time + DAY_S)
