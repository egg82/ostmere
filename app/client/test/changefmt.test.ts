// A modifier's change shows as a signed percent, toward zero, with the fewest digits that tell it apart
// (game/format.ts, change and figures): a change that is not zero never reads as zero, and a text's slots are
// {pct} then {pct_b} in the order served.
import { fixtureContent } from "../fixtures/content";
import { Format } from "../src/game/format";
import { Text } from "../src/game/text";

const format = new Format(new Text(fixtureContent), fixtureContent.scales);

// basis points -> shown
const cases: Array<[number, string]> = [
  [1000, "+10%"], [5000, "+50%"], [10000, "+100%"], [-2000, "-20%"], [-3333, "-33.33%"], [6666, "+66.66%"],
  [150, "+1.5%"], [1, "+0.01%"], [-1, "-0.01%"], [0, "0%"],
];
for (const [bp, want] of cases) {
  const got = format.change(bp);
  if (got !== want) throw new Error(`${bp} bp: got "${got}", want "${want}"`);
}

const two = format.figures([10000, 20000]);
if (two["pct"] !== "+100%" || two["pct_b"] !== "+200%") throw new Error(`two figures: ${JSON.stringify(two)}`);
const none = format.figures([]);
if (Object.keys(none).length !== 0) throw new Error(`no figures: ${JSON.stringify(none)}`);
