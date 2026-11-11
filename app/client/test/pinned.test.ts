// Bringing a part into view under the pinned strip (ui/dom.ts, revealBelow): after the browser's nearest scroll, a top
// left under the pinned part's bottom is scrolled clear by exactly that much, in whichever scroller moves (the phone's
// game, the desktop's panel); a top already clear moves nothing.
import { revealBelow } from "../src/ui/dom";

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

/** A scroller whose content moves with its scrollTop, holding a node laid out at `at` and a pinned part ending at `pin`. */
function world(at: number, pin: number, scrolled: number) {
  const scroller = { scrollTop: scrolled };
  const still = { scrollTop: 0 };   // the other layout's scroller: it scrolls nothing here
  const node = { getBoundingClientRect: () => ({ top: at - scroller.scrollTop, bottom: at - scroller.scrollTop + 40 }), scrollIntoView: () => undefined };
  const pinned = { getBoundingClientRect: () => ({ top: 0, bottom: pin }) };
  return { scroller, still, node, pinned };
}

{
  const w = world(579, 490, 579);   // scrolled to the foot: the tabs sit at the top of the viewport, under the strip
  revealBelow(w.node, w.pinned, [w.scroller, w.still]);
  expect("scrolled up by what the strip covered", w.scroller.scrollTop, 89);
  expect("the node's top is at the strip's bottom", w.node.getBoundingClientRect().top, 490);
}

{
  const w = world(579, 490, 0);   // not scrolled: already clear
  revealBelow(w.node, w.pinned, [w.still, w.scroller]);
  expect("a clear node moves nothing", [w.scroller.scrollTop, w.still.scrollTop], [0, 0]);
}
