"""Which card wrote a line ("Lines", engine.Line.card): a completion's own line, its outcome's and finished's lines and a
failed tap's line name the card, however it was run; a chip's line and a trigger's name none. The page puts a line
the player's tap wrote on that card (docs/design/opening-screen.md, "Cards")."""
from ashfall_app.engine import (
    AtLeast, CardCount, CardDef, CardId, ChipDef, ChipId, Line, LineKey, Outcome, StoreDef, StoreId, StoreValue, TriggerDef,
    TapCard, TriggerId, Unlock, UnlockKind, Amount, advance_logged, decide_logged, new_save,
)
from ashfall_app.engine.rules import Rules
from cards_world import Q, rules, tap, with_mix

X, Y = StoreId("x"), StoreId("y")
CC, CU, CF, CK = (CardId(n) for n in ("cc", "cu", "cf", "ck"))
WARM = ChipId("warm")


def world() -> Rules:
    """cc: capped, own lines plus outcome and finished lines; cu: uncapped with a tap line; cf: short of its input,
    so a tap fails; ck: its outcome unlocks a chip whose latch already holds, which then shows with its on_line. A
    trigger fires on cu's second completion."""
    return rules(
        [StoreDef(X, 100 * Q, 0), StoreDef(Y, 100 * Q, 5 * Q)],
        cards=[CardDef(CC, 100, cap=2, lines=(LineKey("c.1"), LineKey("c.2")),
                       outcome=Outcome(lines=(LineKey("c.out"),)), finished=Outcome(lines=(LineKey("c.fin"),))),
               CardDef(CU, 100, lines=(LineKey("cu.tap"),)),
               CardDef(CF, 100, inputs=(Amount(X, Q),)),
               CardDef(CK, 100, cap=1, outcome=Outcome(unlocks=(Unlock(UnlockKind.CHIP, WARM),)))],
        chips=[ChipDef(WARM, AtLeast(StoreValue(Y), Q, Q), (), on_line=LineKey("warm.on"))],
        triggers=[TriggerDef(TriggerId("t"), AtLeast(CardCount(CU), 2, 2), Outcome(lines=(LineKey("t.fired"),)))],
        opening=[Unlock(UnlockKind.CARD, c) for c in (CC, CU, CF, CK)])


def cards(lines: tuple[Line, ...]) -> list[tuple[str, CardId | None]]:
    return [(ln.key, ln.card) for ln in lines]


def test_a_tapped_capped_completion_names_its_card_on_every_line_it_wrote():
    r = world()
    step = advance_logged(tap(new_save(r), r, 0, CC), r, 100)
    assert cards(step.lines) == [("c.1", CC), ("c.out", CC)]


def test_a_mixed_completion_names_its_card_too():
    """The engine says who wrote the line, not who ran it: the page decides that only a player's tap puts it on the card."""
    r = world()
    step = advance_logged(with_mix(new_save(r), r, 0, {CC: 10_000}), r, 200)
    assert cards(step.lines) == [("c.1", CC), ("c.out", CC), ("c.2", CC), ("c.out", CC), ("c.fin", CC)]


def test_an_uncapped_tap_line_names_its_card_and_a_failed_tap_has_none():
    r = world()
    assert cards(advance_logged(tap(new_save(r), r, 0, CU), r, 100).lines) == [("cu.tap", CU)]
    assert cards(decide_logged(new_save(r), r, 0, TapCard(CF)).lines) == []


def test_a_chip_line_an_outcome_shows_and_a_trigger_line_name_no_card():
    r = world()
    step = advance_logged(tap(new_save(r), r, 0, CK), r, 100)
    assert cards(step.lines) == [("warm.on", None)]
    s = tap(new_save(r), r, 0, CU)
    s = tap(advance_logged(s, r, 100).save, r, 100, CU)
    assert cards(advance_logged(s, r, 200).lines) == [("cu.tap", CU), ("t.fired", None)]
