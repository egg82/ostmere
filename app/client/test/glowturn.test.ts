// The glow offered while the reveal is busy waits its turn there (ui/fresh.ts); a control out of sight takes no turn
// (ui/reveal.ts), so its turn comes at once. Then it must take the glow, not offer again: day one's playthrough hit
// "Maximum call stack size exceeded" in the opening, Glow.offer -> Reveal.effect -> (out of sight, run now) -> offer.
// The fake DOM's nodes have empty rects, so every node here is out of sight.
import { install } from "./fake-dom";
import { Glow } from "../src/ui/fresh";
import { Reveal } from "../src/ui/reveal";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

function check(label: string, block: () => void): void {
  try { block(); } catch (e) { throw new Error(`${label}: ${(e as Error).message}`); }
}

check("an out-of-sight control offered the glow while a line is read takes it", () => {
  const reveal = new Reveal();
  const glow = new Glow(reveal);
  const band = document.createElement("li");
  reveal.line([band], "1", 3000);
  reveal.start(performance.now());
  expect("the reveal is busy (a line is being read)", reveal.busy, true);
  const button = document.createElement("button");
  expect("offered", glow.offer(button), true);
  expect("it has the glow", button.classList.contains("glow"), true);
});

// Control: with nothing waiting the glow goes on at once, and a second control does not take it.
{
  const glow = new Glow(new Reveal());
  const a = document.createElement("button");
  const b = document.createElement("button");
  document.body.replaceChildren(a, b);
  expect("at once", glow.offer(a) && a.classList.contains("glow"), true);
  expect("one at a time", glow.offer(b) || b.classList.contains("glow"), false);
}
