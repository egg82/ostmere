"""Two engine questions day one's content rests on, answered by test (content/team/day-one.md, "Open" 4; DESIGN.txt,
KNOWN GAPS, "READY solves only StoreValue and SkillLevel").

1. A card on a lane other than HANDS trains its skill: tapped by the player, by an order or by the queue, its XP line
   runs at a full share for its bar's time, exactly as a hands tap's does (DESIGN.txt, "Projects": its flows and XP are
   ordinary rates). Day one's Smoke lane trains Cooking.
2. A queued card waiting on a discrete requires (Unlocked, CardCount) starts at the instant the last of its
   requires turns true, whichever kind that is and whatever turned it: a trigger, a capped card's completion in the
   mix, an uncapped card's count, a lane tap's landing. The gap the DESIGN entry names is a discrete subject turning
   true at an instant that does not evaluate; every outcome lands at one that does (a COMPLETION, a TAP_DONE, a
   TRIGGER), and CardCount is solved off the work segment, so READY sees it. Planted mutants: tests/dayone/MUTANTS.txt."""
import pytest

from ashfall_app.engine import (
    BP, HANDS, QUANTITY_SCALE, ActionId, AfterTime, Amount, AtLeast, CardCount, CardDef, CardId, CardShare, Condition,
    FeatureId, Flow, LaneDef, LaneId, Mix, MixId, Order, Outcome, PacingCurve, QueueEntry, Rules, Save, SaveMix,
    SetOrders, SetQueue, SkillDef, SkillId, StandingDef, StoreDef, StoreId, StoreValue, SwitchMix, TapCard, TriggerDef,
    TriggerId, Unlock, UnlockKind, Unlocked, advance, decide, new_save, per_hour, xp,
)

Q = QUANTITY_SCALE
X, Y = StoreId("x"), StoreId("y")
K = SkillId("cooking")
RACK = LaneId("rack")
SMOKE, GATED, WORK, COUNTED, RACK_STEP = (CardId(n) for n in ("smoke", "gated", "work", "counted", "rack_step"))
F = FeatureId("f")
MAKER = ActionId("maker")
LANE_XP = 3600
"""One XP item a second at a full share: a 100 s bar trains exactly 100 items."""


def _rules(cards: list[CardDef], triggers: list[TriggerDef] | None = None, maker_per_hour: int = 0) -> Rules:
    """Gated by an opening (everything but F), since with none every Unlocked condition reads true."""
    return Rules(
        stores=(StoreDef(X, 100 * Q, 0), StoreDef(Y, 100 * Q, 0)), skills=(SkillDef(K),),
        standing=(StandingDef(MAKER, makes=(Flow(X, per_hour(maker_per_hour)),)),),
        curve=PacingCurve((10**9 * Q,)), lanes=(LaneDef(RACK),), cards=tuple(cards),
        triggers=tuple(triggers or ()),
        opening=(Unlock(UnlockKind.STORE, X), Unlock(UnlockKind.STORE, Y), Unlock(UnlockKind.SKILL, K),
                 Unlock(UnlockKind.ACTION, MAKER), *(Unlock(UnlockKind.CARD, c.id) for c in cards)))


# ---------- 1. a lane card trains its skill ----------

def _smoke_rules() -> Rules:
    return _rules([CardDef(SMOKE, 100, lane=RACK, skill=K, xp_per_hour=per_hour(LANE_XP),
                           outcome=Outcome(stores=(Amount(Y, Q),)))])


@pytest.mark.parametrize("by", ["player", "order", "queue"])
def test_a_lane_card_trains_its_skill_however_it_is_tapped(by: str):
    r = _smoke_rules()
    s = new_save(r)
    if by == "player":
        s = decide(s, r, 0, TapCard(SMOKE))
    elif by == "order":
        s = decide(s, r, 0, SetOrders((Order(AtLeast(StoreValue(Y), 0, 0), TapCard(SMOKE)),)))
    else:
        s = decide(s, r, 0, SetQueue((QueueEntry(TapCard(SMOKE), AtLeast(CardCount(SMOKE), 1, 1)),)))
    assert xp(s, r, K, 50) == 50 * Q
    assert xp(s, r, K, 100) == 100 * Q   # the whole bar's time, and no more once it lands (the queue pops at 1)
    if by != "order":
        assert xp(s, r, K, 400) == 100 * Q


def test_a_lane_card_trains_while_the_hands_run_the_mix():
    """The lane runs beside the hands: a mix on HANDS takes nothing from the lane's XP line."""
    hands = CardId("hands_card")
    r = _rules([CardDef(SMOKE, 100, lane=RACK, skill=K, xp_per_hour=per_hour(LANE_XP)),
                CardDef(hands, 10, makes=(Flow(X, per_hour(1)),))])
    s = decide(new_save(r), r, 0, SaveMix(Mix(MixId("m"), (CardShare(hands, BP),))))
    s = decide(decide(s, r, 0, SwitchMix(MixId("m"))), r, 0, TapCard(SMOKE))
    assert xp(s, r, K, 100) == 100 * Q


# ---------- 2. a queued card on discrete requires ----------

def _queued(r: Rules, s: Save) -> Save:
    return decide(s, r, s.time, SetQueue((QueueEntry(TapCard(GATED), AtLeast(CardCount(GATED), 1, 1)),)))


def _start(s: Save, r: Rules, horizon: int = 2_000) -> int | None:
    """The first second the hands hold GATED, stepping a second at a time, each step carried on from the last."""
    for t in range(s.time, horizon):
        s = advance(s, r, t)
        if next(ls for ls in s.lanes if ls.lane == HANDS).card == GATED:
            return t
    return None


def _gated(*requires: Condition) -> CardDef:
    return CardDef(GATED, 5, cap=1, requires=requires)


ON_F = AtLeast(Unlocked(Unlock(UnlockKind.FEATURE, F)), 1, 1)
UNLOCK_F = Outcome(unlocks=(Unlock(UnlockKind.FEATURE, F),))


def _feature_vocabulary() -> list[CardDef]:
    """A card whose finish names F, so F is in the feature vocabulary the rules accept (never run here)."""
    return [CardDef(CardId("names_f"), 1, cap=1, finished=UNLOCK_F)]


def test_an_unlock_by_a_trigger_starts_the_queued_card_at_once():
    r = _rules([_gated(ON_F), *_feature_vocabulary()],
               triggers=[TriggerDef(TriggerId("t"), AfterTime(100), UNLOCK_F)])
    assert _start(_queued(r, new_save(r)), r) == 100


def test_an_unlock_by_a_capped_card_finishing_in_the_mix_starts_it_at_once():
    r = _rules([_gated(ON_F), CardDef(WORK, 40, cap=1, finished=UNLOCK_F)])
    s = decide(new_save(r), r, 0, SaveMix(Mix(MixId("m"), (CardShare(WORK, BP),))))
    s = _queued(r, decide(s, r, 0, SwitchMix(MixId("m"))))
    assert _start(s, r) == 40


def test_a_count_of_an_uncapped_card_in_the_mix_starts_it_at_the_count():
    """An uncapped card's completions are not events; CardCount is solved off its work, so READY falls there."""
    r = _rules([_gated(AtLeast(CardCount(COUNTED), 2, 2)), CardDef(COUNTED, 30)])
    s = decide(new_save(r), r, 0, SaveMix(Mix(MixId("m"), (CardShare(COUNTED, BP),))))
    s = _queued(r, decide(s, r, 0, SwitchMix(MixId("m"))))
    assert _start(s, r) == 60


def test_a_count_and_an_unlock_by_a_lane_tap_landing_start_it_at_the_landing():
    r = _rules([_gated(AtLeast(CardCount(RACK_STEP), 1, 1), ON_F), CardDef(RACK_STEP, 70, lane=RACK, cap=1,
                                                                            finished=UNLOCK_F)])
    s = _queued(r, decide(new_save(r), r, 0, TapCard(RACK_STEP)))
    assert _start(s, r) == 70


@pytest.mark.parametrize("unlock_at, store_at, expected", [(50, 300, 300), (300, 100, 300)])
def test_a_discrete_and_a_store_requires_start_it_when_the_last_holds(unlock_at: int, store_at: int, expected: int):
    """Day one's Take stock shape: a feature and a store level, whichever comes last. The maker fills x at 36 items an
    hour (one per 100 s); x >= store_at / 100 items is reached at store_at."""
    r = _rules([_gated(ON_F, AtLeast(StoreValue(X), store_at // 100 * Q, store_at // 100 * Q)), *_feature_vocabulary()],
               triggers=[TriggerDef(TriggerId("t"), AfterTime(unlock_at), UNLOCK_F)], maker_per_hour=36)
    assert _start(_queued(r, new_save(r)), r) == expected
