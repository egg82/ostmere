// One thing at a time (docs/design/opening-screen.md): a line's reading time; a live step's lines lead their batch,
// each holding the next turn for its reading time; a batch sent while another waits follows it; which lines go on a
// card (the player's own taps only); and the reveal's line, slot-taking and straggler paths against a stand-in DOM.
import { fixtureStep } from "../fixtures/steps";
import type { Card, LogLine, View } from "../src/api/types";
import { ArrivalQueue, MAX_GAP_MS, MIN_GAP_MS } from "../src/game/arrivals";
import { READING, readingMs } from "../src/game/reading";
import { TapLines } from "../src/game/taplines";

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

function times<T>(q: ArrivalQueue<T>, from: number, until = from + 30_000): Array<[number, T[]]> {
  const out: Array<[number, T[]]> = [];
  for (let t = from; t <= until && !q.idle; t += 10) for (const group of q.due(t)) out.push([t - from, group]);
  return out;
}

// Reading time: words at READING.wpm, never under the floor.
{
  expect("short: the floor", readingMs("a b c"), READING.floorMs);
  expect("empty: the floor", readingMs("   "), READING.floorMs);
  const words = Array.from({ length: 29 }, (_, i) => `w${i}`).join(" ");
  expect("29 words", readingMs(words), Math.round((29 / READING.wpm) * 60_000));
  expect("runs of spaces are one gap", readingMs(words.replaceAll(" ", "  \n ")), readingMs(words));
  if (readingMs(words) <= READING.floorMs) throw new Error("a long line must outlast the floor");
}

// A line leads its batch, whatever was sent first; what came with it waits the line's reading time.
{
  const q = new ArrivalQueue<string>();
  q.push("card", "c1", null, "card");
  q.push("skill", "s", 20, "skill at 20");   // a known time does not put it before the line
  q.push("chip", "cold", null, "chip");
  q.push("line", "1", null, "line", 3000);
  q.start(0, false);
  expect("line first, then the rest after its hold", times(q, 0),
    [[0, ["line"]], [3000, ["skill at 20"]], [3000 + MAX_GAP_MS, ["chip"]], [3000 + 2 * MAX_GAP_MS, ["card"]]]);
}

// Two lines: each holds the next for its own reading time; the band and the card copy of one line show together.
{
  const q = new ArrivalQueue<string>();
  q.push("line", "1", null, "band 1", 3000);
  q.push("line", "1", null, "card 1");
  q.push("line", "2", null, "band 2", 5000);
  q.push("card", "c", null, "card");
  q.start(100, false);
  expect("two lines", times(q, 100), [[0, ["band 1", "card 1"]], [3000, ["band 2"]], [8000, ["card"]]]);
}

// Reduced motion: the lines still lead (a wait is not motion); the rest then come together.
{
  const q = new ArrivalQueue<string>();
  q.push("card", "a", null, "a");
  q.push("card", "b", null, "b");
  q.push("line", "1", null, "line", 3000);
  q.start(0, true);
  expect("reduced", times(q, 0), [[0, ["line"]], [3000, ["a"]], [3000, ["b"]]]);
}

// A batch sent while another is still waiting follows it: its line waits for the one before to be read.
{
  const q = new ArrivalQueue<string>();
  q.push("line", "1", null, "first line", 4000);
  q.push("card", "c", null, "first card");
  q.start(0, false);
  expect("first line at once", q.due(0), [["first line"]]);
  q.push("line", "2", null, "second line", 3000);
  q.start(1000, false);
  expect("then the first card, then the second line", times(q, 1000).map(([t, g]) => [t + 1000, g]),
    [[4000, ["first card"]], [4000 + MIN_GAP_MS, ["second line"]]]);
}

// A tap or key shows everything still waiting, a batch not yet started included.
{
  const q = new ArrivalQueue<string>();
  q.push("line", "1", null, "line", 3000);
  q.push("card", "c", null, "card");
  q.start(0, false);
  q.due(0);
  q.push("store", "wood", null, "late");
  expect("skip", q.skip(), [["card"], ["late"]]);
  expect("idle after", q.idle, true);
}

// Which lines go on a card: written by a card the player tapped, until that tap ends. Not the mix's, a rule's, or a
// chip's; not a later line of a card whose tap has ended.
{
  const at = 50;
  const base = fixtureStep("mid", at).view;
  const c0 = base.cards[0];
  if (!c0) throw new Error("fixture has no card");
  const withBy = (by: Card["by"]): View => ({ ...base, cards: base.cards.map((c) => (c.card === c0.card ? { ...c, by } : c)) });
  const line = (card: string | null): LogLine => ({ at, seq: 0, key: "k", card });
  const taps = new TapLines();
  expect("not tapped: band only", taps.cardOf(line(c0.card)), null);
  taps.tap(c0.card);
  expect("tapped: on its card", taps.cardOf(line(c0.card)), c0.card);
  expect("a chip's line: band only", taps.cardOf(line(null)), null);
  expect("another card's: band only", taps.cardOf(line("someone-else")), null);
  taps.observe(withBy("tap"), withBy(null), null);
  expect("while it runs: still the player's", taps.cardOf(line(c0.card)), c0.card);
  taps.observe(withBy(null), withBy("tap"), null);
  expect("the tap ended: a later line (the mix's) is band only", taps.cardOf(line(c0.card)), null);
  taps.tap(c0.card);
  taps.observe(withBy(null), withBy(null), c0.card);
  expect("a failed tap ends it at once", taps.cardOf(line(c0.card)), null);
}

// The reveal on the page (ui/reveal.ts), against a stand-in DOM: a line, its card copy, a card taking its slot at its
// turn, and a straggler drawn while a line is still being read.
{
  const listeners = new Map<string, () => void>();
  const g = globalThis as Record<string, unknown>;
  const before = { window: g["window"], document: g["document"], performance: g["performance"] };
  let now = 0;
  Object.assign(globalThis, {
    window: { matchMedia: () => ({ matches: false }), innerWidth: 400, innerHeight: 800 },
    document: {
      addEventListener: (t: string, f: () => void) => void listeners.set(t, f),
      removeEventListener: (t: string, f: () => void) => { if (listeners.get(t) === f) listeners.delete(t); },
    },
    performance: { now: () => now },
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
  const band = node(), onCard = node();
  const card = { ...node(), getBoundingClientRect: () => ({ top: 0, bottom: 0, left: 0, right: 0 }) };   // not in the page yet
  let slot = "old card";
  const old = { isConnected: true, getBoundingClientRect: () => ({ top: 100, bottom: 150, left: 10, right: 300 }),
    replaceWith: () => { slot = "new card"; old.isConnected = false; } };
  r.collect();
  r.line([asEl(band), asEl(onCard)], "1", 3000);
  r.arrive(asEl(card), "card", "c", old as unknown as HTMLElement);   // sight is the slot's: it waits its turn -- a fake DOM double stands in for the real type
  expect("collected: all held", state([band, onCard, card]), ["held", "held", "held"]);
  r.start(0);
  expect("the line shows, band and card", state([band, onCard, card]), ["shown", "shown", "held"]);
  expect("the old card keeps the slot", slot, "old card");
  now = 2000;
  const straggler = node();
  r.arrive(asEl(straggler), "skill", "s");
  expect("a straggler waits while the line is read", state([straggler]), ["held"]);
  r.tick(2999);
  expect("not before the reading time", state([card]), ["held"]);
  r.tick(3000);
  expect("its turn: the card takes the slot", [state([card]), slot], [["shown"], "new card"]);
  r.tick(3000 + MIN_GAP_MS);
  expect("then the straggler", [state([straggler]), listeners.size], [["shown"], 0]);

  const b2 = node(), c2 = node();
  r.collect();
  r.line([asEl(b2)], "2", 3000);
  r.arrive(asEl(c2), "card", "d");
  r.start(10_000);
  listeners.get("click")?.();
  expect("a tap shows the card at once", [state([b2, c2]), listeners.size], [["shown", "shown"], 0]);

  const plain = node();
  r.arrive(asEl(plain), "card", "x");
  expect("nothing waiting: shown at once", state([plain]), ["shown"]);

  // An effect (a ring, a burst, the glow) runs at once when nothing waits, else at its turn after the line.
  const ran: string[] = [];
  r.effect(asEl(node()), "skill", () => ran.push("idle"));
  expect("effect, idle: at once", [ran, r.busy], [["idle"], false]);
  const b3 = node();
  now = 20_000;
  r.collect();
  r.line([asEl(b3)], "3", 3000);
  r.effect(asEl(node()), "skill", () => ran.push("burst"));
  r.start(now);
  expect("effect with a line: waits", [ran, r.busy], [["idle"], true]);
  r.tick(now + 3000);
  now += 3000;
  expect("effect: its turn after the line", [ran, r.busy], [["idle", "burst"], false]);

  // A line shown with nothing behind it still holds what comes next (a later step's effect) for its reading time.
  r.collect();
  r.line([asEl(node())], "4", 3000);
  r.start(now);
  now += 1000;
  r.effect(asEl(node()), "card", () => ran.push("glow"));
  expect("while the line is read: waits", ran.length, 2);
  r.tick(now + 1999);
  expect("not before its reading time", ran.length, 2);
  r.tick(now + 2000);
  expect("then", ran, ["idle", "burst", "glow"]);

  // The glow waits its turn too: offered while a line is read, it comes on after.
  const { Glow } = await import("../src/ui/fresh");
  const glow = new Glow(r);
  const target = { ...node(), addEventListener: () => undefined };
  now += 5000;
  r.collect();
  r.line([asEl(node())], "5", 3000);
  r.start(now);
  expect("offered while a line is read", glow.offer(target as unknown as HTMLElement), true);   // a fake DOM double -- it has only what this test reads
  expect("not on yet", target.classList.has("glow"), false);
  now += 3000;
  r.tick(now);
  expect("on at its turn", target.classList.has("glow"), true);
  Object.assign(globalThis, before);
}
