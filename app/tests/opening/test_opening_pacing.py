"""The opening's drip (docs/decisions.md, "The opening is fun first"): no gate counts taps (an authoring rule), either
craft first reaches the end, and tapping extra early never reaches the end sooner than its steps. How the opening
moves (effort between new things, runs of taps, what a day away opens, how the crafts show) is its readout
(report.py), never a threshold."""
from dataclasses import replace

import pytest

from ashfall_app.engine import (
    AtLeast, AtMost, CardCount, CardId, Condition, Flow, Rules, SkillLevel, StoreId, StoreValue, TriggerDef, TriggerId,
    TapCard, UnlockKind, advance_logged, decide_logged,
)
from tests.opening.playthrough import CRAFTS, Player, opening_rules
from tests.opening.routes import EagerForager

pytestmark = pytest.mark.playthrough

# ---------- no gate counts taps ----------

def counted_gates(rules: Rules) -> list[str]:
    """Every gate that counts repeats of one card: a CardCount above 1 on an uncapped card or above a capped card's
    cap, a trigger on a store only one repeatable card makes (a standing action making it too is another maker), and a
    skill level that opens anything (a level pays a find, never an opening)."""
    caps = {c.id: c.cap for c in rules.cards}
    makers: dict[StoreId, list[CardId]] = {}
    for c in rules.cards:
        for store in {f.store for f in c.makes} | {a.store for a in c.outcome.stores}:
            makers.setdefault(store, []).append(c.id)
    standing_made = {f.store for a in rules.standing for f in a.makes}
    conditions: list[tuple[str, Condition]] = [(f"trigger {t.id}", t.when) for t in rules.triggers]
    conditions += [(f"card {c.id}", r) for c in rules.cards for r in c.requires]
    conditions += [(f"chip {c.id}", c.when) for c in rules.chips]
    found: list[str] = []
    for where, cond in conditions:
        if not isinstance(cond, (AtLeast, AtMost)):
            continue
        s = cond.subject
        if isinstance(s, CardCount) and cond.value > (caps[s.card] or 1):
            found.append(f"{where} counts {cond.value} of {s.card}")
        if where.startswith("trigger") and isinstance(s, StoreValue) and isinstance(cond, AtLeast):
            only = makers.get(s.store, [])
            if len(only) == 1 and caps[only[0]] is None and s.store not in standing_made:
                found.append(f"{where} counts {s.store}, made only by {only[0]}")
    found += [f"trigger {t.id} opens at a level" for t in rules.triggers
              if isinstance(t.when, AtLeast) and isinstance(t.when.subject, SkillLevel) and t.outcome.unlocks]
    return found


def test_no_gate_counts_taps_of_one_card():
    assert counted_gates(opening_rules()) == []


@pytest.mark.parametrize("when", [
    AtLeast(CardCount(CardId("gather_wood")), 6, 6),
    AtLeast(CardCount(CardId("clear_spot")), 3, 3),
    AtLeast(StoreValue(StoreId("planted_store")), 10 * 3_600_000, 10 * 3_600_000),   # the one card that makes it
])
def test_the_gate_check_catches_a_count(when: AtLeast):
    """The probe can fail: v1's kind of gate, added to the shipped rules, is reported. The store of the last case is
    made by one uncapped card planted here, so no shipped card's second maker can take the case away."""
    rules = opening_rules()
    maker = next(c for c in rules.cards if c.cap is None)
    cards = tuple(replace(c, makes=(*c.makes, Flow(StoreId("planted_store"), 1))) if c is maker else c for c in rules.cards)
    planted = replace(rules, cards=cards,
                      triggers=(*rules.triggers, TriggerDef(TriggerId("t_planted"), when, rules.triggers[0].outcome)))
    assert [g for g in counted_gates(planted) if "t_planted" in g]


# ---------- the choice ----------

def test_either_craft_first_reaches_the_end(typical: Player, fireback_first: Player):
    for p, craft in ((typical, CRAFTS[0]), (fireback_first, CRAFTS[1])):
        built = [v.card for _, _, v in p.decisions if isinstance(v, TapCard) and v.card in CRAFTS]
        assert built[0] == craft and set(built) == set(CRAFTS)


ORDER_LINES = {CRAFTS[0]: "l_stool_first", CRAFTS[1]: "l_fireback_first"}
CRAFT_LINES = {CRAFTS[0]: "l_stool", CRAFTS[1]: "l_fireback"}
"""The line on what the player built first, as reading by the fire starts with the other not built."""


def test_the_craft_built_first_gets_its_line_once_as_reading_starts(typical: Player, fireback_first: Player):
    for p, craft in ((typical, CRAFTS[0]), (fireback_first, CRAFTS[1])):
        keys: list[str] = [ln.key for ln in p.lines]
        assert [k for k in keys if k in ORDER_LINES.values()] == [ORDER_LINES[craft]]
        read = next(t for t, _, v in p.decisions if isinstance(v, TapCard) and v.card == "read_by_fire")
        assert next(ln.time for ln in p.lines if ln.key == ORDER_LINES[craft]) == read
        assert keys.index(CRAFT_LINES[craft]) < keys.index(ORDER_LINES[craft])
        assert keys.index(ORDER_LINES[craft]) < keys.index("l_read")


def test_both_crafts_built_before_reading_get_neither_line(typical: Player):
    p = typical.at(lambda q: q.completed(CRAFTS[0]))
    s, r, lines = p.save, p.rules, list[str]()
    for card in (CRAFTS[1], "read_by_fire"):
        tapped = decide_logged(s, r, s.time, TapCard(CardId(card)))
        step = advance_logged(tapped.save, r, s.time + 30)
        s, lines = step.save, lines + [ln.key for ln in (*tapped.lines, *step.lines)]
    assert "l_read" in lines and not set(lines) & set(ORDER_LINES.values())


# ---------- tapping ahead ----------

def test_tapping_extra_early_cannot_reach_the_end_before_its_steps(eager_forager: EagerForager):
    p = eager_forager   # routes.EagerForager: forages by hand to a full store whenever foraging is open
    forage = p.card("forage")
    assert forage is not None and forage.completions >= 6   # the probe did forage extra (by hand and by its rule)
    assert p.end_at is not None and all(p.completed(c) for c in (*CRAFTS, "roast_roots"))
    assert p.has(UnlockKind.FEATURE, "keeps_going")
