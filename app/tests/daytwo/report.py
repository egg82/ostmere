"""The pacing simulator's report and readouts for day two: every route (or the push ones), each day-two visit's counters
(the same columns as day one's report) with the edge of written content and returns during a long wait marked, when
each story id landed and was seen in hours after B3, each absence's unlocks, the story-shape flags, when B4 and the
beats from B5 land, what the stores lose to their caps; then the invariant checks, the Camp's levels, the day-three
placeholder levels and the 2 AM comparison. The readouts (NAMES, one per push route) are the deterministic part,
committed under tests/readouts/ and compared by test_daytwo_readouts.py; nothing in them is a threshold. Minutes,
hours and ids only (CLAUDE.md, "Never spoil the owner").

    python -m tests.daytwo.report            # from app/: every route, seed 0
    python -m tests.daytwo.report --push     # the push routes only
    python -m tests.daytwo.report --lines    # also the state lists of day two's text keys
    python -m tests.daytwo.report lazy evenings  # only these routes (the 2 AM pair only with whenever)
"""
import sys
import time

from tests import sidelayer
from tests.daytwo import abs_band, caps, checks, later, lines
from tests.daytwo.parity import her_task_at_b3, two_am2
from tests.daytwo.player import DayTwoPlayer
from tests.daytwo.routes import PUSH_ROUTES, ROUTES, day2
from tests.daytwo.story import flatcheck2, play_day
from tests.daytwo.verdicts import verdicts
from tests.dayone.parity import compare
from tests.dayone.report import row

NAMES = tuple(f"daytwo-{name}" for name in PUSH_ROUTES)


def route_text(name: str, p: DayTwoPlayer) -> str:
    """One route's readout: what day two's play did, as figures."""
    b3 = checks.b3_at(p)
    assert p.end_at is not None
    marked = checks.marks(p)
    out = [f"{name}: B3 {(b3 - p.end_at) / 3600:.1f} h after the end; B4 {checks.b4_hours(p)} h after B3; "
           f"{len(checks.day_visits(p))} day-two visits"]
    lay = sidelayer.layers()
    out += [row(w, p) + "  | " + sidelayer.line(sidelayer.count((n.thing for n in w.news), lay))
            + (f"  [{marked[w.label]}]" if w.label in marked else "") for w in checks.windows(p)]
    hours = {b: round((t - b3) / 3600, 2) for b, t in sorted(p.landed_at.items(), key=lambda kv: (kv[1], kv[0])) if t >= b3}
    out += [f"  landed (h after B3) {hours}",
            f"  seen   (h after B3) { {b: round((p.seen_at[b] - b3) / 3600, 2) for b in hours if b in p.seen_at} }"]
    out += [f"  away {label}: {len(opened)} {opened}" for label, opened in checks.absences(p)]
    out.append(f"  flatcheck {flatcheck2(p)}")
    pace = abs_band.load_pace()
    out.append("  " + abs_band.summary(name, abs_band.reached(p.landed_at, p.history[0][0].time, pace), pace))
    out += caps.lines_of(name, caps.day_two_loss(p))
    return "\n".join(out) + "\n"


def readouts() -> dict[str, str]:
    return {f"daytwo-{name}": route_text(name, day2(name)) for name in PUSH_ROUTES}


def route_report(name: str) -> DayTwoPlayer:
    t0 = time.process_time()
    p = day2(name)
    cpu = time.process_time() - t0
    print(f"\n{route_text(name, p)}  played in {cpu:.1f} CPU s")
    for wk, c in sidelayer.per_week(p.news, sidelayer.layers(), play_day).items():
        print(f"  week {wk}: {sidelayer.line(c)}")
    print(f"  camp levels (h after B3) {later.camp(p)}")
    for beat in later.PLACEHOLDERS:
        lv = later.level_at(p, beat)
        print(f"  {beat}: {lv.skill} {lv.level}, at B3 {lv.at_b3}, at B4 {lv.at_b4}, "
              f"projected {lv.hours_after_b4} h after B4: {lv.verdict}")
    skills = [str(s.skill) for s in p.save.skills]
    print("  projected levels at B4 / +10 h / +30 h: " + ", ".join(
        f"{s} {'/'.join(str(later.level_after(p, s, h)) for h in (0, 10, 30))}" for s in skills))
    for check, problems in verdicts(name).items():
        print(f"  {check:12s} {'FAIL' if problems else 'ok':4s} {'; '.join(problems)[:300]}")
    return p


def two_am_report() -> None:
    t0 = time.process_time()
    w, b = two_am2()
    diffs = compare(w, b)
    print(f"\n2 AM, day two (whenever vs babysitter given its reveals, {time.process_time() - t0:.1f} CPU s): "
          f"{'level' if not diffs else ''}")
    for d in diffs:
        print(f"  {d}")
    moved = her_task_at_b3()
    print("\nher task changed at B3 instead of at the whenever player's return: "
          + ("the whenever player never changes it" if moved is None else ("level" if not compare(*moved) else "")))
    for d in [] if moved is None else compare(*moved):
        print(f"  {d}")


def main(argv: list[str]) -> int:
    named = [a for a in argv if a in ROUTES]
    names = named or list(PUSH_ROUTES if "--push" in argv else ROUTES)
    plays = {name: route_report(name) for name in names}
    if not named or "whenever" in named:
        two_am_report()
    if "--lines" in argv:
        print("\n".join(lines.report(plays)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
