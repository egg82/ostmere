"""Combat's lines have homes (docs/design/combat-plan.md, item 9): the combat feature's line on the story fight's
finish, the hurt chip's on and off lines, the first poultice's line, and each fight's pools for one
fight won and lost, served on its FightInfo, listed in Content.line_infos, and checked against text by the loader; and
every side strength's source has a label the fight panel shows."""
import pytest

from ashfall_app.api.content_models import Content
from ashfall_app.api.service import Game
from ashfall_app.opening.checks import check_opening
from ashfall_app.opening.lock import line_keys
from ashfall_app.opening.refs import outcomes
from ashfall_app.opening.schema import CHAPTERS, IN_WRITING, Opening, load_opening
from ashfall_app.saves.ruleset import ruleset


@pytest.fixture(scope="module")
def everything() -> Opening:
    """Every chapter, those in writing too, loaded in setup (not timed): each chapter adds to the load."""
    return load_opening(chapters=(*CHAPTERS, *IN_WRITING))


def test_the_story_fight_the_chip_and_the_poultice_carry_their_lines(everything: Opening):
    o = everything
    cards = {c.id: c for c in o.cards}
    assert cards["b7_stand"].finished.line_keys[-1] == "l_combat_first"
    assert next(t for t in o.triggers if t.id == "t_poultice_first").outcome.line_keys == ["l_poultice"]
    hurt = next(ch for ch in o.chips if ch.id == "hurt")
    assert (hurt.on_line_key, hurt.off_line_key) == ("l_hurt", "l_healed")


def test_every_fight_has_both_pools_and_they_are_lines(everything: Opening):
    o = everything
    fights = [c.fight for c in o.cards if c.fight] + [a.fight for a in o.standing if a.fight]
    assert len(fights) >= 3   # week one's three, and every later chapter's
    keys = set(line_keys(o))
    for f in fights:
        assert f.won_line_keys and f.lost_line_keys
        assert {*f.won_line_keys, *f.lost_line_keys} <= keys


def test_the_content_serves_each_fights_pools(everything: Opening):
    o = everything
    content = Game(o, ruleset(o, [], "test", 1)).content()
    hunt = next(c for c in content.card_infos if c.card == "hunt_wolf").fight
    rats = next(a for a in content.standing_infos if a.action == "rats").fight
    assert hunt is not None and hunt.won_line_keys == [f"l_fight_hunt_won_{i}" for i in (1, 2, 3)]
    assert hunt.lost_line_keys == [f"l_fight_hunt_lost_{i}" for i in (1, 2, 3)]
    assert rats is not None and rats.won_line_keys == [f"l_fight_rats_won_{i}" for i in (1, 2, 3)]
    pack = next(a for a in content.standing_infos if a.action == "pack").fight
    assert pack is not None and pack.won_line_keys == [f"l_fight_pack_won_{i}" for i in (1, 2, 3)]
    assert pack.lost_line_keys == [f"l_fight_pack_lost_{i}" for i in (1, 2, 3)]


def test_a_pool_key_missing_from_text_fails(everything: Opening):
    o = everything
    text = {k: v for k, v in o.text.items() if k != "l_fight_crows_lost_1"}
    with pytest.raises(ValueError, match="action crows: key 'l_fight_crows_lost_1' is not in text"):
        check_opening(o.model_copy(update={"text": text}))


def side_sources(o: Opening) -> list[tuple[str, str]]:
    """(where, source) for every modifier aimed at a side's strength."""
    mods = [*((w, m) for w, out in outcomes(o) for m in out.modifiers),
            *((f"chip {c.id}", m) for c in o.chips for m in c.effects),
            *((f"camp level {n}", m) for n, lv in enumerate(o.camp.levels if o.camp else [], start=1) for m in lv.modifiers)]
    return [(w, m.source) for w, m in mods if m.target == "side"]


def unworded(o: Opening, content: Content) -> list[str]:
    """Side sources the fight panel would show as a raw id: it words a card, skill, chip, store or labelled feature
    (client/src/ui/fightpanel.ts, sourceName)."""
    named = {*(c.card for c in content.card_infos), *(s.skill for s in content.skill_infos),
             *(c.chip for c in content.chip_infos), *(s.store for s in content.store_infos),
             *(f.feature for f in content.feature_infos if f.label_key)}
    return [f"{w}: {s}" for w, s in side_sources(o) if s not in named]


def test_every_side_strengths_source_has_a_label_the_fight_panel_shows(everything: Opening):
    o = everything
    content = Game(o, ruleset(o, [], "test", 1)).content()
    assert len(side_sources(o)) >= 6 and unworded(o, content) == []
    no_melee = content.model_copy(update={"skill_infos": [s for s in content.skill_infos if s.skill != "melee"]})
    assert unworded(o, no_melee) == ["trigger t_melee_2: melee", "trigger t_melee_4: melee"]
