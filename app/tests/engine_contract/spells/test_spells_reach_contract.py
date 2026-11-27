"""The reach (engine/design/spells.txt, "SPELLS": Reach, Resolving, Read model; invariant 188; api/contract/spells.txt:
View.chains), written blind from those parts alone. A group of 60 at fought 10 makes 50 due, so a reach under 50 is the
length."""
from hypothesis import given, strategies as st

from ashfall_app.engine import (
    BP, AfterTime, ChainReach, Modifier, ModifierKind, Outcome, TriggerDef, TriggerId, advance, chain_views, decide, new_save,
    TapCard,
)
from contract_gen import few
from spells_world import SPELL, entry, kills, per_instant, play, reach_of, world

PER = 3600
ADD, MUL = ModifierKind.ADD_BP, ModifierKind.MUL_BP
GROUP = 60


def run_length(base: int, mods: tuple[Modifier, ...]) -> int:
    got = per_instant(play(world(GROUP, base, per=PER), (0,), mods=mods)[1])
    return got[0][1] if got else 0


def shown(base: int, mods: tuple[Modifier, ...]) -> int:
    r = world(GROUP, base, per=PER)
    return chain_views(new_save(r, mods), r)[0].reach.value


@kills(6, 7, 22)
@given(st.integers(1, 4), st.lists(st.integers(0, 15_000), max_size=2), st.lists(st.integers(BP, 15_000), max_size=2))
@few(25)
def test_the_reach_is_the_store_caps_arithmetic_and_shown_and_run_agree(base: int, adds: list[int], muls: list[int]):
    mods = (*(entry(SPELL, ADD, a) for a in adds), *(entry(SPELL, MUL, m) for m in muls))
    want = reach_of(base, mods)
    assert shown(base, mods) == want == run_length(base, mods)


@kills(22)
def test_the_reach_is_rounded_down_once_after_every_entry_not_entry_by_entry():
    mods = tuple(entry(SPELL, MUL, 15_000) for _ in range(3))     # 1 * 1.5 ** 3 = 3.375
    assert shown(1, mods) == run_length(1, mods) == 3
    mods = (entry(SPELL, ADD, 5000), entry(SPELL, ADD, 2500))     # 3 * 1.75 = 5.25
    assert shown(3, mods) == run_length(3, mods) == 5


@kills(6)
def test_the_view_explains_the_reach_as_a_strength_over_the_chain_reach():
    mods = (entry(SPELL, ADD, 5000, "pay"), entry(SPELL, MUL, 20_000, "charm"))
    r = world(GROUP, 3, per=PER)
    e = chain_views(new_save(r, mods), r)[0].reach
    assert e.target == ChainReach(SPELL) and e.base == 3 and e.value == 9
    assert [(m.source, m.amount_bp) for m in e.adds] == [("pay", 5000)] and [(m.source, m.amount_bp) for m in e.muls] == [("charm", 20_000)]


@kills(7, 23)
def test_a_pay_landing_mid_tap_is_run_and_the_reach_shown_before_the_completion_is_the_reach_run():
    """Reach 2 at the tap's start; a trigger at 5 s adds 150%: 5. The view at the start says 2, at 6 s says 5, and the
    completion at 10 runs 5 (never below the 2 shown when the tap started)."""
    pay = TriggerDef(TriggerId("pay"), AfterTime(5), Outcome(modifiers=(entry(SPELL, ADD, 15_000),)))
    r = world(GROUP, 2, per=PER, triggers=(pay,))
    s = decide(new_save(r), r, 0, TapCard(SPELL))
    at_start = chain_views(s, r)[0].reach.value
    assert at_start == 2
    assert chain_views(advance(s, r, 6), r)[0].reach.value == 5
    _, lines = play(r, (0,))
    assert per_instant(lines) == [(10, 5)] and at_start <= 5


@kills(7, 23)
def test_the_reach_is_live_a_tap_started_after_the_pay_runs_it_too():
    pay = TriggerDef(TriggerId("pay"), AfterTime(3), Outcome(modifiers=(entry(SPELL, ADD, 15_000),)))
    r = world(GROUP, 2, per=PER, triggers=(pay,))
    assert per_instant(play(r, (4,))[1]) == [(14, 5)]
