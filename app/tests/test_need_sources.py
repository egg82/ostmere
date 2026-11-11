"""Where a card's input comes from (api/sources.py, View Need.gate and makers): a store no maker makes shows the
condition of the first unfired trigger that grants it, while the need is short and only when a need row can show it (a
skill's level, a card's completions); the makers served are the ones in play; a short store nothing in play can make
again, every grant of it fired, is spent. The table is read off the content
(opening/makers.py)."""
from dataclasses import replace

from ashfall_app import engine as e
from ashfall_app.api import convert
from ashfall_app.api import models as w
from ashfall_app.api.sources import StoreSources, sources, store_sources
from ashfall_app.engine import QUANTITY_SCALE as Q
from ashfall_app.opening.schema import Opening
from tests.engine.test_cards_impl import CHOP, CRAFT, WOOD, rules

LEVEL = e.AtLeast(e.SkillLevel(e.SkillId("k")), 2, 2)
CLOCK = e.AtLeast(e.StoreValue(e.StoreId("plank")), 5 * Q, 5 * Q)


def world(wood: int, *whens: e.Condition) -> tuple[e.Save, e.Rules]:
    triggers = tuple(e.TriggerDef(e.TriggerId(f"t{i}"), when, e.Outcome(stores=(e.Amount(WOOD, 4 * Q),)))
                     for i, when in enumerate(whens))
    r = rules(wood=wood, triggers=triggers)
    return e.new_save(r), r


def pool(wood: int, *whens: e.Condition) -> tuple[e.Save, e.Rules]:
    """world's, with no card making wood: a pool only the triggers fill."""
    _, r = world(wood, *whens)
    r = replace(r, cards=tuple(c for c in r.cards if c.id != CHOP))
    e.validate_rules(r)
    return e.new_save(r), r


def wood_need(save: e.Save, r: e.Rules, table: dict[str, StoreSources]):
    return sources(save, r, e.view(save, r), table)[(str(CRAFT), str(WOOD))]


def granted(*ids: str) -> dict[str, StoreSources]:
    return {str(WOOD): StoreSources((), ids)}


def test_a_short_input_nothing_makes_shows_its_grants_gate():
    s, r = world(0, LEVEL)
    src = wood_need(s, r, granted("t0"))
    assert src.gate == LEVEL and src.makers == ()


def test_no_gate_once_the_grant_has_fired_or_the_need_is_met():
    s, r = world(0, LEVEL)
    assert wood_need(replace(s, fired=(True,)), r, granted("t0")).gate is None
    held, r2 = world(4, LEVEL)
    assert wood_need(held, r2, granted("t0")).gate is None


def test_a_grant_a_need_row_cannot_show_is_passed_over():
    s, r = world(0, CLOCK, LEVEL)
    assert wood_need(s, r, granted("t0", "t1")).gate == LEVEL
    assert wood_need(s, r, granted("t0")).gate is None


def test_a_made_store_shows_no_gate_and_only_makers_in_play():
    s, r = world(0, LEVEL)
    src = wood_need(s, r, {str(WOOD): StoreSources((str(CHOP), "not_in_play"), ("t0",))})
    assert src.gate is None and src.makers == (str(CHOP),)


def test_a_short_pool_whose_grants_all_fired_is_spent():
    s, r = pool(0, CLOCK)
    assert wood_need(replace(s, fired=(True,)), r, granted("t0")).spent


def test_not_spent_while_a_grant_waits_the_need_is_met_or_a_maker_is_in_play():
    s, r = pool(0, CLOCK)
    assert not wood_need(s, r, granted("t0")).spent   # a grant no need row can show still waits
    held, r2 = pool(4, CLOCK)
    assert not wood_need(replace(held, fired=(True,)), r2, granted("t0")).spent
    made, r3 = world(0, CLOCK)
    assert not wood_need(replace(made, fired=(True,)), r3, granted("t0")).spent


def test_the_wire_need_carries_the_gate_and_makers():
    s, r = world(0, LEVEL)
    v = e.view(s, r)
    wire = convert.view(s, v, sources(s, r, v, {str(WOOD): StoreSources((), ("t0",))}))
    need = next(n for c in wire.cards if c.card == CRAFT for n in c.needs if n.store == WOOD)
    assert need.gate == w.AtLeast(watched=w.SkillLevel(skill="k"), value=2, release=2) and need.makers == []
    assert not need.spent
    bare = convert.view(s, v)
    assert all(n.gate is None and n.makers == [] and not n.spent for c in bare.cards for n in c.needs)
    ps, pr = pool(0, LEVEL)
    ps = replace(ps, fired=(True,))
    pv = e.view(ps, pr)
    spent = convert.view(ps, pv, sources(ps, pr, pv, {str(WOOD): StoreSources((), ("t0",))}))
    assert [n.spent for c in spent.cards if c.card == CRAFT for n in c.needs if n.store == WOOD] == [True]


def test_the_content_table(shipped_opening: Opening):
    """Day one's rack input is granted at a Foraging level, its phase pays (past the prestige top) left out; the
    catch is made by cards and by the snares, standing actions."""
    table = store_sources(shipped_opening)
    assert table["tinder_fungus"] == StoreSources((), ("t_tinder",))
    assert table["flint"] == StoreSources((), ("t_flint", "t_flint_2"))
    assert {"hunt_wolf", "snare_1"} <= set(table["catch"].makers)
