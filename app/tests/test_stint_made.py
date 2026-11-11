"""What a goal stint's save gained while it ran (CONTRACT.txt, "RULE RUNS", "Made"; "GOAL STINTS"): the engine reports
the levels of the stores the stint's mix makes when the stint starts and when it lands, and the saves layer carries the
start levels on the entry, turns the pair into `made` at the landing, and stores both."""
import dataclasses

from ashfall_app import engine as e
from ashfall_app.api import goal_models as g
from ashfall_app.api.convert import from_condition
from ashfall_app.api.goalrows import goal_rows
from ashfall_app.engine import BP, CardDef, CardId, CardShare, Mix, MixId, Outcome, QueueEntry, Rules, Save, SaveMix, SetQueue, SwitchMix
from ashfall_app.engine.cards import Amount
from ashfall_app.engine.codec import Json
from ashfall_app.engine.units import units
from ashfall_app.saves.ruleruns import MADE_KEPT, RuleRun, gathered, merged, runs_from_json, runs_to_json, stint_made
from tests.test_goal_rows import GLUE, world, running

QS = e.QUANTITY_SCALE


def _stint(r: Rules, s: Save, shares: dict[str, int]) -> tuple[Save, int | None]:
    """`s` with mix `stint` saved and queued until the next skill level, as the editor's dry run of it reads that row,
    and the instant that goal lands."""
    mix = Mix(MixId("stint"), tuple(CardShare(CardId(c), bp) for c, bp in shares.items()))
    saved = e.decide(s, r, s.time, SaveMix(mix))
    dry = e.decide(saved, r, s.time, SwitchMix(mix.id))
    row = next(x for x in goal_rows(dry, r, e.view(dry, r), []) if x.kind is g.GoalKind.LEVEL)
    entry = QueueEntry(SwitchMix(mix.id), from_condition(row.until, r))
    return e.decide(saved, r, s.time, SetQueue((entry,))), row.lands_at


def _queued(r: Rules, s: Save, shares: dict[str, int]) -> tuple[Save, int, e.Order]:
    """`s` with a stint of `shares` queued until the next skill level, when that lands, and the stint's order."""
    queued, lands_at = _stint(r, s, shares)
    assert lands_at is not None
    return queued, lands_at, e.Order(queued.queue[0].until, queued.queue[0].verb)


def _levels(r: Rules, queued: Save, lands_at: int) -> tuple[tuple[tuple[str, int], ...], tuple[tuple[str, int], ...]]:
    """The levels on the stint's start (the queue set again after it was cleared) and on its landing."""
    cleared = e.decide(queued, r, queued.time, SetQueue(()))
    [began] = e.decide_logged(cleared, r, cleared.time, SetQueue(queued.queue)).rule_changes
    [landed] = e.advance_logged(queued, r, lands_at + 60).rule_changes
    assert began.on and landed.ended is e.Ended.STINT, "control: a start and a landing"
    return began.levels, landed.levels


def test_a_stint_reports_the_amount_of_the_store_its_mix_makes_at_its_start_and_its_landing() -> None:
    r, s = world(logs=40)
    queued, lands_at, _ = _queued(r, running(r, s, {"fell": BP}), {"saw": BP})
    assert lands_at - queued.time == 2 * 3600, "control: saw trains at half chop's rate"
    assert _levels(r, queued, lands_at) == ((("plank", 0),), (("plank", units(12)),))   # saw makes 6 an hour


def test_levels_come_in_rules_stores_order_whatever_the_mix_order() -> None:
    r, s = world(logs=40)
    assert [d.id for d in r.stores][:2] == [e.StoreId("log"), e.StoreId("plank")], "control: log before plank"
    queued, lands_at, _ = _queued(r, running(r, s, {"fell": BP}), {"saw": BP // 2, "fell": BP // 2})
    assert _levels(r, queued, lands_at) == ((("log", units(40)), ("plank", 0)),
                                           (("log", units(34)), ("plank", units(12))))


def test_a_mix_whose_cards_make_nothing_and_a_card_at_share_zero_report_no_levels() -> None:
    r, s = world(logs=40)
    s = running(r, s, {"fell": BP})
    for shares in ({"chop": BP}, {"saw": 0, "chop": BP}):
        queued, lands_at, _ = _queued(r, s, shares)
        assert _levels(r, queued, lands_at) == ((), ()), shares
    queued, lands_at, _ = _queued(r, s, {"saw": BP})
    assert _levels(r, queued, lands_at)[0] != (), "control: the same world reports levels once saw has a share"


def test_the_stores_of_a_cards_outcome_count_as_stores_it_makes() -> None:
    r, _ = world(logs=40)
    dig = CardDef(CardId("dig"), 3600, outcome=Outcome(stores=(Amount(GLUE, units(2)),)))
    r = dataclasses.replace(r, cards=(*r.cards, dig), opening=(*(r.opening or ()), e.Unlock(e.UnlockKind.CARD, dig.id)))
    queued, lands_at, _ = _queued(r, running(r, e.new_save(r), {"fell": BP}), {"dig": BP // 2, "chop": BP // 2})
    assert _levels(r, queued, lands_at) == ((("glue", 0),), (("glue", units(2)),))


def _stint_order(store: str | None = None) -> e.Order:
    """A stint's order: until `store` reaches a whole item, else until a skill level."""
    until = (e.AtLeast(e.StoreValue(e.StoreId(store)), QS, QS) if store
             else e.AtLeast(e.SkillLevel(e.SkillId("k")), 2, 2))
    return e.Order(until, e.SwitchMix(e.MixId("m")))


def test_made_is_the_net_gain_of_each_store_reported_at_both_ends() -> None:
    order = _stint_order()
    on = (("a", 2 * QS), ("b", 9 * QS))
    assert stint_made(order, on, (("a", 7 * QS), ("b", 4 * QS))) == (("a", 5 * QS),), "a store that fell is not a gain"
    assert stint_made(order, on, on) == ()


def test_made_lists_gains_of_a_whole_item_or_more_and_keeps_the_amount_in_quantity_units() -> None:
    order = _stint_order()
    assert stint_made(order, (("a", 0),), (("a", QS - 1),)) == ()
    assert stint_made(order, (("a", 0),), (("a", QS),)) == (("a", QS),)
    assert stint_made(order, (("a", 5),), (("a", 5 + QS + QS // 2),)) == (("a", QS + QS // 2),)


def test_made_names_the_goals_store_first_then_the_largest_and_at_most_made_kept() -> None:
    off = (("a", 3 * QS), ("b", 9 * QS), ("goal", 1 * QS), ("c", 5 * QS))
    on = tuple((s, 0) for s, _ in off)
    assert MADE_KEPT == 2
    assert stint_made(_stint_order("goal"), on, off) == (("goal", QS), ("b", 9 * QS))
    assert stint_made(_stint_order(), on, off) == (("b", 9 * QS), ("c", 5 * QS))
    assert stint_made(_stint_order("a"), on, off) == (("a", 3 * QS), ("b", 9 * QS))


def test_a_goal_store_that_gained_less_than_an_item_is_not_listed_and_the_largest_take_its_place() -> None:
    on = (("a", 0), ("goal", 0), ("b", 0))
    off = (("a", 3 * QS), ("goal", QS - 1), ("b", 4 * QS))
    assert stint_made(_stint_order("goal"), on, off) == (("b", 4 * QS), ("a", 3 * QS))


def test_equal_gains_keep_the_order_of_the_levels_at_the_landing() -> None:
    on = (("a", 0), ("b", 0), ("c", 0), ("d", 0))
    assert stint_made(_stint_order(), on, (("c", 5 * QS), ("a", 5 * QS), ("d", 5 * QS), ("b", QS))) == (("c", 5 * QS), ("a", 5 * QS))


def _on(t: int, order: e.Order, levels: tuple[tuple[e.StoreId, int], ...] = ()) -> e.RuleChange:
    return e.RuleChange(t, order, True, None, None, levels)


def _landed(t: int, order: e.Order, levels: tuple[tuple[e.StoreId, int], ...] = (), why: e.Ended = e.Ended.STINT) -> e.RuleChange:
    return e.RuleChange(t, order, False, None, why, levels)


A, B = e.StoreId("a"), e.StoreId("b")
ON = ((A, 2 * QS), (B, 0))
OFF = ((A, 6 * QS), (B, 3 * QS))
MADE = ((A, 4 * QS), (B, 3 * QS))


def test_the_entry_carries_the_levels_at_the_start_and_an_ended_stint_gets_its_made_at_the_landing() -> None:
    order = _stint_order()
    live = merged((), (_on(10, order, ON),), (order,))
    assert live[0].on_levels == ON and live[0].made == ()
    [done] = merged(live, (_landed(30, order, OFF),), ())
    assert (done.ended, done.on_at, done.off_at, done.made) == (e.Ended.STINT, 10, 30, MADE)
    assert done.made == stint_made(order, ON, OFF)


def test_a_landing_in_the_same_batch_as_the_start_makes_the_same_made() -> None:
    order = _stint_order()
    [done] = merged((), (_on(10, order, ON), _landed(30, order, OFF)), ())
    assert done.made == MADE
    [again] = gathered((), (_on(10, order, ON), _landed(30, order, OFF)))
    assert again.made == MADE


def test_made_is_empty_for_a_stint_with_no_start_and_for_an_end_that_is_not_a_stint() -> None:
    order = _stint_order()
    [unseen] = merged((), (_landed(30, order, OFF),), ())
    assert (unseen.on_at, unseen.made) == (None, ())
    rule = e.Order(e.AtMost(e.StoreValue(e.StoreId("s0")), 4, 9), e.SwitchMix(e.MixId("m")))
    [season] = merged((), (_on(10, rule), _landed(30, rule, (), e.Ended.SEASON)), ())
    assert (season.ended, season.made) == (e.Ended.SEASON, ())
    [live] = merged((), (_on(10, rule),), (rule,))
    assert live.made == ()


def test_levels_on_an_end_that_is_not_a_stints_still_make_nothing() -> None:
    """CONTRACT.txt: made is [] on every entry but an ended stint's, whatever the change carried."""
    rule = e.Order(e.AtMost(e.StoreValue(e.StoreId("s0")), 4, 9), e.SwitchMix(e.MixId("m")))
    [season] = merged((), (_on(10, rule, ON), _landed(30, rule, OFF, e.Ended.SEASON)), ())
    assert (season.ended, season.made) == (e.Ended.SEASON, ())


def test_slices_gathered_then_read_back_end_with_the_made_of_one_merge() -> None:
    order = _stint_order()
    whole = merged((), (_on(10, order, ON), _landed(30, order, OFF)), ())
    stored = runs_from_json(runs_to_json(gathered((), (_on(10, order, ON),))))
    assert merged(stored, (_landed(30, order, OFF),), ()) == whole and whole[0].made == MADE
    start = runs_from_json(runs_to_json(merged((), (_on(10, order, ON),), (order,))))
    assert start[0].on_levels == ON, "control: the start levels survive the stored form"


def _stored(runs: tuple[RuleRun, ...]) -> dict[str, Json]:
    stored = runs_to_json(runs)
    assert isinstance(stored, dict)
    return stored


def test_levels_round_trip_and_the_stored_form_is_unchanged_while_no_entry_has_any() -> None:
    order, plain = _stint_order(), e.Order(e.AtMost(e.StoreValue(e.StoreId("s0")), 4, 9), e.SwitchMix(e.MixId("m")))
    bare = merged((), (_on(10, plain),), (plain,))
    assert _stored(bare) == {"orders": e.verb_to_json(e.SetOrders((plain,))), "runs": [[1, 10, None, None, None]]}
    live = merged((), (_on(10, order, ON),), (order,))
    done = merged(live, (_landed(30, order, OFF),), ())
    for runs in (live, done, merged(done, (_on(40, plain),), (plain,))):
        assert runs_from_json(runs_to_json(runs)) == runs
    assert set(_stored(live)) - set(_stored(bare)), "control: the levels are stored under keys of their own"


def test_a_stored_form_with_no_level_keys_reads_with_empty_levels_and_a_malformed_one_loses_only_the_levels() -> None:
    order = _stint_order()
    live = merged((), (_on(10, order, ON),), (order,))
    done = merged(live, (_landed(30, order, OFF),), ())
    plain = tuple(dataclasses.replace(run, on_levels=(), made=()) for run in done)
    assert plain[0].ended is e.Ended.STINT
    full = _stored(done)
    own = [k for k in full if k not in _stored(plain)]
    assert own, "control: there are level keys to take away"
    older = {k: v for k, v in full.items() if k not in own}
    assert runs_from_json(older) == plain
    junks: list[Json] = ["nope", 7, [[1, 2, 3]], [["a"]], [[1, "x"]], {"a": 1}, None]
    for junk in junks:
        bad: Json = {**full, **dict.fromkeys(own, junk)}
        assert runs_from_json(bad) == plain, junk
