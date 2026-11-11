// The town's rules on the Rules tab are written as the hands' are (CONTRACT.txt, "The town's mix"): the always rule worded
// by the town's title (never the mix's id), every town rule with the hands' ≡ (menu and key and drag, reordering among the
// town's rules alone), and a new town rule from the full editor, doing a town mix and nothing else, set immediately before
// the town's first always rule. The views are the engine's own (fixtures/townwire.ts) with one town rule added.
import { fakeDocument, type FakeEl, FakeEvent, install, pointer } from "./fake-dom";
import { testContext } from "./context";
import { townStep } from "../fixtures/town";
import type { Decision, Order, View } from "../src/api/types";
import { RulesTab } from "../src/ui/rules";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}
const q = (root: FakeEl, sel: string): FakeEl[] => root.querySelectorAll(sel);
const one = (root: FakeEl, sel: string, n = 0): FakeEl => {
  const found = q(root, sel)[n];
  if (!found) throw new Error(`no ${sel} [${n}]`);
  return found;
};
const sent = (d: Decision | undefined): Order[] => (d?.kind === "set_orders" ? d.orders : []);

const base = townStep("town").view;
const always = base.orders.findIndex((o) => o.then.kind === "switch_mix" && o.then.mix_id === "town:main");
const TOWN_THEN: Order["then"] = { kind: "switch_mix", mix_id: "town:main" };
const first: Order = { when: { kind: "after_time", at: 0 }, then: TOWN_THEN };
const WHEN = base.orders.find((o) => o.when.kind !== "after_time")!.when;   // a store rule the day-two page has
const mine: Order = { when: WHEN, then: TOWN_THEN };
const other: Order = { when: { ...WHEN, watched: { kind: "store_value", store: "wood" } } as Order["when"], then: TOWN_THEN };

/** The town view with two town rules above its always rule, so the always rule is the last of three. */
function twoRules(): View {
  const orders = [...base.orders.slice(0, always), mine, other, ...base.orders.slice(always)];
  const pad = <T,>(a: T[], v: T): T[] => [...a.slice(0, always), v, v, ...a.slice(always)];
  return { ...base, orders, orders_on: pad(base.orders_on, false), order_states: pad(base.order_states, "waiting" as View["order_states"][number]), town_mix_order: always + 2 };
}

function rig(view: View, writing = true) {
  const { ctx, got } = testContext();
  if (writing) ctx.keeps.keepRuleSeen();   // writing rules is open, as it is by day three
  const tab = new RulesTab(ctx);
  document.body.replaceChildren(tab.root);
  tab.update(view);
  return { root: fakeDocument.body.firstElementChild as FakeEl, got };
}
const rows = (root: FakeEl): FakeEl[] => q(root, ".rules-town .town-rule");

{  // the always rule is worded by the town's title, not the mix's id
  const { root } = rig(base);
  expect("always rule's words", one(root, ".town-rule .rule-when").textContent, "Camp, always");
  expect("no raw id anywhere in the town section", /town:/.test(one(root, ".rules-town").shown()), false);
}

{  // each town rule has the hands' ≡; its menu moves it among the town's rules and removes it
  const view = twoRules();
  const { root, got } = rig(view);
  expect("three town rows, each with a handle", rows(root).map((r) => q(r, ".rule-handle").length), [1, 1, 1]);
  one(root, ".rules-town .rule-handle", 1).click();
  const menu = one(root, ".rules-town .rule-menu");
  expect("menu", q(menu, "button").map((b) => b.textContent), ["Move up", "Move down", "Remove"]);
  q(menu, "button")[0]!.click();
  expect("Move up swaps the two town rules and nothing else", sent(got.decided[0]).map((o) => JSON.stringify(o)), view.orders.map((_, i) => JSON.stringify(view.orders[i === always ? always + 1 : i === always + 1 ? always : i])));
}

{  // the menu's ends: the first town rule can't go up, the last can't go down; Remove drops it alone
  const view = twoRules();
  const { root, got } = rig(view);
  one(root, ".rules-town .rule-handle", 0).click();
  expect("first can't move up", q(one(root, ".rules-town .rule-menu"), "button")[0]!.disabled, true);
  q(one(root, ".rules-town .rule-menu"), "button")[2]!.click();
  expect("Remove drops that rule alone", sent(got.decided[0]).length, view.orders.length - 1);
  const last = rig(view);
  one(last.root, ".rules-town .rule-handle", 2).click();
  expect("last can't move down", q(one(last.root, ".rules-town .rule-menu"), "button")[1]!.disabled, true);
}

{  // the arrow keys move it; a hands rule's menu never reaches the town
  const view = twoRules();
  const { root, got } = rig(view);
  one(root, ".rules-town .rule-handle", 1).dispatchEvent(new FakeEvent("keydown", { key: "ArrowDown" }));
  expect("ArrowDown moves it below the next", sent(got.decided[0]).slice(always, always + 3), [mine, first, other]);
  const hands = q(root, ".rules-list .rule-handle");
  hands[hands.length - 1]!.click();
  expect("the last hands rule can't move down into the town", q(one(root, ".rules-list .rule-menu"), "button")[1]!.disabled, true);
}

{  // dragging ≡ among the town's rows sends the permuted list
  const view = twoRules();
  const { root, got } = rig(view);
  const town = rows(root);
  town.forEach((row, i) => { row.rect = { left: 0, top: i * 50, width: 300, height: 48, right: 300, bottom: i * 50 + 48 }; });
  const handle = one(town[0]!, ".rule-handle");
  handle.dispatchEvent(pointer("pointerdown", 10, 10));
  handle.dispatchEvent(pointer("pointermove", 10, 120));
  expect("the drop mark is on the town's last row", town.map((n) => n.classList.contains("drop-after")), [false, false, true]);
  handle.dispatchEvent(pointer("pointerup", 10, 120));
  expect("the first town rule now stands last", sent(got.decided[0]).slice(always, always + 3), [other, first, mine]);
}

{  // a new town rule: the full editor, doing a town mix and nothing else
  const { root, got } = rig(base);
  one(root, ".rules-town .town-new").click();
  const cond = one(root, ".cond");
  expect("only the town's mix is offered to do", q(cond, ".cond-mix, .cond-task").map((b) => b.textContent), ["Camp"]);
  expect("and no hands mix", q(cond, ".cond-mix").some((b) => b.dataset.mix !== "town:main"), false);
  one(cond, ".cond-mix").click();
  one(cond, `.cond-store[data-store="${(WHEN as { watched: { store: string } }).watched.store}"]`).click();
  one(cond, ".cond-actions .primary").click();
  const orders = sent(got.decided[0]);
  expect("set immediately before the town's first always rule", [orders.length, orders[always]?.then, orders[always + 1]], [base.orders.length + 1, TOWN_THEN, first]);
}

{  // writing a town rule is gated as writing a hands rule is
  expect("no New rule before the taught step", q(rig(base, false).root, ".town-new, .rules-new").length, 0);
}

{  // the hands' editor never offers a town mix
  const { root } = rig(base);
  one(root, ".rules-new").click();
  one(root, ".cond-more").click();
  expect("no town mix among the hands' choices", q(root, ".cond-mix").some((b) => b.dataset.mix === "town:main"), false);
}
