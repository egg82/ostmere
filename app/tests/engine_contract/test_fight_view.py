"""View.fights (DESIGN.txt, "FIGHTS", "View"): reading writes nothing, a tap's kept odds show, the strengths and tallies."""
from ashfall_app.engine import (
    QUANTITY_SCALE as Q, AfterTime, Modifier, ModifierKind, Outcome, SideStrength, SourceId, TapCard, ThreatStrength,
    TriggerDef, TriggerId, advance, decide, new_save, next_event, strength, value, view,
)
from fight_world import HAND, HUNT, LOST, RAID, RLOST, FOUGHT, WOLF, loss_bp, started, world


def ramp_to(p_after: int) -> TriggerDef:
    """At t=30 the side gains p_after - 1 times its base (base 1 -> p_after)."""
    return TriggerDef(TriggerId("up"), AfterTime(30), Outcome(modifiers=(
        Modifier(SideStrength(HAND), ModifierKind.ADD_BP, (p_after - 1) * 10_000, SourceId("spear")),)))


def test_reading_a_view_changes_nothing_and_a_view_is_the_same_whenever_it_is_read():
    r = world(2, 6, triggers=(ramp_to(9),))
    s = started(r)
    s = advance(s, r, 20)
    copy, first = s, view(s, r)
    view(advance(s, r, 3000), r)                       # a later read of the same save must not leak into this one
    next_event(s, r)
    assert s == copy and advance(s, r, s.time) == s
    assert view(s, r) == first


def test_a_running_tap_reports_the_loss_share_it_started_at_after_a_side_entry_is_appended_mid_tap():
    r = world(1, 4, triggers=(ramp_to(16),))           # at 30s the side goes 1 -> 16
    start, later = loss_bp(1, 4), loss_bp(16, 4)
    assert start != later
    mid = advance(decide(new_save(r), r, 0, TapCard(HUNT)), r, 40)
    assert mid.fired == (True,)
    by_runner = {f.runner: f for f in view(mid, r).fights}
    assert by_runner[HUNT].loss_bp == start            # kept to the tap's end
    assert by_runner[RAID].loss_bp == later            # a standing fight is live
    assert by_runner[HUNT].power.value == strength(mid, r, SideStrength(HAND)) != strength(new_save(r), r, SideStrength(HAND))
    done = advance(mid, r, 100)
    assert {f.runner: f.loss_bp for f in view(decide(done, r, 100, TapCard(HUNT)), r).fights}[HUNT] == later


def test_fights_list_cards_then_standing_with_the_strengths_and_whole_tallies():
    r = world(2, 6)
    s = advance(started(r), r, 7200)
    cards, standing = view(s, r).fights
    assert (cards.runner, standing.runner) == (HUNT, RAID)
    for f in (cards, standing):
        assert (f.side, f.threat) == (HAND, WOLF)
        assert f.power.value == strength(s, r, SideStrength(HAND)) and f.threat_strength.value == strength(s, r, ThreatStrength(WOLF))
        assert f.loss_bp == loss_bp(2, 6) and 0 < f.lost <= f.fought
    assert cards.fought == 72 and cards.lost == value(s, r, LOST, 7200) // Q
    assert (standing.fought, standing.lost) == (value(s, r, FOUGHT, 7200) // Q, value(s, r, RLOST, 7200) // Q)
    assert standing.fought == 4 and standing.lost > 0


def test_a_fight_free_world_has_no_fights():
    assert view(new_save(world(2, 6, fight=False)), world(2, 6, fight=False)).fights == ()
