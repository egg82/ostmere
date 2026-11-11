"""The ladder readout: each played route through the edge of played content on the live engine, printing per skill the
game time every level was first reached and the gap from the one before, with the current phase's top and when it was
reached, then each card's share of the running mixes by game day, flagging the cards whose share went to zero and
stayed there ("Each new layer reworks the old ones", docs/decisions.md), then each skill's XP by source per band of game
days (sources.py) and whether one saved mix shape always wins (dominance.py: at each sampled instant every saved hands
mix is scored alone as the running mix, by the levels it gains per game hour, and the shape of the best one wins; the
shapes and the definition are in dominance.py). Times in game days, shares in percent. It reports and fails nothing; its text per push route (NAMES) is committed under tests/readouts/ and compared by
tests/weektwo/test_ladder_readouts.py, whose job has week two's plays. Ids, levels and times only (CLAUDE.md, "Never
spoil the owner").

    python -m tests.ladder.readout                    # from app/: the push routes through day twelve, seed 0
    python -m tests.ladder.readout typical sharp      # the named routes
    python -m tests.ladder.readout typical --last 6   # only each skill's last 6 levels
    python -m tests.ladder.readout typical --skills   # only the skills' ladders
    python -m tests.ladder.readout typical --shares   # only the cards' shares, XP sources and the dominance verdict
    python -m tests.ladder.readout typical --step 2   # sample the shares every 2 game hours (the default 4)
"""
import sys
import time

from ashfall_app.engine import Save, advance
from tests.daytwo.player import DayTwoPlayer
from tests.ladder.dominance import Dominance, dominance
from tests.ladder.reach import reaches
from tests.ladder.shares import DAY_S, day_averages, gone_quiet
from tests.ladder.sources import BANDS, band_label, band_shares
from tests.ladder.ticks import (
    at_time, card_shares, counted_at, mix_scores, phase_progress, phase_top_level, xp_by_source,
)
from tests.weektwo.routes import TWELVE_PUSH_ROUTES, twelve

HOUR_S = 3600
STEP_H = 4
NAMES = tuple(f"ladder-{name}" for name in TWELVE_PUSH_ROUTES)


def days(seconds: int | None) -> str:
    return "     -" if seconds is None else f"{seconds / DAY_S:6.2f}"


def played_saves(p: DayTwoPlayer) -> list[Save]:
    """The saves the route passed through, ending at its last."""
    saves = [s for s, _ in p.history]
    return saves if saves[-1].time >= p.save.time else [*saves, p.save]


def skill_rows(p: DayTwoPlayer, last: int | None) -> list[str]:
    """One block per skill: its levels' first-reach times, then its phase's top."""
    rules, saves = p.rules, played_saves(p)
    save_at, end = at_time(saves, lambda s, t: advance(s, rules, t)), saves[-1]
    times = [s.time for s in saves]
    out: list[str] = []
    for sk in rules.skills:
        at = counted_at(rules, save_at, sk.id)
        reached, top = at(end.time), phase_top_level(rules, end, sk.id)
        levels = list(range(2, reached + 1))
        out.append(f"  {sk.id}: level {reached} of {top} ({phase_progress(rules, end, sk.id):.2f}% of the phase)")
        out.extend(f"    L{r.level:<3d}{days(r.at)} d  gap {days(r.gap)} d"
                   for r in reaches(times, at, levels[-last:] if last else levels))
        (hit,) = reaches(times, at, [top])
        out.append(f"    top L{top}: " + (f"{days(hit.at).strip()} d" if hit.at is not None else "not by the edge"))
    return out


def sampled(p: DayTwoPlayer, step_h: int) -> list[tuple[int, Save]]:
    """The route's save every `step_h` game hours from instant 0 to its end, each played on once for every reading."""
    rules, saves = p.rules, played_saves(p)
    save_at = at_time(saves, lambda s, t: advance(s, rules, t))
    return [(t, save_at(t)) for t in range(0, saves[-1].time, step_h * HOUR_S)]


def share_rows(p: DayTwoPlayer, at: list[tuple[int, Save]]) -> list[str]:
    """Each card's mean share by day, then the cards that held a share and have held none since some day."""
    rules, end = p.rules, played_saves(p)[-1].time
    samples = [(t, card_shares(rules, s)) for t, s in at]
    found = day_averages(samples, -(-end // DAY_S))
    head = "    day:" + "".join(f"{i + 1:4d}" for i in range(len(found)))
    rows = [f"    {c[:22]:22s}" + "".join(f"{_cell(day.get(c, 0.0)):>4s}" for day in found)
            for c in sorted({c for day in found for c in day})]
    quiet = gone_quiet(found)
    return [head, *rows, "  quiet since: " + (", ".join(f"{c} day {d}" for c, d in sorted(quiet.items())) or "none")]


def source_rows(p: DayTwoPlayer, at: list[tuple[int, Save]]) -> list[str]:
    """Per skill and band of game days, the sources of its XP in percent, those under 1% pooled as other."""
    found = band_shares([(t, xp_by_source(p.rules, s)) for t, s in at])
    out: list[str] = []
    for sk in p.rules.skills:
        for band in BANDS:
            got = found.get(str(sk.id), {}).get(band)
            if got:
                big = sorted(((c, v) for c, v in got.items() if v >= 1), key=lambda cv: (-cv[1], cv[0]))
                rest = sum(v for v in got.values() if v < 1)
                cells = [f"{c} {v:.0f}" for c, v in big] + ([f"other {rest:.0f}"] if rest >= 0.5 else [])
                out.append(f"    {str(sk.id)[:14]:14s} d{band_label(band):5s} " + ", ".join(cells))
    return out


def dominance_rows(p: DayTwoPlayer, at: list[tuple[int, Save]]) -> list[str]:
    """Whether one saved mix shape wins at every instant two or more shapes are saved, and the wins of each shape."""
    found = dominance([(t, mix_scores(p.rules, s)) for t, s in at])
    return dominance_text(found, len(at))


def dominance_text(found: Dominance, sampled_n: int) -> list[str]:
    wins = found.wins
    out = [f"    {sampled_n} instants sampled: {len(found.winners)} compared, {found.single} with fewer than two shapes "
           f"saved, {found.left_out} left out (a tie or no XP)"]
    for i, shape in enumerate(found.shapes):
        out.append(f"    shape {i + 1}, wins {wins.get(i, 0)}: " + ", ".join(f"{c} {bp / 100:.0f}" for c, bp in shape))
    verdict = ("no instant has two shapes to compare" if not found.winners else
               f"yes, shape {next(iter(wins)) + 1} wins every compared instant" if found.always else
               "no, " + ", ".join(f"shape {i + 1} wins {n}" for i, n in sorted(wins.items())))
    return [*out, f"  one shape always wins: {verdict}"]


def _cell(percent: float) -> str:
    return "." if percent == 0 else "~" if percent < 0.5 else f"{percent:.0f}"


def route_text(name: str, p: DayTwoPlayer) -> str:
    """A route's readout: every skill's ladder and every card's share by day, sampled every STEP_H game hours."""
    at = sampled(p, STEP_H)
    return "\n".join([f"== {name}: the edge at game day {p.save.time / DAY_S:.2f}", *skill_rows(p, None),
                      "  card share of the running mixes by day, percent (. none, ~ under 0.5)",
                      *share_rows(p, at),
                      "  XP by source per band of game days, percent of the skill's XP",
                      *source_rows(p, at),
                      "  saved mix shapes, scored alone as the running mix by levels gained per game hour",
                      *dominance_rows(p, at)]) + "\n"


def readouts() -> dict[str, str]:
    return {f"ladder-{name}": route_text(name, twelve(name)) for name in TWELVE_PUSH_ROUTES}


def route_report(name: str, last: int | None, skills: bool, shares: bool, step_h: int) -> None:
    t0 = time.process_time()
    p = twelve(name)
    print(f"\n== {name}: the edge at game day {p.save.time / DAY_S:.2f} (played in {time.process_time() - t0:.0f} CPU s)")
    if skills:
        print("\n".join(skill_rows(p, last)))
    if shares:
        at = sampled(p, step_h)
        print("\n  card share of the running mixes by day, percent (. none, ~ under 0.5)")
        print("\n".join(share_rows(p, at)))
        print("\n  XP by source per band of game days, percent of the skill's XP")
        print("\n".join(source_rows(p, at)))
        print("\n  saved mix shapes, scored alone as the running mix by levels gained per game hour")
        print("\n".join(dominance_rows(p, at)))
    print(f"  (read in {time.process_time() - t0:.0f} CPU s)")


def main(argv: list[str]) -> int:
    def option(flag: str) -> int | None:
        return int(argv[argv.index(flag) + 1]) if flag in argv else None

    values = {str(option(f)) for f in ("--last", "--step") if f in argv}
    names = [a for a in argv if not a.startswith("--") and a not in values] or list(TWELVE_PUSH_ROUTES)
    only_skills, only_shares = "--skills" in argv, "--shares" in argv
    for name in names:
        route_report(name, option("--last"), only_skills or not only_shares, only_shares or not only_skills,
                     option("--step") or STEP_H)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
