// What arrived while away is revealed in turn (game/arrivals.ts, ui/reveal.ts): kind order unless times are known, the
// first at once and the rest 400–700 ms apart within a 4 s cap, a tap or key showing the rest, everything at once under
// reduced motion, and nothing held back outside a return.
import { ArrivalQueue, CAP_MS, MAX_GAP_MS, MIN_GAP_MS } from "../src/game/arrivals";

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

/** Every reveal time of a started queue, by stepping a fake clock in 10 ms steps. */
function times<T>(q: ArrivalQueue<T>, from: number, until = from + 10_000): Array<[number, T[]]> {
  const out: Array<[number, T[]]> = [];
  for (let t = from; t <= until && !q.idle; t += 10) for (const group of q.due(t)) out.push([t - from, group]);
  return out;
}

// Order: kinds in their fixed order, sends of one kind in the order they were sent; known times first, by time.
{
  const q = new ArrivalQueue<string>();
  q.push("card", "c1", null, "card c1");
  q.push("store", "wood", null, "line wood");
  q.push("chip", "cold", null, "chip cold");
  q.push("card", "c2", null, "card c2");
  q.push("feature", "ledger", null, "feature ledger");
  q.push("skill", "s", 50, "skill s at 50");
  q.push("card", "c3", 20, "card c3 at 20");
  q.start(0, false);
  expect("order", times(q, 0).map(([, g]) => g[0]), ["card c3 at 20", "skill s at 50", "feature ledger", "chip cold", "line wood", "card c1", "card c2"]);
}

// The same kind and id sent twice arrive as one (a ledger line and its rule offer).
{
  const q = new ArrivalQueue<string>();
  q.push("store", "wood", null, "line");
  q.push("card", "c1", null, "card");
  q.push("store", "wood", null, "offer");
  q.start(0, false);
  expect("joined", times(q, 0).map(([, g]) => g), [["line", "offer"], ["card"]]);
}

// Pace: the first at once; gaps within 400–700 ms; never past the cap; past it, the rest arrive together.
for (const n of [2, 3, 6, 7, 11, 20]) {
  const q = new ArrivalQueue<number>();
  for (let i = 0; i < n; i += 1) q.push("card", `c${i}`, null, i);
  q.start(1000, false);
  const at = times(q, 1000).map(([t]) => t);
  expect(`n=${n}: all shown once`, at.length, n);
  expect(`n=${n}: the first at once`, at[0], 0);
  const last = at[at.length - 1] ?? -1;
  if (last > CAP_MS) throw new Error(`n=${n}: the last at ${last} ms, past the cap`);
  const gaps = at.slice(1).map((t, i) => t - (at[i] ?? 0)).filter((g) => g > 0);
  for (const g of gaps) if (g < MIN_GAP_MS - 10 || g > MAX_GAP_MS + 10) throw new Error(`n=${n}: a gap of ${g} ms`);
  if (n === 20) expect("n=20: the rest together at the cap", at.filter((t) => t === CAP_MS).length > 1, true);
  if (n === 3) expect("n=3: unhurried", gaps, [MAX_GAP_MS, MAX_GAP_MS]);
}

// Skip (a tap or key): everything still waiting at once, in order; then nothing is left.
{
  const q = new ArrivalQueue<string>();
  for (const id of ["a", "b", "c", "d"]) q.push("card", id, null, id);
  q.start(0, false);
  expect("first at once", q.due(0), [["a"]]);
  expect("skip shows the rest", q.skip(), [["b"], ["c"], ["d"]]);
  expect("then idle", q.idle, true);
  expect("nothing after", q.due(1e9), []);
}

// Reduced motion: no stagger, everything due at once.
{
  const q = new ArrivalQueue<string>();
  for (const id of ["a", "b", "c"]) q.push("card", id, null, id);
  q.start(0, true);
  expect("reduced: all at once", q.due(0), [["a"], ["b"], ["c"]]);
}

// Out of sight (below the fold): due at once and takes no turn; what is in sight keeps the pace, from the first.
{
  const q = new ArrivalQueue<string>();
  for (const id of ["a", "low1", "b", "low2", "c"]) q.push("card", id, null, id);
  q.start(0, false, (p) => !p[0]?.startsWith("low"));
  expect("unseen at once, then the first in sight", q.due(0), [["low1"], ["low2"], ["a"]]);
  expect("the rest at the in-sight pace", times(q, 0).map(([t, g]) => [t, g[0]]), [[MAX_GAP_MS, "b"], [2 * MAX_GAP_MS, "c"]]);
}

// A held arrival that is not a line (a ledger line, read before the cards): its kind keeps the pace, and the next kind
// waits out its reading time; a join keeps the longer hold (an offer sent before its line); out of sight it holds nothing.
{
  const q = new ArrivalQueue<string>();
  q.push("line", "l", null, "line", 3000);
  q.push("store", "wood", null, "offer");
  q.push("store", "wood", null, "wood", 3000);
  q.push("store", "stone", null, "stone", 3000);
  q.push("card", "c1", null, "c1");
  q.push("card", "c2", null, "c2");
  q.start(0, false);
  expect("the cards after the ledger is read", times(q, 0).map(([t, g]) => [t, g.at(-1)]),
    [[0, "line"], [3000, "wood"], [3000 + MAX_GAP_MS, "stone"], [6000 + MAX_GAP_MS, "c1"], [6000 + 2 * MAX_GAP_MS, "c2"]]);
  const low = new ArrivalQueue<string>();
  low.push("store", "wood", null, "low", 3000);
  low.push("card", "c1", null, "c1");
  low.start(0, false, (p) => p[0] !== "low");
  expect("out of sight: no hold", [low.due(0), low.quiet(1)], [[["low"], ["c1"]], true]);
  const joined = new ArrivalQueue<string>();
  joined.push("store", "wood", null, "offer");
  joined.push("store", "wood", null, "wood", 3000);
  joined.push("card", "c1", null, "c1");
  joined.start(0, false);
  expect("a join keeps the longer hold", times(joined, 0).map(([t]) => t), [0, 3000]);
}

// Nothing sent: idle from the start, nothing due.
{
  const q = new ArrivalQueue<string>();
  expect("empty is idle", q.idle, true);
  q.start(0, false);
  expect("empty: nothing due", q.due(1e9), []);
}

// The reveal on the page (ui/reveal.ts), against a stand-in DOM: what each node shows, and the input listeners.
{
  const listeners = new Map<string, () => void>();
  let reduced = false;
  const g = globalThis as Record<string, unknown>;
  const before = { window: g["window"], document: g["document"] };   // put back after: the test files share one process
  Object.assign(globalThis, {
    window: { matchMedia: () => ({ matches: reduced }), innerWidth: 400, innerHeight: 800 },
    document: {
      addEventListener: (t: string, f: () => void) => void listeners.set(t, f),
      removeEventListener: (t: string, f: () => void) => { if (listeners.get(t) === f) listeners.delete(t); },
    },
  });
  const { Reveal } = await import("../src/ui/reveal");
  const node = (top = 100) => {
    const cls = new Set<string>();
    return {
      offsetWidth: 0, getBoundingClientRect: () => ({ top, bottom: top + 50, left: 10, right: 300 }),
      classList: { add: (c: string) => void cls.add(c), remove: (c: string) => void cls.delete(c), has: (c: string) => cls.has(c) },
      addEventListener: () => undefined, removeEventListener: () => undefined,
    };
  };
  type Fake = ReturnType<typeof node>;
  const asEl = (n: Fake) => n as unknown as HTMLElement;   // a fake DOM double -- it has only what this test reads
  const state = (ns: Fake[]) => ns.map((n) => (n.classList.has("held") ? "held" : n.classList.has("arrive") ? "shown" : "none"));

  const r = new Reveal();
  const plain = node();
  r.arrive(asEl(plain), "card", "x");
  expect("not away: shown at once", state([plain]), ["shown"]);
  expect("not away: no listeners", listeners.size, 0);

  const ns = [node(), node(), node()];
  r.collect();
  ns.forEach((n, i) => r.arrive(asEl(n), "card", `c${i}`));
  expect("collected: all held", state(ns), ["held", "held", "held"]);
  r.start(0);
  expect("started: the first shows", state(ns), ["shown", "held", "held"]);
  expect("listening for a tap's click (never its press, which a shown line would move) and a key", [...listeners.keys()].sort(), ["click", "keydown"]);
  r.tick(MAX_GAP_MS);
  expect("its turn: the second shows", state(ns), ["shown", "shown", "held"]);
  listeners.get("click")?.();
  expect("a tap shows the rest", state(ns), ["shown", "shown", "shown"]);
  expect("listeners gone", listeners.size, 0);

  const more = [node(), node()];
  r.collect();
  more.forEach((n, i) => r.arrive(asEl(n), "chip", `k${i}`));
  r.start(0);
  r.tick(CAP_MS);
  expect("in time, all shown and done", [state(more), listeners.size], [["shown", "shown"], 0]);

  const fold = [node(100), node(900), node(300)];   // the second is below the fold
  r.collect();
  fold.forEach((n, i) => r.arrive(asEl(n), "card", `f${i}`));
  r.start(0);
  expect("below the fold: shown at once, beside the first in sight", state(fold), ["shown", "shown", "held"]);
  r.tick(MAX_GAP_MS);
  expect("then the next in sight", [state(fold), listeners.size], [["shown", "shown", "shown"], 0]);

  reduced = true;
  const still = [node(), node(), node()];
  r.collect();
  still.forEach((n, i) => r.arrive(asEl(n), "skill", `s${i}`));
  r.start(0);
  expect("reduced motion: everything at once", [state(still), listeners.size], [["shown", "shown", "shown"], 0]);
  reduced = false;
  const read = [node(), node()];   // a ledger line held for its reading, then a card
  r.collect();
  r.arrive(asEl(read[0]!), "store", "wood", 3000);
  r.arrive(asEl(read[1]!), "card", "after");
  r.start(0);
  r.tick(MAX_GAP_MS);
  expect("the card waits out the line's reading", state(read), ["shown", "held"]);
  r.tick(3000);
  expect("then it shows", state(read), ["shown", "shown"]);
  Object.assign(globalThis, before);
}
