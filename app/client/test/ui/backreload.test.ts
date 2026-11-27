// A page reloaded with a sheet open (the self-update, or the player) finds the history entries its last run pushed, and
// no layer for them: they are walked off at load, so back is the player's, not a stale entry that does nothing.
import { install } from "../fake-dom";

install();
history.pushState({ ostmere: 1 }, "");
history.pushState({ ostmere: 2 }, "");

const { openSheet, walkOffStale } = await import("../../src/ui/back");

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}
const depth = (): number => (history.state as { ostmere?: number } | null)?.ostmere ?? 0;
const settle = async (): Promise<void> => { for (let i = 0; i < 4; i++) await new Promise((done) => setTimeout(done, 0)); };

walkOffStale();
await settle();
expect("the entries of the run before are given back at load", depth(), 0);

const sheet = document.createElement("dialog");
openSheet(sheet);
expect("a sheet opened now holds one entry", [sheet.open, depth()], [true, 1]);
history.back();
await settle();
expect("back closes it", [sheet.open, depth()], [false, 0]);
