"""The track, the menu and the rank entries (prestige.track/ranks_taken/menu, pickentries), read off a save whose
picks are set directly: they read the picks and nothing else, so no play is needed."""
from collections import Counter
from dataclasses import replace

from hypothesis import given, strategies as st

from ashfall_app.engine import (
    BP, Modifier, ModifierKind, NodeId, PhaseState, Rules, Run, RunKind, Save, SkillId, SourceId, modified_rate,
    new_save,
)
from ashfall_app.engine.nodes import NODE_PREFIX
from ashfall_app.engine.pickentries import pick_entries, pick_source
from ashfall_app.engine.prestige import menu, ranks_taken, track
from prestige_world import (
    J, J1, K, K_RANKS, MAKE_OTHER, MENU_SIZE, N1, N2, N3, N4, NODES, rules, without_prestige,
)

R = rules()


def picked(save: Save, picks: dict[SkillId, tuple[NodeId, ...]]) -> Save:
    """`save` with each skill's PhaseState set to just its picks (the phase one above their count)."""
    return replace(save, skills=tuple(
        replace(s, phase=PhaseState(phase=len(picks[s.skill]) + 1, picks=picks[s.skill])) if s.skill in picks else s
        for s in save.skills))


def model_menu(rules: Rules, skill: SkillId, picks: tuple[NodeId, ...]) -> tuple[NodeId, ...]:
    taken = Counter(picks)
    open_ = [n.id for n in rules.nodes if n.skill == skill and taken[n.id] < n.ranks]
    return tuple(open_[:MENU_SIZE])


def test_a_skills_track_is_its_nodes_in_rules_order():
    assert [n.id for n in track(R, K)] == [N1, N2, N3, N4]
    assert [n.id for n in track(R, J)] == [J1]
    assert track(R, SkillId("ghost")) == ()
    assert track(without_prestige(R), K) == ()


def test_the_first_menu_is_the_first_unfinished_nodes_of_the_track():
    save = new_save(R)
    assert menu(save, R, K) == (N1, N2)
    assert menu(save, R, J) == (J1,)


def test_a_node_stays_on_the_menu_until_its_last_rank_and_then_leaves_it():
    s = new_save(R)
    assert menu(picked(s, {K: (N1,)}), R, K) == (N1, N2)
    assert menu(picked(s, {K: (N1, N1)}), R, K) == (N2, N3)
    assert menu(picked(s, {K: (N2,)}), R, K) == (N1, N3)
    assert menu(picked(s, {K: (N1, N1, N2, N3)}), R, K) == (N3, N4)


def test_a_finished_track_has_an_empty_menu():
    done = (N1, N1, N2, N3, N3, N3, N4)
    assert len(done) == K_RANKS
    assert menu(picked(new_save(R), {K: done}), R, K) == ()
    assert menu(picked(new_save(R), {K: done}), R, J) == (J1,)


def test_the_menu_is_empty_with_no_prestige_or_an_unknown_skill():
    assert menu(new_save(R), without_prestige(R), K) == ()
    assert menu(new_save(R), R, SkillId("ghost")) == ()


def test_the_menu_size_caps_the_menu():
    three = rules(menu_size=3)
    assert menu(new_save(three), three, K) == (N1, N2, N3)


def test_ranks_taken_counts_the_skills_picks_of_the_node():
    s = picked(new_save(R), {K: (N1, N2, N1), J: (J1,)})
    assert [ranks_taken(s, R, n) for n in (N1, N2, N3, N4, J1)] == [2, 1, 0, 0, 1]
    assert ranks_taken(s, R, NodeId("ghost")) == 0


@st.composite
def pick_sequences(draw: st.DrawFn) -> dict[SkillId, tuple[NodeId, ...]]:
    """Valid picks per skill, each drawn from that skill's menu as the model reads it."""
    out: dict[SkillId, tuple[NodeId, ...]] = {}
    for skill in (K, J):
        picks: tuple[NodeId, ...] = ()
        for index in draw(st.lists(st.integers(0, 2), max_size=K_RANKS + 1)):
            open_ = model_menu(R, skill, picks)
            if not open_:
                break
            picks += (open_[index % len(open_)],)
        out[skill] = picks
    return out


@given(pick_sequences())
def test_the_menu_is_the_first_unfinished_nodes_of_the_track_in_order(picks: dict[SkillId, tuple[NodeId, ...]]):
    """A function of the track and the picks: no draw (it stays fixed over time: test_click_and_undo.py)."""
    save = picked(new_save(R), picks)
    for skill in (K, J):
        found = menu(save, R, skill)
        assert found == model_menu(R, skill, picks[skill])
        assert len(found) <= MENU_SIZE
        assert all(ranks_taken(save, R, n) < next(d for d in NODES if d.id == n).ranks for n in found)


@given(pick_sequences())
def test_ranks_taken_never_passes_a_nodes_ranks(picks: dict[SkillId, tuple[NodeId, ...]]):
    save = picked(new_save(R), picks)
    for node in NODES:
        assert 0 <= ranks_taken(save, R, node.id) <= node.ranks


def expected_entries(picks: dict[SkillId, tuple[NodeId, ...]]) -> tuple[Modifier, ...]:
    taken = Counter(n for ps in picks.values() for n in ps)
    return tuple(Modifier(d.target, ModifierKind.MUL_BP, BP + taken[d.id] * d.per_rank_bp, SourceId(NODE_PREFIX + d.id))
                 for d in NODES if taken[d.id] > 0)


def test_a_rank_entrys_source_names_its_node():
    assert pick_source(N1) == NODE_PREFIX + "n1" == "node:n1"


@given(pick_sequences())
def test_one_mul_entry_per_node_taken_BP_plus_ranks_times_per_rank_in_rules_order(picks: dict[SkillId, tuple[NodeId, ...]]):
    assert pick_entries(picked(new_save(R), picks), R) == expected_entries(picks)


def test_no_picks_no_entries_and_no_prestige_no_entries():
    assert pick_entries(new_save(R), R) == ()
    bare = without_prestige(R)
    assert pick_entries(picked(new_save(bare), {K: (N1,)}), bare) == ()


def stack_rate(picks: tuple[NodeId, ...]) -> int:
    """MAKE_OTHER's per-hour at a base chosen so every product below is exact."""
    stack = pick_entries(picked(new_save(R), {K: picks}), R)
    return modified_rate(MAKE_OTHER, 1_000_000, BP, stack, Run(RunKind.FULL)).per_hour


def test_ranks_within_a_node_add_and_nodes_compound():
    assert stack_rate(()) == 1_000_000
    assert stack_rate((N1,)) == 1_100_000
    assert stack_rate((N1, N1)) == 1_200_000   # adds: 1 + 2 * 0.10, not 1.1 * 1.1
    assert stack_rate((N4,)) == 1_500_000
    assert stack_rate((N1, N1, N4)) == 1_800_000   # compounds: 1.2 * 1.5, not 1 + 0.2 + 0.5


def test_a_full_track_lands_at_the_product_over_its_nodes():
    """The bound is fixed by the content: (1 + 2 * 0.10) * (1 + 1 * 0.50) on the one target both nodes aim at."""
    full = tuple(n.id for n in NODES if n.skill == K for _ in range(n.ranks))
    assert stack_rate(full) == 1_800_000
