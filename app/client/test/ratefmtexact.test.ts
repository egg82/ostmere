// A rate per minute is cut toward zero exactly (game/format.ts, perMinute): every whole item/h from 1 to 6000 shows the
// hundredths of its exact quotient, not the hundredth a floating-point product lands under. Reference: integer cents,
// floor(items * 100 / 60), shown by the same number format.
import { fixtureContent, R } from "../fixtures/content";
import { Format } from "../src/game/format";
import { Text } from "../src/game/text";

const format = new Format(new Text(fixtureContent), fixtureContent.scales);
const shown = new Intl.NumberFormat(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 7, signDisplay: "exceptZero" });

let exact = 0;
const wrong: string[] = [];
for (let items = 1; items <= 6000; items++) {
  const cents = Math.floor((items * 100) / 60);
  if ((items * 100) % 60 === 0) exact++;
  const want = `${shown.format(cents / 100)}/min`;
  const got = format.perMinute(items * R);
  if (got !== want) wrong.push(`${items}/h: got "${got}", want "${want}"`);
}
if (exact !== 2000) throw new Error(`the reference saw ${exact} exact rates, expected 2000`);
if (wrong.length > 0) throw new Error(`${wrong.length} rates wrong, first: ${wrong.slice(0, 3).join("; ")}`);
