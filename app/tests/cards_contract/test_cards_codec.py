"""Invariant 30 with cards, and the codec's FORMAT 8 (old saves decode as StateFormatError): saves holding card work
mid-bar, a raised cap, a tap mid-bar and a greyed mix round-trip exactly (a recorded end:
test_cards_end.py); equal saves and
only equal saves encode alike; any text encode did not give for these rules, an older format's envelope included, raises
StateFormatError (DESIGN.txt, "Codec"; codec.py)."""
import json
import re

import pytest
from hypothesis import given

from ashfall_app.engine import (
    FORMAT, HANDS, Amount, CapRaise, CardDef, CardId, LineKey, Outcome, Rules, Save, StateFormatError, StoreDef,
    StoreId, advance, decode, encode, new_save, rules_digest,
)
from cards_gen import Scenario, few, play, scenario_st, timeline
from cards_world import Q, RACK, lane, raised, rich_rules, rich_saves, rules, tap, with_mix, work

X, Y = StoreId("x"), StoreId("y")
C, RZ, F = CardId("c"), CardId("rz"), CardId("f")


def special():
    """Saves showing each new kind of state: card work mid-bar, a tap mid-bar, a raised cap, a greyed
    mix. Each is checked to hold its kind, so a codec test cannot pass over a state the run never reached."""
    r = rules([StoreDef(X, 100 * Q, 10 * Q), StoreDef(Y, 100 * Q, Q)],
              cards=[CardDef(C, 100, cap=2, inputs=(Amount(X, Q),)),
                     CardDef(RZ, 50, lane=RACK, cap=5, outcome=Outcome(raises=(CapRaise(C, 1),))),
                     CardDef(F, 100, inputs=(Amount(Y, Q),), failed_line=LineKey("f.failed"))],
              lanes=[RACK])
    s = with_mix(new_save(r), r, 0, {C: 5000})
    mid = advance(s, r, 50)
    tapped = advance(tap(mid, r, 50, F), r, 80)
    greyed = advance(s, r, 400)
    raised_ = advance(tap(greyed, r, 400, RZ), r, 460)
    assert work(mid, C).start_value > 0
    assert lane(tapped, HANDS).card == F and work(tapped, F).start_value > 0
    assert work(greyed, C).rate == 0 and raised(raised_, C) == 1
    return r, [s, mid, tapped, greyed, raised_]


@pytest.fixture(scope="module")
def cases():
    return [(rich_rules(), rich_saves()), special()]


def test_saves_round_trip(cases: list[tuple[Rules, list[Save]]]):
    """Invariant 30: decode(encode(s, r), r) == s for every kind of state."""
    for r, saves in cases:
        for s in saves:
            assert decode(encode(s, r), r) == s, s.time


def test_the_text_is_canonical_json_of_format_9_carrying_the_digest(cases: list[tuple[Rules, list[Save]]]):
    """codec: sorted keys, no whitespace, FORMAT 9, rules_digest(r) and the manifest in the envelope, and the card state
    tagged by its class."""
    assert FORMAT == 9
    for r, saves in cases:
        for s in saves:
            text = encode(s, r)
            doc = json.loads(text)
            assert json.dumps(doc, sort_keys=True, separators=(",", ":")) == text
            assert doc["format"] == 9 and doc["rules"] == rules_digest(r)
            assert set(doc) == {"format", "rules", "manifest", "save"}
            assert doc["manifest"]["cards"] == [{"id": c.id, "work_s": c.work_s, "lane": c.lane, "cap": c.cap}
                                                for c in r.cards]
            assert re.fullmatch(r"[0-9a-f]{64}", doc["rules"])
    r, saves = cases[1]
    assert '"@":"CardState"' in encode(saves[1], r) and '"@":"LaneState"' in encode(saves[2], r)


def test_an_older_format_save_raises(cases: list[tuple[Rules, list[Save]]]):
    """FORMAT is 9 (a mix without holds), and an envelope of another format (the projects-era 1, the cards-era 2, the
    end's 3, the manifest's 4, chips_seen's 5, no failed attempt's 6, the offers' 7, a tap's kept speed's 8, or 10) raises StateFormatError even when its save
    part is a save of these rules."""
    for r, saves in cases:
        doc = json.loads(encode(saves[-1], r))
        for other in (1, 2, 3, 4, 5, 6, 7, 8, 10):
            bad = json.dumps({**doc, "format": other}, sort_keys=True, separators=(",", ":"))
            assert bad != encode(saves[-1], r)
            with pytest.raises(StateFormatError):
                decode(bad, r)


def test_equal_iff_same_text(cases: list[tuple[Rules, list[Save]]]):
    """Invariant 30: encode(s1) == encode(s2) iff s1 == s2."""
    for r, saves in cases:
        texts = [encode(s, r) for s in saves]
        for i, a in enumerate(saves):
            for j, b in enumerate(saves):
                assert (texts[i] == texts[j]) == (a == b), (i, j)


def test_text_encode_did_not_give_raises(cases: list[tuple[Rules, list[Save]]]):
    """Invariant 30: truncated, extended, reformatted, wrongly shaped text, or another digest, raises StateFormatError
    and never another error or a save."""
    r, saves = cases[1]
    text = encode(saves[2], r)
    digest = rules_digest(r)
    doc = json.loads(text)
    for bad in ["", "{", "null", "[]", "{}", text[:-1], text[: len(text) // 2], text + "x", text + "\n",
                json.dumps(doc, sort_keys=True, indent=1), json.dumps(doc, sort_keys=True),
                text.replace(digest, "0" * 64), text.replace('"@":"CardState"', '"@":"ProjectState"', 1)]:
        assert bad != text
        with pytest.raises(StateFormatError):
            decode(bad, r)


@few(8)
@given(sc=scenario_st())
def test_random_saves_round_trip(sc: Scenario):
    """Invariant 30 over random card worlds: every sampled save round-trips, and equal-iff-same-text holds among them."""
    s = play(sc)
    saves = timeline(s, sc.rules, sc.offsets, events=2)
    texts = [encode(x, sc.rules) for x in saves]
    for x, t in zip(saves, texts):
        assert decode(t, sc.rules) == x
    for i in range(len(saves)):
        for j in range(len(saves)):
            assert (texts[i] == texts[j]) == (saves[i] == saves[j])
