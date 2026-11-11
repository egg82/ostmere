"""The counters and checks on one played route (content/team/day-one.md, "Per visit"; the plan's section 3), each a
pure function of the player's records. The counters (`figures`, `absences`, `near_promise`) are what the readout prints
(report.py), never held to a number; the checks (`story_order`, `boosts_shown_unready`) return their problems (empty:
the check holds). Both name visits, minutes and content ids only (CLAUDE.md, "Never spoil the owner").

A visit is measured from its start (the return: what landed while away is shown then) to its end. Its new things are
the News stamped inside it; the bigger ones are a new kind of thing (BIGGER): a story beat, a page part or feature, a
skill row, a rule offered, a control (When ready), a producer or a lane's card. Its actions are its decisions, taps
and others; an idle stretch is the time between two consecutive moments of activity (an action, a new thing, the
visit's start), up to the last one: the player leaves when nothing is left, as the opening's own window ends at its
end moment. A visit's active time, start to last activity, is a figure too."""
from collections.abc import Iterable
from dataclasses import dataclass
from itertools import groupby

from ashfall_app.engine import BP, Condition, Rules, Save, TriggerDef, Unlock, UnlockKind, View, advance
from tests.dayone.beats import STORY
from tests.dayone.player import DayOnePlayer
from tests.opening.playthrough import News

PER_VISIT_GAP = 3600
"""A visit after this long away is a return; shorter ones are a look in the same sitting."""
ACTIVE_GAP_S = 90
"""What lands this soon after the player's last moment of activity is still the visit's (`_moments`)."""
DAY_FORWARD_S = 24 * 3600
BIGGER = ("beat:", "feature:", "skill:", "order_card:", "control:", "offer:")
QUIET = ("retired:", "end", "answered:", "answer:")
"""Not a new thing to the player: a step leaving the panel, the end moment's own marker, the player's own answer."""


@dataclass(frozen=True)
class Window:
    """One visit (or the opening's session) as the checks read it."""

    label: str
    start: int
    end: int
    gap: int
    news: tuple[News, ...]
    acts: tuple[tuple[int, str, str], ...]


def windows(p: DayOnePlayer) -> list[Window]:
    return [_window(p, f"V{v.index}", v.start, v.end, v.gap) for v in p.visits]


def opening_window(p: DayOnePlayer) -> Window:
    """The opening's own session, start to end moment: the reference every later visit is held to."""
    assert p.end_at is not None
    return _window(p, "opening", 0, p.end_at, 0)


def _window(p: DayOnePlayer, label: str, start: int, end: int, gap: int) -> Window:
    news = tuple(n for n in p.news if start <= n.at <= end and not n.thing.startswith(QUIET) and _visible(p, n))
    acts = tuple((t, kind, what) for t, kind, what in p.acts if start <= t <= end)
    if label == "opening":
        acts = tuple((t, kind, _label(v)) for t, kind, v in p.decisions if t <= end)
    return Window(label, start, end, gap, news, acts)


def _label(verb: object) -> str:
    card = getattr(verb, "card", None)
    return card if isinstance(card, str) else type(verb).__name__


def _visible(p: DayOnePlayer, n: News) -> bool:
    """A standing action is a new thing only when it moves a store the player can see."""
    if not n.thing.startswith("action:"):
        return True
    action = next(a for a in p.rules.standing if a.id == n.thing.split(":", 1)[1])
    shown = {u.id for u in p.save.unlocked if u.kind is UnlockKind.STORE}
    return any(f.store in shown for f in (*action.makes, *action.costs))


def bigger(n: News, rules: Rules) -> bool:
    if n.thing.startswith(BIGGER) or n.thing.startswith("action:"):
        return True
    if n.thing.startswith("card:"):
        return next(c for c in rules.cards if c.id == n.thing.split(":", 1)[1]).lane != "hands"
    return False


# ---------- per visit ----------

@dataclass(frozen=True)
class Figures:
    """One visit's counters, as the readout prints them."""

    new: int
    bigger: int
    first_s: int | None
    """Seconds from the return to the first new thing, or None when nothing new came."""
    decisions: int
    actions: int
    idle_s: int
    run: int
    effort: int
    """The most actions between two bigger things."""


def figures(w: Window, rules: Rules) -> Figures:
    return Figures(len(w.news), sum(1 for n in w.news if bigger(n, rules)), (w.news[0].at - w.start) if w.news else None,
                   sum(1 for _, kind, _ in w.acts if kind == "decision"), len(w.acts), longest_idle(w), longest_run(w)[1],
                   max(efforts(w, rules), default=0))


def _moments(w: Window) -> list[int]:
    """The visit's activity window, start to its last moment: every act, what is new up to the last act, and then what
    lands while each lands within ACTIVE_GAP_S of the one before (the last step's own landing). A thing landing longer
    after the player's last act (a level the mix reached) is met at the next look, not activity in this visit."""
    every = sorted({w.start, *(n.at for n in w.news), *(t for t, _, _ in w.acts)})
    last_act = max((t for t, _, _ in w.acts), default=w.start)
    kept = [m for m in every if m <= last_act]
    for m in (m for m in every if m > last_act):
        if m - kept[-1] > ACTIVE_GAP_S:
            break
        kept.append(m)
    return kept


def longest_idle(w: Window) -> int:
    """The longest stretch between two moments of activity, up to the visit's last: the player leaves when nothing
    is left, as the opening's window ends at its own end (Window)."""
    moments = _moments(w)
    return max((b - a for a, b in zip(moments, moments[1:])), default=0)


def active_s(w: Window) -> int:
    """From the return to the visit's last activity."""
    return _moments(w)[-1] - w.start


def longest_run(w: Window) -> tuple[str, int]:
    taps = [what for _, kind, what in w.acts if kind == "tap"]
    runs = [(card, len(list(g))) for card, g in groupby(taps)]
    return max(runs, key=lambda r: r[1], default=("", 0))


def efforts(w: Window, rules: Rules) -> list[int]:
    """Actions from the visit's start, or one bigger thing, to the next bigger thing or the visit's end."""
    marks = [w.start, *sorted({n.at for n in w.news if bigger(n, rules)}), w.end + 1]
    return [sum(1 for t, _, _ in w.acts if a <= t < b) for a, b in zip(marks, marks[1:])]


def visits_held(p: DayOnePlayer) -> list[Window]:
    return [w for w in windows(p) if w.gap >= PER_VISIT_GAP]


# ---------- away ----------

def absence_unlocks(rules: Rules, exit_save: Save, span: int = DAY_FORWARD_S) -> list[str]:
    """What opens with nobody deciding for `span` from a visit's exit: each trigger or step whose landing unlocks
    something new to see (a store, a retirement or a level's find are not openings); a trigger's two builds are one,
    and so are triggers on the same condition (one moment, split so a released outcome stays as it was)."""
    return unlocks_between(rules, exit_save, advance(exit_save, rules, exit_save.time + span))


def unlocks_between(rules: Rules, exit_save: Save, later: Save) -> list[str]:
    """absence_unlocks between two saves of one play: what opened from `exit_save` to `later` with nobody deciding."""
    fired = [t for t, a, b in zip(rules.triggers, exit_save.fired, later.fired) if b and not a]
    found = [f"trigger {t.id}" for t in one_per_moment(t for t in fired if opens(rules, t.outcome.unlocks, later, exit_save))]
    done_before = {c.card: c.work.start_value for c in exit_save.cards}
    for c in rules.cards:
        after = next((s.work.start_value for s in later.cards if s.card == c.id), 0)
        if c.cap is not None and after >= c.work_s * BP > done_before.get(c.id, 0) \
                and opens(rules, c.finished.unlocks, later, exit_save):
            found.append(f"card {c.id}")
    return found


def one_per_moment(triggers: Iterable[TriggerDef]) -> list[TriggerDef]:
    """The first of each set of triggers with the same condition: they always fire together, so they are one moment."""
    seen: set[Condition] = set()
    out: list[TriggerDef] = []
    for t in triggers:
        if t.when not in seen:
            seen.add(t.when)
            out.append(t)
    return out


def opens(rules: Rules, unlocks: tuple[Unlock, ...], save: Save, before: Save | None = None) -> bool:
    """An outcome opens something to see: a card, a page part, a skill row, a chip, an offer, a journal entry or note
    (api/CONTRACT.txt, "JOURNAL"), or a standing action that moves a store on the ledger (a store alone, a retirement, a
    hidden clock are not openings, nor is anything already open in `before`)."""
    shown = {u.id for u in save.unlocked if u.kind is UnlockKind.STORE}
    known: set[Unlock] = set() if before is None else set(before.unlocked)
    for u in (u for u in unlocks if u not in known):
        if u.kind in (UnlockKind.CARD, UnlockKind.FEATURE, UnlockKind.SKILL, UnlockKind.CHIP, UnlockKind.OFFER,
                      UnlockKind.ENTRY, UnlockKind.NOTE):
            return True
        if u.kind is UnlockKind.ACTION:
            a = next(a for a in rules.standing if a.id == u.id)
            if any(f.store in shown for f in (*a.makes, *a.costs)):
                return True
    return False


def absences(p: DayOnePlayer) -> list[tuple[str, list[str]]]:
    """(visit, what a day away from its exit opens with nobody deciding) for each visit."""
    out: list[tuple[str, list[str]]] = []
    for v in p.visits:
        assert v.exit is not None
        out.append((f"V{v.index}", absence_unlocks(p.rules, v.exit)))
    return out


# ---------- the story ----------

def story_order(landed_at: dict[str, int]) -> list[str]:
    """Day one's beats all land, in the authored order (H6 < H7 < B3 and H1 < H2 among them)."""
    missing = [b for b in STORY if b not in landed_at]
    order = sorted((b for b in STORY if b in landed_at), key=lambda b: (landed_at[b], STORY.index(b)))
    found = [f"never landed: {missing}"] if missing else []
    return found + ([f"order {order}"] if order != [b for b in STORY if b in order] else [])


def near_promise(held: list[Window], near: frozenset[str]) -> list[str]:
    """The visits after an hour away that show no beat opening, advancing or paying the near promise."""
    return [f"{w.label}: near promise untouched" for w in held
            if not any(n.thing.split(":", 1)[1] in near for n in w.news if n.thing.startswith("beat:"))]


def b3_hours(p: DayOnePlayer) -> float | None:
    assert p.end_at is not None
    return None if "B3" not in p.landed_at else round((p.landed_at["B3"] - p.end_at) / 3600, 1)


# ---------- queueable before it can be afforded ----------

def boosts_shown_unready(seen: Iterable[View], returns: set[int], end_at: int, boosts: tuple[str, ...]) -> list[str]:
    """Each push of each rate- or cap-raising step is on screen unready with a known ready time during a visit before
    it turns ready, so the queue can wait on it, unless it turns ready while the player is there (the plan's design
    rule for the 2 AM test). `seen`: every view the player saw, in order; `returns`: the times it came back. A push
    first seen ready on a return was readied unseen, and the babysitter is ahead."""
    views = list(seen)
    found: list[str] = []
    for card in boosts:
        queueable: set[int] = set()
        done: set[int] = set()
        for v in views:
            cv = next((c for c in v.cards if c.card == card), None)
            if cv is None or cv.completions in done:
                continue
            if cv.blocker is not None:
                if cv.blocker.ready_at is not None:
                    queueable.add(cv.completions)
                continue
            done.add(cv.completions)
            if v.time in returns and cv.completions not in queueable:
                found.append(f"{card} push {cv.completions + 1} first seen ready on a return, "
                             f"{(v.time - end_at) / 3600:.1f}h after the end")
    return found
