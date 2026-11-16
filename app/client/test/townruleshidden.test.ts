// The town's rules show only once the town has a second mix to switch to (CONTRACT.txt, "The town's mix"): with one
// town mix a town rule has nothing to do, so the Rules tab draws no town section and no New rule for it, and the town's
// always rule, which stays in the engine, is drawn nowhere. The hands' rules are as they were. The view is the engine's
// own town over the day-two page (one town mix, town:main); the control adds a second.
import { fakeDocument, type FakeEl, install } from "./fake-dom";
import { testContext } from "./context";
import { townStep } from "../fixtures/town";
import type { View } from "../src/api/types";
import type { RuleSide } from "../src/game/ruleside";
import { RulesTab } from "../src/ui/rules";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

function rules(view: View, side: RuleSide = "camp"): FakeEl {   // the town is drawn on Camp, the hands' rules on Mine
  const { ctx } = testContext();
  ctx.keeps.keepRuleSeen();   // writing rules is open, as it is by day three
  const tab = new RulesTab(ctx, { get: () => side, set: () => undefined });
  document.body.replaceChildren(tab.root);
  tab.update(view);
  return fakeDocument.body.firstElementChild as FakeEl;
}

const one = townStep("town").view;
const town = one.mixes.find((m) => m.id === "town:main")!;
const two: View = { ...one, mixes: [...one.mixes, { ...town, id: "Camp 2" }] };
const handsRows = (root: FakeEl): number => root.querySelectorAll(".rules-list .rule-handle").length;

const control = rules(two);
expect("control, two town mixes: the town's section", control.querySelectorAll(".rules-town").length, 1);
const root = rules(one);
expect("the hands' rules are as they were", handsRows(rules(one, "mine")), handsRows(rules(two, "mine")));
expect("one town mix: no town section", root.querySelectorAll(".rules-town").length, 0);
expect("and no New rule for the town", root.querySelectorAll(".town-new").length, 0);
