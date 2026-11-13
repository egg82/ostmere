"""Each of day one's checks can fail and each counter reads what it claims: a planted wrong record, rule or route turns
a check red or moves its counter, and a clean one does neither, so no verdict or readout on the real routes is the
probe's own doing (docs/engineering.md: proven able to fail)."""
from collections.abc import Callable
from dataclasses import replace

import pytest

from ashfall_app.engine import (
    AfterTime, AtLeast, Blocker, CardId, EntryId, NoteId, Outcome, StoreId, StoreValue, TriggerDef, TriggerId, Unlock,
    UnlockKind, new_save, view,
)
from tests.dayone import checks
from tests.dayone.bands import B3_CARD, b3_relative, presence_steps
from tests.dayone.beats import STORY, near_promise_beats
from tests.dayone.checks import Window
from tests.dayone.story import flatcheck
from tests.dayone.verdicts import story_problems
from tests.opening.playthrough import News, opening_rules

START = 10_000


def window(news: list[tuple[int, str]], acts: list[tuple[int, str, str]], length: int = 600) -> Window:
    return Window("V9", START, START + length, 7200, tuple(News(START + t, thing, 0, 0) for t, thing in news),
                  tuple((START + t, kind, what) for t, kind, what in acts))


def clean() -> Window:
    """A busy visit: a beat at once, a new thing every minute, a bigger one every 150 s, a decision, taps of
    different cards."""
    news = [(0, "beat:H2"), *((60 * i, f"level:s{i}:2") for i in range(1, 10)), (150, "feature:f"), (300, "skill:s"),
            (450, "feature:g")]
    acts = [(20 + 45 * i, "tap", f"c{i % 3}") for i in range(12)] + [(200, "decision", "SetQueue")]
    return window(news, sorted(acts))


def test_a_busy_visit_reads_its_counts():
    f = checks.figures(clean(), opening_rules())
    assert (f.new, f.bigger, f.first_s, f.decisions, f.actions, f.run) == (13, 4, 0, 1, 13, 1)
    assert f.idle_s <= 60 and f.effort <= 5


def _no_bigger(w: Window) -> Window:
    return replace(w, news=tuple(n for n in w.news if not n.thing.startswith(checks.BIGGER)))


def _one_new(w: Window) -> Window:
    return replace(w, news=w.news[1:2])


def _late_news(w: Window) -> Window:
    return replace(w, news=tuple(replace(n, at=n.at + 120) for n in w.news))


def _no_decision(w: Window) -> Window:
    return replace(w, acts=tuple(a for a in w.acts if a[1] != "decision"))


def _idle_middle(w: Window) -> Window:
    """Nothing happens from 100 s to 250 s into the visit."""
    return replace(w, news=tuple(n for n in w.news if not START + 100 < n.at < START + 250),
                   acts=tuple(a for a in w.acts if not START + 100 < a[0] < START + 250))


def _short_busy() -> Window:
    """A two-minute return: a beat, a bigger thing, new things every half minute, a decision, a few taps."""
    news = [(0, "beat:H5"), (20, "feature:f"), (50, "level:a:2"), (80, "level:b:2"), (110, "card:look_out")]
    acts = [(5, "tap", "c0"), (30, "decision", "SetQueue"), (60, "tap", "c1"), (100, "tap", "c0")]
    return window(news, acts, length=720)


def _one_card(w: Window) -> Window:
    return replace(w, acts=tuple((t, "tap", "same") for t, _, _ in w.acts))


def _one_bigger(w: Window) -> Window:
    return replace(w, news=tuple(n for n in w.news if not n.thing.startswith(("feature:", "skill:"))))


PLANTS: dict[str, tuple[Callable[[Window], Window], Callable[[checks.Figures], bool]]] = {
    "bigger": (_no_bigger, lambda f: f.bigger == 0),
    "new things": (_one_new, lambda f: f.new == 1),
    "first new thing": (_late_news, lambda f: f.first_s == 120),
    "no decision": (_no_decision, lambda f: f.decisions == 0),
    "idle": (_idle_middle, lambda f: f.idle_s >= 150),
    "times running": (_one_card, lambda f: f.run == 13),
    "actions between bigger": (_one_bigger, lambda f: f.effort > checks.figures(clean(), opening_rules()).effort),
}
"""Each planted fault, and how the counter it moves reads it."""


@pytest.mark.parametrize("plant", sorted(PLANTS))
def test_each_planted_fault_moves_its_counter(plant: str):
    fault, reads = PLANTS[plant]
    assert reads(checks.figures(fault(clean()), opening_rules())), checks.figures(fault(clean()), opening_rules())


def test_a_visit_ends_with_its_last_activity():
    """Idle is measured to the visit's last activity, as the opening's window ends at its end moment: a visit the player
    sits on after its things are done is not idle, nor is a level the mix reaches after the player is done."""
    idle = checks.longest_idle(clean())
    assert checks.longest_idle(replace(clean(), end=clean().end + 3600)) == idle
    stray = replace(clean(), news=(*clean().news, News(START + 1200, "level:x:3", 0, 0)))
    assert checks.longest_idle(stray) == idle and checks.active_s(stray) == checks.active_s(clean())
    assert checks.active_s(_short_busy()) < 150


def test_a_day_away_counts_each_new_opening_once():
    """From a new save, nobody deciding: a planted trigger opening a third thing in the same day is counted; one
    opening what is already open is not; two on the same condition are one moment, a moment apart two."""
    rules = opening_rules()
    base = checks.absence_unlocks(rules, new_save(rules))
    planted = TriggerDef(TriggerId("t_planted"), AfterTime(100),
                         Outcome(unlocks=(Unlock(UnlockKind.CARD, CardId("rest")),)))
    more = replace(rules, triggers=(*rules.triggers, planted))
    assert checks.absence_unlocks(more, new_save(more)) == [*base, "trigger t_planted"]
    again = TriggerDef(TriggerId("t_again"), AfterTime(100),
                       Outcome(unlocks=(Unlock(UnlockKind.CARD, CardId("stand_up")),)))
    shown = replace(rules, triggers=(*rules.triggers, again))
    assert "trigger t_again" not in checks.absence_unlocks(shown, new_save(shown))   # open from the start: nothing new
    twin = TriggerDef(TriggerId("t_twin"), AfterTime(100), Outcome(unlocks=(Unlock(UnlockKind.CARD, CardId("knap_edge")),)))
    paired = replace(more, triggers=(*more.triggers, twin))
    found = checks.absence_unlocks(paired, new_save(paired))
    assert "trigger t_planted" in found and "trigger t_twin" not in found   # the same condition: one moment
    split = replace(more, triggers=(*more.triggers, replace(twin, when=AfterTime(101))))
    assert "trigger t_twin" in checks.absence_unlocks(split, new_save(split))   # a moment apart counts on its own


def test_a_journal_entry_and_a_note_each_count_as_something_opened():
    """api/CONTRACT.txt, "JOURNAL": an entry and each of its notes are unlocks, so a day away that writes them is
    counted. A planted note alone, an entry alone, and an entry with its note in one outcome (one moment) each report."""
    rules = opening_rules()
    base = checks.absence_unlocks(rules, new_save(rules))

    def planted(name: str, *unlocks: Unlock) -> list[str]:
        t = TriggerDef(TriggerId(name), AfterTime(100), Outcome(unlocks=unlocks))
        more = replace(rules, triggers=(*rules.triggers, t))
        return [f for f in checks.absence_unlocks(more, new_save(more)) if f not in base]

    entry, note = Unlock(UnlockKind.ENTRY, EntryId("e_planted")), Unlock(UnlockKind.NOTE, NoteId("n_planted"))
    assert planted("t_note", note) == ["trigger t_note"]
    assert planted("t_entry", entry) == ["trigger t_entry"]
    assert planted("t_both", entry, note) == ["trigger t_both"]
    assert planted("t_store", Unlock(UnlockKind.STORE, StoreId("damp_wood"))) == []     # control: a store alone is no opening


def test_the_story_order_check_catches_a_swap_and_a_missing_beat():
    landed = {b: 100 * i for i, b in enumerate(STORY)}
    assert checks.story_order(landed) == []
    assert checks.story_order({**landed, "H7": landed["B3"] + 1})
    assert checks.story_order({b: t for b, t in landed.items() if b != "H6"})
    assert checks.story_order({b: t for b, t in landed.items() if b != "B3"}) == ["never landed: ['B3']"]
    assert checks.story_order({b: t for b, t in landed.items() if b != "B3"}, all_land=False) == []
    short = {b: t for b, t in landed.items() if b != "B3"}
    assert story_problems("babysitter", short) == ["never landed: ['B3']"]   # held: not a reported route
    assert story_problems("lazy", short) == []


def test_the_near_promise_check_catches_a_visit_without_it():
    near = near_promise_beats()
    assert {"H1", "B3"} <= near and "H2" not in near   # read off beats.yaml, the closing ref's spine entry included
    touched = window([(0, "beat:H3")], [])
    assert checks.near_promise([touched], near) == []
    assert checks.near_promise([window([(0, "beat:H2")], [])], near)


def test_the_relative_band_allows_one_gap_per_presence_step():
    gaps = [3.0, 9.0, 4.0]
    assert b3_relative(16.6, 3.6, gaps, 2) == []                   # 3.6 + 9 + 4
    assert b3_relative(16.7, 3.6, gaps, 2)
    assert b3_relative(7.0, 3.6, gaps, 0)                          # no presence step: no lag allowed
    assert b3_relative(None, 3.6, gaps, 2) and b3_relative(5.0, None, gaps, 2)


def test_presence_steps_are_read_off_the_content():
    """Today's chain has its steps, the trigger that opens take_stock among them; the same trigger under another id is
    that step under that id, and a card's completion that also opens take_stock (in front of the player) makes the
    trigger no wait."""
    rules = opening_rules()
    today = presence_steps(rules)
    assert "t_stock_shown" in today
    opener = next(t for t in rules.triggers if t.id == "t_stock_shown")
    planted = replace(opener, id=TriggerId("t_planted"))
    moved = replace(rules, triggers=tuple(planted if t is opener else t for t in rules.triggers))
    assert presence_steps(moved) == sorted([*(x for x in today if x != "t_stock_shown"), "t_planted"])
    stock = Unlock(UnlockKind.CARD, CardId(B3_CARD))
    rack = next(c for c in rules.cards if c.id == "build_smoke_rack")
    also = replace(rack, finished=replace(rack.finished, unlocks=(*rack.finished.unlocks, stock)))
    beside = replace(rules, cards=tuple(also if c is rack else c for c in rules.cards))
    assert "t_stock_shown" not in presence_steps(beside)


def test_flatcheck_passes_the_authored_hours_and_flags_a_swap():
    assert flatcheck({"hours": {}, "visits": {}}) == []
    assert flatcheck({"hours": {"H6": 13.5, "H7": 13.0}, "visits": {}})


def test_the_queueable_check_catches_a_step_first_seen_ready_on_a_return():
    rules = opening_rules()
    base = view(new_save(rules), rules)
    card = base.cards[0]
    unready = replace(card, blocker=Blocker(AtLeast(StoreValue(StoreId("x")), 1, 1), 50))
    seen = [replace(base, time=10, cards=(unready,)), replace(base, time=20, cards=(card,))]
    boost = (card.card,)
    assert checks.boosts_shown_unready(seen, {20}, 0, boost) == []          # queued while unready, then ready
    assert checks.boosts_shown_unready(seen[1:], {20}, 0, boost)            # first seen ready on a return
    assert checks.boosts_shown_unready(seen[1:], set(), 0, boost) == []     # ready while there: tapped at once
