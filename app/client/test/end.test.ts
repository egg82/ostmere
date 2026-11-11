// The end keys on view.ended_at (CONTRACT.txt, "The end"): live, the end lines, and what waits on the end only once
// they have been read; reopened, an end the page had shown is replayed only if it was under thirty game seconds ago,
// and an end that happened while the page was shut plays like a live one.
import { Catalog } from "../src/game/catalog";
import { fixtureContent } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { View } from "../src/api/types";
import { TheEnd } from "../src/ui/end";

let timers: (() => void)[] = [];
Object.assign(globalThis, {
  window: { setTimeout: (f: () => void) => { timers.push(f); return timers.length; }, clearTimeout: () => undefined },
  fetch: () => Promise.resolve(new Response("")),
});

function check(ok: boolean, what: string): void {
  if (!ok) throw new Error(what);
}

const END = 600;
const ended = (at: number): View => ({ ...fixtureStep("covered", at).view, ended_at: END });
const before = (at: number): View => ({ ...fixtureStep("mid", at).view, ended_at: null });

/** A fresh page (as after a reload or a new game): its first view, then the next. What it said, and when the end
 * was behind. */
function run(first: View, next: View) {
  timers = [];
  const said: string[] = [];
  let reads = 0;
  const end = new TheEnd(new Catalog(fixtureContent), (keys) => said.push(...keys), () => { reads += 1; });
  end.update(first, true);
  const behindFirst = end.behind;
  end.update(next, false);
  const behindAtOnce = end.behind;
  const waiting = timers.length;
  for (const f of timers) f();
  return { said, behindFirst, behindAtOnce, waiting, behindAfter: end.behind, reads };
}

const endKeys = fixtureContent.end_line_keys;

{  // live: the end lines, and the end behind only after their read time, with a redraw then
  const r = run(before(END - 12), ended(END));
  check(r.said.join() === endKeys.join(), `live: the end lines go to the log: ${r.said.join()}`);
  check(!r.behindAtOnce && r.waiting > 0 && r.behindAfter && r.reads === 1, "live: what waits on the end waits for the lines to be read");
}

{  // reloaded 12 s after an end it had shown: the lines again, on the same delay
  const r = run(ended(END + 5), ended(END + 12));
  check(r.said.join() === endKeys.join(), `a reload just after the end replays its lines: ${r.said.join()}`);
  check(!r.behindFirst && !r.behindAtOnce && r.behindAfter, "a reload just after the end waits for its lines again");
}

{  // reloaded long after: dusk only (the scene's business), no lines, behind at once
  const r = run(ended(END + 200), ended(END + 300));
  check(r.said.length === 0 && r.waiting === 0 && r.behindAtOnce, "an end long ago replays no lines and is behind at once");
}

{  // it ended while the page was shut, an hour ago: never shown, so it plays like a live end
  const r = run(before(END - 100), ended(END + 3600));
  check(r.said.join() === endKeys.join() && !r.behindAtOnce && r.behindAfter, "an end that happened while away plays in full");
}

{  // before the end nothing is said and nothing is behind
  const r = run(before(END - 100), before(END - 50));
  check(r.said.length === 0 && r.waiting === 0 && !r.behindAfter, "no end, no lines");
}
