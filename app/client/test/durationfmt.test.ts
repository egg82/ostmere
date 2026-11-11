// A span of game seconds (game/format.ts, duration): rounded up, so a countdown never reads zero before its moment;
// under DAYS_FROM_H hours in hours, minutes and seconds, from it in days and hours, rounded up to the hour.
import { fixtureContent } from "../fixtures/content";
import { DAYS_FROM_H, Format } from "../src/game/format";
import { Text } from "../src/game/text";

const format = new Format(new Text(fixtureContent), fixtureContent.scales);
const H = 3600;

// seconds -> shown (the fixture's texts put a space before each unit)
const cases: Array<[number, string]> = [
  [0, "0 s"], [0.2, "1 s"], [59, "59 s"], [61, "1 m 1 s"], [H, "1 h"], [H + 60, "1 h 1 m"],
  [DAYS_FROM_H * H - 1, "47 h 59 m"], [DAYS_FROM_H * H, "2 d"], [DAYS_FROM_H * H + 1, "2 d 1 h"],
  [115 * H + 57 * 60, "4 d 20 h"], [132 * H + 9 * 60, "5 d 13 h"], [7 * 24 * H, "7 d"], [-5, "0 s"],
];
for (const [s, want] of cases) {
  const got = format.duration(s);
  if (got !== want) throw new Error(`${s} s: got "${got}", want "${want}"`);
}
