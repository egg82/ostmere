// The page's return rules against the cases shared with the simulator (fixtures/arrival_cases.json; the Python side is
// tests/dayone/test_dayone_absence.py): where each line of a return goes, and when a batch's reveal is over.
import { readFileSync } from "node:fs";
import { dayOneStep } from "../fixtures/dayone";
import { fixtureContent } from "../fixtures/content";
import type { LogLine, View } from "../src/api/types";
import { ArrivalQueue } from "../src/game/arrivals";
import { awayLines } from "../src/game/awaylines";
import { Catalog } from "../src/game/catalog";

interface CardCase { card: string; cap: number | null }
interface AwayCase {
  name: string; chips: Array<{ chip: string; on: string | null; off: string | null }>; shown: string[];
  cards: CardCase[]; cards_before: CardCase[]; lines: Array<[string, string | null]>; expect: string[];
}
/** `rest`: every arrival that is not a line; of those, `ledger_ms` are ledger lines (their holds) and `behind` come after them. */
interface ScheduleCase { name: string; holds_ms: number[]; rest: number; ledger_ms?: number[]; behind?: number; end_ms: number }
const cases = JSON.parse(readFileSync("fixtures/arrival_cases.json", "utf8")) as { away_lines: AwayCase[]; schedule: ScheduleCase[] };

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const base = dayOneStep("landed", 4000).view;
const cardView = (c: CardCase): View["cards"][number] => ({ ...base.cards[0]!, card: c.card, cap: c.cap });

for (const c of cases.away_lines) {
  const catalog = new Catalog({
    ...fixtureContent,
    chip_infos: c.chips.map((ch) => ({ ...fixtureContent.chip_infos[0]!, chip: ch.chip, on_line_key: ch.on, off_line_key: ch.off })),
  });
  const lines: LogLine[] = c.lines.map(([key, card], i) => ({ at: 3000 + i, seq: 0, key, card }));
  const view: View = { ...base, chips: c.shown, cards: c.cards.map(cardView) };
  const prev: View = { ...base, cards: c.cards_before.map(cardView) };
  expect(c.name, awayLines(catalog, lines, view, prev), c.expect);
}

/** When the last arrival of a started batch is over: its due time, plus the reading time if it is a line. */
function endOf(c: ScheduleCase): number {
  const q = new ArrivalQueue<number>();
  c.holds_ms.forEach((hold, i) => q.push("line", `l${i}`, null, i, hold));
  const ledger = c.ledger_ms ?? [];
  const behind = c.behind ?? 0;
  for (let i = 0; i < c.rest - ledger.length - behind; i++) q.push("chip", `k${i}`, null, i);
  ledger.forEach((hold, i) => q.push("store", `s${i}`, null, i, hold));
  for (let i = 0; i < behind; i++) q.push("card", `c${i}`, null, i);
  q.start(0, false);
  let last = 0;
  for (let t = 0; t <= 12_000 && !q.idle; t++) if (q.due(t).length > 0) last = t;
  return c.rest > 0 ? last : last + (c.holds_ms.at(-1) ?? 0);
}

for (const c of cases.schedule) {
  const got = endOf(c);
  if (Math.abs(got - c.end_ms) > 1) throw new Error(`${c.name}: got ${got}, want ${c.end_ms}`);
}
