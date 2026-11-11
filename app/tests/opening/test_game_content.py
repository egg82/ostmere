"""The game contract's static content and the finished game's view, served: labels for every lane and skill, what
each skill level and Camp level pays, the first mix the page offers, the end feature and its lines, the fixed ui text,
and the card panel and Completed tab filled from the engine."""
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from ashfall_app.api.content_models import CardPresentation, Content
from ashfall_app.api.models import AtLeast, AtMost, StoreValue, View
from ashfall_app.api.service import Game
from ashfall_app.engine import new_save, units
from ashfall_app.main import create_app
from ashfall_app.opening.ui_keys import UI_KEYS
from ashfall_app.opening.convert import camp_cap
from ashfall_app.opening.name_checks import without_slots
from ashfall_app.opening.schema import B7, CHAPTERS, DAY_ELEVEN, DAY_FIVE, DAY_FOUR, DAY_SIX, DAY_TWELVE
from ashfall_app.opening.renames import load_renames
from ashfall_app.saves.ruleset import ruleset
from tests.opening.playthrough import Player, opening, opening_rules


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(create_app())


@pytest.fixture(scope="module")
def content(client: TestClient) -> Content:
    return Content.model_validate(client.get("/api/content").json())


@pytest.fixture(scope="module")
def game_wire() -> Game:
    o = opening()
    return Game(o, ruleset(o, load_renames(), "dev", 1))


def shipped(always: list[str], *later: tuple[Path, list[str]]) -> list[str]:
    """A hand list of ids in content order that holds whether or not a chapter in writing ships: `always`, then each
    later chapter's ids while that chapter is in CHAPTERS."""
    return always + [i for chapter, ids in later if chapter in CHAPTERS for i in ids]


@pytest.fixture(scope="module")
def end_view(game_wire: Game, typical: Player) -> View:
    """The view the routes would serve for the typical route's (routes.py) finished save (api/service.py, as every
    Step's), built in setup: a view of the whole opening grows with every chapter shipped."""
    return game_wire.view(typical.save)


def test_every_lane_and_skill_has_a_label_that_is_text(content: Content):
    keys = {t.key: t.text for t in content.text_entries}
    assert [x.lane for x in content.lane_infos][:2] == ["hands", "rack"]   # the opening's; its chapters' follow
    assert [s.skill for s in content.skill_infos][:3] == ["scavenging", "woodcutting", "foraging"]
    for label in [*content.lane_infos, *content.skill_infos]:
        assert label.label_key in keys
    assert keys[content.lane_infos[0].label_key] == "Hands"


def test_each_skill_row_says_what_its_levels_pay(content: Content):
    keys = {t.key: t.text for t in content.text_entries}
    scavenging = next(s for s in content.skill_infos if s.skill == "scavenging")
    authored = next(s for s in opening().skills if s.id == "scavenging")
    assert [lv.level for lv in scavenging.levels] == [lv.level for lv in authored.levels][:len(scavenging.levels)]
    assert [lv.level for lv in scavenging.levels][:3] == [2, 3, 4]
    assert all(lv.pays_key in keys for s in content.skill_infos for lv in s.levels)
    top = len(opening().curve_items) + 1
    mixed = {"scavenging", "woodcutting", "foraging"}   # trained by hands cards: the mix drives them to the curve's top
    assert all(top in {lv.level for lv in s.levels} for s in content.skill_infos if s.skill in mixed)


def test_the_camp_bar_and_its_levels_are_served(content: Content):
    camp, authored = content.camp, opening().camp
    assert camp is not None and authored is not None and camp.store in {s.store for s in content.store_infos}
    assert [lv.at for lv in camp.camp_levels] == [units(lv.at_items) for lv in authored.levels]
    cap = next(s.cap for s in content.store_infos if s.store == camp.store)
    assert cap == units(camp_cap(authored)) and cap <= camp.camp_levels[-1].at


def test_each_camp_level_says_what_its_pays_names_and_what_lifts_it(content: Content):
    """CampLevel.names: a rate's runner and store, a cap's store, from the level's modifiers; none for a held level
    (its marker is "?"). lifted_by as authored."""
    camp, authored = content.camp, opening().camp
    assert camp is not None and authored is not None
    cards = {c.card for c in content.card_infos}
    stores = {s.store for s in content.store_infos}
    for served, lv in zip(camp.camp_levels, authored.levels, strict=True):
        assert served.lifted_by == lv.lifted_by
        want: set[tuple[str, str]] = set()
        for m in [] if lv.held else lv.modifiers:
            if m.target in ("rate", "work"):
                want.add(("card" if m.id in cards else "action", m.id))
            if m.target == "cap":
                want.add(("store", m.id))
            if m.store is not None:
                want.add(("store", m.store))
        got = {(u.category.value, u.id) for u in served.names}
        assert got == want and len(served.names) == len(got)
        assert all(i in cards or i in stores or k == "action" for k, i in got)
    assert any(lv.names for lv in camp.camp_levels) and any(lv.lifted_by for lv in camp.camp_levels)


def test_the_first_mix_offer_and_the_crafts_skill_needs(content: Content):
    infos = {c.card: c for c in content.card_infos}
    assert content.first_mix.card_ids == ["gather_wood", "scavenge"]
    assert all(infos[c].lane == "hands" for c in content.first_mix.card_ids)
    assert content.first_mix.feature in {f.feature for f in content.feature_infos}
    assert [(n.skill, n.level) for n in infos["make_stool"].skill_needs] == [("woodcutting", 2)]
    assert infos["make_stool"].presentation == CardPresentation.CRAFT and infos["ring_it"].skill_needs == []


def test_a_short_need_can_name_the_card_that_makes_it(content: Content):
    """StoreInfo.made_by, read off the content: a card's lump or flow (stones, roots, dry wood, both woods), a skill
    trained whose level pays a find (flint, from scavenging), a completion a find waits on (the nail), but not a find
    beside a card that makes the store (Woodcutting's stones); nothing for a store only a standing action fills
    (warmth)."""
    made = {s.store: s.made_by for s in content.store_infos}
    assert made["stones"] == ["scavenge", "n1_scavenge", "n2_scavenge"]
    assert made["roots"] == shipped(["forage", "n1_forage", "n2_forage"], (DAY_FIVE, ["n3_forage"]), (DAY_ELEVEN, ["n5_forage", "n7_forage", "n6_forage"]))
    assert made["dry_wood"] == shipped(["lay_to_dry"], (DAY_FIVE, ["hand_on_stone"]), (DAY_TWELVE, ["stone_ring"]))
    assert made["damp_wood"] == shipped(["gather_wood", "woodcutting", "n1_gather", "n1_cut", "n2_gather", "n2_cut"],
                                        (DAY_FIVE, ["n3_gather"]),
                                        (DAY_ELEVEN, ["n5_gather", "n5_cut", "n7_gather", "n7_cut", "n6_gather", "n6_cut"]))
    assert made["flint"] == ["scavenge", "field_track"] and made["nails"] == ["scavenge"]
    assert made["warmth"] == []


def test_step_needs_glows_order_offers_and_carried_things_are_served(content: Content):
    """ring_it waits on two clearings and strike_fire on the ring; the glow is on the first card, the strike, day two's stool, day three's and each later chapter's that ships;
    the roots order is offered once eating has started; the book is a thing carried; the Camp's last level is held."""
    infos = {c.card: c for c in content.card_infos}
    assert [(n.card, n.count) for n in infos["ring_it"].step_needs] == [("clear_spot", 2)]
    assert [(n.card, n.count) for n in infos["strike_fire"].step_needs] == [("ring_it", 1)]
    assert [c.card for c in content.card_infos if c.glows] == shipped(
        ["stand_up", "strike_fire", "give_stool", "walk_edge", "track_end", "bank_hearth"],
        (DAY_FOUR, ["sit_up_5"]), (DAY_FIVE, ["hand_on_stone"]), (B7, ["bank_fire_6", "b7_stand"]), (DAY_SIX, ["sit_fire_7"]), (DAY_ELEVEN, ["keep_vigil"]),
        (DAY_TWELVE, ["sit_last_night"]))
    roots = next(c for c in content.order_cards if c.store == "roots")
    assert roots.offered_after is not None and (roots.offered_after.category, roots.offered_after.id) == ("action", "eating")
    assert next(c for c in content.order_cards if c.store == "dry_wood").offered_after is None
    assert [f.feature for f in content.feature_infos if f.label_key] == shipped(
        ["book", "posts_fire", "margin_watch", "posts_deep", "lookout", "watch_fed", "skin_post"],
        (DAY_ELEVEN, ["door_gate", "ditch_dug"]),
        (DAY_TWELVE, ["spoil_ring", "shaft_bound", "meat_below", "rack_kept", "crows_off", "crows_kept"]))
    authored = opening().camp
    assert content.camp is not None and authored is not None
    assert [lv.held for lv in content.camp.camp_levels] == [lv.held for lv in authored.levels]
    assert content.camp.camp_levels[-1].held and not any(lv.held for lv in content.camp.camp_levels[:2])


def test_the_fixed_ui_text_is_served_and_has_no_digit(content: Content):
    keys = {t.key: t.text for t in content.text_entries}
    assert set(UI_KEYS) <= set(keys) and len(UI_KEYS) > 15
    assert all(not any(c.isdigit() for c in without_slots(t)) for t in keys.values())
    assert len(keys["ui.mix.default"]) in range(1, 41)
    assert content.order_cards and all(
        isinstance(c.when, (AtMost, AtLeast)) and isinstance(c.when.watched, StoreValue) and c.when.watched.store == c.store
        for c in content.order_cards)
    assert keys["ui.rule.chip"] == "While {chip}" and keys["ui.hands.while_chip"] == "while {chip}"


def test_the_rest_offer_is_served_as_the_tired_chips_after_the_end(content: Content):
    """The second mix's offer: rest on energy, answering the tired chip with the chip's own `when` (so the page words
    it as the chip), waiting for the end; day one's hunger rule is the same shape on the hungry chip; day eight's roofs
    card and day nine's wind card answer their chips as their own `when` and do not wait; the ledger's cards answer no chip and never
    wait for it."""
    chips = {c.chip: c for c in content.chip_infos}
    rest = next(c for c in content.order_cards if c.chip is not None)
    assert (rest.store, rest.chip, rest.after_end, rest.then.model_dump()) == \
        ("energy", "tired", True, {"kind": "tap_card", "card": "rest"})
    assert rest.when == chips["tired"].when
    others = [(c.store, c.chip, c.after_end) for c in content.order_cards if c is not rest]
    assert others[:2] == [("dry_wood", None, False), ("roots", None, False)]   # the opening's; its chapters' follow
    hunger = next(c for c in content.order_cards if c.chip == "hungry")
    assert (hunger.store, hunger.after_end, hunger.when) == ("fullness", True, chips["hungry"].when)
    roofs = next(c for c in content.order_cards if c.chip == "ash_laden")
    assert (roofs.store, roofs.after_end, roofs.when) == ("roof_ash", False, chips["ash_laden"].when)
    draughty = next(c for c in content.order_cards if c.chip == "draughty")
    assert (draughty.store, draughty.after_end, draughty.when) == ("wind_torn", False, chips["draughty"].when)
    assert all(chip is None and not after_end
               for _, chip, after_end in others if chip not in ("hungry", "ash_laden", "draughty"))
    assert all(c.when != chips["tired"].when for c in chips.values() if c.chip != "tired")


def test_the_end_feature_is_declared_and_its_lines_are_text(content: Content):
    keys = {t.key for t in content.text_entries}
    assert opening().end_feature in {f.feature for f in content.feature_infos}
    assert content.end_line_keys and set(content.end_line_keys) <= keys


def test_a_new_game_lists_only_the_hands(game_wire: Game):
    v = game_wire.view(new_save(opening_rules()))
    assert [b.lane for b in v.lanes] == ["hands"] and v.runs_out_at is None


@pytest.mark.playthrough
def test_the_finished_opening_serves_the_card_panel_and_the_completed_tab(end_view: View, content: Content):
    v = end_view
    assert opening().end_feature in {u.id for u in v.unlocked} and v.ended_at is not None
    assert [b.lane for b in v.lanes] == ["hands", "rack"]
    done = {c.card for c in v.completed}
    assert {"stand_up", "make_stool", "build_fireback", "gather_wood"} <= done
    assert {"woodcutting", "scavenge"} <= {c.card for c in v.cards} and not done & {c.card for c in v.cards}
    bar = next(s for s in v.skills if s.skill == "scavenging")
    assert bar.level_xp <= bar.xp.start_value and (bar.next_level_xp is None or bar.xp.start_value < bar.next_level_xp)
    assert bar.level_xp == ([0, *opening().curve_items][bar.level - 1]) * 3_600_000
    assert [m.id for m in v.mixes] == [v.active_mix_id] == [opening().text["ui.mix.default"]]
    assert v.greyed_mix_ids == []
