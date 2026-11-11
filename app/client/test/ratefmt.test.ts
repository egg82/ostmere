// A rate shows the fewest digits that still tell it apart (game/format.ts, perMinute): whole when it is whole, trailing
// zeros never, and a rate that is not zero never reads as zero; a flat line carries no sign.
import { fixtureContent, R } from "../fixtures/content";
import { Format } from "../src/game/format";
import { Text } from "../src/game/text";

const format = new Format(new Text(fixtureContent), fixtureContent.scales);
const perHour = (items: number): string => format.perMinute(items * R);

// items per hour -> shown per minute
const cases: Array<[number, string]> = [
  [120, "+2/min"], [90, "+1.5/min"], [15, "+0.25/min"], [80, "+1.33/min"], [7200, "+120/min"], [-80, "-1.33/min"], [-4, "-0.06/min"],
  [0, "0/min"],
  [0.5, "+0.008/min"], [-0.5, "-0.008/min"], [0.06, "+0.001/min"],
];
for (const [items, want] of cases) {
  const got = perHour(items);
  if (got !== want) throw new Error(`${items}/h: got "${got}", want "${want}"`);
}
