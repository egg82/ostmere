"""Forecast.hands_free_at (engine design/, "Hands free"): the first instant the player's work stops holding the
hands, after a forecast that began with it holding them. Behaviour-level: each case is a save the player set up, read
through the public forecast."""
from ashfall_app.engine import (
    HANDS, QUANTITY_SCALE, AtLeast, AtMost, CardCount, CardDef, CardId, Flow, Mix, MixId, CardShare, Order, PacingCurve,
    QueueEntry, Rules, Save, SaveMix, SetOrders, SetQueue, SkillDef, SkillId, StoreDef, StoreId, StoreValue, SwitchMix,
    TapCard, advance, decide, forecast, new_save,
)

Q = QUANTITY_SCALE
X = StoreId("x")
LONG, SHORT, CHORE, IDLE = CardId("long"), CardId("short"), CardId("chore"), CardId("idle")
MIX = MixId("m")


def world() -> Rules:
    return Rules(
        stores=(StoreDef(X, 1000 * Q),), skills=(SkillDef(SkillId("k")),), standing=(),
        curve=PacingCurve((10**15,)), max_firings_per_instant=1000, lanes=(),
        cards=(CardDef(LONG, 3600, makes=(Flow(X, 100 * Q),)), CardDef(SHORT, 60), CardDef(CHORE, 300),
               CardDef(IDLE, 100, makes=(Flow(X, 100 * Q),))),
        chips=(), triggers=(), opening=None,
    )


R = world()


def free_at(s: Save, until: int) -> int | None:
    return forecast(s, R, until).hands_free_at


def tapped(card: CardId, t: int = 0) -> Save:
    return decide(new_save(R), R, t, TapCard(card))


def queued(*entries: QueueEntry) -> Save:
    return decide(new_save(R), R, 0, SetQueue(entries))


def test_a_tap_the_player_started_frees_the_hands_where_it_lands():
    assert free_at(tapped(LONG), 7200) == 3600


def test_nothing_the_player_gave_means_no_free_moment():
    assert free_at(new_save(R), 7200) is None


def test_a_tap_landing_past_until_is_not_known():
    assert free_at(tapped(LONG), 3599) is None
    assert free_at(tapped(LONG), 3600) == 3600


def test_the_queue_holds_the_hands_until_its_last_entry_pops():
    s = queued(QueueEntry(TapCard(SHORT), AtLeast(CardCount(SHORT), 3, 3)))
    assert free_at(s, 7200) == 180


def test_a_goal_stint_holds_the_hands_while_its_mix_runs():
    """A stint taps nothing: its mix runs on the hands until its goal, and it is the player's work all the same."""
    s = decide(new_save(R), R, 0, SaveMix(Mix(MIX, (CardShare(IDLE, 10_000),))))
    s = decide(s, R, 0, SetQueue((QueueEntry(SwitchMix(MIX), AtLeast(StoreValue(X), 50 * Q, 50 * Q)),)))
    at = free_at(s, 7200)
    assert at is not None and 0 < at < 7200
    assert advance(s, R, at - 1).queue and not advance(s, R, at).queue


def test_a_queued_tap_still_running_after_its_entry_popped_holds_the_hands_to_its_landing():
    s = queued(QueueEntry(TapCard(LONG), AtLeast(StoreValue(X), 10 * Q, 10 * Q)))
    assert advance(s, R, 3599).queue == (), "control: the entry popped partway through the tap"
    assert free_at(s, 7200) == 3600


def test_a_rule_taking_the_hands_as_the_players_tap_lands_does_not_hold_them():
    s = decide(tapped(LONG), R, 0, SetOrders((Order(AtMost(CardCount(CHORE), 0, 0), TapCard(CHORE)),)))
    assert advance(s, R, 3600).lanes[0].card == CHORE, "control: the rule tapped as the hands came free"
    assert free_at(s, 7200) == 3600


def test_a_rules_tap_alone_is_not_the_players_work():
    s = decide(new_save(R), R, 0, SetOrders((Order(AtMost(CardCount(CHORE), 0, 0), TapCard(CHORE)),)))
    assert s.lanes[0].lane == HANDS and s.lanes[0].card == CHORE
    assert free_at(s, 7200) is None


def test_the_queue_running_on_after_a_tap_keeps_the_hands_held():
    s = decide(tapped(LONG), R, 0, SetQueue((QueueEntry(TapCard(SHORT), AtLeast(CardCount(SHORT), 2, 2)),)))
    assert free_at(s, 7200) == 3600 + 120


def test_a_forecast_begun_later_on_the_same_path_finds_the_same_moment():
    for s in (tapped(LONG), queued(QueueEntry(TapCard(SHORT), AtLeast(CardCount(SHORT), 3, 3)))):
        first = free_at(s, 7200)
        assert first is not None
        assert free_at(advance(s, R, first - 1), 7200) == first
        assert free_at(advance(s, R, first), 7200) is None, "already free where it begins"


def test_a_rules_tap_still_running_after_the_rule_let_go_is_still_the_rules():
    """The rule taps the long card and lets go partway through it; the player's stint, whose goal that tap reaches,
    pops before the tap lands. The hands are free at the pop: the tap running on is the rule's."""
    s = decide(new_save(R), R, 0, SaveMix(Mix(MIX, (CardShare(IDLE, 10_000),))))
    s = decide(s, R, 0, SetOrders((Order(AtMost(StoreValue(X), 10 * Q, 10 * Q), TapCard(LONG)),)))
    s = decide(s, R, 0, SetQueue((QueueEntry(SwitchMix(MIX), AtLeast(StoreValue(X), 20 * Q, 20 * Q)),)))
    assert s.lanes[0].card == LONG
    at = free_at(s, 7200)
    assert at is not None and at < 3600
    gone = advance(s, R, at)
    assert gone.queue == () and gone.lanes[0].card == LONG and gone.latches == (False,), \
        "control: the stint popped while the rule's tap ran on with its rule let go"


def test_a_rule_retapping_the_card_the_player_tapped_takes_over_at_its_landing():
    s = decide(tapped(CHORE), R, 0, SetOrders((Order(AtLeast(CardCount(CHORE), 1, 1), TapCard(CHORE)),)))
    assert advance(s, R, 301).lanes[0].card == CHORE, "control: the rule tapped the same card again"
    assert free_at(s, 7200) == 300


def test_a_stint_holds_the_hands_through_an_instant_where_nothing_is_tapped():
    """A rule's chore lands partway through the stint: the hands run no tap then, and the stint still holds them."""
    s = decide(new_save(R), R, 0, SaveMix(Mix(MIX, (CardShare(IDLE, 10_000),))))
    s = decide(s, R, 0, SetOrders((Order(AtMost(CardCount(CHORE), 0, 0), TapCard(CHORE)),)))
    s = decide(s, R, 0, SetQueue((QueueEntry(SwitchMix(MIX), AtLeast(StoreValue(X), 50 * Q, 50 * Q)),)))
    assert s.lanes[0].card == CHORE
    at = free_at(s, 7200)
    assert at is not None and at > 300
    assert advance(s, R, at - 1).queue and not advance(s, R, at).queue
