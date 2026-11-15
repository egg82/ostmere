// A reordered rule slides to its new place (ui/ruleslide.ts): the rows that change place start at their old tops and are
// released onto the .slide transition (--settle-ms, --settle-ease in game.css); a reduced-motion move only lands.
import { fakeDocument, FakeEl, FakeEvent, install } from "./fake-dom";
import { fixtureContent } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { Decision, View } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { Keeps } from "../src/game/keeps";
import { HandStreak } from "../src/game/stall";
import { Glow } from "../src/ui/fresh";
import type { PartContext } from "../src/ui/part";
import { RulesTab } from "../src/ui/rules";
import { shiftOf } from "../src/ui/ruleslide";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

expect("one rule moved down two: it lands last, the two between shift up", [...shiftOf([0, 1, 2], 0, 2)], [[0, 1], [1, 2], [2, 0]]);
expect("one rule moved up one", [...shiftOf([0, 1, 2], 2, 1)], [[1, 2], [2, 1]]);
expect("a group with a gap in its indexes keeps the gap's rule out", [...shiftOf([0, 1, 3], 0, 1)], [[0, 1], [1, 0]]);
expect("in place moves nothing", [...shiftOf([0, 1, 2], 1, 1)], []);

const catalog = new Catalog(fixtureContent);
const base = fixtureStep("rulestab", 100).view;   // three hands rules, then a bench task rule

// Rows are laid out 40px apart by their rule index, as a list draws them.
const proto = FakeEl.prototype as unknown as { getBoundingClientRect(this: FakeEl): unknown };
const real = proto.getBoundingClientRect;
proto.getBoundingClientRect = function (this: FakeEl) {
  const top = this.classList.contains("rules-row") ? Number(this.dataset.rule) * 40 : 0;
  return { left: 0, top, width: 300, height: 40, right: 300, bottom: top + 40 };
};

// What each row's offset was when the list was last forced to lay out (the moment the slide is released).
let laidOut: string[] = [];
const root0 = Object.getOwnPropertyDescriptor(FakeEl.prototype, "offsetHeight")!;
Object.defineProperty(FakeEl.prototype, "offsetHeight", { get(this: FakeEl) {
  laidOut = this.querySelectorAll(".rules-list > .rules-row").filter((n) => n.dataset.rule !== undefined).map((n) => n.style["transform"] ?? "");
  return root0.get!.call(this);
} });

function run(reduced: boolean): FakeEl[] {
  laidOut = [];
  (globalThis as unknown as { window: { matchMedia: () => unknown } }).window.matchMedia = () => ({ matches: reduced, addEventListener: () => {} });
  const decided: Decision[] = [];
  const ctx = {
    catalog,
    actions: { decide: (d: Decision) => decided.push(d), dryRun: () => Promise.resolve(null), editMix: () => undefined, newMix: () => undefined, openSelector: () => undefined, openRules: () => undefined, orderSent: () => undefined, highlight: () => undefined },
    fires: { fresh: [], running: new Set() }, glow: new Glow(), streak: new HandStreak(),
    arrivals: { arrive: () => undefined }, endBehind: () => true, keeps: new Keeps(), repeats: () => ({ taps: [], switches: [] }), ruleRuns: () => [], lesson: () => null,
  } as unknown as PartContext;
  const tab = new RulesTab(ctx);
  const root = tab.root as unknown as FakeEl;
  fakeDocument.body.replaceChildren(root);
  tab.update(base);
  root.querySelectorAll(".rule-handle")[0]!.dispatchEvent(new FakeEvent("keydown", { key: "ArrowDown" }));
  const sent = decided[0];
  if (sent?.kind !== "set_orders") throw new Error("the move sent no set_orders");
  tab.update({ ...base, orders: sent.orders } as View);
  return root.querySelectorAll(".rules-list > .rules-row").filter((n) => n.dataset.rule !== undefined);
}

const rows = run(false);
expect("the rules that swapped start at their old tops, the rest stay", laidOut, ["translateY(40px)", "translateY(-40px)", ""]);
expect("and are released onto the slide transition", rows.map((n) => n.classList.contains("slide")), [true, true, false]);

const still = run(true);
expect("under reduced motion the move lands: no offset set, no slide", [laidOut, still.map((n) => n.classList.contains("slide"))], [[], [false, false, false]]);

proto.getBoundingClientRect = real;
