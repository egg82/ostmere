"""FORMAT 9: a Mix has no holds (engine DESIGN.txt, "Codec"). UPGRADES[8] drops holds from every saved mix, so a format 8
save loads and runs on as the same save, and a SaveMix the decision log kept before FORMAT 9, its mix carrying an empty
holds, reads back as the same verb, so an old log still replays."""
import json

import pytest

from ashfall_app.engine import (
    BP, FORMAT, QUANTITY_SCALE as Q, UPGRADES, Amount, CardDef, CardId, CardShare, Mix, MixId, Outcome, Rules, SaveMix,
    StateFormatError, StoreDef, StoreId, SwitchMix, advance, decide, encode, new_save, rebase, verb_from_json,
    verb_to_json,
)
from ashfall_app.engine.codec import Json
from tests.cards_contract.cards_world import rules as world
from tests.format8 import as_format_8

WOOD, PLANK = StoreId("wood"), StoreId("plank")
CHOP, CRAFT = CardId("chop"), CardId("craft")
MIX = Mix(MixId("m"), (CardShare(CHOP, BP // 2), CardShare(CRAFT, BP // 4)))


def rules() -> Rules:
    """chop makes wood a unit a completion; craft turns two wood into a plank, so the mix moves both stores."""
    return world([StoreDef(WOOD, 100 * Q, 4 * Q), StoreDef(PLANK, 100 * Q)],
                 cards=[CardDef(CHOP, 10, outcome=Outcome(stores=(Amount(WOOD, Q),))),
                        CardDef(CRAFT, 20, inputs=(Amount(WOOD, 2 * Q),), outcome=Outcome(stores=(Amount(PLANK, Q),)))])


def test_a_format_8_save_with_empty_holds_loads_as_the_same_save_and_runs_on_identically():
    r = rules()
    s = decide(decide(new_save(r), r, 0, SaveMix(MIX)), r, 0, SwitchMix(MIX.id))
    s = advance(s, r, 500)
    old = as_format_8(encode(s, r))
    assert FORMAT == 9 and '"holds":[]' in old
    loaded = rebase(old, r)
    assert loaded == s
    assert advance(loaded, r, 50_000) == advance(s, r, 50_000)


def test_upgrade_8_drops_holds_from_each_mix_and_nothing_else():
    r = rules()
    s = decide(new_save(r), r, 0, SaveMix(MIX))
    old = json.loads(as_format_8(encode(s, r)))
    mixes = [{k: v for k, v in m.items() if k != "holds"} for m in old["save"]["mixes"]]
    assert UPGRADES[8](old) == {**old, "format": 9, "save": {**old["save"], "mixes": mixes}}


def test_upgrade_8_refuses_a_mix_that_has_no_holds():
    r = rules()
    doc = json.loads(encode(decide(new_save(r), r, 0, SaveMix(MIX)), r))
    with pytest.raises(StateFormatError):
        UPGRADES[8]({**doc, "format": 8})


def test_a_logged_save_mix_with_empty_holds_reads_back_as_the_same_verb():
    verb = SaveMix(MIX)
    logged = verb_to_json(verb)
    assert isinstance(logged, dict) and isinstance(logged["mix"], dict)
    old: Json = {**logged, "mix": {**logged["mix"], "holds": []}}
    assert verb_from_json(old) == verb == verb_from_json(logged)


def test_a_logged_save_mix_with_a_hold_is_not_a_verb():
    logged = verb_to_json(SaveMix(MIX))
    assert isinstance(logged, dict) and isinstance(logged["mix"], dict)
    held: Json = {**logged, "mix": {**logged["mix"], "holds": [{"@": "Hold", "store": "wood", "card": "chop", "level": 0}]}}
    with pytest.raises(StateFormatError):
        verb_from_json(held)
