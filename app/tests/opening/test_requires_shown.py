"""Every require that can refuse a card's tap is drawn on the card's face before the tap (docs/decisions/principles.md,
"Progress is stated, never hinted": a gate on progress may not hide). The check is opening/face_checks.py, run over
the shipped chapters and the ones in writing. The requires it cannot yet see drawn are held in
tests/held/card_faces.json, per card and require, and the list only shrinks: `python -m tests.opening.test_requires_shown
--write` (from app/) lowers it once one is drawn; never run it to let a new one through."""
import sys
from pathlib import Path

import pytest

from ashfall_app.opening.entries import ConditionEntry
from ashfall_app.opening.face_checks import check_clocks, undrawn
from ashfall_app.opening.schema import CHAPTERS, IN_WRITING, Opening, load_opening
from tests.held_ledger import Ledger, dump, load, problems, tally, total

HELD = Path(__file__).resolve().parents[1] / "held/card_faces.json"


def full() -> Opening:
    return load_opening(chapters=(*CHAPTERS, *IN_WRITING))


def ledger(o: Opening) -> Ledger:
    return tally([(card, f"{kind}:{id_}") for card, kind, id_ in undrawn(o)])


def wrong(o: Opening, held: Ledger) -> list[str]:
    return problems(ledger(o), held, "draw it on the card's face (opening/face_checks.py)",
                    "python -m tests.opening.test_requires_shown --write")


@pytest.fixture(scope="module")
def content() -> Opening:
    return full()


def test_every_tappable_card_draws_its_requires(content: Opening):
    assert sum(len(c.requires) for c in content.cards) > 20, "checked almost no requires: the check is blind"
    found = wrong(content, load(HELD))
    assert not found, "\n".join(found)


def planted(o: Opening, card: str, *requires: ConditionEntry) -> Opening:
    cards = [c.model_copy(update={"requires": [*c.requires, *requires]}) if c.id == card else c for c in o.cards]
    return o.model_copy(update={"cards": cards})


@pytest.mark.parametrize(("require", "kind"), [
    (ConditionEntry(test="at_least", subject_kind="unlocked", unlock_kind="feature", id="night", value=1), "unlocked"),
    (ConditionEntry(test="at_most", subject_kind="store", id="stones", value=3), "store"),
    (ConditionEntry(test="at_least", subject_kind="store", id="b7_clock", value=1), "store"),
    (ConditionEntry(test="after_time", value=60), "after_time"),
])
def test_a_require_the_face_cannot_draw_is_named(content: Opening, require: ConditionEntry, kind: str):
    assert ("take_stock", kind, require.id or "") in undrawn(planted(content, "take_stock", require))


def test_a_skill_level_a_step_a_tally_and_a_time_of_day_are_drawn(content: Opening):
    o = planted(content, "take_stock", ConditionEntry(test="at_least", subject_kind="skill_level", id="foraging", value=9),
                ConditionEntry(test="at_least", subject_kind="card_count", id="strike_fire", value=1),
                ConditionEntry(test="at_least", subject_kind="store", id="arrivals", value=1),
                ConditionEntry(test="at_least", subject_kind="store", id="night_5", value=5))
    assert not [x for x in undrawn(o) if x[0] == "take_stock"]


def test_a_clock_with_no_time_of_day_is_not(content: Opening):
    stores = [s.model_copy(update={"clock": None}) if s.id == "night_5" else s for s in content.stores]
    assert ("sit_up_5", "store", "night_5") in undrawn(content.model_copy(update={"stores": stores}))


@pytest.mark.parametrize(("store", "says"), [("stones", "shown to the player"), ("bay", "not made by standing actions")])
def test_a_time_of_day_on_a_store_that_is_no_clock_fails_the_load(content: Opening, store: str, says: str):
    stores = [s.model_copy(update={"clock": "night"}) if s.id == store else s for s in content.stores]
    with pytest.raises(ValueError, match=f"store {store}: .*{says}"):
        check_clocks(content.model_copy(update={"stores": stores}))


def test_a_clock_is_a_countdown_only_alone_and_once_its_maker_runs(content: Opening):
    assert [r.id for r in next(c for c in content.cards if c.id == "sit_last_night").requires] == ["drift_clock"], \
        "the control card no longer waits on its clock alone"
    assert not [x for x in undrawn(content) if x[0] == "sit_last_night"]
    o = planted(content, "sit_last_night", ConditionEntry(test="at_least", subject_kind="skill_level", id="foraging", value=2))
    assert ("sit_last_night", "store", "drift_clock") in undrawn(o)


def test_a_ruled_lanes_cards_are_not_checked(content: Opening):
    ruled = {x.id for x in content.lanes if x.ruled}
    tasks = [c.id for c in content.cards if c.lane in ruled and c.requires]
    assert tasks, "no ruled lane's card has a require: the control is blind"
    assert not [x for x in undrawn(content) if x[0] in tasks]


def test_a_new_undrawn_require_and_a_drawn_held_one_are_told_apart(content: Opening):
    held = ledger(content)
    assert wrong(content, held) == []
    new = wrong(planted(content, "take_stock", ConditionEntry(test="after_time", value=60)), held)
    assert len(new) == 1 and "take_stock after_time:" in new[0] and "draw it" in new[0]
    stale = wrong(content, {**held, "take_stock": {"store:roots": 1}})
    assert len(stale) == 1 and "stale, lower it" in stale[0]


if __name__ == "__main__":
    if sys.argv[1:] == ["--write"]:
        led = ledger(full())
        HELD.write_text(dump(led))
        print(f"wrote {HELD.name}: {total(led)} requires held")
