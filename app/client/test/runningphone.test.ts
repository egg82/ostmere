// On a phone the running-now row is part of the pinned strip, whose measured height (ui/headseat.ts, a ResizeObserver
// on the stage) is the room the cards scroll in: a row that only hides (visibility) keeps its height and the cards keep
// less room. While the splits match the row must leave layout there; a desktop keeps it (nothing under a finger moves).
// Layout cannot be drawn by fake-dom, so this reads the rules; the measured result is in the branch's renders.
import { readFileSync } from "node:fs";

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const css = readFileSync("src/game.css", "utf8");
const phoneAt = css.indexOf("/* The phone frame");
const phone = css.slice(phoneAt, css.indexOf("/* desktop (and a phone in landscape)"));
expect("the phone block was found", phone.length > 100, true);
expect("a matched row leaves the phone's layout", /\.running-now\.matched \{ display: none; \}/.test(phone), true);
expect("the row still keeps its room elsewhere", /\n\.running-now\.matched \{ visibility: hidden; \}/.test(css), true);
