"""Rule guards on a share of a store's cap (docs/design/rule-guards.md, "Contract (blind)", statements 9 and 10;
"Guards": a guard keeps a band, a store's maximum rising). A guard is read exactly as a `when` is, so its share levels
read as the quantities engine DESIGN.txt "SHARE LEVELS" gives, band of one item included; `_amounts` is that table,
and the expected switches are worked from those quantities."""
from fractions import Fraction
from math import ceil, floor

from hypothesis import given, strategies as st

from ashfall_app.engine import BP, AtLeast, AtMost, Rules, Save, StoreValue, SwitchMix, advance, view
from contract_gen import few
from guards_world import ALWAYS, DOWN, IDLE, RM, T, UP, Q, cap_raise, guarded, kills, rules, start

HALF, FULL = BP // 2, BP


def _share(kind: bool, b: int) -> AtLeast | AtMost:
    """A page-shaped share guard: both levels the same share b."""
    cls = AtLeast if kind else AtMost
    return cls(StoreValue(T), b, b, value_of_cap=True, release_of_cap=True)


def _amounts(kind: bool, b: int, cap_items: int) -> tuple[int, int]:
    """(value, release) in quantity units for _share(kind, b) on a store of cap_items whole items (SHARE LEVELS)."""
    x = Fraction(b * cap_items, BP)
    if kind:
        value, release = ceil(x) * Q, (floor(x) + 1) * Q
        return value, (release if release <= value - Q else min(release, value, max(value - Q, Q)))
    value, release = (floor(x) + 1) * Q - 1, ceil(x) * Q - 1
    return value, (release if release >= value + Q else max(release, value, min(value + Q, cap_items * Q - 1)))


def _mixes(r: Rules, s: Save, until: int) -> list[object]:
    out: list[object] = []
    cur = s
    for t in range(until + 1):
        cur = advance(cur, r, t)
        out.append(view(cur, r).running_mix)
    return out


def _chase(kind: bool, value: int, release: int, cap_items: int, until: int) -> list[object]:
    """The running mix each second for a boundary-chasing rule: an at-least guard on a rule whose mix (UP) fills T from
    empty, or an at-most guard on one whose mix (DOWN) drains it from full; the player's mix runs the other way."""
    rule, player = (UP, DOWN) if kind else (DOWN, UP)
    x, latch = (0 if kind else cap_items), False
    out: list[object] = []
    for t in range(until + 1):
        q = x * Q
        if kind:
            latch = (q >= value) if (t == 0 or not latch) else not (q < release)
        else:
            latch = (q <= value) if (t == 0 or not latch) else not (q > release)
        out.append(player if latch else rule)
        step = 1 if out[-1] == UP else -1
        x = max(0, min(cap_items, x + step))
    return out


# ---- statement 9 ------------------------------------------------------------------------------------------------------

@kills(12)
def test_a_full_guard_blocks_at_full_and_lets_go_one_item_under():
    """Statement 9 at full: "unless T is full" on a rule filling a 10-item T from empty comes on at 10 (t = 10), lets go
    at the first second T is under 9 (t = 12), and comes on again at full (t = 14)."""
    r = rules(t0=0, cap=10)
    s = start(r, (guarded(ALWAYS, SwitchMix(UP), _share(True, FULL)),), active=DOWN)
    assert _mixes(r, s, 15) == [UP] * 10 + [DOWN, DOWN, UP, UP, DOWN, DOWN]


@kills(13)
def test_a_full_guard_comes_on_at_the_caps_whole_items():
    """Statement 9: with T's cap 10.5 items, full is 10 whole items: the guard comes on at 10 (t = 10), though T could
    still rise half an item."""
    r = rules(t0=0, cap=10, triggers=(cap_raise(0, 10_500),))
    s = start(r, (guarded(ALWAYS, SwitchMix(UP), _share(True, FULL)),), active=DOWN)
    got = _mixes(r, s, 11)
    assert got[:10] == [UP] * 10 and got[10] == DOWN


@kills(12, 13)
@few(15)
@given(kind=st.booleans(), b=st.integers(0, BP), cap_items=st.integers(2, 24))
def test_a_share_guard_switches_at_the_quantities_its_share_reads_as(kind: bool, b: int, cap_items: int):
    """Statement 9: a guard with both levels the same share b of T's cap comes on where a `when` of that share would
    and lets go at least one item past it, never past full or empty: the boundary-chasing rule's mix switches exactly
    where the share's quantities (band included) say."""
    value, release = _amounts(kind, b, cap_items)
    r = rules(t0=0 if kind else cap_items, cap=cap_items)
    rule, player = (UP, DOWN) if kind else (DOWN, UP)
    s = start(r, (guarded(ALWAYS, SwitchMix(rule), _share(kind, b)),), active=player)
    until = 3 * cap_items + 4
    assert _mixes(r, s, until) == _chase(kind, value, release, cap_items, until)


@kills(12)
def test_a_share_guard_and_the_same_guard_in_amounts_pause_alike():
    """Statement 9: "unless T is half or more" on 10 items reads as "5 or more, until under 4"; the two guards give the
    same switches on a filling rule."""
    r = rules(t0=0, cap=10)
    share = start(r, (guarded(ALWAYS, SwitchMix(UP), _share(True, HALF)),), active=DOWN)
    amount = start(r, (guarded(ALWAYS, SwitchMix(UP), AtLeast(StoreValue(T), 5 * Q, 4 * Q)),), active=DOWN)
    assert _mixes(r, share, 20) == _mixes(r, amount, 20) == _chase(True, 5 * Q, 4 * Q, 10, 20)


# ---- statement 10 -----------------------------------------------------------------------------------------------------

def _raised(guard_share: int, factor_bp: int) -> tuple[Rules, Save]:
    """T rises one item a second from 0 to its 10-item cap (reached at 10) and stays there; the rule switches to RM
    unless T is at guard_share of its cap; at 20 a trigger multiplies T's cap by factor_bp / BP."""
    r = rules(t0=0, cap=10, t_rate=1, triggers=(cap_raise(20, factor_bp),))
    return r, start(r, (guarded(ALWAYS, SwitchMix(RM), _share(True, guard_share)),))


@kills(11)
def test_a_rule_paused_on_full_resumes_at_a_raise_that_leaves_it_past_the_new_release():
    """Statement 10: paused on full from 10; the cap doubles at 20 (full is 20, the release 19) and T is 10, past it:
    the rule's mix runs from 20 exactly, until T is full again at 30."""
    r, s = _raised(FULL, 2 * BP)
    assert _mixes(r, s, 31) == [RM] * 10 + [IDLE] * 10 + [RM] * 10 + [IDLE] * 2


@kills(13)
def test_a_raise_that_leaves_the_caps_whole_items_alone_keeps_the_rule_paused():
    """Statement 10's other side: a raise to 10.5 items leaves full at 10 whole items, which T shows; still paused."""
    r, s = _raised(FULL, 10_500)
    assert _mixes(r, s, 32) == [RM] * 10 + [IDLE] * 23


@kills(11)
def test_a_half_guard_moves_with_the_cap_at_the_raise():
    """Statement 10 for a share under full: "unless half or more" on 10 items comes on at 5. Tripling the cap at 20
    makes it "15 or more, until under 14"; T is 10, past the release, so the rule runs from 20, and pauses again at 15
    (t = 25)."""
    r, s = _raised(HALF, 3 * BP)
    assert _mixes(r, s, 26) == [RM] * 5 + [IDLE] * 15 + [RM] * 5 + [IDLE] * 2


@kills(11)
def test_a_raise_that_leaves_the_store_inside_the_new_band_keeps_the_rule_paused():
    """Statement 10: a raise to 12 items makes the half guard "6 or more, until under 5"; T at 10 is not past it."""
    r, s = _raised(HALF, 12_000)
    assert _mixes(r, s, 30) == [RM] * 5 + [IDLE] * 26
