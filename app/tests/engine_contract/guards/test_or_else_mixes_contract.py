"""A rule of mixes runs the first of its mixes that is not greyed (docs/design/rule-guards.md, "Contract (blind)",
statement 18; "Or else": for mixes, the earlier mix runs from the instant it stops being greyed). A hands card of one
second's work and a cap of c completes at seconds 1..c under a full share, so its mix greys at c; a mix that is not the
running one does no work and cannot grey."""
from hypothesis import given, strategies as st

from ashfall_app.engine import BP, CardShare, Mix, SaveMix, SwitchMix, advance, decide, view
from contract_gen import few
from guards_world import kills
from or_else_world import ALWAYS, G1, G2, GP, M1, M2, M3, PL, mixes, raise_at, rule, rules, start


@kills(2, 10)
def test_the_second_mix_runs_from_the_instant_the_first_greys():
    """Statement 18: M1 (cap 3) runs 0 to 2 and greys at 3, where M2 runs on."""
    r = rules(cap={G1: 3})
    s = start(r, (rule(ALWAYS, SwitchMix(M1), (SwitchMix(M2),)),))
    assert mixes(r, s, 8) == [M1] * 3 + [M2] * 6


@kills(2, 9, 10)
def test_the_first_mix_runs_again_from_the_instant_a_raise_un_greys_it():
    """Statement 18: a cap raise at 6 un-greys M1, which runs again from 6; M2 ran from 3 to 5."""
    r = rules(cap={G1: 3}, triggers=(raise_at(6, G1, 5),))
    s = start(r, (rule(ALWAYS, SwitchMix(M1), (SwitchMix(M2),)),))
    assert mixes(r, s, 9) == [M1] * 3 + [M2] * 3 + [M1] * 4


@kills(9)
def test_the_first_mix_runs_again_from_the_instant_a_savemix_un_greys_it():
    """Statement 18: SaveMix of M1 as a mix of an uncapped card at 6: M1 runs again at 6 and after."""
    r = rules(cap={G1: 3})
    s = start(r, (rule(ALWAYS, SwitchMix(M1), (SwitchMix(M2),)),))
    s = advance(s, r, 5)
    s = decide(s, r, 6, SaveMix(Mix(M1, (CardShare(GP, BP),))))
    assert view(s, r).running_mix == M1
    assert view(advance(s, r, 8), r).running_mix == M1


@kills(10)
def test_with_every_listed_mix_greyed_the_players_own_mix_runs():
    """Statement 18: M1 and M2 each grey after two completions (at 2 and 4); from 4 the rule runs nothing and the
    player's mix does."""
    r = rules(cap={G1: 2, G2: 2})
    s = start(r, (rule(ALWAYS, SwitchMix(M1), (SwitchMix(M2),)),))
    assert mixes(r, s, 6) == [M1, M1, M2, M2, PL, PL, PL]


@kills(2, 9, 10)
@few(40)
@given(c1=st.integers(1, 4), c2=st.integers(1, 4))
def test_the_running_mix_is_the_first_not_greyed_at_every_second(c1: int, c2: int):
    """Statement 18, for every pair of caps: M1 until it greys at c1, then M2 until it greys at c1 + c2, then the
    player's own mix."""
    r = rules(cap={G1: c1, G2: c2})
    s = start(r, (rule(ALWAYS, SwitchMix(M1), (SwitchMix(M2),)),))
    want = [M1 if t < c1 else M2 if t < c1 + c2 else PL for t in range(c1 + c2 + 3)]
    assert mixes(r, s, c1 + c2 + 2) == want


@kills(2, 10)
def test_three_mixes_are_tried_in_listed_order():
    """Statement 18 with two fallbacks: M1 greys at 1, M2 at 2, so M1 runs at 0, M2 at 1 and M3 from 2."""
    r = rules(cap={G1: 1, G2: 1})
    s = start(r, (rule(ALWAYS, SwitchMix(M1), (SwitchMix(M2), SwitchMix(M3))),))
    assert mixes(r, s, 4) == [M1, M2, M3, M3, M3]
