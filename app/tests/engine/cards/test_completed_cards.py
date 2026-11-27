"""counts.completed_cards against the per-card rule it reads in one pass (design/cards.txt, "Caps", "Retired"): a capped card
at its effective cap, a retired one, never one under its raised cap, an uncapped one, or a capped one with no state."""
from dataclasses import replace

from ashfall_app.engine import BP, CardDef, CardId, PacingCurve, Rules, Unlock, UnlockKind, new_save, validate_rules
from ashfall_app.engine.cards.cards import CardState
from ashfall_app.engine.cards.counts import completed_cards, is_completed
from ashfall_app.engine.core.segments import Segment

AT_CAP, RAISED, FREE, UNTOUCHED, GONE = (CardId(c) for c in ("at_cap", "raised", "free", "untouched", "gone"))
WORK_S = 5


def test_completed_cards_holds_exactly_the_cards_is_completed_holds_for():
    ids = (AT_CAP, RAISED, FREE, UNTOUCHED, GONE)
    r = Rules(stores=(), skills=(), standing=(), curve=PacingCurve((10**9,)),
              cards=(CardDef(AT_CAP, WORK_S, cap=2), CardDef(RAISED, WORK_S, cap=1), CardDef(FREE, WORK_S),
                     CardDef(UNTOUCHED, WORK_S, cap=1), CardDef(GONE, WORK_S)),
              opening=tuple(Unlock(UnlockKind.CARD, c) for c in ids))
    validate_rules(r)
    done = WORK_S * BP
    s = new_save(r)
    s = replace(s, cards=(CardState(AT_CAP, Segment(0, 2 * done, 0), 0), CardState(RAISED, Segment(0, done, 0), 1),
                          CardState(FREE, Segment(0, 50 * done, 0), 0)),
                unlocked=(*s.unlocked, Unlock(UnlockKind.RETIRED, GONE)))
    assert completed_cards(s, r) == {AT_CAP, GONE}
    assert completed_cards(s, r) == {c for c in ids if is_completed(s, r, c)}
