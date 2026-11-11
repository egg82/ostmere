"""Drains, part four: the codec and the digest (engine DESIGN.txt, "DRAINS", invariant 128). Written blind from that part
and the public interface; the `kills` marker names the rows of MUTANTS_drains.txt each test must turn red for.

fixtures/pre_drains.json is the output of the engine at the commit before drains existed (its rules digest, its
manifest and one encoded save) for the rules `pinned()` builds: the proof that rules without a drain are unchanged."""
import json
from dataclasses import fields
from pathlib import Path

import pytest

from ashfall_app.engine import (
    FORMAT, QUANTITY_SCALE as Q, Amount, CardDef, Save, advance, decode, encode, new_save, rebase, rules_digest,
)
from ashfall_app.engine.codec import manifest
from drains_world import X, X2, cure, kills, mixed, pinned, tapped, world
from tests.format8 import as_format_8

PIN = Path(__file__).resolve().parent / "fixtures" / "pre_drains.json"


@kills(13)
def test_rules_without_a_drain_keep_their_digest_manifest_and_saves_text():
    pin = json.loads(PIN.read_text())
    r, s = pinned()
    assert rules_digest(r) == pin["digest"]
    assert json.loads(json.dumps(manifest(r))) == pin["manifest"]
    assert as_format_8(encode(s, r)) == pin["encoded"]   # the pin is a format 8 text
    assert rebase(pin["encoded"], r) == s


@kills(12)
@pytest.mark.parametrize("other", [
    cure(11 * Q), cure(10 * Q, drains=(Amount(X, 10 * Q), Amount(X2, Q))), cure(10 * Q, drains=(Amount(X2, 10 * Q),)),
], ids=["other amount", "second drain", "other store"])
def test_adding_or_changing_a_drain_changes_the_rules_digest(other: CardDef):
    without = rules_digest(world(cure(10 * Q, drains=())))
    one = rules_digest(world(cure()))
    assert one != without and rules_digest(world(other)) not in (without, one)


@kills(12)
def test_the_manifest_and_save_fields_do_not_move_for_a_drain():
    r = world(cure())
    assert json.loads(json.dumps(manifest(r))) == json.loads(json.dumps(manifest(world(cure(drains=())))))
    assert '"drains"' not in json.dumps(manifest(r))
    assert FORMAT == 9 and "drains" not in {f.name for f in fields(Save)}


@kills(12)
@pytest.mark.parametrize("how", ["new", "tapped", "mixed, mid-drain", "mixed, at zero"])
def test_a_save_under_rules_with_drains_round_trips(how: str):
    r = world(cure(), x0=4 * Q)
    s = {"new": lambda: new_save(r), "tapped": lambda: advance(tapped(r), r, 30),
         "mixed, mid-drain": lambda: advance(mixed(r), r, 30), "mixed, at zero": lambda: advance(mixed(r), r, 70)}[how]()
    assert decode(encode(s, r), r) == s
    assert encode(decode(encode(s, r), r), r) == encode(s, r)
