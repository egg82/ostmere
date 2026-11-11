"""What the rules did lately, as the save keeps it (saves/ruleruns.py; docs/design/opening-screen.md, "Lately"): one
entry per rule, counting its starts and keeping its last start and let-go with levels; an entry whose rule the save no
longer has goes; past KEPT, the entries changed longest ago go; and the stored form reads back as written."""
from ashfall_app import engine as e
from ashfall_app.engine.codec import Json
from ashfall_app.saves.ruleruns import KEPT, RuleRun, gathered, merged, runs_from_json, runs_to_json, standing

S = e.StoreId("s0")


def rule(n: int) -> e.Order:
    return e.Order(e.AtMost(e.StoreValue(S), n, n + 5), e.SwitchMix(e.MixId(f"m{n}")))


def on(t: int, order: e.Order, level: int | None = 3) -> e.RuleChange:
    return e.RuleChange(t, order, True, level)


def off(t: int, order: e.Order, level: int | None = 9) -> e.RuleChange:
    return e.RuleChange(t, order, False, level)


def test_one_entry_per_rule_counts_starts_and_keeps_the_last_start_and_let_go():
    a = rule(1)
    runs = merged((), (on(10, a, 3), off(20, a, 9), on(30, a, 2), off(40, a, 8)), (a,))
    assert runs == (RuleRun(a, starts=2, on_at=30, on_level=2, off_at=40, off_level=8),)
    runs = merged(runs, (on(50, a, 1),), (a,))
    assert runs == (RuleRun(a, starts=3, on_at=50, on_level=1, off_at=40, off_level=8),)


def test_the_most_recent_change_comes_first():
    a, b = rule(1), rule(2)
    runs = merged((), (on(10, a), on(20, b), off(30, a)), (a, b))
    assert [r.order for r in runs] == [a, b]


def test_a_rule_the_save_no_longer_has_loses_its_entry_and_a_reorder_keeps_it():
    a, b = rule(1), rule(2)
    runs = merged((), (on(10, a), on(20, b)), (a, b))
    assert [r.order for r in merged(runs, (), (b, a))] == [b, a]   # reordered: both kept
    edited = rule(7)
    assert [r.order for r in merged(runs, (), (edited, b))] == [b]   # a was edited into another rule


def test_a_let_go_with_no_start_recorded_makes_no_entry():
    a = rule(1)
    assert merged((), (off(10, a),), (a,)) == ()


def test_past_kept_the_entries_changed_longest_ago_go_and_the_rest_stay():
    orders = tuple(rule(n) for n in range(KEPT + 3))
    runs = merged((), tuple(on(10 * n, o) for n, o in enumerate(orders)), orders)
    assert len(runs) == KEPT
    assert [r.order for r in runs] == list(reversed(orders))[:KEPT]   # the newest KEPT stay
    assert all(o not in [r.order for r in runs] for o in orders[:3])   # the three oldest went


def test_the_stored_form_reads_back_and_anything_else_reads_as_none():
    a, b = rule(1), e.Order(e.AfterTime(0), e.TapCard(e.CardId("c")))
    runs = merged((), (on(10, a), off(20, a), on(30, b, None)), (a, b))
    assert runs_from_json(runs_to_json(runs)) == runs
    assert runs_from_json(None) == ()
    assert runs_from_json({"orders": "nope", "runs": []}) == ()
    assert runs_from_json([1, 2]) == ()
    stored = runs_to_json(runs)
    assert isinstance(stored, dict)
    bad: Json = {**stored, "runs": [[1, 10, "3", None, None] for _ in runs]}
    assert runs_from_json(bad) == ()   # not a number


def test_slices_gathered_unpruned_end_as_one_write_and_pruning_each_slice_would_not():
    rules = tuple(rule(n) for n in range(KEPT + 1))
    first = tuple(on(10 + n, r) for n, r in enumerate(rules))   # the oldest, rules[0], falls past KEPT here
    then = (on(100, rules[0]),)
    whole = merged((), first + then, rules)
    stored = runs_from_json(runs_to_json(gathered((), first)))   # a slice that stopped short, read back
    assert merged(stored, then, rules) == whole
    assert whole[0] == RuleRun(rules[0], starts=2, on_at=100, on_level=3)
    assert merged(merged((), first, rules), then, rules) != whole   # control: pruned per slice, its first start is lost


def ended(t: int, order: e.Order, why: e.Ended = e.Ended.SEASON, level: int | None = 4) -> e.RuleChange:
    return e.RuleChange(t, order, False, level, why)


def test_a_rule_the_game_ended_keeps_its_entry_after_it_leaves_the_orders():
    a, b = rule(1), rule(2)
    runs = merged((), (on(10, a, 3), on(20, b), ended(30, a, e.Ended.LEFT, 4)), (b,))
    assert runs == (RuleRun(a, 1, 10, 3, 30, 4, e.Ended.LEFT), RuleRun(b, 1, 20, 3))


def test_an_ended_rule_that_never_came_on_gets_an_entry_with_no_start():
    a = rule(1)
    assert merged((), (ended(30, a),), ()) == (RuleRun(a, 0, None, None, 30, 4, e.Ended.SEASON),)


def test_the_rule_set_again_starts_a_fresh_entry_at_its_next_start():
    a = rule(1)
    runs = merged((), (on(10, a), off(15, a), on(20, a), ended(30, a)), ())
    assert merged(runs, (off(40, a), on(50, a, 2)), (a,)) == (RuleRun(a, 1, 50, 2),)


def test_an_ended_entry_is_stored_with_its_reason_and_a_live_one_as_before():
    a, b = rule(1), rule(2)
    runs = merged((), (on(10, a), ended(30, a), ended(40, b, e.Ended.LEFT)), ())
    stored = runs_to_json(runs)
    assert isinstance(stored, dict) and stored["runs"] == [[0, None, None, 40, 4, "left"], [1, 10, 3, 30, 4, "season"]]
    assert runs_from_json(stored) == runs
    live = merged((), (on(10, a),), (a,))
    assert runs_to_json(live) == {"orders": e.verb_to_json(e.SetOrders((a,))), "runs": [[1, 10, 3, None, None]]}
    bad: list[Json] = [[0, None, None, 40, 4, "gone"], [0, None, None, 40, 4], [1, 10, 3, None, None, None]]
    for entry in bad:
        assert runs_from_json({"orders": e.verb_to_json(e.SetOrders((a,))), "runs": [entry]}) == ()


def test_a_stint_in_the_queue_keeps_its_start_until_it_pops_and_then_stays_as_an_ended_entry():
    until = e.AtLeast(e.SkillLevel(e.SkillId("k")), 2, 2)
    entry = e.QueueEntry(e.SwitchMix(e.MixId("m1")), until)
    order = e.Order(until, entry.verb)
    assert standing((), (entry,)) == (order,) and standing((), ()) == ()
    live = merged((), (on(10, order, None),), standing((), (entry,)))
    assert live == (RuleRun(order, 1, 10, None),), "control: pruned away if the queue were not counted"
    assert merged(live, (), ()) == (), "the entry goes with its stint when the player removes it"
    done = merged(live, (ended(30, order, e.Ended.STINT, None),), ())
    assert done == (RuleRun(order, 1, 10, None, 30, None, e.Ended.STINT),)
    assert runs_from_json(runs_to_json(done)) == done
