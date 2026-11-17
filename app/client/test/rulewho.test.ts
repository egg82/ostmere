// A new rule is offered for a person only while their lane holds a task a rule can do (ui/rulewho.ts, ui/personpage.ts;
// docs/decisions/principles.md, "Every option offered works as worded"): on Camp a rule does a person's tasks and no mix,
// and a one-off or a card at its cap is no task a rule can do, so a person with only those would open an empty Do row.
import { fakeDocument, type FakeEl, install } from "./fake-dom";
import { testContext } from "./context";
import { pageRig } from "./personrig";
import { townStep } from "../fixtures/town";
import type { View } from "../src/api/types";
import type { RuleSide } from "../src/game/ruleside";
import { RulesTab } from "../src/ui/rules";
import { whoChoices } from "../src/ui/rulewho";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const town = townStep("town").view;
const { ctx } = testContext();
const lanes = (v: View): string[] => whoChoices(ctx, v).flatMap((w) => (w.lane === undefined ? [] : [w.lane]));
// The mason's every card made a one-off (cap 1): nothing of theirs can be done again.
const oneOffs: View = { ...town, cards: town.cards.map((c) => (ctx.catalog.laneOf(c.card) === "mason" ? { ...c, cap: 1, completions: 0 } : c)) };
const newRule = (page: ReturnType<typeof pageRig>["page"]): boolean => page.querySelectorAll(".person-rules button").some((b) => (b.textContent ?? "").includes("New rule"));

expect("both people are offered while each has a task", lanes(town), ["helper", "mason"]);
expect("a person with no task a rule can do is not offered", lanes(oneOffs), ["helper"]);

{  // their page offers no New rule either; the helper's still does
  const rig = pageRig(oneOffs);
  const order = Array.from(rig.root.querySelectorAll(".person-change")).map((b) => b.closest("[data-lane]")?.dataset.lane ?? "");
  const mason = order.indexOf("mason"), helper = order.indexOf("helper");
  expect("both people have a Change", mason >= 0 && helper >= 0, true);
  expect("no New rule on the mason's page", newRule(rig.open(mason)), false);
  expect("a New rule on the helper's page", newRule(rig.open(helper)), true);
}

{  // with no person holding such a task and the town with no second mix, Camp has nothing to make a rule for
  const none: View = { ...town, cards: town.cards.map((c) => (ctx.catalog.ruled(c.card) ? { ...c, cap: 1, completions: 0 } : c)) };
  const camp = (v: View): FakeEl => {
    const { ctx: tabCtx } = testContext();
    tabCtx.keeps.keepRuleSeen();
    let side: RuleSide = "camp";
    const tab = new RulesTab(tabCtx, { get: () => side, set: (s) => { side = s; } });
    document.body.replaceChildren(tab.root);
    tab.update(v);
    return fakeDocument.body.firstElementChild as FakeEl;
  };
  expect("Camp offers a New rule while someone has a task", camp(town).querySelectorAll(".rules-new").length, 1);
  expect("no one to rule: no New rule on Camp", camp(none).querySelectorAll(".rules-new").length, 0);
}
