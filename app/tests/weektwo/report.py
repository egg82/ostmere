"""The pacing simulator's report and readouts for a played route through day eight (docs/design/week-two-plan.md, item
1): the hours day eight's beats land, its visits with spend and decide (queuing a stage refused) per visit and per
absence, the fights each runner fought and lost, the chapter's spine beats beside their target days, what each absence
opens, and what the stores lose to their caps away from the chapter's end; the same for days nine, eleven, twelve,
fifteen, sixteen, eighteen, nineteen, twenty-two, twenty-three and twenty-five; and the whole game's pacing readout (pacing.py).
The readouts (NAMES: per chapter, one per route and one for typical's visits) are committed under tests/readouts/ and
compared by test_weektwo_readouts.py; nothing in them is a threshold. Minutes, hours and ids only (CLAUDE.md, "Never
spoil the owner").

    python -m tests.weektwo.report typical sharp      # from app/: the named routes through day eight, seed 0
    python -m tests.weektwo.report typical --seeds 3  # seeds 0, 1 and 2
    python -m tests.weektwo.report typical --lines    # also each text key of day_eight.toml with its states
    python -m tests.weektwo.report typical --nine     # through day nine instead, with its absences' unlocks
    python -m tests.weektwo.report typical --eleven   # through day eleven, the same
    python -m tests.weektwo.report typical --twelve   # through day twelve to night 14, the same
    python -m tests.weektwo.report typical --fifteen  # through day fifteen to B14, the same
    python -m tests.weektwo.report typical --sixteen  # through day sixteen to B15, the same
    python -m tests.weektwo.report typical --eighteen  # through day eighteen to B16, the same
    python -m tests.weektwo.report typical --nineteen  # through day nineteen to T13, the same
    python -m tests.weektwo.report typical --twentytwo  # through day twenty-two to B19, the same
    python -m tests.weektwo.report typical --twentythree  # through day twenty-three to B20, the same
    python -m tests.weektwo.report typical --twentyfive  # through day twenty-five to B21, the same
    python -m tests.weektwo.report typical --twentyseven  # through day twenty-seven to I13, the same
"""
import sys
import time

from collections import Counter

from ashfall_app.engine import StoreId, units
from ashfall_app.engine.rates import store_value
from ashfall_app.opening.schema import DAY_EIGHT
from tests.daythree import content as c3
from tests.daythree import counters, lines
from tests.daythree.report import absence_line
from tests.daythree.chapter import Later
from tests.daytwo import abs_band
from tests.daytwo import checks as checks2
from tests.daytwo.player import DayTwoPlayer
from tests.dayone.absence import daily
from tests.weekone import verdicts as v1
from tests.weekone.report import chapter_text, fought
from tests.weektwo import pacing, verdicts
from tests.weektwo.routes import (
    NINE_PUSH_ROUTES, eighteen, eleven, fifteen, nine, nineteen, sixteen, twelve, twentyfive, twentyseven, twentythree, twentytwo, week2,
)

HOURS = ("G2", "B8", "U1", "U2", "SL15", "SL16", "U3", "B9")
NINE_HOURS = ("B9", "E1", "SL18", "SL17", "E2", "E3", "B10")
ELEVEN_HOURS = ("B10", "O-family", "Z1", "O-guard", "Z2", "SL19", "Z3", "A31", "B11")
TWELVE_HOURS = ("B11", "S1", "SL20", "S2", "B12", "SL21", "S3", "N14", "A32", "S4")
FIFTEEN_HOURS = ("S4", "B13", "SL22", "T1", "SL23", "T3", "T2", "B14")
SIXTEEN_HOURS = ("B14", "O-road", "A36", "T4", "SL24", "SL25", "T5", "T6", "SL26", "A35", "B15")
EIGHTEEN_HOURS = ("B15", "SL27", "T7", "T8", "T9", "arr15", "B16")
NINETEEN_HOURS = ("B16", "T10", "T11", "SL28", "B17", "T12", "A38", "T13")
TWENTYTWO_HOURS = ("T13", "I1", "B18", "SL29", "I2", "I3", "I4", "SL30", "B19")
TWENTYTHREE_HOURS = ("B19", "SL31", "I5", "I6", "O-book", "SL32", "I7", "SL33", "A39", "B20")
TWENTYFIVE_HOURS = ("B20", "I8", "I9", "SL34", "SL35", "I10", "O-widowers", "B21")
TWENTYSEVEN_HOURS = ("B21", "I11", "SL36", "I12", "A40", "I13")
ROUTES = NINE_PUSH_ROUTES
"""The routes each chapter's readout lists."""
PACING = tuple(f"weektwo-pacing-{r}" for r in ROUTES)
"""The whole game's pacing readouts, one per route (pacing.py)."""
NAMES = (*(n for c in verdicts.CHAPTERS for n in (*(f"weektwo-{c}-{r}" for r in ROUTES), f"weektwo-{c}")), *PACING)
BLOOM = StoreId("bloom")


def store_units(p: DayTwoPlayer, chapter: Later, store: StoreId) -> float:
    return store_value(verdicts.exit_save(p, chapter), store) / units(1)


def route_text(chapter: str, name: str, p: DayTwoPlayer, days: list[Counter[str]] | None) -> str:
    """A route's readout for one chapter: its spine beats beside their target days, what each absence between its
    visits opens, each calendar day's arrivals after week one's (`days`, from day nine on), and on typical's day
    twelve what the late store holds at the ends of days eleven and twelve."""
    later = verdicts.CHAPTERS[chapter]
    out = [abs_band.summary(name, verdicts.days(p, later), abs_band.load_pace())]
    out += [f"  away {label}: {len(opened)} {opened}" for label, opened in verdicts.absences(p, later)]
    if days is not None:
        out += [f"days after week one's {verdicts.WEEK_ONE_DAYS} with no arrival but lines: "
                f"{[verdicts.WEEK_ONE_DAYS + d for d in daily.empty_days(days)]}", *daily.lines_of(days)]
    if chapter == "twelve" and name == "typical":
        out.append(f"{BLOOM} at the end of day eleven {store_units(p, verdicts.ELEVEN, BLOOM):.1f}, "
                   f"of day twelve {store_units(p, verdicts.TWELVE, BLOOM):.1f}")
    return "\n".join(out) + "\n"


def readouts() -> dict[str, str]:
    texts: dict[str, str] = {}
    for chapter, play in verdicts.PLAYS.items():
        for name in ROUTES:
            p = play(name)
            texts[f"weektwo-{chapter}-{name}"] = route_text(chapter, name, p,
                                                           None if chapter == "eight" else verdicts.calendar_days(p))
        p = play("typical")
        found = verdicts.counts(p, verdicts.CHAPTERS[chapter], verdicts.typical_decided(chapter))
        texts[f"weektwo-{chapter}"] = chapter_text(chapter, found, checks2.marks(p, first=1),
                                                   v1.cap_lines(p, verdicts.CHAPTERS[chapter]))
    for name in ROUTES:
        p = twentyseven(name)
        texts[f"weektwo-pacing-{name}"] = pacing.text(name, p, verdicts.calendar_days(p))
    return texts


def route_report(name: str, seed: int, p: DayTwoPlayer, chapter: Later = verdicts.EIGHT) -> None:
    hours = {verdicts.EIGHT.start: HOURS, verdicts.NINE.start: NINE_HOURS, verdicts.ELEVEN.start: ELEVEN_HOURS,
             verdicts.FIFTEEN.start: FIFTEEN_HOURS, verdicts.SIXTEEN.start: SIXTEEN_HOURS,
             verdicts.EIGHTEEN.start: EIGHTEEN_HOURS,
             verdicts.NINETEEN.start: NINETEEN_HOURS,
             verdicts.TWENTYTWO.start: TWENTYTWO_HOURS,
             verdicts.TWENTYTHREE.start: TWENTYTHREE_HOURS,
             verdicts.TWENTYFIVE.start: TWENTYFIVE_HOURS,
             verdicts.TWENTYSEVEN.start: TWENTYSEVEN_HOURS}.get(chapter.start, TWELVE_HOURS)
    print(f"\n{name} seed {seed}: hours " + ", ".join(f"{b} {v1.hour(p, b)}" for b in hours))
    print(f"  fights: {fought(p)}")
    print(f"  {abs_band.summary(name, verdicts.days(p, chapter), abs_band.load_pace())}")
    found = verdicts.counts(p, chapter)
    print(f"  {chapter.start} to {chapter.stop}: {len(found)} visits")
    for c in found:
        print(f"    {c.label:>4} gap {c.gap / 3600:5.1f} h  {counters.line(c)}")
    print(absence_line(found))
    print("    unlocks per absence: " + "; ".join(f"{a} {len(u)}" for a, u in verdicts.absences(p, chapter)))
    print("\n".join(v1.cap_lines(p, chapter)))


def line_states(plays: dict[str, DayTwoPlayer]) -> list[str]:
    first = {n: v1.span(p, verdicts.EIGHT)[0] for n, p in plays.items()}
    return [f"\n== {DAY_EIGHT.name}", *lines.report(plays, lines.chapter_keys(DAY_EIGHT), c3.opening3(), first,
                                                    {n: p.landed_at["G2"] for n, p in plays.items()})]


def main(argv: list[str]) -> int:
    seeds = int(argv[argv.index("--seeds") + 1]) if "--seeds" in argv else 1
    names = [a for i, a in enumerate(argv) if not a.startswith("--") and (i == 0 or argv[i - 1] != "--seeds")]
    to_nine, to_eleven, to_twelve, to_fifteen = "--nine" in argv, "--eleven" in argv, "--twelve" in argv, "--fifteen" in argv
    to_sixteen, to_eighteen, to_nineteen = "--sixteen" in argv, "--eighteen" in argv, "--nineteen" in argv
    to_twentytwo, to_twentythree, to_twentyfive = "--twentytwo" in argv, "--twentythree" in argv, "--twentyfive" in argv
    to_twentyseven = "--twentyseven" in argv
    for seed in range(seeds):
        for name in names:
            t0 = time.process_time()
            if to_twentyseven:
                route_report(name, seed, twentyseven(name, seed), verdicts.TWENTYSEVEN)
            elif to_twentyfive:
                route_report(name, seed, twentyfive(name, seed), verdicts.TWENTYFIVE)
            elif to_twentythree:
                route_report(name, seed, twentythree(name, seed), verdicts.TWENTYTHREE)
            elif to_twentytwo:
                route_report(name, seed, twentytwo(name, seed), verdicts.TWENTYTWO)
            elif to_nineteen:
                route_report(name, seed, nineteen(name, seed), verdicts.NINETEEN)
            elif to_eighteen:
                route_report(name, seed, eighteen(name, seed), verdicts.EIGHTEEN)
            elif to_sixteen:
                route_report(name, seed, sixteen(name, seed), verdicts.SIXTEEN)
            elif to_fifteen:
                route_report(name, seed, fifteen(name, seed), verdicts.FIFTEEN)
            elif to_twelve:
                route_report(name, seed, twelve(name, seed), verdicts.TWELVE)
            elif to_eleven:
                route_report(name, seed, eleven(name, seed), verdicts.ELEVEN)
            elif to_nine:
                route_report(name, seed, nine(name, seed), verdicts.NINE)
            else:
                route_report(name, seed, week2(name, seed))
            print(f"  ({time.process_time() - t0:.1f} CPU s)")
    if "--lines" in argv:
        print("\n".join(line_states({n: week2(n) for n in names})))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
