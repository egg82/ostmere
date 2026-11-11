"""The pacing simulator's report and readouts for a played route through days four to six
(docs/design/days-four-to-seven-plan.md, item 1; combat-plan.md, item 9): the hours B5 to G2 land, each chapter's visits
with spend and decide per visit and per absence, the fights each runner fought and lost, the beats beside their target
days, each calendar day's arrivals, night 7 against the season's turn, and what the stores lose to their caps away from
each chapter's end. The readouts (NAMES: one per route the days are read on, one per chapter's visits) are committed
under tests/readouts/ and compared by test_weekone_readouts.py and test_weekone_routes.py; nothing in them is a
threshold. Minutes, hours and ids only (CLAUDE.md, "Never spoil the owner").

    python -m tests.weekone.report typical            # from app/: the named routes through days four to six
    python -m tests.weekone.report typical --lines    # also each text key of the four chapter files with its states
"""
import sys
import time
from collections import Counter

from ashfall_app.engine import view
from ashfall_app.opening.schema import DAY_TWO
from tests.daythree import content as c3
from tests.daythree import counters, lines
from tests.daythree.report import absence_line
from tests.daytwo import abs_band
from tests.daytwo import checks as checks2
from tests.daytwo.player import DayTwoPlayer
from tests.dayone import capcheck, daily
from tests.weekone import verdicts
from tests.weekone.routes import week1

FILES = {"day_four.toml": "B5", "day_five.toml": "B6", "b7.toml": "B6", "day_six.toml": "B7"}
"""Each chapter file and the beat its keys are read from."""
BEATS = ("B5", "B6", "B7", "A27", "G1", "N7", "G2")
DAY_ROUTES = ("typical", "sharp", "whenever")
"""The routes whose calendar days the readout lists."""
NAMES = (*(f"weekone-{name}" for name in DAY_ROUTES), *(f"weekone-{chapter}" for chapter in verdicts.CHAPTERS))


def route_text(name: str, p: DayTwoPlayer, days: list[Counter[str]]) -> str:
    """A route's readout: when the beats land beside their target days, and each calendar day's arrivals by kind."""
    pace = abs_band.load_pace()
    out = [abs_band.summary(name, abs_band.reached(p.landed_at, p.history[0][0].time, pace), pace),
           f"days with no arrival but lines: {daily.empty_days(days)}", *daily.lines_of(days)]
    return "\n".join(out) + "\n"


def chapter_text(chapter: str, found: list[counters.Counts], marked: dict[str, str]) -> str:
    """A chapter's visits on the typical route: spend and decide per visit and per absence, the edge of written
    content and returns during a long wait marked."""
    out = [f"chapter {chapter}: {len(found)} visits on typical"]
    out += [f"  {c.label:>4} gap {c.gap / 3600:5.1f} h  {counters.line(c)}" + (f"  [{marked[c.label]}]" if c.label in marked else "")
            for c in found]
    return "\n".join([*out, absence_line(found)]) + "\n"


def readouts() -> dict[str, str]:
    texts = {f"weekone-{name}": route_text(name, week1(name), verdicts.calendar_days(week1(name))) for name in DAY_ROUTES}
    p = week1("typical")
    marked = checks2.marks(p, first=1)
    for chapter in verdicts.CHAPTERS:
        texts[f"weekone-{chapter}"] = chapter_text(chapter, verdicts.counts_of(p, chapter, verdicts.typical_decided(chapter)),
                                                   marked)
    return texts


def fought(p: DayTwoPlayer) -> str:
    return ", ".join(f"{f.runner} fought {f.fought} lost {f.lost}" for f in view(p.save, p.rules).fights)


def route_report(name: str, p: DayTwoPlayer) -> None:
    print(f"\n{name}: hours " + ", ".join(f"{b} {verdicts.hour(p, b)}" for b in BEATS) + f" | season's turn {verdicts.season_turn_h():g} h")
    print(f"  fights: {fought(p)}")
    print(route_text(name, p, verdicts.calendar_days(p)), end="")
    print(f"  night 7: {verdicts.night_seven(p) or 'before the turn'}")
    camp = c3.opening3().camp
    marked = checks2.marks(p, first=1)
    for chapter, found in verdicts.chapter_counts(p).items():
        print(chapter_text(chapter, found, marked), end="")
        failing = capcheck.failing(verdicts.exit_save(p, verdicts.CHAPTERS[chapter]), p.rules, (camp.store,) if camp else ())
        print(f"    cap_loss at the end: {'FAIL ' + '; '.join(capcheck.problems(failing)) if failing else 'ok'}")


def line_states(plays: dict[str, DayTwoPlayer]) -> list[str]:
    out = list[str]()
    for file, beat in FILES.items():
        first = {n: verdicts.span(p, verdicts.CHAPTERS["four" if beat == "B5" else "five" if beat == "B6" else "six"])[0]
                 for n, p in plays.items()}
        out += [f"\n== {file}", *lines.report(plays, lines.chapter_keys(DAY_TWO.parent / file), c3.opening3(), first,
                                              {n: p.landed_at[beat] for n, p in plays.items()})]
    return out


def main(argv: list[str]) -> int:
    plays = {name: week1(name) for name in argv if not name.startswith("--")}
    for name, p in plays.items():
        t0 = time.process_time()
        route_report(name, p)
        print(f"  ({time.process_time() - t0:.1f} CPU s)")
    if "--lines" in argv:
        print("\n".join(line_states(plays)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
