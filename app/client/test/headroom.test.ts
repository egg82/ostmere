// On a desktop the head sits above the art (src/ui/headseat.ts) and its room comes out of the skills and ledger under
// the art, not the art: the root learns the head's measured height and the panel's floor gives it up (src/game.css).
// Both are layout, which fake-dom cannot draw, so this reads the rule and the call; the measured result is in the
// branch's before/after renders.
import { readFileSync } from "node:fs";

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const css = readFileSync("src/game.css", "utf8");
const low = [...css.matchAll(/^ {2}\.low \{([^}]*)\}/gm)].map((m) => m[1] ?? "");
expect("the panel under the art has rules", low.length > 0, true);
expect("its floor gives up the head's height", low.some((r) => /min-height: [^;]*- var\(--head-h/.test(r)), true);
const seat = readFileSync("src/ui/headseat.ts", "utf8");
expect("the root learns the head's height", /"--head-h"/.test(seat) && /watch\.observe\(head\)/.test(seat), true);
