"""An offer answer's figures are served, never typed into its cost text (api/CONTRACT.txt, "OFFERS" and "Text and
numbers", {pct} {gain}): AnswerInfo.change_bp and AnswerInfo.gains are the answer's own modifiers and stores, and its
cost text holds a pct slot for each change and no gain slot beyond what is served."""
import re
from pathlib import Path

import pytest

from ashfall_app.api.content_models import AnswerInfo, Content
from ashfall_app.api.service import Game
from ashfall_app.engine import QUANTITY_SCALE
from ashfall_app.opening.schema import CHAPTERS, IN_WRITING, load_opening
from ashfall_app.saves.ruleset import ruleset
from tests.shipped_ruleset import ShippedRuleset

PCT = ("{pct}", "{pct_b}")
GAIN = ("{gain}", "{gain_b}")


def served(chapters: tuple[Path, ...]) -> Content:
    o = load_opening(chapters=chapters)
    return Game(o, ruleset(o, "dev", 1)).content()


@pytest.fixture(scope="module")
def content(shipped_ruleset: ShippedRuleset) -> Content:
    return shipped_ruleset.make_game(shipped_ruleset.opening, shipped_ruleset.rs).content()


@pytest.fixture(scope="module")
def in_writing(content: Content) -> Content:
    """With the chapters in writing merged: the shipped content itself while none is in writing."""
    return served((*CHAPTERS, *IN_WRITING)) if IN_WRITING else content


def answers(content: Content) -> dict[str, AnswerInfo]:
    return {a.answer: a for x in content.offer_infos for a in x.answers}


def mismatches(content: Content, texts: dict[str, str] | None = None) -> list[str]:
    text = texts or {t.key: t.text for t in content.text_entries}
    bad: list[str] = []
    for a in answers(content).values():
        pct = [s for s in PCT if s in text[a.cost_key]]
        if pct != list(PCT[:len(a.change_bp[:2])]):
            bad.append(f"{a.answer} ({a.cost_key}): text has {pct}, served {len(a.change_bp)} change(s)")
        gain = [s for s in GAIN if s in text[a.cost_key]]
        if len(gain) > len(a.gains[:2]) or gain != list(GAIN[:len(gain)]):
            bad.append(f"{a.answer} ({a.cost_key}): text has {gain}, served {len(a.gains)} gain(s)")
    return bad


def test_the_served_changes_and_gains_are_the_answers_own_numbers(content: Content, in_writing: Content):
    got = answers(in_writing)
    assert got["o_bank_hers"].change_bp == [-1000] and got["o_bank_his"].change_bp == [1000]
    assert got["o_deep_sink"].change_bp == [2500, -1000]
    assert [(g.store, g.quantity) for g in got["o_rack_down"].gains] == [("smoked", 6 * QUANTITY_SCALE)]
    assert got["o_deep_pace"].gains == []
    assert got["o_pair_room"].change_bp == [] and got["o_pair_room"].gains == []
    assert answers(content)["o_bank_hers"].change_bp == [-1000]


def test_every_cost_text_holds_a_pct_slot_for_each_change_it_is_served(content: Content):
    assert len(answers(content)) >= 10
    assert mismatches(content) == []


def test_a_text_with_a_slot_too_few_or_too_many_is_caught(content: Content):
    text = {t.key: t.text for t in content.text_entries}
    one = answers(content)["o_bank_hers"].cost_key
    assert mismatches(content, {**text, one: re.sub(r"\{pct\}", "", text[one])}) != []
    assert mismatches(content, {**text, one: text[one] + " {pct_b}"}) != []
    assert mismatches(content, {**text, one: text[one] + " {gain}"}) != []


HIDDEN = {
    "ask_wait", "b9_clock", "drift_clock", "drift_left", "e2_clock", "roof_ash", "wind_left",
    "guard_made", "night_12", "stranger_clock", "z1_clock",
    "bear_season", "dig_clock", "morning_13", "night_14",
    "clear_clock", "frost_left", "grow_left", "night_15", "rime", "roof_wind_left", "meals",
    "table_clock", "rows_black_left", "tear_left", "torn_clock",
    "b15_clock", "choir_clock", "starer_clock", "covers_torn", "b15_2h", "choir_6h", "starer_floor",
    "cut_night_clock", "b17_clock", "r2_clock", "b17_floor", "night_21", "fungus_stews", "beds_covered",
    "still_left", "thaw_left", "film", "still_clock", "pace_clock", "pace_3h", "still_30",
    "sorrel_clock", "sorrel_12h", "sorrel_16h", "cache_torn", "night_24",
}


def test_the_bookkeeping_stores_are_served_hidden_and_no_other(in_writing: Content):
    served_hidden = {s.store for s in in_writing.store_infos if s.hidden}
    assert served_hidden == HIDDEN
    assert {s.store for s in in_writing.store_infos} > HIDDEN


def test_no_answer_gain_is_a_hidden_store(in_writing: Content):
    hidden = {s.store for s in in_writing.store_infos if s.hidden}
    gains = [g.store for a in answers(in_writing).values() for g in a.gains]
    assert "smoked" in gains and "ask_wait" not in gains
    assert not hidden & set(gains)


def test_no_hidden_store_is_unlocked_so_none_has_a_ledger_line():
    """A store has a ledger line in the view only once something unlocks it as a store; the control is a store that is."""
    text = load_opening(chapters=(*CHAPTERS, *IN_WRITING)).model_dump_json()
    unlocked = set(re.findall(r'"unlock_kind":"store","id":"(\w+)"', text))
    assert unlocked
    assert not unlocked & HIDDEN
