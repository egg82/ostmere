"""A chip's lines ("Chips"): its on_line is emitted the first time the chip shows in a save and never again, however
often it clears and shows again, whether its latch rising or its unlock showed it; its off_line each time it stops
showing. The chip itself shows every time."""
import json

from ashfall_app.engine import (
    Amount, AtMost, CardDef, CardId, ChipDef, ChipId, Flow, LineKey, Outcome, Save, StandingDef, StoreDef, StoreId,
    StoreValue, ActionId, Unlock, UnlockKind, advance, advance_logged, encode, new_save, rebase, view,
)
from ashfall_app.engine.rules import Rules
from cards_world import Q, rules, tap

E, R, U, TIRED, DRAIN = StoreId("e"), CardId("rest"), CardId("notice"), ChipId("tired"), ActionId("drain")
ON, OFF = LineKey("tired.on"), LineKey("tired.off")


def world(locked: bool = False) -> Rules:
    """e drains one a second from ten; tired shows at three or less and clears at six or more; each rest, a second's
    tap, puts seven back. Locked: the chip is shown only once notice, a one-off, unlocks it."""
    opening = [Unlock(UnlockKind.CARD, R), Unlock(UnlockKind.CARD, U), Unlock(UnlockKind.ACTION, DRAIN)]
    return rules(
        [StoreDef(E, 10 * Q, 10 * Q)],
        standing=[StandingDef(DRAIN, costs=(Flow(E, Q),))],
        cards=[CardDef(R, 1, outcome=Outcome(stores=(Amount(E, 7 * Q),))),
               CardDef(U, 1, cap=1, outcome=Outcome(unlocks=(Unlock(UnlockKind.CHIP, TIRED),)))],
        chips=[ChipDef(TIRED, AtMost(StoreValue(E), 3 * Q, 6 * Q), on_line=ON, off_line=OFF)],
        opening=opening if locked else None)


def cycles(r: Rules, n: int, s: Save, t: int) -> tuple[list[str], int]:
    """n rounds from s at t of: run until tired shows, then rest until it clears. The keys logged, and how many rounds
    the chip showed in."""
    keys, shown = list[str](), 0
    for _ in range(n):
        for want in (True, False):
            while (TIRED in view(s, r).chips) != want:
                t += 1
                step = advance_logged(s, r, t)
                s, keys = step.save, keys + [ln.key for ln in step.lines]
            if want:
                shown += 1
                s = tap(s, r, t, R)
    return keys, shown


def test_the_on_line_plays_the_first_time_the_chip_shows_and_never_again():
    r = world()
    keys, shown = cycles(r, 4, new_save(r), 0)
    assert shown == 4
    assert keys.count(ON) == 1 and keys.index(ON) < keys.index(OFF)
    assert keys.count(OFF) == 4


def test_an_unlock_that_shows_the_chip_plays_its_on_line_once_too():
    r = world(locked=True)
    s = advance(new_save(r), r, 7)
    assert TIRED not in view(s, r).chips
    keys, shown = cycles(r, 4, tap(s, r, 7, U), 7)
    assert shown == 4
    assert keys.count(ON) == 1 and keys.index(ON) < keys.index(OFF)
    assert keys.count(OFF) == 4


def test_a_format_4_save_whose_chip_showed_never_plays_its_on_line_again():
    """Upgrade 4 to 5: a chip in a format 4 save's unlock set counts as seen, so a save that played the line before the
    upgrade does not play it again when the chip next shows."""
    r = world(locked=True)
    s = advance(tap(advance(new_save(r), r, 7), r, 7, U), r, 8)
    s = advance(tap(s, r, 8, R), r, 10)
    assert TIRED not in view(s, r).chips
    doc = json.loads(encode(s, r))
    del doc["save"]["chips_seen"]
    del doc["manifest"]["offers"]
    doc["save"]["lanes"] = [{**{k: v for k, v in ls.items() if k != "speed"}, "failed": False, "failed_timer": None}
                            for ls in doc["save"]["lanes"]]
    old = json.dumps({**doc, "format": 4}, sort_keys=True, separators=(",", ":"))
    s2 = rebase(old, r)
    assert s2 == s
    keys, shown = cycles(r, 2, s2, s2.time)
    assert shown == 2 and ON not in keys
