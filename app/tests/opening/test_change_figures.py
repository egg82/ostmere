"""A figure in a level's, upside's or chip's text is a slot fed by the served change_bp, never typed into the text
(api/CONTRACT.txt, "Text and numbers", {pct}): every served text holds exactly as many pct slots as its entry serves
changes, and the changes are the rules' own numbers."""
import re

import pytest

from ashfall_app.api.content_models import Content
from ashfall_app.api.service import Game
from ashfall_app.opening.schema import load_opening
from ashfall_app.opening.renames import load_renames
from ashfall_app.saves.ruleset import ruleset
from tests.opening.edited import Edit, edited, same

SLOTS = ("{pct}", "{pct_b}")


@pytest.fixture(scope="module")
def content() -> Content:
    o = load_opening()
    return Game(o, ruleset(o, load_renames(), "dev", 1)).content()


def worded(content: Content) -> list[tuple[str, str, list[int]]]:
    """Every (where, text key, served changes) the page fills pct slots for. A camp level that serves from and to may
    word them instead of its changes, so it is held to the slots it has, not to all it could."""
    out = [(f"skill {s.skill} {lv.level}", lv.pays_key, lv.change_bp) for s in content.skill_infos for lv in s.levels]
    out += [(f"camp level at {lv.at}", lv.pays_key, lv.change_bp) for lv in (content.camp.camp_levels if content.camp else [])
            if lv.pays_from is None]
    out += [(f"card {c.card}", c.upside_key, c.change_bp) for c in content.card_infos if c.upside_key]
    out += [(f"chip {c.chip}", c.cost_key, c.change_bp) for c in content.chip_infos if c.cost_key]
    return out


def slot_mismatches(content: Content, texts: dict[str, str] | None = None) -> list[str]:
    text = texts or {t.key: t.text for t in content.text_entries}
    bad: list[str] = []
    for where, key, changes in worded(content):
        held = [s for s in SLOTS if s in text[key]]
        if held != list(SLOTS[:len(changes[:2])]):
            bad.append(f"{where} ({key}): text has {held}, served {len(changes)} change(s)")
    return bad


def test_every_text_holds_a_pct_slot_for_each_change_it_is_served(content: Content):
    assert len(worded(content)) > 50
    assert slot_mismatches(content) == []


def test_a_text_with_a_slot_too_few_or_too_many_is_caught(content: Content):
    text = {t.key: t.text for t in content.text_entries}
    key = next(k for _, k, ch in worded(content) if len(ch) == 1)
    assert slot_mismatches(content, {**text, key: re.sub(r"\{pct\}", "", text[key])}) != []
    assert slot_mismatches(content, {**text, key: text[key] + " {pct_b}"}) != []


def test_the_served_changes_are_the_rules_numbers(content: Content):
    skills = {s.skill: {lv.level: lv.change_bp for lv in s.levels} for s in content.skill_infos}
    assert skills["woodcutting"][4] == [1000] and skills["cooking"][2] == [5000]
    assert skills["woodcutting"][3] == [] and skills["woodcutting"][6] == [1000]
    cards = {c.card: c.change_bp for c in content.card_infos}
    assert cards["build_larder"] == [10000, 20000] and cards["build_fireback"] == [-3333]
    assert {c.chip: c.change_bp for c in content.chip_infos}["tired"] == [-5000]


def test_a_camp_level_with_a_pct_slot_is_served_the_change(content: Content):
    text = {t.key: t.text for t in content.text_entries}
    levels = content.camp.camp_levels if content.camp else []
    slotted = [lv for lv in levels if "{pct}" in text[lv.pays_key]]
    assert slotted and all(lv.change_bp == [5000] for lv in slotted)
    assert all(lv.change_bp == [] for lv in levels if lv.held)


def served_card_changes(card: str, data: Edit = same) -> list[int]:
    o = edited(data=data)
    return {c.card: c.change_bp for c in Game(o, ruleset(o, load_renames(), "dev", 1)).content().card_infos}[card]


def test_a_staged_build_is_served_the_change_its_stages_outcome_carries():
    assert served_card_changes("palisade") == [5000]


def modifier_removed(part: str) -> str:
    """The palisade's stage outcome without its modifier."""
    return re.sub(r'outcome = \{ modifiers = \[\{ target = "side", id = "gap"[^\n]*\n', "", part)


def test_a_staged_build_with_no_modifier_is_served_none():
    assert served_card_changes("palisade", modifier_removed) == []


def test_a_plain_card_is_served_its_finish(content: Content):
    assert {c.card: c.change_bp for c in content.card_infos}["build_fireback"] == [-3333]


def test_a_card_holding_entries_while_it_runs_is_served_them_at_its_full_share(content: Content):
    """Its own card's, a town card's (expanded per lane) and one a later chapter's while_running table gives."""
    cards = {c.card: c.change_bp for c in content.card_infos}
    assert (cards["n2_guard"], cards["n7_guard"]) == ([15000], [15000])
    assert (cards["n5_watch"], cards["n1_watch"]) == ([5000], [5000])
