// The Rules tab has no town section, with one town mix or two (contract/the-towns-mix.txt, "The town's mix"): the town's always rule,
// which stays in the engine, is drawn nowhere, and the hands' rules are as they were. The view is the engine's own town
// over the day-two page (one town mix, town:main); the second adds another under a new name.
import { fakeDocument, type FakeEl, install } from "./fake-dom";
import { testContext } from "./context";
import { townStep } from "../fixtures/town";
import type { View } from "../src/api/types";
import type { RuleSide } from "../src/game/rules/ruleside";
import { RulesTab } from "../src/ui/rules/rules";

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

const townRule = (v: View): string => String(v.orders.findIndex((o) => o.then.kind === "switch_mix" && o.then.mix_id === "town:main"));
const drawn = (root: FakeEl): string[] => root.querySelectorAll("[data-rule]").map((n) => n.dataset.rule ?? "");
expect("the hands' rules are as they were", handsRows(rules(one, "mine")), handsRows(rules(two, "mine")));
expect("the hands' rules are drawn", handsRows(rules(one, "mine")) > 0, true);
for (const [label, view] of [["one town mix", one], ["two town mixes", two]] as const) {
  expect(`${label}: the town's always rule is in the save`, Number(townRule(view)) >= 0, true);
  expect(`${label}: no town section`, rules(view).querySelectorAll(".rules-town").length, 0);
  expect(`${label}: the town's always rule is drawn nowhere`, [...drawn(rules(view)), ...drawn(rules(view, "mine"))].includes(townRule(view)), false);
}
