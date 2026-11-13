"""The pacing simulator's report and readouts for day one: every route (or the push ones), each visit's counters beside
the opening's own, when each story id landed and was seen, what a day away from each visit opens, the visits that
leave the near promise untouched, the content team's story-shape flags, the goals, the leaves that name only a speed
level, the invariant checks' verdicts and the 2 AM comparison; the human-paced player's day; the absence ladder; the
rebase loads. The readouts (NAMES) are the deterministic part, committed under tests/readouts/ and compared by
test_dayone_readouts.py; nothing in them is a threshold. Minutes, hours and ids only (CLAUDE.md, "Never spoil the owner").

    python -m tests.dayone.report            # from app/: every route, seed 0
    python -m tests.dayone.report --push     # the push routes only
    python -m tests.dayone.report --lines    # also the line state lists
    python -m tests.dayone.report --goals    # also each goal sample: the open goals (* when the setup drives it)
                                             # and whether weighting decides which comes first
    python -m tests.dayone.report --human    # only the human-paced player's day (human_flags.py)
    python -m tests.dayone.report --absence  # only the absence ladder: what a return holds after 1 h to 7 days (absence.py)
"""
import sys
import time

from tests.dayone import absence, checks, goals, human_report
from tests.dayone import human_flags as hf
from tests.dayone.beats import near_promise_beats
from tests.dayone.human import HumanPlayer, human_day, thresholds
from tests.dayone.levelpays import day_one_exits, leave_point, leave_points, speed_only_leaves
from tests.dayone.parity import compare
from tests.dayone.player import DayOnePlayer
from tests.dayone.routes import PUSH_ROUTES, ROUTES, day, two_am
from tests.dayone.screen import FIRST_S, aimless, chip_after, early, stated, views
from tests.dayone.story import AWAY, ended_saves, flatcheck, rebase_line, rebased_case, route_json
from tests.dayone.verdicts import verdicts
from tests.opening.playthrough import opening

NAMES = (*(f"dayone-{name}" for name in PUSH_ROUTES), "dayone-human", "dayone-absence", "dayone-rebase")


def row(w: checks.Window, p: DayOnePlayer) -> str:
    f = checks.figures(w, p.rules)
    return (f"  {w.label:8s} gap {w.gap / 3600:5.1f}h  active {checks.active_s(w) / 60:4.1f}m  new {f.new:3d}  "
            f"bigger {f.bigger:2d}  first {'-' if f.first_s is None else f.first_s:>4}s  decisions {f.decisions:2d}  "
            f"actions {f.actions:3d}  idle {f.idle_s:4d}s  run {f.run}  effort {f.effort:2d}")


def _b3_text(p: DayOnePlayer) -> str:
    hours = checks.b3_hours(p)
    return "B3 never landed" if hours is None else f"B3 {hours}h after it"


def route_text(name: str, p: DayOnePlayer) -> str:
    """One route's readout: what the route did, as figures."""
    assert p.end_at is not None
    held = checks.visits_held(p)
    out = [f"{name}: the end at {p.end_at / 60:.1f}m; {_b3_text(p)}; {len(p.visits)} visits",
           row(checks.opening_window(p), p), *(row(w, p) for w in checks.windows(p))]
    hours = {b: round((t - p.end_at) / 3600, 2) for b, t in sorted(p.landed_at.items(), key=lambda kv: (kv[1], kv[0]))}
    seen = {b: round((p.seen_at[b] - p.end_at) / 3600, 2) for b in hours if b in p.seen_at}
    out += [f"  landed (h) {hours}", f"  seen (h)   {seen}"]
    out += [f"  a day away from {label} opens {len(opened)} {opened}" for label, opened in checks.absences(p)]
    out.append(f"  near promise untouched in {checks.near_promise(held, near_promise_beats())} of {len(held)} returns")
    out.append(f"  flatcheck {flatcheck(route_json(p))}")
    g = goals.goal_summary(goals.goal_samples(p))
    out.append(f"  goals: {g.samples} samples, {g.choice_due} with a choice due, {g.undriven} of those with no goal the "
               f"setup drives; weighting decides the order at {g.decided} of {g.judged} with a pair")
    out.append(f"  leaves naming only a speed level {speed_only_leaves(leave_points(p), p.rules)}")
    return "\n".join(out) + "\n"


def human_text(p: HumanPlayer, found: list[hf.Session]) -> str:
    """The human-paced player's day: its sessions and flags, its unlocks, the views stating no aim, the mechanics drawn
    in the first minutes, and the leaves naming only a speed level."""
    assert p.end_at is not None
    th = thresholds()
    seen = stated(opening().aims, views(p))
    gaps = aimless(seen)
    shown = {s.label: s.leave for s in found if s.leave is not None}
    points = [leave_point(p, label, save, shown[label]) for label, save in day_one_exits(p)]
    out = [f"the opening ends at {p.end_at / 60:.1f}m; dead gap {th.dead_gap} = {th.dead_gap_s():.0f}s",
           *human_report.session_lines(p, found),
           f"{sum(len(s.dead) for s in found)} dead stretches; {sum(1 for s in found if hf.bored(s))} bored leaves of "
           f"{sum(1 for s in found if s.leave)}",
           "unlocks, earned (typical lands it sooner than by_hand) or fixed-time", *human_report.unlock_lines(p, th),
           f"views stating no aim: {len(gaps)} of {len(seen)}" + (f", the first at {gaps[0] / 60:.1f}m" if gaps else ""),
           f"mechanics drawn in the first {FIRST_S // 60} minutes: {sorted(early(p, chip_after()))}",
           f"leaves naming only a speed level {speed_only_leaves(points, p.rules)}"]
    return "\n".join(out) + "\n"


def absence_text(points: list[absence.Point]) -> str:
    return "\n".join(absence.lines_of(points)) + "\n"


def rebase_text() -> str:
    return "rebased golden ends: what the load and the time away open\n" + "\n".join(
        rebase_line(path, away, rebased_case(path, away)) for path in ended_saves() for away in AWAY) + "\n"


def readouts() -> dict[str, str]:
    p = human_day()
    texts = {f"dayone-{name}": route_text(name, day(name)) for name in PUSH_ROUTES}
    texts["dayone-human"] = human_text(p, hf.sessions(p, thresholds()))
    texts["dayone-absence"] = absence_text(absence.ladder(p, visits=(1, 2, 3), hours=(1, 8, 24)))
    texts["dayone-rebase"] = rebase_text()
    return texts


def route_report(name: str) -> None:
    t0 = time.perf_counter()
    p = day(name)
    played = time.perf_counter() - t0
    print(f"\n{route_text(name, p)}  played in {played:.2f}s")
    for check, problems in verdicts(name).items():
        print(f"  {check:13s} {'FAIL' if problems else 'ok':4s} {'; '.join(problems)[:300]}")


def lines_report(names: list[str]) -> None:
    """Each day-one line key with the states it fired in: route, visit, present or seen on return, and the builds."""
    print("\nline states")
    states: dict[str, set[str]] = {}
    for name in names:
        p = day(name)
        for ln in p.lines:
            if p.end_at is None or ln.time < p.end_at:
                continue
            v = next((v for v in p.visits if v.start <= ln.time <= v.end), None)
            where = f"V{v.index} present" if v is not None else "away"
            states.setdefault(ln.key, set()).add(f"{name} {where}")
    for key in sorted(states):
        print(f"  {key:18s} {sorted(states[key])}")


def goals_report(names: list[str]) -> None:
    for name in names:
        found = goals.goal_samples(day(name))
        print(f"\n{name} goals")
        for s in found:
            print(f"  +{s.at_min:7.1f}m  weighting {'-' if s.weighting is None else s.weighting!s:5s}  {' '.join(s.goals)}")


def main(argv: list[str]) -> int:
    if "--human" in argv:
        human_report.main()
        return 0
    if "--absence" in argv:
        absence.main()
        return 0
    names = list(PUSH_ROUTES if "--push" in argv else ROUTES)
    for name in names:
        route_report(name)
    t0 = time.perf_counter()
    w, b = two_am()
    print(f"\n2 AM (whenever vs babysitter given its reveals, {time.perf_counter() - t0:.2f}s): "
          f"{'level' if not compare(w, b) else ''}")
    for diff in compare(w, b):
        print(f"  {diff}")
    if "--lines" in argv:
        lines_report(names)
    if "--goals" in argv:
        goals_report(names)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
