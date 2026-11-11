// A phone's rule editor gets the art's height (src/game.css), and the pinned stage hands the panel its exact height
// (src/ui/headseat.ts). Both are layout, which fake-dom cannot draw (no ResizeObserver, no media match), so this reads
// the rule and the call; the measured result is in the branch's before/after renders.
import { readFileSync } from "node:fs";

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const css = readFileSync("src/game.css", "utf8");
const phone = css.slice(css.indexOf("/* phone editor:"), css.indexOf("/* desktop (and a phone in landscape)"));
expect("the phone block was found", phone.length > 100, true);
expect("the art leaves while a rule is built", /\.game:has\(\.rules \.cond\) \.scene-box \{ display: none; \}/.test(phone), true);

// offsetHeight rounds, so a panel laid on it left a fractional seam under the stage: the height must be the exact one.
const seat = readFileSync("src/ui/headseat.ts", "utf8");
expect("--scene-vh is set from the exact height", seat.includes("getBoundingClientRect().height"), true);
expect("and never from the rounded one", /\.offsetHeight/.test(seat), false);
