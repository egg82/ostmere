"""Teaching the second mix after the end (docs/design/opening-screen.md, the hands strip and "Dots and the one glow"),
played by the scripted player kept going past the end (afterend.py) on the session's shared runs (routes.py). The
rest offer never shows before the end lines are read; a player who rests by hand meets it, takes it, and never taps
rest again while the rule's mix does the resting; the Mixes list's door glows when that rule first comes on by itself,
a step or two later. Each run prints its timeline in minutes (pytest -s). The nightly deep run adds seeds 1-2 and the
player who mixed rest, who is never tired and never meets the offer (it met the rule's lesson at the ledger's offer:
test_first_rule_offer.py)."""
import pytest

from tests.opening.afterend import AfterEnd, AfterEndPlayer, offer_shows, rest_card
from tests.opening.routes import AFTER_END_MINUTES, DEEP, after_end_plays, plays

pytestmark = pytest.mark.playthrough
Run = tuple[AfterEnd, AfterEndPlayer]


def mm(t: int | None) -> str:
    return "never" if t is None else f"{t / 60:.1f}m"


def gap(a: int | None, b: int | None) -> int | None:
    return None if a is None or b is None else a - b


def first_by_itself_after(a: AfterEnd, t: int | None) -> int | None:
    return None if t is None else next((at for at, _ in a.came_on if at > t), None)


def show(kind: str, seed: int, a: AfterEnd) -> None:
    effort = gap(a.effort_at.get("door"), a.effort_at.get("offer"))
    print(f"{kind} seed {seed}: end {mm(a.end_at)}; read -> offer {mm(gap(a.offer_at, a.read_at))}; "
          f"offer -> accepted {mm(gap(a.accepted_at, a.offer_at))}; accepted -> first rule by itself "
          f"{mm(gap(first_by_itself_after(a, a.accepted_at), a.accepted_at))}; read -> door "
          f"{mm(gap(a.door_at, a.read_at))}; actions between the two {effort}; rest taps after {a.rest_taps_after}")


@pytest.mark.parametrize("a_route", plays(), indirect=True)
def test_the_rest_offer_never_shows_before_the_end_lines_are_read(a_route: AfterEndPlayer):
    assert rest_card().after_end
    assert a_route.shown_early == []


def test_the_gate_is_what_hides_it(typical: AfterEndPlayer, by_hand: AfterEndPlayer):
    """The probe can fail: the offer's test short of the gate held before the end (a player tired in the opening), and
    without after_end it would have shown then."""
    assert typical.wanted_early + by_hand.wanted_early
    assert offer_shows(False, False, False, True) and not offer_shows(True, False, False, True)


@pytest.mark.parametrize("an_after_end", [r for r in after_end_plays() if r[0] == "by_hand"], indirect=True)
def test_a_player_who_rests_by_hand_meets_the_offer_takes_it_and_never_taps_rest_again(an_after_end: Run):
    a, p = an_after_end
    show("by_hand", p.seed, a)
    assert a.offer_at is not None and a.accepted_at is not None and a.offer_at >= a.read_at
    assert a.rest_taps_after == 0
    door = a.door_at
    assert door is not None and door > a.accepted_at
    assert door == first_by_itself_after(a, a.accepted_at)


@pytest.mark.skipif(not DEEP, reason="the nightly deep run's: every kind of player past the end")
@pytest.mark.parametrize("an_after_end", [r for r in after_end_plays() if r[0] == "typical"] or [("typical", 0)],
                         indirect=True)
def test_a_player_who_mixed_rest_is_never_tired_after_the_end(an_after_end: Run):
    """Printed rather than asserted on the nudges: rest in the player's own mix keeps tiredness away,
    so the offer never comes; nothing breaks."""
    a, p = an_after_end
    show("typical", p.seed, a)
    met = "never meets" if a.offer_at is None else "meets"
    print(f"typical seed {p.seed}: {met} the offer in {AFTER_END_MINUTES} minutes")
    assert a.offer_at is None or a.offer_at >= a.read_at
    assert p.end_at is not None
