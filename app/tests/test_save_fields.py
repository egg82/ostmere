"""`Save` (engine/state.py) has the fields in tests/held/save_fields.json and no more: a new engine part adds its own
state type, never a field on `Save` (docs/systems.md, "The engine"). The held fields are the ones that predate the rule;
the list only shrinks. `python tests/test_save_fields.py --write` (from app/) rewrites it after a field is removed;
never run it to let a field through."""
import dataclasses
import sys
from pathlib import Path

from ashfall_app.engine.state import Save
from held_ledger import Ledger, dump, load, problems, tally, total

HELD = Path(__file__).resolve().parent / "held/save_fields.json"


def ledger(names: list[str]) -> Ledger:
    return tally([("Save", n) for n in names])


def save_fields() -> list[str]:
    return [f.name for f in dataclasses.fields(Save)]


def wrong(names: list[str], held: Ledger) -> list[str]:
    return problems(
        ledger(names), held,
        "a new field on Save: give the engine part its own state type (docs/systems.md, \"The engine\")",
        "python tests/test_save_fields.py --write",
    )


def test_the_gate_sees_the_fields():
    names = save_fields()
    assert {"time", "stores", "ended_at"} <= set(names), f"the scan found only {names}: it would pass on nothing"


def test_save_has_only_the_held_fields():
    found = wrong(save_fields(), load(HELD))
    assert not found, "\n".join(found)


def test_a_new_field_and_a_removed_one_are_told_apart():
    held = ledger(["time", "stores"])
    assert wrong(["time", "stores"], held) == []
    added = wrong(["time", "stores", "weather"], held)
    assert len(added) == 1 and "weather" in added[0] and "own state type" in added[0]
    removed = wrong(["time"], held)
    assert len(removed) == 1 and "stores" in removed[0] and "stale, lower it" in removed[0]


if __name__ == "__main__":
    if sys.argv[1:] == ["--write"]:
        led = ledger(save_fields())
        HELD.write_text(dump(led))
        print(f"wrote {HELD.name}: {total(led)} fields held")
