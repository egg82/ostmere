// The rule editor's "Unless" (docs/design/rule-guards.md, "How the page words it", "The saved shape"; statements 27 and
// 28 of its contract): the simple editor never opens a rule holding a guard or a fallback; the full editor, behind More
// options, builds only guards the engine accepts, a store guard's release one item past its value, both levels of a
// share guard the same share, at most Content.limits.max_unless, none twice, and keeps what it does not write.
import { fakeDocument, FakeEl, FakeEvent, install } from "../../fake-dom";
import { testContext } from "../../context";
import { fixtureContent, BP, Q } from "../../../fixtures/content";
import { guardsStep } from "../../../fixtures/guards";
import { fixtureStep } from "../../../fixtures/steps";
import type { Condition, Decision, Order, View } from "../../../src/api/types";
import { buildGuard, guardValid } from "../../../src/game/condition/guarddraft";
import { RulesTab } from "../../../src/ui/rules/rules";

install();

const failures: string[] = [];
function check(name: string, run: () => void): void {
  try { run(); } catch (e) { failures.push(`${name}: ${e instanceof Error ? e.message : String(e)}`); }
}
function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}
const q = (root: FakeEl, sel: string): FakeEl[] => root.querySelectorAll(sel);
const one = (root: FakeEl, sel: string, n = 0): FakeEl => {
  const found = q(root, sel)[n];
  if (!found) throw new Error(`no ${sel} [${n}]`);
  return found;
};

const rules = fixtureStep("rulestab", 100).view;   // wood (cap 40), stone (cap 20), warmth, a bench task
const guarded = guardsStep("guards", 100).view;     // rule 3 smokes the catch with two guards and a fallback
const store = (s: string) => ({ kind: "store_value" as const, store: s });
const atLeast = (s: string, value: number, release: number, share = false): Condition =>
  ({ kind: "at_least", watched: store(s), value, release, value_of_cap: share, release_of_cap: share });
const atMost = (s: string, value: number, release: number, share = false): Condition =>
  ({ kind: "at_most", watched: store(s), value, release, value_of_cap: share, release_of_cap: share });

interface Rig { tab: RulesTab; root: FakeEl; decided: Decision[] }
function rig(view: View): Rig {
  const { ctx, got } = testContext();
  ctx.keeps.keepRuleSeen();
  const tab = new RulesTab(ctx);
  document.body.replaceChildren(tab.root);
  const root = fakeDocument.body.firstElementChild;
  if (!root) throw new Error("nothing mounted");
  tab.update(view);
  return { tab, root, decided: got.decided };
}
const sent = (r: Rig): Order[] => {
  const d = r.decided.find((x) => x.kind === "set_orders");
  if (!d || d.kind !== "set_orders") throw new Error("no set_orders sent");
  return d.orders;
};
const savedRule = (r: Rig): Order => sent(r).at(-1)!;
const add = (cond: FakeEl): FakeEl => one(cond, ".cond-actions .primary");

/** A new full-editor rule "gather when wood is low", its guards row open, a guard's picker open and `s` chosen. */
function newGuard(r: Rig, s: string): FakeEl {
  one(r.root, ".rules-new").click();
  const cond = one(r.root, ".cond");
  one(cond, ".cond-task[data-card=\"gather\"]").click();
  one(cond, ".cond-more").click();
  one(cond, ".cond-store[data-store=\"wood\"]").click();
  one(cond, ".cond-guard-add").click();
  one(cond, `.cond-guard-what .cond-store[data-store="${s}"]`).click();
  return cond;
}
const confirm = (cond: FakeEl): void => one(cond, ".cond-guard-done").click();
const exact = (cond: FakeEl): void => one(cond, ".cond-guard-pick .cond-form", 1).click();
const step = (cond: FakeEl, dir: "less" | "more", times = 1): void => {
  for (let i = 0; i < times; i++) one(cond, '.cond-guard-pick [data-form="items"] [role="slider"]').dispatchEvent(Object.assign(new FakeEvent("keydown"), { key: dir === "less" ? "ArrowLeft" : "ArrowRight" }));
};

// 28: a store guard on a share is one share for both levels ("unless stone is full").
check("28 a share guard keeps the same share at both levels", () => {
  const r = rig(rules);
  const cond = newGuard(r, "stone");
  confirm(cond);
  add(cond).click();
  expect("unless is the share guard", savedRule(r).unless, [atLeast("stone", BP, BP, true)]);
});

// 28: whole items put the release one item past the value, for both tests.
check("28 an 'n or more' guard lets go one item under its value", () => {
  const r = rig(rules);
  const cond = newGuard(r, "stone");
  exact(cond);
  step(cond, "less", 2);   // full (20) in items, two under
  confirm(cond);
  add(cond).click();
  expect("unless", savedRule(r).unless, [atLeast("stone", 18 * Q, 17 * Q)]);
});

check("28 an 'under n' guard lets go one item past its value", () => {
  const r = rig(rules);
  const cond = newGuard(r, "stone");
  exact(cond);
  step(cond, "less", 2);
  one(cond, ".cond-guard-pick .cond-test", 1).click();
  confirm(cond);
  add(cond).click();
  expect("unless", savedRule(r).unless, [atMost("stone", 18 * Q - 1, 19 * Q - 1)]);
});

// 28: a guard the engine would let block forever, or whose release leaves the store, is not offered.
check("28 the page builds no guard that is always on or whose release leaves the store", () => {
  const ok = (test: "reaches" | "below", level: { items: number } | { share: number }) => guardValid({ store: "stone", test, level }, 20);
  expect("or more of 1 item is never let go", ok("reaches", { items: 1 }), false);
  expect("or more of the cap is", ok("reaches", { items: 20 }), true);
  expect("under the cap would let go past full", ok("below", { items: 20 }), false);
  expect("under 19 is", ok("below", { items: 19 }), true);
  expect("or more of empty is always on", ok("reaches", { share: 0 }), false);
  expect("under full is always on", ok("below", { share: BP }), false);
  expect("a store of one item has no band", guardValid({ store: "stone", test: "reaches", level: { share: BP } }, 1), false);
  expect("share guard stores one share twice", buildGuard({ store: "stone", test: "below", level: { share: 2500 } }, Q), atMost("stone", 2500, 2500, true));
});

check("28 at the stone's cap the guard button 'under' steps to the last item that keeps its release inside", () => {
  const r = rig(rules);
  const cond = newGuard(r, "stone");
  exact(cond);                                      // 20 items
  one(cond, ".cond-guard-pick .cond-test", 1).click();   // under: 20 is past the cap, so it moves to a quarter
  confirm(cond);
  add(cond).click();
  expect("unless", savedRule(r).unless, [atMost("stone", 2500, 2500, true)]);
});

// 28: at most max_unless guards; none twice.
check("28 a fourth guard is not offered", () => {
  const max = fixtureContent.limits.max_unless;
  expect("the limit is the served three", max, 3);
  const three = [atLeast("stone", BP, BP, true), atLeast("wood", BP, BP, true), atMost("wood", 5 * Q - 1, 6 * Q - 1)];
  const view: View = { ...rules, orders: [{ ...rules.orders[0]!, unless: three }, ...rules.orders.slice(1)], order_guards: rules.orders.map((_, i) => (i === 0 ? three.map(() => ({ on: false, lets_go: null })) : [])) };
  const r = rig(view);
  one(r.root, ".rules-list .rule-cond", 0).click();
  const cond = one(r.root, ".cond");
  expect("three guards drawn", q(cond, ".cond-guard").length, 3);
  expect("no add", one(cond, ".cond-guard-add").hidden, true);
});

check("28 a guard already listed is not added twice", () => {
  const r = rig(rules);
  const cond = newGuard(r, "stone");
  confirm(cond);
  one(cond, ".cond-guard-add").click();
  one(cond, ".cond-guard-what .cond-store[data-store=\"stone\"]").click();
  confirm(cond);
  expect("one guard row", q(cond, ".cond-guard").length, 1);
  add(cond).click();
  expect("unless", savedRule(r).unless.length, 1);
});

check("28 a guard is removed with its row's button, and the sentence reads it", () => {
  const r = rig(rules);
  const cond = newGuard(r, "stone");
  confirm(cond);
  expect("the sentence", one(cond, ".cond-sentence").textContent?.includes(", unless Flint is full"), true);
  one(cond, ".cond-guard-drop").click();
  expect("no guard row", q(cond, ".cond-guard").length, 0);
  add(cond).click();
  expect("unless", savedRule(r).unless, []);
});

check("28 a chip is a guard in one tap", () => {
  const r = rig({ ...rules, chips_seen: ["tired"] });
  one(r.root, ".rules-new").click();
  const cond = one(r.root, ".cond");
  one(cond, ".cond-task[data-card=\"gather\"]").click();
  one(cond, ".cond-more").click();
  one(cond, ".cond-store[data-store=\"wood\"]").click();
  one(cond, ".cond-guard-add").click();
  one(cond, ".cond-guard-what .cond-chip[data-chip=\"tired\"], .cond-guard-what .cond-chip", 0).click();
  add(cond).click();
  const tired = fixtureContent.chip_infos.find((c) => c.chip === "tired")!.when;
  expect("unless is the chip's own condition", savedRule(r).unless, [tired]);
});

// 28: editing a rule keeps the guards and fallbacks it holds that the edit does not touch.
check("28 saving a changed rule keeps its guards and its fallbacks", () => {
  const r = rig(guarded);
  one(r.root, ".rule-cond", 3).click();
  const cond = one(r.root, ".cond");
  expect("its guards are drawn", q(cond, ".cond-guard").length, 2);
  one(cond, ".cond-guard-drop", 1).click();
  add(cond).click();
  const was = guarded.orders[3]!;
  expect("one guard fewer, the rest as they were", sent(r)[3], { ...was, unless: [was.unless[0]] });
});

// 27: the simple editor never opens a rule holding a guard or a fallback.
check("27 a rule holding a guard opens in the full editor", () => {
  const r = rig(guarded);
  one(r.root, ".rules-list .rule-cond", 1).click();
  expect("More options is not offered: the editor is full", one(one(r.root, ".cond"), ".cond-more").hidden, true);
});

check("27 a lane's Change on a rule holding a guard does not open the lane's task editor", () => {
  const r = rig(guarded);
  r.tab.open(guarded, { lane: "smoke", rule: 3 });
  const cond = one(r.root, ".cond");
  expect("the full editor's More options exists (and is hidden: full)", q(cond, ".cond-more").length, 1);
  expect("its guards are drawn", q(cond, ".cond-guard").length, 2);
});

check("27 a copy of a rule holding a guard opens in the full editor, guards copied", () => {
  const shares = atMost("wood", 2500, 7500, true);
  const gather = { kind: "switch_mix" as const, mix_id: "Gather by hand" };
  const copied = (unless: Condition[]): FakeEl => {
    const view: View = { ...rules, orders: [{ when: shares, then: gather, unless, or_else: [], below_next: false }, ...rules.orders.slice(1)] };
    const r = rig(view);
    one(r.root, ".rule-cond", 0).click();
    one(one(r.root, ".cond"), ".cond-actions .quiet", 1).click();
    return one(r.root, ".cond");
  };
  expect("control: the same rule with no guard copies into the quick add", one(copied([]), ".cond-more").hidden, false);
  const cond = copied([atLeast("stone", BP, BP, true)]);
  expect("full", one(cond, ".cond-more").hidden, true);
  expect("the guard comes with it", q(cond, ".cond-guard").length, 1);
});

check("27 a new rule opens simple, with no guards row", () => {
  const r = rig(rules);
  one(r.root, ".rules-new").click();
  const cond = one(r.root, ".cond");
  expect("More options offered", one(cond, ".cond-more").hidden, false);
  expect("guards behind it", one(cond, ".cond-guards").hidden, true);
  one(cond, ".cond-more").click();
  expect("guards open with it", one(cond, ".cond-guards").hidden, false);
});

if (failures.length > 0) throw new Error(`${failures.length} failed:\n${failures.join("\n")}`);
