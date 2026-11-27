// The Rules page's Mine | Camp switch (docs/decisions/mixes.md, "Mine and Camp"; ui/ruleswitch.ts, game/ruleside.ts):
// a rule is on the side of the lane its action runs on, the switch shows only once a second person has hands and keeps
// its side per device, a new rule offers its side's tasks alone, and a rule the player saves lands on its own side.
// The views are the engine's own town (fixtures/town.ts) over the day-two page.
import { fakeDocument, type FakeEl, install } from "./fake-dom";
import { testContext } from "./context";
import { fixtureStep } from "../fixtures/steps";
import { townStep } from "../fixtures/town";
import type { View } from "../src/api/types";
import type { SideKept } from "../src/app/ruleside";
import { landedSide, ruleSideOf, type RuleSide } from "../src/game/ruleside";
import { people } from "../src/game/town";
import { RulesTab } from "../src/ui/rules/rules";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const both = townStep("town").view;
const alone = fixtureStep("restrule", 0).view;   // the player alone: no person has hands
const memory = (side: RuleSide = "mine"): SideKept & { side: RuleSide } => ({ side, get() { return this.side; }, set(s) { this.side = s; } });

function rules(view: View, kept: SideKept) {
  const { ctx, got } = testContext();
  ctx.keeps.keepRuleSeen();
  const tab = new RulesTab(ctx, kept);
  document.body.replaceChildren(tab.root);
  tab.update(view);
  return { root: fakeDocument.body.firstElementChild as FakeEl, tab, got, ctx };
}
const ids = (nodes: FakeEl[]): string[] => nodes.map((n) => n.dataset.rule ?? "").filter((r) => r !== "");
const pick = (root: FakeEl, side: RuleSide): void => { root.querySelector(`.rules-side-pick[data-side="${side}"]`)?.click(); };

const cat = testContext().ctx.catalog;
const handsRule = both.orders.findIndex((o) => o.then.kind === "switch_mix" && o.then.mix_id !== "town:main" && o.when.kind !== "after_time");
const townRule = both.orders.findIndex((o) => o.then.kind === "switch_mix" && o.then.mix_id === "town:main");
const personRule = both.orders.findIndex((o) => o.then.kind === "tap_card" && cat.ruled(o.then.card));

{  // the side follows the lane the action runs on
  expect("a hands rule and the engine's town rule and a person's task are in the save", [handsRule, townRule, personRule].every((i) => i >= 0), true);
  expect("a hands rule: Mine", ruleSideOf(cat, both, handsRule), "mine");
  expect("a town rule: Camp", ruleSideOf(cat, both, townRule), "camp");
  expect("a person's task: Camp", ruleSideOf(cat, both, personRule), "camp");
}

{  // a save with a hands rule and a town rule puts each under its side
  const mine = rules(both, memory("mine")).root;
  expect("Mine lists the hands rule", ids(mine.querySelectorAll(".rules-list .rules-row")).includes(String(handsRule)), true);
  expect("Mine has no town rule", ids(mine.querySelectorAll(".rules-row")).includes(String(townRule)), false);
  expect("Mine has no person's task", mine.querySelectorAll(".task-rule").length, 0);
  const camp = rules(both, memory("camp")).root;
  expect("Camp has no town rule", ids(camp.querySelectorAll(".rules-row")).includes(String(townRule)), false);
  expect("Camp lists the person's task", camp.querySelectorAll(".task-rule").length > 0, true);
  expect("Camp has no hands rule", ids(camp.querySelectorAll(".rules-row")).includes(String(handsRule)), false);
  expect("Camp has no Otherwise", camp.querySelectorAll(".otherwise").length, 0);
}

{  // one person: no switch, and the page is the one list it was
  const { root } = rules(alone, memory("camp"));
  expect("no switch", root.querySelectorAll(".rules-side").length, 0);
  expect("the hands' rules show whatever side the device kept", root.querySelectorAll(".rules-list .rule-handle").length > 0, true);
}

{  // the switch shows with a second person, and its choice is kept for the next page
  const kept = memory("mine");
  const { root } = rules(both, kept);
  expect("two buttons", root.querySelectorAll(".rules-side-pick").map((b) => b.textContent), ["Mine", "Camp"]);
  expect("Mine is pressed", root.querySelector(".rules-side-pick[aria-pressed=\"true\"]")?.dataset.side, "mine");
  pick(root, "camp");
  expect("kept", kept.side, "camp");
  expect("Camp is shown", root.querySelectorAll(".task-rule").length > 0, true);
  expect("a new page on this device opens on Camp", rules(both, kept).root.querySelectorAll(".task-rule").length > 0, true);
}

{  // a new rule offers its side's tasks alone; Camp has one New rule, asking who it is for by name
  const open = (side: RuleSide) => {
    const r = rules(both, memory(side));
    expect(`${side}: one New rule`, r.root.querySelectorAll(".rules-new").length, 1);
    r.root.querySelector(".rules-new")?.click();
    return r.root;
  };
  const doing = (root: FakeEl): string[] => root.querySelectorAll(".cond-task").map((b) => b.dataset.card ?? "");
  const camp = open("camp");
  const who = camp.querySelectorAll(".rules-who button");
  expect("Camp asks for each person by name", who.map((b) => b.textContent), people(cat, both).map((l) => cat.laneLabel(l, both)));
  who[0]?.click();
  const first = people(cat, both)[0]!;
  expect("a person's New rule offers that person's tasks alone", doing(camp).length > 0 && doing(camp).every((c) => cat.laneOf(c) === first), true);
  const mine = doing(open("mine"));
  expect("Mine offers tasks", mine.length > 0, true);
  expect("Mine offers none of a person's", mine.some((c) => cat.ruled(c)), false);
}

{  // a rule saved lands on its side; opening a person's lane editor shows Camp
  const added = { ...both.orders[personRule]!, when: { kind: "after_time" as const, at: 5 } };
  expect("a person's rule added: Camp", landedSide(cat, both, { kind: "set_orders", orders: [...both.orders, added] }), "camp");
  expect("a hands rule added: Mine", landedSide(cat, both, { kind: "set_orders", orders: [...both.orders, { ...both.orders[handsRule]!, when: { kind: "after_time", at: 5 } }] }), "mine");
  expect("a removal lands nowhere", landedSide(cat, both, { kind: "set_orders", orders: both.orders.slice(1) }), null);
  const kept = memory("mine");
  const { tab } = rules(both, kept);
  tab.open(both, { lane: both.orders[personRule]!.then.kind === "tap_card" ? cat.laneOf((both.orders[personRule]!.then as { card: string }).card) : "", rule: personRule });
  expect("the lane editor opens on Camp", kept.side, "camp");
}
