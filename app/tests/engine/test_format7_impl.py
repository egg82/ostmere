"""FORMAT 7: the manifest's offers, and UPGRADES[6], which adds them empty and changes nothing else (engine DESIGN.txt,
part "TOWNSFOLK, INSTALLED RULES AND OFFERS", "Codec")."""
import json

import pytest

from ashfall_app.engine import (
    FORMAT, UPGRADES, AnswerId, CardDef, CardId, LaneDef, LaneId, OfferId, PacingCurve, Rules, SkillDef, SkillId,
    StateFormatError, StoreDef, StoreId, encode, new_save, rebase,
)
from ashfall_app.engine.offers import AnswerDef, OfferDef

Q = 1000


def world() -> Rules:
    return Rules(stores=(StoreDef(StoreId("x"), 10 * Q),), skills=(SkillDef(SkillId("k")),), standing=(),
                 curve=PacingCurve((10 * Q,)), lanes=(LaneDef(LaneId("rack")),), cards=(CardDef(CardId("c"), 5),),
                 offers=(OfferDef(OfferId("o"), (AnswerDef(AnswerId("yes")), AnswerDef(AnswerId("no")))),))


def as_format_6(text: str) -> str:
    doc = json.loads(text)
    del doc["manifest"]["offers"]
    for ls in doc["save"]["lanes"]:
        del ls["speed"]   # format 8's
    return json.dumps({**doc, "format": 6}, sort_keys=True, separators=(",", ":"))


def test_the_manifest_lists_each_offer_with_its_answers_in_rules_order():
    r = world()
    doc = json.loads(encode(new_save(r), r))
    assert doc["format"] == FORMAT >= 7
    assert doc["manifest"]["offers"] == [{"id": "o", "answers": ["yes", "no"]}]


def test_upgrade_6_adds_empty_offers_and_nothing_else():
    r = Rules(stores=world().stores, skills=world().skills, standing=(), curve=world().curve)
    text = encode(new_save(r), r)
    old = json.loads(as_format_6(text))
    up = UPGRADES[6](old)
    assert up == {**old, "format": 7, "manifest": {**old["manifest"], "offers": []}}
    assert rebase(as_format_6(text), r) == new_save(r)


def test_upgrade_6_refuses_an_envelope_that_already_has_offers():
    r = world()
    doc = json.loads(encode(new_save(r), r))
    with pytest.raises(StateFormatError):
        UPGRADES[6]({**doc, "format": 6})
