"""The per-tester sheet's mechanical rows for one save, from what the app records (docs/tester-protocol.md).

    python tools/tester_sheet.py --sql 15          # the one read-only query: save, its decision log, what the page keeps
    psql -d ashfall -Atc "$(python tools/tester_sheet.py --sql 15)" | python tools/tester_sheet.py -

A row with no recorded source prints NOT_RECORDED, never 0 or empty. Sources: `saves` (start and last write), `save_decisions`
(kind, game time, wall time, the context each was made under; kept 30 days), `saves.presentation` (lessons ended, mix dots
touched) over `accounts.presentation` (offers answered; the lesson keys an account kept before lessons were per save are
left out). The leave beacon and the Umami events carry no save id, so neither feeds a row; the lesson.end log line
repeats what `saves.presentation` holds.
"""
import json
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Any

NOT_RECORDED = "— not recorded (observer notes)"
IDLE_S = 60

QUERY = """select json_build_object(
  'save', (select row_to_json(t) from (select s.id, s.started_at, s.updated_at, s.decisions, s.game_time, s.ended_at from saves s where s.id = {id}) t),
  'decisions', coalesce((select json_agg(row_to_json(d) order by d.n) from (
      select n, at, wall, kind, jsonb_array_length(verb->'orders') as orders, context->>'mix' as mix, context->'chips' as chips
      from save_decisions where save_id = {id}) d), '[]'::json),
  'presentation', (select (a.presentation - 'rule_seen' - 'mix_offered' - 'lessons' - 'lesson_ends') || s.presentation
      from accounts a join saves s on s.account_id = a.id where s.id = {id}))"""


@dataclass(frozen=True)
class Logged:
    n: int
    at: int
    wall: datetime
    kind: str
    orders: int | None   # set_orders only: how many orders it left standing
    mix: str | None   # the mix the hands ran; None when none ran or the row predates contexts
    chips: tuple[str, ...] | None   # None for a row that predates contexts


def _logged(d: dict[str, Any]) -> Logged:
    chips = d.get("chips")
    return Logged(n=d["n"], at=d["at"], wall=datetime.fromisoformat(d["wall"]), kind=d["kind"], orders=d.get("orders"),
                  mix=d.get("mix"), chips=None if chips is None else tuple(chips))


def _span(seconds: float) -> str:
    s = round(seconds)
    if s >= 3600:
        return f"{s // 3600}h{s % 3600 // 60:02d}m"
    return f"{s // 60}m{s % 60:02d}s" if s >= 60 else f"{s}s"


def _since(start: datetime, d: Logged) -> str:
    return f"{_span((d.wall - start).total_seconds())} after the game began (decision {d.n}, game time {d.at})"


def _first_row(label: str, start: datetime, save: dict[str, Any], log: list[Logged], kind: str, orders: bool = False) -> str:
    """The first decision of `kind`. Only the oldest decisions are ever deleted, so a log that starts at 1 still holds the
    first of everything; one that does not may be missing it."""
    found = next((d for d in log if d.kind == kind and (not orders or (d.orders or 0) > 0)), None)
    from_the_start = bool(log) and log[0].n == 1
    if found is not None and from_the_start:
        return f"{label}: {_since(start, found)}"
    if found is None and len(log) == save["decisions"]:
        return f"{label}: none yet"
    return f"{label}: {NOT_RECORDED}"


def _idle_row(log: list[Logged]) -> str:
    for before, after in zip(log, log[1:]):
        gap = (after.wall - before.wall).total_seconds()
        if gap > IDLE_S:
            screen = ("the mix running %s, chips shown %s" % (before.mix or "none", ", ".join(before.chips) or "none")
                      if before.chips is not None else "context not kept for this row")
            return (f"first idle gap over {IDLE_S}s: {_span(gap)}, after decision {before.n} (game time {before.at}); "
                    f"on screen (PROXY: the context of that last decision, not a screen capture): {screen}")
    return f"first idle gap over {IDLE_S}s: none between recorded decisions"


def _offers_row(presentation: dict[str, Any]) -> str:
    answered = {k: len(presentation[k]) for k in ("mix_offered", "switch_offered", "mix_stopped") if k in presentation}
    shown = f"offers shown, and taken against declined: {NOT_RECORDED}"
    if not answered:
        return f"offers answered: {NOT_RECORDED}\n{shown}"
    counts = ", ".join(f"{k} {n}" for k, n in answered.items())
    return f"offers answered (the account's, all saves; taken and declined not told apart): {counts}\n{shown}"


def _lessons_rows(presentation: dict[str, Any]) -> list[str]:
    if "lesson_ends" not in presentation:
        return [f"lessons ended: {NOT_RECORDED}"]
    ends = {e["lesson"]: e for e in presentation["lesson_ends"]}
    rows = [f"lesson {e['lesson']}: {'skipped' if e['skipped'] else 'done'} at step {e['step']}, longest wait {e['longest_wait_s']}s"
            for e in ends.values()]
    rows += [f"lesson {name}: ended, step and wait {NOT_RECORDED}" for name in presentation.get("lessons", []) if name not in ends]
    return rows or ["lessons ended: none yet"]


def _last_row(save: dict[str, Any], log: list[Logged]) -> str:
    if not log:
        return f"last action before leaving: {NOT_RECORDED}"
    last = log[-1]
    return (f"last recorded action: {last.kind} (decision {last.n}, game time {last.at}), save last written {save['updated_at']}; "
            f"the leave itself is {NOT_RECORDED}")


def sheet(doc: dict[str, Any]) -> str:
    """The sheet's mechanical rows for the document the query returns."""
    save = doc["save"]
    presentation: dict[str, Any] = doc["presentation"] or dict[str, Any]()
    log = [_logged(d) for d in doc["decisions"]]
    start = datetime.fromisoformat(save["started_at"])
    held = f"decisions on the save {save['decisions']}, in the log {len(log)}" + ("" if len(log) == save["decisions"] else " (older ones deleted)")
    rows = [f"save {save['id']}: {held}",
            _first_row("time to first tap", start, save, log, "tap_card"),
            _first_row("first built mix (by the player or an accepted offer, not told apart)", start, save, log, "save_mix"),
            _first_row("first built rule", start, save, log, "set_orders", orders=True),
            _idle_row(log), _offers_row(presentation), *_lessons_rows(presentation), _last_row(save, log)]
    return "\n".join(rows)


def main(argv: list[str]) -> None:
    if len(argv) == 3 and argv[1] == "--sql" and argv[2].isdecimal():
        print(QUERY.format(id=int(argv[2])))
    elif len(argv) == 2:
        print(sheet(json.load(sys.stdin if argv[1] == "-" else open(argv[1], encoding="utf-8"))))
    else:
        sys.exit("usage: tester_sheet.py --sql <save id> | tester_sheet.py <document.json | ->")


if __name__ == "__main__":
    main(sys.argv)
