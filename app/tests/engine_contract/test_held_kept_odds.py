"""Invariant 115 (engine DESIGN.txt, "ENTRIES HELD WHILE A CARD RUNS": "A tap keeps its odds"; FIGHTS): a HANDS fight tap
started at T pays loss_bp as read on the save just before T until it lands, whatever held entries come or go
meanwhile, the entries the tap itself yields included; mixed fights, fights on a repeating or declared-lane tap, and
standing fights read the live stack and move at the instant."""
from ashfall_app.engine import (
    BP, QUANTITY_SCALE as Q, CardShare, CardId, Mix, Rules, Save, SaveMix, TapCard, advance, decide, new_save, value, view,
)
from held_world import GH, HF, HFR, HM, HURT, LOST, RAID, hands, ja, kills, loss, odds_loss, ruled_fight, world
from town_mix_world import always, orders


def fight_loss(s: Save, r: Rules, runner: CardId | str) -> int:
    return next(f.loss_bp for f in view(s, r).fights if f.runner == runner)


@kills(1, 2, 3, 4, 6, 12, 13, 14, 16)
def test_a_hands_fight_tap_pays_the_odds_read_before_it_started_whatever_it_yields_or_is_added():
    """gh holds 2500 in the hands' mix. At 10 the player taps hf (100 s): gh's share is yielded, so the raid's odds
    fall back to base at once, while hf keeps the odds it showed before the tap. A SaveMix at 60 doubles gh's share
    (live odds move, hf's do not); when hf lands at 110 it has paid its kept odds and shows the live ones."""
    r = world()
    s = advance(hands(r, (GH, 5000)), r, 10)
    kept = odds_loss(2500)
    assert fight_loss(s, r, HF) == kept == loss(s, r), "before the tap hf shows the live odds"
    s = decide(s, r, 10, TapCard(HF))
    for t in (10, 59):
        a = advance(s, r, t)
        assert (fight_loss(a, r, HF), fight_loss(a, r, RAID)) == (kept, odds_loss(0)), t
    s = decide(advance(s, r, 60), r, 60, SaveMix(Mix(HM, (CardShare(GH, BP),))))
    mid = advance(s, r, 109)
    assert (fight_loss(mid, r, HF), fight_loss(mid, r, RAID)) == (kept, odds_loss(0)), "yielded while the tap runs"
    done = advance(s, r, 110)
    assert fight_loss(done, r, HF) == fight_loss(done, r, RAID) == odds_loss(5000)
    assert abs(value(done, r, LOST, 110) - Q * kept // BP) <= 2, "the lost tally is what the kept odds pay"
    assert abs(value(done, r, HURT, 110) - 2 * Q * kept // BP) <= 4


@kills(3, 4, 16)
def test_a_held_entry_that_comes_during_a_tap_moves_the_live_odds_and_the_kept_ones_only_from_its_end():
    """la joins at 40 (ga holds 4000 from then): the raid's odds move at 40; hf, tapped at 0 (lands 100), keeps the
    odds it started at until 100, then shows the live ones."""
    r = world((ja(40),))
    s = decide(new_save(r), r, 0, TapCard(HF))
    kept = odds_loss(0)
    assert fight_loss(advance(s, r, 39), r, RAID) == kept
    for t in (40, 99):
        a = advance(s, r, t)
        assert (fight_loss(a, r, HF), fight_loss(a, r, RAID)) == (kept, odds_loss(4000)), t
    done = advance(s, r, 100)
    assert fight_loss(done, r, HF) == odds_loss(4000)
    assert abs(value(done, r, LOST, 100) - Q * kept // BP) <= 2


@kills(3, 4)
def test_a_fight_on_a_repeating_tap_reads_the_live_stack_and_moves_at_the_instant():
    """hfr on lb under lb's always rule is a repeating tap: when la's guard starts holding at 40, hfr's odds move then."""
    r = world((ja(40),), extra=(ruled_fight(),))
    s = decide(new_save(r), r, 0, orders(always(HFR)))
    assert fight_loss(advance(s, r, 39), r, HFR) == odds_loss(0)
    for t in (40, 41, 99):
        assert fight_loss(advance(s, r, t), r, HFR) == odds_loss(4000), t
