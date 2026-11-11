"""Invariant 114 (engine DESIGN.txt, "ENTRIES HELD WHILE A CARD RUNS": "The entries", "Instants", "Codec"): a held entry
aims only at sides and is never stored. No threat explanation and no rate, work or lane speed Explanation lists one;
s.modifiers and every LaneState.speed of a save hold none; and rules without while_running keep the digest, the
manifest and the save text they had before this part (the pins below were taken from the engine before it)."""
import hashlib
import json

from ashfall_app.engine import (
    CardDef, Explanation, FlowKind, Modifier, RateRef, Rules, Save, TapCard, ThreatStrength, advance, decide, decode, encode, explain,
    explain_strength, explain_work, new_save, rules_digest, view,
)
from ashfall_app.engine.codec import manifest
from fight_world import world as fight_world
from held_world import GA, GA2, GAC, GH, GH2, HELD, HF, WOLF, hands, held_mods, ja, kills, plain, town, world
from town_mix_world import A1, B1, LA, LB, TM, TOWN_RULE, always, joiner, orders, start, world as town_world
from tests.format8 import as_format_8

PIN_DIGEST = "06a2d30a601da3d907c5b542b1f67cdcda4d564a05f0233758c0826071c68b5a"
PIN_SAVE_SHA = "c3255e6f4f950070be2eb011aabd9a0b2ed277167701551ddde5e7c0d8fa5392"
PIN_MANIFEST_SHA = "3a95e34cf7786a6d1fcacd9ed3d82d578cb2452d92465fa6e2aeea571123bfa7"


def held_sourced(mods: tuple[Modifier, ...]) -> list[Modifier]:
    return [m for m in mods if str(m.source).startswith(HELD)]


def busy_saves() -> list[tuple[Save, Rules]]:
    """Saves with guards holding on both layers and a tapped fight card, at several instants."""
    r = world((ja(),))
    out: list[tuple[Save, Rules]] = []
    starts = (decide(town(r, (GA, 4000), (GA2, 3000)), r, 0, orders(TOWN_RULE, always(GAC))),
              hands(r, (GH, 4000), (GH2, 4000)), decide(new_save(r), r, 0, TapCard(HF)))
    for s in starts:
        out += [(advance(s, r, t), r) for t in (0, 7, 19, 20, 55, 120)]
    return out


def lines(r: Rules) -> list[RateRef]:
    """Every rate line of every runner: makes, outcome stores and wounds (and the lost tally) are MAKE lines; costs,
    inputs and loses are COST lines."""
    refs: list[RateRef] = []
    for runner in (*r.standing, *r.cards):
        fight = runner.fight
        make = [f.store for f in runner.makes]
        cost = [f.store for f in runner.costs]
        if isinstance(runner, CardDef):
            make += [a.store for a in runner.outcome.stores]
            cost += [a.store for a in runner.inputs]
        if fight is not None:
            make += [a.store for a in fight.wounds] + [fight.lost]
            cost += [a.store for a in fight.loses]
        refs += [RateRef(runner.id, FlowKind.MAKE, s) for s in make] + [RateRef(runner.id, FlowKind.COST, s) for s in cost]
    return refs


def explanations(s: Save, r: Rules) -> list[Explanation]:
    return [explain(s, r, ref) for ref in lines(r)] + [explain_work(s, r, c.id) for c in r.cards]


@kills(3, 17)
def test_no_threat_rate_or_work_explanation_lists_a_held_entry():
    saves = busy_saves()
    assert any(held_mods(s, r) for s, r in saves), "the premise: some of these saves hold entries"
    assert len(lines(saves[0][1])) > 10
    for s, r in saves:
        t = explain_strength(s, r, ThreatStrength(WOLF))
        assert not held_sourced(t.adds + t.muls)
        for e in explanations(s, r):
            assert not held_sourced(e.adds + e.muls), (e.ref, s.time)


@kills(14)
def test_nothing_is_stored_a_held_entry_is_in_no_modifiers_no_lane_speed_and_not_in_the_text():
    for s, r in busy_saves():
        assert held_sourced(s.modifiers) == [] and s.modifiers == ()
        assert all(held_sourced(ls.speed or ()) == [] for ls in s.lanes)
        assert HELD not in encode(s, r)


@kills(14)
def test_a_save_under_guards_equals_its_hand_twin_in_everything_but_the_stores_the_odds_move():
    """The same verbs under the same rules with the guards stripped leave the same decisions in the save (mixes, active,
    orders, queue, lanes, modifiers): a held entry adds nothing to them."""
    r = world((ja(),))
    twin = plain(r)

    def key(rules: Rules) -> tuple[object, ...]:
        s = decide(town(rules, (GA, 4000)), rules, 0, orders(TOWN_RULE, always(GAC)))
        return (s.modifiers, s.mixes, s.active, s.orders, s.queue, s.lanes, s.unlocked)

    assert key(r) == key(twin)


def test_reading_writes_nothing_and_a_decoded_save_holds_the_same_entries():
    for s, r in busy_saves():
        copy = s
        view(s, r)
        explain_strength(s, r, ThreatStrength(WOLF))
        assert s == copy and advance(s, r, s.time) == s
        assert held_mods(decode(encode(s, r), r), r) == held_mods(s, r)


@kills(20)
def test_rules_without_while_running_keep_their_digest_manifest_and_save_text():
    """The pins were taken from the engine before this part: a card with an empty while_running encodes as it did."""
    r = town_world((joiner("ja", LA, TM, A1), joiner("jb", LB, TM, B1)))
    assert rules_digest(r) == PIN_DIGEST
    s = advance(start(r, orders(TOWN_RULE, always(A1))), r, 345)
    assert hashlib.sha256(as_format_8(encode(s, r)).encode()).hexdigest() == PIN_SAVE_SHA   # pinned at format 8
    assert hashlib.sha256(json.dumps(manifest(r), sort_keys=True).encode()).hexdigest() == PIN_MANIFEST_SHA


@kills(20)
def test_a_second_world_without_the_field_keeps_its_digest_too():
    """The fight suite's world (pin taken from the engine before this part): a different set of rules, same promise."""
    assert rules_digest(fight_world(2, 5)) == "243695bd9aec8543d7305799397be355be9ccb0d35d4a3518c23d8b313598b19"


def test_rules_with_while_running_have_their_own_digest_and_the_same_manifest_as_without():
    r = world((ja(),))
    assert rules_digest(r) != rules_digest(plain(r))
    assert manifest(r) == manifest(plain(r))
