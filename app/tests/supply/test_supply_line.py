"""The supply line's running shapes on the fixture outpost (chapter.py): the upkeep draws the outpost's store and
pauses when it is dry, and picks up again when the filler refills it; and the same line lands the same tallies
whether the player watches it (a look at every step) or is away (one long advance)."""
from ashfall_app.engine import (
    BP, QUANTITY_SCALE as Q, CardShare, CardId, Mix, MixId, Rules, Save, SaveMix, SwitchMix, TapCard, advance, decide, new_save, value_at,
    view,
)
from tests.supply.chapter import FOUGHT, GATHER, HAUL, HOLD_A, HOLD_B, HOUR, KEPT, KEEP, LOST, POST, rules

H = HOUR


def store(s: Save, which: str, at: int | None = None) -> float:
    seg = next(x.segment for x in s.stores if x.store == which)
    return value_at(seg, s.time if at is None else at) / Q


def gathering(r: Rules, at: int = 0) -> Save:
    mix = Mix(MixId("gather_only"), (CardShare(GATHER, BP),))
    return decide(decide(new_save(r), r, at, SaveMix(mix)), r, at, SwitchMix(mix.id))


def haul(s: Save, r: Rules, at: int) -> Save:
    """Tap the filler at `at`: it runs its hour and lands, the gatherer's mix back after."""
    s = advance(s, r, at)
    return decide(s, r, at, TapCard(HAUL))


def test_the_upkeep_pauses_dry_and_resumes_when_the_filler_refills_the_outposts_store() -> None:
    r = rules(fight=False)
    s = advance(gathering(r), r, 2 * H)
    assert store(s, str(POST)) == 0 and store(s, str(KEPT)) == 0, "dry from the start: the upkeep has nothing to draw"
    s = haul(s, r, 2 * H)
    s = advance(s, r, 3 * H)
    assert store(s, str(POST)) + store(s, str(KEPT)) == 4, "the filler's 4 went to the store and the upkeep"
    assert store(s, str(KEPT)) > 0, "the upkeep ran as soon as there was something to draw"
    s = advance(s, r, 12 * H)
    assert store(s, str(POST)) == 0 and store(s, str(KEPT)) == 4, "the 4 lasted 8 hours and the upkeep stopped there"
    s = haul(s, r, 12 * H)
    s = advance(s, r, 24 * H)
    assert store(s, str(KEPT)) == 8, "it picked up the hour the store was refilled and ran the 4 again"


def test_the_upkeep_never_runs_past_what_the_store_holds() -> None:
    """The control: with the upkeep left out the same refill leaves the outpost's store whole."""
    r = rules(fight=False, upkeep=False)
    s = advance(haul(advance(gathering(r), r, 2 * H), r, 2 * H), r, 8 * H)
    assert store(s, str(POST)) == 4 and KEEP not in {a.id for a in r.standing}


def line(r: Rules, hold: CardId | None = HOLD_A):
    """The filler and a hold card (or, with none, a larger filler) in a mix beside the gatherer, with the upkeep and the
    raid standing."""
    held = (CardShare(HAUL, BP // 4), CardShare(hold, BP // 4)) if hold else (CardShare(HAUL, BP // 2),)
    mix = Mix(MixId("line"), (CardShare(GATHER, BP // 2), *held))
    s = advance(new_save(r), r, H // 2)
    return decide(decide(s, r, H // 2, SaveMix(mix)), r, H // 2, SwitchMix(mix.id))


def tallies(s: Save) -> dict[str, float]:
    return {str(x.store): store(s, str(x.store)) for x in s.stores}


UNTIL = 12 * H
STEP = 60 * 7


def watched(r: Rules, tap_at: int | None = None) -> Save:
    """The line with a look at every step. `tap_at`: a hold card tapped by hand then, which the away player never does."""
    s = line(r)
    for t in range(H // 2 + STEP, UNTIL, STEP):
        s = advance(s, r, t)
        view(s, r)
        if t == tap_at:
            s = decide(s, r, t, TapCard(HOLD_B))
    return advance(s, r, UNTIL)


def test_a_player_watching_and_one_away_land_the_same_tallies() -> None:
    r = rules()
    away = advance(line(r), r, UNTIL)
    assert tallies(watched(r)) == tallies(away)
    t = tallies(away)
    assert t[str(KEPT)] > 0 and t[str(FOUGHT)] > 0 and t[str(LOST)] > 0, "the upkeep and the raid both ran"


def test_a_tap_made_only_while_watching_lands_other_tallies() -> None:
    """The control: the comparison above can tell, since a hand tap on one side alone moves the tallies."""
    r = rules()
    assert tallies(watched(r, tap_at=H // 2 + STEP * 90)) != tallies(advance(line(r), r, UNTIL))


def lost_share(hold: CardId | None) -> float:
    r = rules()
    s = advance(line(r, hold), r, 30 * H)
    return store(s, str(LOST)) / store(s, str(FOUGHT))


def test_each_hold_card_running_holds_the_hands_side_so_fewer_raids_are_lost() -> None:
    bare = lost_share(None)
    assert bare > 0 and lost_share(HOLD_A) < bare and lost_share(HOLD_B) < bare
