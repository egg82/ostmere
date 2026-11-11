"""A person leaves the town, part three: a rebase lands a leave already past (engine DESIGN.txt, "LEAVES", "Rebase",
invariant 154). Written blind from that part and the public interface; the `kills` marker names the rows of
MUTANTS_leaves.txt each test must turn red for. The save is written under rules with no leave at 55 (ac running, due at
70, ad's order on since 50) and loaded under rules whose leave is at 40."""
from ashfall_app.engine import (
    QUANTITY_SCALE as Q, Save, advance, advance_logged, decode, encode, rebase, rebase_logged, view,
)
from leaves_world import (
    AC, AC_DONE, AFTER_MIXES, HM, LA, LEAVE_AT, ORDER_AC, ORDER_AD, ORDER_BC, TOWN_RULE, X, Y, Z, ended_changes, expected_ends, kills, left, logged_end, rules, scene,
)
from town_mix_world import lane_card, stored

NOW = 55


def written() -> str:
    old = rules(None)
    return encode(advance(scene(old), old, NOW), old)


@kills(16)
def test_a_save_past_the_leave_loads_with_the_person_gone_and_its_stores_as_they_were():
    """Invariant 154: at the save's time LEFT is held, la's orders and shares are gone, its tap ended; the stores read
    as they did (y 3.5 items, ac's rate-form payment, and no more after)."""
    old, new = rules(None), rules(LEAVE_AT)
    before = decode(written(), old)
    after = rebase(written(), new)
    assert after.time == NOW and lane_card(before, LA) == AC   # the premise: the tap was under way
    assert left(LA) in after.unlocked
    assert (after.orders, after.latches) == ((TOWN_RULE, ORDER_BC), (before.latches[0], before.latches[3]))
    assert {m.id: m for m in after.mixes} == AFTER_MIXES
    assert lane_card(after, LA) is None
    for store in (X, Y, Z):
        assert stored(after, new, store, NOW) == stored(before, old, store, NOW)
    assert [stored(after, new, Y, t) for t in (NOW, 70, 500)] == [7 * Q // 2] * 3


@kills(6, 16)
def test_the_rebase_logs_each_removed_order_as_ended_left_at_the_saves_time():
    new = rules(LEAVE_AT)
    assert ended_changes(rebase_logged(written(), new).rule_changes) == expected_ends(
        logged_end(NOW, ORDER_AC, None, "LEFT"), logged_end(NOW, ORDER_AD, 7 * Q // 2, "LEFT"))


@kills(3, 16)
def test_a_rebased_save_loads_decodes_advances_and_views_without_error_and_pays_nothing():
    new = rules(LEAVE_AT)
    after: Save = rebase(written(), new)
    assert decode(encode(after, new), new) == after
    lines = advance_logged(after, new, 1000).lines
    assert not [ln for ln in lines if ln.key == AC_DONE or ln.card == AC]
    assert view(advance(after, new, 1000), new).greyed_mixes == (HM,)


@kills(16)
def test_a_leave_not_yet_due_at_the_rebase_changes_nothing():
    old, late = rules(None), rules(10**6)
    before, after = decode(written(), old), rebase(written(), late)
    assert left(LA) not in after.unlocked and after.orders == before.orders and after.mixes == before.mixes
    assert lane_card(after, LA) == AC
