"""A figure in a level's, upside's or chip's text is a slot fed by the served change_bp, never typed into the text
(api/CONTRACT.txt, "Text and numbers", {pct}): every served text holds exactly as many pct slots as its entry serves
changes, and the changes are the rules' own numbers."""
import re

import pytest

from ashfall_app.api.content_models import Content
from ashfall_app.api.service import Game
from ashfall_app.opening.entries import ModifierEntry
from ashfall_app.opening.schema import load_opening
from ashfall_app.saves.ruleset import ruleset
from tests.opening.edited import Edit, edited, same

SLOTS = ("{pct}", "{pct_b}")


@pytest.fixture(scope="module")
def content() -> Content:
    o = load_opening()
    return Game(o, ruleset(o, "dev", 1)).content()


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
    return {c.card: c.change_bp for c in Game(o, ruleset(o, "dev", 1)).content().card_infos}[card]


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


def test_each_staked_sink_is_served_the_entries_it_holds_at_its_full_share(content: Content):
    """The watch's larder and gap entries, one figure."""
    cards = {c.card: c.change_bp for c in content.card_infos}
    assert [cards[c] for c in ("n1_watch", "n2_watch", "n4_watch", "n6_watch")] == [[5000]] * 4


def test_every_track_card_is_served_what_its_reach_pays(content: Content):
    """The hands' and each person's: the one figure every reach of track laid pays the hunt, which a later chapter
    declares."""
    cards = {c.card: c.change_bp for c in content.card_infos}
    track = sorted(c for c in cards if c.endswith("field_track"))
    assert len(track) == 8 and [cards[c] for c in track] == [[1000]] * 8


def test_a_card_that_holds_entries_serves_them_and_the_rest_serve_none(content: Content):
    watch = next(c for c in content.card_infos if c.card == "n4_watch")
    assert [(k.side, k.lane, k.amount_bp, k.slot) for k in watch.kept] == [("larder", None, 5000, 0), ("gap", None, 5000, 0)]
    assert 5000 in watch.change_bp
    holders = [c for c in content.card_infos if c.kept]
    assert all((k.side is None) != (k.lane is None) for c in holders for k in c.kept)
    assert [c.card for c in content.card_infos if not c.kept and c.card == "stew"] == ["stew"]


def test_a_kept_entry_names_its_slot_and_an_equal_unscaled_change_has_another(content: Content):
    for c in (c for c in content.card_infos if c.kept):
        assert all(c.change_bp[k.slot] == k.amount_bp for k in c.kept), c.card
    o = load_opening()
    same_amount = ModifierEntry(target="rate", id="x", flow="make", store="x", kind="add_bp", amount_bp=5000, source="x")
    cards = [c.model_copy(update={"outcome": c.outcome.model_copy(update={"modifiers": [same_amount]})}) if c.id == "n4_watch" else c
             for c in o.cards]
    served = Game(o.model_copy(update={"cards": cards}), ruleset(o, "dev", 1)).content()
    watch = next(c for c in served.card_infos if c.card == "n4_watch")
    assert (watch.change_bp, [k.slot for k in watch.kept]) == ([5000, 5000], [1, 1])
