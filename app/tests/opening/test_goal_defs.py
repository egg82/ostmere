"""What each story beat waits on (opening/goals.py), read off the content through day fifteen: a beat whose condition,
or the condition of a trigger that feeds its gate (the one giving an unlock it needs, and so on back), reads a store the
player is never shown is carried on screen, a wait on the clock by the wait line's countdown
(ui/story/waitline.ts) naming the shown stores that keep it moving, which a standing action's lines must move for a countdown
to exist, a store cards fill by a row of its own in the Camp bar's box with those cards marked (ui/story/goals.ts,
game/story.ts). Trigger ids only."""
from collections.abc import Callable
from functools import cache

from ashfall_app.engine import QUANTITY_SCALE, AtLeast, AtMost, Rules, StoreValue, TriggerDef, Unlock, UnlockKind, Unlocked
from ashfall_app.opening.goals import GoalDef, goal_defs, moved_by, story
from ashfall_app.opening.entries import ConditionEntry, OutcomeEntry, TriggerEntry
from ashfall_app.opening.refs import outcomes
from ashfall_app.opening.schema import CHAPTERS, IN_WRITING, Opening, load_opening, to_rules


@cache
def merged() -> tuple[Opening, Rules]:
    o = load_opening(chapters=CHAPTERS + IN_WRITING)
    return o, to_rules(o)


def never_shown(o: Opening, r: Rules) -> set[str]:
    """Stores no outcome or start ever unlocks, and hidden ones."""
    given = {u for t in r.triggers for u in t.outcome.unlocks} | {u for c in r.cards for u in c.outcome.unlocks}
    given |= {u for c in r.cards for u in c.finished.unlocks} | set(r.opening or ())
    return {s.id for s in o.stores if s.hidden or Unlock(UnlockKind.STORE, s.id) not in given}


def reads(t: TriggerDef) -> set[str]:
    conds = (t.when, *t.requires)
    return {str(c.subject.store) for c in conds if isinstance(c, (AtLeast, AtMost)) and isinstance(c.subject, StoreValue)}


def feeder(o: Opening, r: Rules) -> Callable[[str], list[str]]:
    """The walk from a trigger to every trigger that feeds its gate: the ones giving an unlock its `when` or requires
    read, and the ones giving a standing action that moves a store they read, and theirs in turn. An unlock a card or an
    answer gives is on screen as that card or answer."""
    by_id = {str(t.id): t for t in r.triggers}
    givers: dict[Unlock, list[str]] = {}
    for t in r.triggers:
        for u in t.outcome.unlocks:
            givers.setdefault(u, []).append(str(t.id))
    movers: dict[str, list[str]] = {}
    for a in o.standing:
        for s in moved_by(a):
            movers.setdefault(s, []).append(a.id)

    def walk(tid: str) -> list[str]:
        seen: dict[str, None] = {}
        todo = [tid]
        while todo:
            x = todo.pop()
            if x in seen:
                continue
            seen[x] = None
            for c in (by_id[x].when, *by_id[x].requires):
                if isinstance(c, AtLeast) and isinstance(c.subject, Unlocked):
                    todo += givers.get(c.subject.unlock, [])
            for store in reads(by_id[x]):
                todo += [g for a in movers.get(store, []) for g in givers.get(Unlock(UnlockKind.ACTION, a), [])]
        return list(seen)

    return walk


def runnable(o: Opening, r: Rules) -> set[str]:
    """The standing actions something unlocks: the start, a trigger, a card or an answer."""
    given = {(u.unlock_kind, u.id) for _, out in outcomes(o) for u in out.unlocks} | {(u.unlock_kind, u.id) for u in o.start}
    return {a.id for a in o.standing if ("action", a.id) in given}


def on_unshown(o: Opening, r: Rules, defs: dict[str, GoalDef]) -> list[str]:
    """Story beats whose gate, or a gate feeding it, reads a never-shown store with no goal on it: nothing on screen
    could carry the wait. Each is named by the trigger that reads the store."""
    camp = None if o.camp is None else o.camp.store
    hidden = never_shown(o, r) - {camp}
    by_id = {str(t.id): t for t in r.triggers}
    live, feeding = runnable(o, r), feeder(o, r)
    found = {m for t in r.triggers if story(t.outcome) for m in feeding(str(t.id))
             if reads(by_id[m]) & hidden and not _carried(o, defs.get(m), reads(by_id[m]) & hidden, live)}
    return [t.id for t in r.triggers if t.id in found]


def _carried(o: Opening, d: GoalDef | None, stores: set[str], live: set[str]) -> bool:
    """A clock is carried when a standing action that something unlocks moves each store it reads, so the wait line has
    a time to count down to (or, with a store of fed_by dry, a stop to name); a store when cards make it; a card
    fight's lost tally by its card, the wait line naming it and the count."""
    if d is None:
        return False
    if d.kind == "clock":
        return all(any(s in moved_by(a) and a.id in live for a in o.standing) for s in stores)
    if d.kind == "fight":
        return stores == {d.tally}
    return d.kind == "store" and stores == {d.subject} and bool(d.makers)


def test_every_beat_on_a_store_never_shown_is_carried_on_screen():
    o, r = merged()
    defs = goal_defs(o, r)
    hidden = never_shown(o, r)
    assert sum(1 for t in r.triggers if story(t.outcome) and reads(t) & hidden) > 20, "found too few: the probe is blind"
    assert on_unshown(o, r, defs) == []


def test_the_check_fails_a_beat_whose_wait_nothing_carries():
    o, r = merged()
    defs = goal_defs(o, r)
    planted = {**defs, "t_prints": GoalDef("card", "smoke_catch", 1)}
    assert on_unshown(o, r, planted) == ["t_prints"]


def test_the_check_fails_a_clock_nothing_moves():
    """t_prints' clock with the standing action that moves its store taken out: no countdown can be served."""
    o, r = merged()
    defs = goal_defs(o, r)
    still = o.model_copy(update={"standing": [a for a in o.standing if "h7_clock" not in moved_by(a)]})
    assert len(still.standing) < len(o.standing)
    assert "t_prints" in on_unshown(still, r, defs)
    assert set(on_unshown(still, r, defs)) <= {t.id for t in r.triggers if "h7_clock" in reads(t)}


def test_h7s_wait_names_the_store_that_keeps_it_moving():
    o, r = merged()
    assert goal_defs(o, r)["t_prints"] == GoalDef("clock", None, 0, fed_by=("roots",))


def with_lost_beat() -> tuple[Opening, Rules, str, str]:
    """The content with a story beat added that waits on a card fight's lost tally: a fixture, no content of its own."""
    o, _ = merged()
    card = next(c for c in o.cards if c.fight is not None)
    assert card.fight is not None
    beat = TriggerEntry(id="t_fixture_lost", when=ConditionEntry(test="at_least", subject_kind="store", id=card.fight.lost, value=3),
                        outcome=OutcomeEntry(unlocks=[next(t.outcome.unlocks[0] for t in o.triggers if t.outcome.unlocks)]))
    o2 = o.model_copy(update={"triggers": [*o.triggers, beat]})
    return o2, to_rules(o2), card.id, card.fight.lost


def test_a_wait_on_a_card_fights_lost_tally_is_carried_by_its_card():
    o, r, card, tally = with_lost_beat()
    defs = goal_defs(o, r)
    assert defs["t_fixture_lost"] == GoalDef("fight", card, 3 * QUANTITY_SCALE, tally=tally)
    assert tally in never_shown(o, r), "the tally is never a shown store: the probe is blind"
    assert on_unshown(o, r, defs) == []


def test_the_check_fails_a_fight_wait_that_nothing_carries():
    o, r, card, _ = with_lost_beat()
    planted = {**goal_defs(o, r), "t_fixture_lost": GoalDef("card", card, 1)}
    assert on_unshown(o, r, planted) == ["t_fixture_lost"]


def test_a_beats_gate_is_followed_back_to_the_clock_that_has_to_start():
    """t_b16 waits on a clock a standing action moves, that t_starer unlocks, which waits on meals, which t_b14's table
    makes: the chain reaches each, so what holds them is read too."""
    o, r = merged()
    chain = feeder(o, r)("t_b16")
    assert {"t_starer", "t_b14"} <= set(chain)
    assert feeder(o, r)("t_prints")[0] == "t_prints", "the walk starts at the beat"


def test_a_clock_whose_standing_action_nothing_unlocks_is_not_carried():
    o, r = merged()
    defs = goal_defs(o, r)
    live = runnable(o, r)
    assert "walk_out" in live, "control: the standing action is unlocked by an answer"
    assert _carried(o, defs["t_walk_out"], {"walk_out"}, live)
    assert not _carried(o, defs["t_walk_out"], {"walk_out"}, live - {"walk_out"})


def test_meals_is_stated_and_its_clock_names_the_count():
    o, r = merged()
    d = goal_defs(o, r)["t_starer"]
    assert (d.kind, d.count, d.target) == ("clock", "meals", 56 * QUANTITY_SCALE)
    assert goal_defs(o, r)["t_prints"].count is None


def test_the_check_fails_a_gate_feeding_a_beat_that_nothing_carries():
    o, r = merged()
    planted = {k: v for k, v in goal_defs(o, r).items() if k != "t_starer"}
    assert "t_starer" in on_unshown(o, r, planted)
