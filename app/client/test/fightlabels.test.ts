// Which fights of a window read as lost is the page's draw over the engine's exact count (CONTRACT.txt, "FIGHTS";
// engine DESIGN.txt, "FIGHTS"): the same on every call, and exactly the served lost count. The checker runs on the real
// labeller and on two planted ones, which it must reject: a draw that rolls fresh each call, and one that ignores the count.
import { entries, labels, oddsOf, poolLine, windows, type Window } from "../src/game/fights";
import { fightsStep } from "../fixtures/fights";

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

type Labeller = (save: number, w: Window) => boolean[];

/** Every window of the grid: two calls agree, the window has `fought` entries, and exactly `lost` of them read lost. */
function holds(label: Labeller): string | null {
  let seen = 0;
  for (const save of [1, 7]) for (const runner of ["hunt", "raiders"]) for (const start of [0, 3, 40]) {
    for (let fought = 1; fought <= 12; fought++) for (let lost = 0; lost <= fought; lost++) {
      const w = { runner, start, fought, lost, lostBefore: 0 };
      const a = label(save, w);
      seen += 1;
      if (JSON.stringify(a) !== JSON.stringify(label(save, w))) return `save ${save} ${runner} ${start} ${fought}/${lost}: a second call differs`;
      if (a.length !== fought || a.filter(Boolean).length !== lost) return `${runner} ${fought}/${lost}: ${a.filter(Boolean).length} of ${a.length} read lost`;
    }
  }
  return seen > 1000 ? null : "the grid was too small to mean anything";
}

expect("the real labels hold the count and repeat", holds(labels), null);
const planted: Array<[string, Labeller]> = [
  ["a fresh roll each call", (_s, w) => Array.from({ length: w.fought }, () => Math.random() < w.lost / w.fought)],
  ["the lost count ignored", (s, w) => labels(s, { ...w, lost: Math.min(w.fought, 1) })],
];
for (const [name, bad] of planted) if (holds(bad) === null) throw new Error(`the check passed a planted labeller (${name})`);

// The draw is keyed by save, runner and start: a window elsewhere is arranged differently somewhere in the grid.
const w: Window = { runner: "hunt", start: 0, fought: 8, lost: 3, lostBefore: 0 };
const arrangements = new Set([labels(1, w), labels(2, w), labels(1, { ...w, runner: "raiders" }), labels(1, { ...w, start: 8 })].map((l) => l.join()));
if (arrangements.size < 3) throw new Error(`the key does not move the draw: ${arrangements.size} arrangements`);

// The odds: the smallest exact pair up to 20, else a percentage, one decimal under 10%.
expect("2000 is 1 in 5", oddsOf(2000, 10_000), { kind: "pair", lost: 1, of: 5 });
expect("4000 is 2 in 5", oddsOf(4000, 10_000), { kind: "pair", lost: 2, of: 5 });
expect("10000 is 1 in 1", oddsOf(10_000, 10_000), { kind: "pair", lost: 1, of: 1 });
expect("750 is a percentage", oddsOf(750, 10_000), { kind: "pct", pct: "7.5" });
expect("3333 is a whole percentage", oddsOf(3333, 10_000), { kind: "pct", pct: "33" });

// The windows between two views, and the arrival queue's entries from them.
const words = { won: (r: string) => `won ${r}`, lost: (r: string) => `lost ${r}`, since: (x: Window) => `since ${x.fought}/${x.lost}` };
const view = fightsStep("fight", 10).view;
const later = { ...view, fights: view.fights.map((f) => ({ ...f, fought: f.fought + 3, lost: f.lost + 1 })) };
expect("the first view has no window", windows(null, view), []);
expect("nothing new, no entries", entries(1, view, view, words), []);
const three = entries(1, view, later, words);
expect("each runner's three fights are three entries", three.length, 6);
expect("exactly one of each runner's reads lost", [three.filter((t) => t === "lost hunt").length, three.filter((t) => t === "lost raiders").length], [1, 1]);
expect("the same window reads the same", entries(1, view, later, words), three);
const many = { ...view, fights: view.fights.map((f) => ({ ...f, fought: f.fought + 40, lost: f.lost + 5 })) };
expect("past three, one summary each with the exact counts", entries(1, view, many, words), ["since 40/5", "since 40/5"]);
expect("a lost count past the window's fights is held to them", windows(view, { ...view, fights: view.fights.map((f) => ({ ...f, fought: f.fought + 1, lost: f.lost + 3 })) }).map((x) => x.lost), [1, 1]);

// A pool reads each line once before any repeats, keyed by save, runner and kind; the same k reads the same line.
const pool = ["a", "b", "c", "d"];
for (const save of [1, 9]) for (let round = 0; round < 3; round++) {
  const drawn = [0, 1, 2, 3].map((i) => poolLine(save, "hunt", "won", pool, round * 4 + i));
  expect(`save ${save} round ${round} spends the pool`, [...drawn].sort(), pool);
}
expect("the same k reads the same line", poolLine(3, "hunt", "lost", pool, 6), poolLine(3, "hunt", "lost", pool, 6));
const orders = new Set([1, 2, 3, 4, 5, 6].map((save) => [0, 1, 2, 3].map((k) => poolLine(save, "hunt", "won", pool, k)).join("")));
if (orders.size < 3) throw new Error(`the save does not move the pool's order: ${orders.size} orders`);
expect("a one-line pool is that line", poolLine(1, "hunt", "won", ["only"], 5), "only");

// Each entry's k counts the runner's wins and losses since it first ran: fought - lost before the window, then on.
const counted: Array<[string, number]> = [];
const counting = { won: (_r: string, k: number) => { counted.push(["won", k]); return ""; },
  lost: (_r: string, k: number) => { counted.push(["lost", k]); return ""; }, since: () => "" };
const before = { ...view, fights: view.fights.slice(0, 1).map((f) => ({ ...f, fought: 10, lost: 4 })) };
entries(1, before, { ...before, fights: before.fights.map((f) => ({ ...f, fought: 13, lost: 5 })) }, counting);
expect("wins count on from 6, the loss from 4", [counted.filter(([k]) => k === "won").map(([, n]) => n), counted.filter(([k]) => k === "lost").map(([, n]) => n)], [[6, 7], [4]]);
