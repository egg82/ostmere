"""The pot on the fire as the content builds it (#473; decisions/mixes.md, "One pot on the fire"): a station lane whose
cards each eat one kind of stew for the whole camp. Ids and fields only."""
from fractions import Fraction

from ashfall_app.engine import BP
from ashfall_app.rules.schema import load_opening


def test_each_pot_eats_as_much_as_the_mouths_it_feeds():
    """Every pot draws its base rate once per eater: the first eater's at its base, each later arrival's trigger adding a
    whole base, each leave taking one back. The eaters are the lanes the stew pot holds a speed on."""
    o = load_opening()
    pots = [c for c in o.cards if any(x.id == c.lane and x.station for x in o.lanes)]
    assert len(pots) == 4, "the pots are not seen: the check is blind"
    eaters = {w.lane for c in pots if c.id == "pot_stew" for w in c.while_running}
    left = sum(1 for t in o.triggers for leave in t.outcome.leaves if leave.lane in eaters)
    assert len(eaters) > 10
    for p in pots:
        (flow,) = p.costs
        base = Fraction(flow.items_per_hour, flow.every_hours)
        adds = sum(m.amount_bp for t in o.triggers for m in t.outcome.modifiers
                   if m.target == "rate" and m.id == p.id and m.flow == "cost" and m.kind == "add_bp" and m.store == flow.store)
        assert base * (BP + adds) / BP == base * (len(eaters) - left), p.id


def test_no_eater_eats_from_a_stew_store_and_only_a_pot_does():
    o = load_opening()
    stews = {s.id for s in o.stores if s.group_key == "store_group_stew"}
    assert len(stews) == 4
    assert not [a.id for a in o.standing if any(f.store in stews for f in a.costs)]
    takers = {c.id for c in o.cards if any(f.store in stews for f in c.costs) or any(i.store in stews for i in c.inputs)}
    assert takers == {c.id for c in o.cards if c.lane == "pot"}


def test_the_first_pot_is_set_by_an_installed_rule_and_each_kind_opens_with_its_recipe():
    o = load_opening()
    installs = [i.tap_card for t in o.triggers for i in t.outcome.orders]
    assert installs.count("pot_stew") == 1 and not [c for c in installs if c.startswith("pot_") and c != "pot_stew"]
    for recipe, pot in (("fungus_stew", "pot_fungus_stew"), ("catch_broth", "pot_catch_broth"), ("barley_stew", "pot_barley_stew")):
        opens = [t for t in o.triggers if any(u.id == pot for u in t.outcome.unlocks)]
        assert [t.when.id for t in opens] == [recipe], pot
