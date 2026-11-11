// The fire's stretch asks one thing at a time (docs/design/opening-screen.md, "One thing at a time" and "Lessons"):
// two red lines with guided rule offers show one Show me, never twins; the other waits until the first is answered
// (its lesson ended, or the offer gone), and a ledger line that arrives holds the cards behind it until it is read.
import { install } from "./fake-dom";
import { testContext } from "./context";
import { fixtureStep } from "../fixtures/steps";
import type { LedgerLine, View } from "../src/api/types";
import { FIRST_MIX, FIRST_RULE } from "../src/game/lessons";
import { READING } from "../src/game/reading";
import { Ledger } from "../src/ui/ledger";
import { Lessons } from "../src/ui/lessons";
import { keepsOf, NEW_FLAT, type Flat } from "./kept";

install();
Object.assign(window, { innerWidth: 400, innerHeight: 800 });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const RECT = { left: 10, top: 10, width: 80, height: 30, right: 90, bottom: 40 };
const KEPT: Flat = { ...NEW_FLAT, lessons: [FIRST_MIX] };
const mid = fixtureStep("mid", 100).view;

/** A falling line nothing covers: red, so its store's order card is offered under it. */
function falling(store: string, value: number): LedgerLine {
  return {
    store, segment: { start: 100, start_value: value, rate: -120_000, limit: 0 }, net_per_hour: -120_000,
    contributions: [{ runner: "tend", per_hour: -120_000 }], empties_at: null, fills_at: null, falling: true, covered: false, starved: false, cap: 40_000,
  };
}
const others = mid.ledger.filter((l) => l.store !== "wood" && l.store !== "stone");
/** The fire's shape: two red lines, each with a rule offer the rule's lesson guides (wood, then stone). */
const twoRed: View = { ...mid, orders: [], orders_on: [], ledger: [falling("wood", 14_000), falling("stone", 1_000), ...others] };

function rig() {
  document.body.replaceChildren();
  const { ctx } = testContext();
  const keeps = keepsOf(KEPT);
  let view = twoRed;
  let clock = 0;
  const holder: { ledger: Ledger | null } = { ledger: null };
  const lessons = new Lessons({ catalog: ctx.catalog, glow: ctx.glow, keeps }, document.body, () => holder.ledger?.update(view, view), document, () => clock);
  const ledger = new Ledger({ ...ctx, keeps, lesson: () => lessons.current, lessonSubject: () => lessons.subject });
  holder.ledger = ledger;
  document.body.append(ledger.root);
  const shows = (): HTMLElement[] => Array.from(document.querySelectorAll<HTMLElement>(`[data-teach="rule-offer"]`));
  const draw = (v: View): void => {
    view = v;
    ledger.update(v, null);
    lessons.update(v);
    for (const n of shows()) Object.assign(n, { rect: RECT });   // the fake DOM's "on show"
  };
  const tick = (t: number): void => {
    clock = t;
    lessons.tick();
    for (const n of shows()) Object.assign(n, { rect: RECT });
  };
  const offered = (): string[] => shows().map((n) => n.dataset["watch"] ?? "");
  return { ctx, lessons, ledger, draw, tick, offered };
}

{  // two guided offers: one Show me, and the other waits while the rule's lesson runs on the first
  const r = rig();
  r.draw(twoRed);
  r.tick(0);
  expect("one Show me, never twins", r.offered(), ["wood"]);
  expect("the rule's lesson runs on it", [r.lessons.current, r.lessons.subject?.["watch"]], [FIRST_RULE, "wood"]);
  (r.lessons.root.querySelector(".lesson-skip") as HTMLButtonElement).click();   // answered: its lesson ended
  expect("then no row and no Show me: the lines carry quiet marks, nothing is built", [r.offered(), document.querySelectorAll(".line-order").length, document.querySelectorAll(".new-dot").length], [[], 0, 2]);
}

{  // the first offer gone without a rule (its line turned white): the waiting one is the Show me now, and the lesson moves to it
  const r = rig();
  r.draw(twoRed);
  r.tick(0);
  const white: View = { ...twoRed, ledger: twoRed.ledger.map((l) => (l.store === "wood" ? { ...l, falling: false, net_per_hour: 0, segment: { ...l.segment, rate: 0 } } : l)) };
  r.draw(white);
  r.tick(1);
  expect("the second offer shows as soon as the first is gone", r.offered(), ["stone"]);
  r.tick(2);
  expect("and the lesson starts on it", [r.lessons.current, r.lessons.subject?.["watch"]], [FIRST_RULE, "stone"]);
}

{  // a ledger line that arrives holds the next turn for its reading time, its offer's sentence counted
  const { ctx } = testContext();
  const sent: Array<[string, string, number]> = [];
  const ledger = new Ledger({ ...ctx, keeps: keepsOf(KEPT), arrivals: { ...ctx.arrivals, arrive: (_n, kind, id, _t, holdMs = 0) => { sent.push([kind, id, holdMs]); } } });
  ledger.update({ ...twoRed, ledger: others }, null);
  ledger.update(twoRed, { ...twoRed, ledger: others });
  const wood = sent.filter(([kind, id]) => kind === "store" && id === "wood");
  expect("the wood line arrived", wood.length > 0, true);
  expect("held at least a reading floor", Math.max(...wood.map(([, , ms]) => ms)) >= READING.floorMs, true);
}
console.log("firestagger: ok");
