"""FULL OUTPUT's implementation choices beside the contract suite (engine_contract/test_full_output.py): rebase
re-decides a full pause rather than reading one written under other rules (DESIGN.txt, "FULL OUTPUT", "Rebase")."""
from dataclasses import replace

from ashfall_app.engine import (
    BP, QUANTITY_SCALE as Q, Amount, CardDef, CardId, CardShare, Mix, MixId, Outcome, PacingCurve, Rules, SaveMix,
    SkillDef, SkillId, StoreDef, StoreId, SwitchMix, advance, decide, encode, new_save, rebase,
)

P, Y = StoreId("p"), StoreId("y")
PULL = CardId("pull")


def _rules(cap: int | None) -> Rules:
    card = CardDef(PULL, 10, inputs=(Amount(P, Q),), outcome=Outcome(stores=(Amount(Y, Q),)), cap=cap)
    return Rules((StoreDef(P, 1000 * Q, 1000 * Q), StoreDef(Y, 4 * Q, 0)), (SkillDef(SkillId("k")),), (),
                 PacingCurve((10**15,)), cards=(card,))


def test_rebase_drops_a_full_pause_and_the_instant_decides_again():
    """Paused full under rules where pull is fillable; rebased onto rules where pull has a cap, the pause would hold
    for good (y never falls), so step 5 drops it and the capped card runs on to its cap."""
    old = _rules(None)
    s = decide(new_save(old), old, 0, SaveMix(Mix(MixId("m"), (CardShare(PULL, BP),))))
    s = advance(decide(s, old, 0, SwitchMix(MixId("m"))), old, 100)
    assert [p.runner for p in s.pauses] == [PULL]
    new = _rules(20)
    after = rebase(encode(s, old), new)
    assert after.pauses == ()
    later = advance(after, new, 1000)
    assert next(st.segment.start_value for st in later.stores if st.store == P) == 980 * Q


def test_rebase_onto_rules_where_the_card_is_still_full_pauses_it_again():
    """The same save rebased onto rules that differ elsewhere: the dropped pause is put back at the rebase's instant."""
    old = _rules(None)
    s = decide(new_save(old), old, 0, SaveMix(Mix(MixId("m"), (CardShare(PULL, BP),))))
    s = advance(decide(s, old, 0, SwitchMix(MixId("m"))), old, 100)
    new = replace(old, max_firings_per_instant=999)
    after = rebase(encode(s, old), new)
    assert [p.runner for p in after.pauses] == [PULL]
