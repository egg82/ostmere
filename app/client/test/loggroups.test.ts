// Which stretch a line belongs to (game/loggroups.ts) and how a stretch is worded (game/logwords.ts).
import { fixtureContent } from "../fixtures/content";
import { Catalog } from "../src/game/catalog";
import { stretches, tally, type LogEntry } from "../src/game/loggroups";
import { awayTitle } from "../src/game/logwords";

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const l = (at: number, kind: LogEntry["kind"] = "story"): LogEntry => ({ text: String(at), at, kind });
const lines = [l(10), l(20, "tap"), l(30), l(40, "find"), l(50)];
const shape = (v: Array<{ left: number; back: number }>): Array<[number | null, number[]]> =>
  stretches(lines, v).map((s) => [s.visit?.left ?? null, s.lines.map((x) => x.at)]);

expect("no visit: one stretch", shape([]), [[null, [10, 20, 30, 40, 50]]]);
expect("a line at the second the player left is before the visit", shape([{ left: 20, back: 35 }]), [[null, [10, 20]], [20, [30, 40, 50]]]);
expect("visits split in order, whatever order they are kept in", shape([{ left: 40, back: 45 }, { left: 10, back: 15 }]),
  [[null, [10]], [10, [20, 30, 40]], [40, [50]]]);
expect("a visit past the last line opens nothing", shape([{ left: 90, back: 99 }]), [[null, [10, 20, 30, 40, 50]]]);
expect("a Log with no lines has no stretch", stretches([], [{ left: 1, back: 2 }]), []);
expect("the tally counts kinds, the story first", tally([...lines].reverse()), [["story", 3], ["tap", 1], ["find", 1]]);

const { text } = new Catalog(fixtureContent);
expect("minutes", awayTitle(text, 54 * 60 + 20), "Away 54m");
expect("an hour and some", awayTitle(text, 5 * 3600 + 3 * 60), "Away 5h 3m");
expect("whole hours", awayTitle(text, 5 * 3600), "Away 5h");
expect("a day or more is days", awayTitle(text, 50 * 3600), "Away 2d");
