// The town on the Rules tab and when it stops (CONTRACT.txt, "The town's mix"; ui/ruletown.ts, game/town.ts): the rules
// naming a town mix are listed under the town's heading, the always one worded ui.rule.town_always, each with the hands' ≡ and Remove in its menu; a
// town mix whose card has retired is greyed: its rule dimmed and passed over, the strip's bars grey with the reason.
// The views are the engine's own (fixtures/townwire.ts); the greyed one is that view with the greyed shape applied (fixtures/town.ts).
import { fakeDocument, type FakeEl, install } from "./fake-dom";
import { testContext } from "./context";
import { townStep } from "../fixtures/town";
import type { View } from "../src/api/types";
import { RulesTab } from "../src/ui/rules";
import { TownStrip } from "../src/ui/townstrip";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const both = townStep("town").view;
const townIndex = both.orders.findIndex((o) => o.then.kind === "switch_mix" && o.then.mix_id === "town:main");
const greyed = townStep("towngrey").view;
const texts = (nodes: FakeEl[]): string[] => nodes.map((n) => n.textContent ?? "");

function rules(view: View) {
  const { ctx, got } = testContext();
  const tab = new RulesTab(ctx);
  document.body.replaceChildren(tab.root);
  tab.update(view);
  return { root: fakeDocument.body.firstElementChild as FakeEl, got };
}
function strip(view: View) {
  const { ctx } = testContext();
  const s = new TownStrip(ctx, () => undefined);
  document.body.replaceChildren(s.root);
  s.update(view);
  return fakeDocument.body.firstElementChild as FakeEl;
}

{  // the town's rule is listed under the town's heading, worded as its always rule, and not among the hands' rules
  const { root } = rules(both);
  const section = root.querySelectorAll(".rules-town");
  expect("one town section", section.length, 1);
  expect("its heading", section[0]?.querySelector(".panel-heading")?.textContent, "Camp");
  expect("the always rule's words", texts(root.querySelectorAll(".town-rule .rule-when")), ["Camp, always"]);
  expect("it is the one on", root.querySelectorAll(".town-rule.active").length, 1);
  expect("not among the hands' rules", root.querySelectorAll(".rules-list .rule-handle").map((h) => h.dataset.rule).includes(String(townIndex)), false);
  expect("the hands' rules are still there", root.querySelectorAll(".rules-list .rule-handle").length > 0, true);
  expect("not dimmed while it runs", root.querySelectorAll(".town-rule.greyed").length, 0);
}

{  // Remove drops that rule, whole list sent
  const { root, got } = rules(both);
  root.querySelector(".town-rule .rule-handle")?.click();
  root.querySelector(".rules-town .rule-menu .danger")?.click();
  const sent = got.decided[0];
  expect("set_orders without the town's rule", sent?.kind === "set_orders" ? sent.orders.length : -1, both.orders.length - 1);
  expect("and the helper's tap rule stays", sent?.kind === "set_orders" ? sent.orders.some((o) => o.then.kind === "tap_card") : false, true);
}

{  // no town yet: no section
  const { root } = rules({ ...both, orders: both.orders.filter((_, i) => i !== townIndex), orders_on: both.orders_on.filter((_, i) => i !== townIndex), order_states: both.order_states.filter((_, i) => i !== townIndex) });
  expect("no town rule, no town section", root.querySelectorAll(".rules-town").length, 0);
}

{  // greyed: the rule is dimmed and says it is passed over
  const { root } = rules(greyed);
  expect("the rule is dimmed", root.querySelectorAll(".town-rule.greyed").length, 1);
  expect("and not the one on", root.querySelectorAll(".town-rule.active").length, 0);
}

{  // greyed: the strip greys its bars, names the card, and still shows each person's split
  const s = strip(greyed);
  expect("greyed class", s.classList.contains("greyed"), true);
  expect("the reason", s.querySelector(".town-status")?.textContent, "stopped · Haul water done");
  expect("status shown", s.querySelector(".town-status")?.hidden, false);
  expect("the split is the mix's, not an empty one", texts(s.querySelectorAll(".town-person")[0]!.querySelectorAll(".town-key-item")), ["Chop logs 60%", "Haul water 30%", "Helper, idle 10%"]);
  const live = strip(both);
  expect("a running town is not greyed", live.classList.contains("greyed"), false);
  expect("and has no reason", live.querySelector(".town-status")?.hidden, true);
}
