"""The report of the human-paced player's day (python -m tests.dayone.report --human): thresholds used, each session's
notable events, dead stretches and leave (a bored leave flagged), and the earned and fixed-time unlocks. Reports, never fails. Times are game
seconds after the opening's end, with the player's clock beside them; beats and promises by id only."""
import time

from tests.dayone import human_flags as hf
from tests.dayone.human import HumanPlayer, Thresholds, human_day, thresholds
from tests.dayone.routes import day
from tests.dayone.schedules import HOUR, OPENING_CLOCK


def at(t: int, end_at: int) -> str:
    """`t` (engine seconds) as hours after the opening's end and the clock on the player's wall (opening at 20:00)."""
    clock = (OPENING_CLOCK + t) % (24 * HOUR)
    return f"+{(t - end_at) / HOUR:.2f}h ({clock // HOUR:02d}:{clock % HOUR // 60:02d})"


def session_lines(p: HumanPlayer, found: list[hf.Session]) -> list[str]:
    assert p.end_at is not None
    out: list[str] = []
    for s in found:
        first = f"{s.notables[0][0] - s.start}s" if s.notables else "never"
        out.append(f"{s.label:8s} {at(s.start, p.end_at)}  {(s.end - s.start) / 60:5.1f}m  {len(s.notables):3d} notable, first "
                   f"{first}")
        out.append("    at +s: " + " ".join(f"{t - s.start}{'' if w == 'decision' else '=' + w}" for t, w in s.notables))
        out += [f"    FLAG no notable event for {(b - a) / 60:.1f}m, {at(a, p.end_at)} to {at(b, p.end_at)}"
                for a, b in s.dead]
        if s.leave is not None:
            named = ", ".join(f"{k} {i} in {d / 60:.0f}m" for k, i, d in s.leave.payoffs)
            out.append(f"    leave {at(s.end, p.end_at)}: payoff named: {named or 'NONE'}; story question open: "
                       f"{', '.join(sorted(s.leave.questions)) or 'NONE'}")
        if hf.bored(s):
            out.append(f"    FLAG bored leave: the screen names nothing to come back for, {at(s.end, p.end_at)}")
    return out


def unlock_lines(p: HumanPlayer, th: Thresholds) -> list[str]:
    assert p.end_at is not None
    found = hf.human_unlocks(p, day("typical"), day("by_hand"), th)
    out = [f"day {d}: {dict(c)}" for d, c in sorted(hf.per_day(found).items())]
    out += [f"  {at(m.at + p.end_at, p.end_at)} {m.label:7s} {' '.join([*map(hf.unlock_name, m.unlocks), *map(hf.stage_name, m.stages)])}"
            for m in found]
    out += [f"FLAG only fixed-time unlocks and stages land: {len(r)} moments, {at(r[0].at + p.end_at, p.end_at)} to "
            f"{at(r[-1].at + p.end_at, p.end_at)}" for r in hf.fixed_runs(found, round(th.v("fixed_run_min")))]
    return out


def main() -> None:
    th = thresholds()
    t0 = time.perf_counter()
    p = human_day()
    assert p.end_at is not None
    found = hf.sessions(p, th)
    print(f"human-paced player: played in {time.perf_counter() - t0:.2f}s; the opening ends at {p.end_at / 60:.1f}m "
          f"(first session in the research: {th.v('first_session_s') / 60:.0f}m); B3 seen {at(p.seen_at['B3'], p.end_at)}"
          if "B3" in p.seen_at else "human-paced player: B3 never seen")
    print(f"dead gap used {th.dead_gap} = {th.dead_gap_s():.0f}s (also recorded: dead_gap_research_s = "
          f"{th.v('dead_gap_research_s'):.0f}s, unused)")
    print("\n".join(session_lines(p, found)))
    print(f"\n{sum(len(s.dead) for s in found)} dead stretches; {sum(1 for s in found if hf.bored(s))} bored leaves "
          f"of {sum(1 for s in found if s.leave)}")
    print("\nunlocks, earned (typical lands it sooner than by_hand) or fixed-time\n" + "\n".join(unlock_lines(p, th)))
