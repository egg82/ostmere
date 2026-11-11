"""A format 8 save written before sides and threats existed (fixtures/pre_fights_f8.txt, the encoder's own output at
the commit before) loads under the same rules unchanged but for its format, and the new Target tags round-trip."""
from pathlib import Path

from ashfall_app.engine import (
    FORMAT, ModifierKind, Modifier, PacingCurve, Rules, SideDef, SideId, SideStrength, SkillDef, SkillId, SourceId,
    StoreCap, StoreDef, StoreId, ThreatDef, ThreatId, ThreatStrength, advance, decode, encode, new_save, rebase,
)

S = StoreId("s0")
RULES = Rules((StoreDef(S, 10**9),), (SkillDef(SkillId("k0")),), (), PacingCurve((10**15,)))
OLD = Path(__file__).parent / "fixtures" / "pre_fights_f8.txt"


def test_a_save_written_before_fights_loads_unchanged_and_re_encodes_to_the_same_text_at_todays_format():
    text = OLD.read_text().strip()
    assert FORMAT == 9
    save = rebase(text, RULES)
    assert save.time == 100 and save.modifiers == (Modifier(StoreCap(S), ModifierKind.ADD_BP, 500, SourceId("belt")),)
    assert encode(save, RULES) == text.replace('"format":8', '"format":9', 1)


def test_declaring_a_side_or_a_threat_changes_the_rules_digest_and_the_new_targets_round_trip():
    rules = Rules(RULES.stores, RULES.skills, (), RULES.curve, sides=(SideDef(SideId("hand"), 4),),
                  threats=(ThreatDef(ThreatId("wolf"), 10),))
    mods = (Modifier(SideStrength(SideId("hand")), ModifierKind.ADD_BP, 500, SourceId("spear")),
            Modifier(ThreatStrength(ThreatId("wolf")), ModifierKind.MUL_BP, 12_000, SourceId("t")))
    save = advance(new_save(rules, mods), rules, 50)
    text = encode(save, rules)
    assert decode(text, rules) == save
    assert encode(new_save(RULES), RULES).split('"rules":')[1][:66] != text.split('"rules":')[1][:66]
