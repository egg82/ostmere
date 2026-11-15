// The rule editor's "Or else" (docs/design/rule-guards.md, "Or else", "How the page words it"; statements 3, 27 and 28 of
// its contract): the full editor, behind More options, builds only fallbacks the engine accepts. Up to
// Content.limits.max_or_else, none twice and none the first action, all taps of one lane or all mixes of one layer. A
// rule holding one never opens in the simple editor, and Save keeps the guards and fallbacks the edit does not touch.
import { fakeDocument, FakeEl, install } from "./fake-dom";
import { Catalog } from "../src/game/catalog";
import { testContext } from "./context";
import { fixtureContent } from "../fixtures/content";
import { guardsStep } from "../fixtures/guards";
import { fixtureStep } from "../fixtures/steps";
import type { Decision, Order, OrderVerb, View } from "../src/api/types";
import { ruleExists } from "../src/game/orders";
import { RulesTab } from "../src/ui/rules";

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

const base = fixtureStep("rulestab", 100).view;   // hands tasks gather, tend, rest ...; rule 0 runs the mix "Gather by hand"; rule 3 taps the bench's shelter
const guarded = guardsStep("guards", 100).view;     // rule 3 taps smoke_catch, or else smoke_roots, with two guards
const tap = (card: string): OrderVerb => ({ kind: "tap_card", card });
const mix = (mix_id: string): OrderVerb => ({ kind: "switch_mix", mix_id });
const gatherCard = base.cards.find((c) => c.card === "gather")!;
/** `v` with more tasks in play (each a copy of Gather's card; the content says which lane it is on) and `mixes` saved. */
const plus = (v: View, cards: string[], mixes: View["mixes"] = []): View =>
  ({ ...v, cards: [...v.cards, ...cards.map((card) => ({ ...gatherCard, card }))], mixes: [...v.mixes, ...mixes] });
const half = fixtureContent.scales.bp / 2;
const town = (id: string, a: string, b: string) => ({ id, components: [{ kind: "card_share" as const, card: a, share_bp: half }, { kind: "card_share" as const, card: b, share_bp: half }] });
const crew = town("Town crew", "chop", "haul");
const crew2 = town("Town rest", "chop", "fetch");
/** `v` with rule `i`'s then and or_else set. */
const rule = (v: View, i: number, then: OrderVerb, or_else: OrderVerb[], unless: Order["unless"] = v.orders[i]!.unless): View =>
  ({ ...v, orders: v.orders.map((o, j) => (j === i ? { ...o, then, or_else, unless } : o)) });

interface Rig { tab: RulesTab; root: FakeEl; decided: Decision[]; view: View }
function rig(view: View, max = fixtureContent.limits.max_or_else): Rig {
  const { ctx, got } = testContext(undefined, new Catalog({ ...fixtureContent, limits: { ...fixtureContent.limits, max_or_else: max } }));
  ctx.keeps.keepRuleSeen();
  const tab = new RulesTab(ctx);
  document.body.replaceChildren(tab.root);
  const root = fakeDocument.body.firstElementChild;
  if (!root) throw new Error("nothing mounted");
  tab.update(view);
  return { tab, root, decided: got.decided, view };
}
const openRule = (r: Rig, i: number): FakeEl => { r.tab.open(r.view, i); return one(r.root, ".cond"); };
const save = (cond: FakeEl): void => one(cond, ".cond-actions .primary").click();
const sentOrders = (r: Rig): Order[] => {
  const d = r.decided.find((x) => x.kind === "set_orders");
  if (!d || d.kind !== "set_orders") throw new Error("no set_orders sent");
  return d.orders;
};
const offered = (cond: FakeEl): string[] => {
  one(cond, ".cond-else-add").click();
  return q(cond, ".cond-else-choice").map((b) => b.dataset.card ?? b.dataset.mix ?? "?");
};
const rows = (cond: FakeEl): string[] => q(cond, ".cond-else-words").map((w) => w.textContent ?? "");

check("28 a rule with two fallbacks is offered no third", () => {
  expect("the limit is the served two", fixtureContent.limits.max_or_else, 2);
  const r = rig(rule(plus(base, ["tend", "rest"]), 0, mix("Gather by hand"), [mix("Rest by the fire"), mix("Rest")]));
  const cond = openRule(r, 0);
  expect("two fallback rows", rows(cond).length, 2);
  expect("no add", one(cond, ".cond-else-add").hidden, true);
  one(cond, ".cond-else-drop").click();
  expect("a removal makes room", one(one(r.root, ".cond"), ".cond-else-add").hidden, false);
});

check("28 the limit is the served one, not a number the page knows", () => {
  const view = plus(rule(base, 0, mix("Gather by hand"), [mix("Rest")]), ["rest", "tend"]);
  expect("one served: no second", one(openRule(rig(view, 1), 0), ".cond-else-add").hidden, true);
  expect("three served: a third", one(openRule(rig(rule(view, 0, mix("Gather by hand"), [mix("Rest"), mix("Rest by the fire")]), 3), 0), ".cond-else-add").hidden, false);
});

check("28 a hands rule is offered the hands' tasks and mixes, none on another lane and none of the town's", () => {
  const r = rig(plus(base, ["smoke_catch", "hew"], [crew]));
  const cond = openRule(r, 0);
  const got = offered(cond);
  expect("some hands task", got.includes("rest"), true);
  expect("another hands mix", got.includes("Morning <b>fire</b> & wood"), true);
  expect("no bench task", got.includes("shelter"), false);
  expect("no smoke task", got.includes("smoke_catch"), false);
  expect("no ruled-lane task", got.includes("hew"), false);
  expect("no town mix", got.includes("Town crew"), false);
});

check("28 a tap on a lane is offered that lane's tasks alone, never a mix", () => {
  const r = rig(plus(rule(guarded, 3, tap("smoke_catch"), []), ["smoke_catch", "smoke_roots", "hew", "shelter"], [crew]));
  const got = offered(openRule(r, 3));
  expect("only the other smoke task", got, ["smoke_roots"]);
});

check("28 a town mix is offered the town's mixes alone", () => {
  const view = plus(rule(base, 0, mix("Town crew"), []), [], [crew, crew2]);
  const got = offered(openRule(rig(view), 0));
  expect("the other town mix", got, ["Town rest"]);
});

check("28 the first action is not offered as its own fallback, nor one already listed", () => {
  const r = rig(plus(base, ["tend", "rest"]));
  const cond = openRule(r, 0);
  const first = offered(cond);
  expect("not the first action (as the mix or as its task)", first.some((c) => c === "Gather by hand" || c === "gather"), false);
  one(cond, ".cond-else-choice[data-mix=\"Rest\"], .cond-else-choice[data-card=\"rest\"]").click();
  expect("one row", rows(cond).length, 1);
  const again = offered(cond);
  expect("not offered twice (as the mix or as its task)", again.some((c) => c === "Rest" || c === "rest"), false);
});

check("28 a fallback is saved with the rule, and a hands task as its solo mix", () => {
  const r = rig(plus(base, ["tend"]));
  const cond = openRule(r, 0);
  offered(cond);
  one(cond, ".cond-else-choice[data-card=\"tend\"]").click();
  expect("the sentence reads it", one(cond, ".cond-sentence").textContent?.includes(", or else "), true);
  save(cond);
  expect("or_else", sentOrders(r)[0]!.or_else, [mix("Rest by the fire")]);
  expect("no other mix saved: it exists", r.decided.some((d) => d.kind === "save_mix"), false);
});

check("28 a hands task with no solo mix is saved as one, ahead of the rule", () => {
  const r = rig(plus(base, ["forage"]));
  const cond = openRule(r, 0);
  offered(cond);
  one(cond, ".cond-else-choice[data-card=\"forage\"]").click();
  save(cond);
  const saved = r.decided.find((d) => d.kind === "save_mix");
  expect("a solo mix is saved first", saved && saved.kind === "save_mix" ? saved.mix.components.map((c) => c.kind === "card_share" ? c.card : "") : null, ["forage"]);
  expect("the rule falls back to it", sentOrders(r)[0]!.or_else.length, 1);
  expect("as a mix", sentOrders(r)[0]!.or_else[0]!.kind, "switch_mix");
  expect("save_mix came before set_orders", r.decided.findIndex((d) => d.kind === "save_mix") < r.decided.findIndex((d) => d.kind === "set_orders"), true);
});

check("28 changing what the rule does drops the fallbacks its lane or layer no longer allows", () => {
  const r = rig(plus(rule(guarded, 3, tap("smoke_catch"), [tap("smoke_roots")]), ["smoke_catch", "smoke_roots"]));
  const cond = openRule(r, 3);
  expect("a fallback row", rows(cond).length, 1);
  one(cond, ".cond-task[data-card=\"shelter\"]").click();
  expect("gone with its lane", rows(cond).length, 0);
});

check("28 a fallback that is no longer offered but still stands is kept on Save", () => {
  const r = rig(plus(rule(guarded, 3, tap("smoke_catch"), [tap("smoke_roots")]), ["smoke_catch"]));   // smoke_roots is not in play any more
  const cond = openRule(r, 3);
  expect("its row is drawn", rows(cond).length, 1);
  one(cond, ".cond-store[data-store=\"catch\"]").click();
  save(cond);
  expect("kept", sentOrders(r)[3]!.or_else, [tap("smoke_roots")]);
});

check("27 a rule holding only a fallback opens in the full editor", () => {
  const r = rig(plus(rule(base, 0, mix("Gather by hand"), [mix("Rest")]), ["rest"]));
  const cond = openRule(r, 0);
  expect("More options is not offered: the editor is full", one(cond, ".cond-more").hidden, true);
  expect("its fallback is drawn", rows(cond), ["Rest"]);
});

check("27 a lane's Change on a rule holding only a fallback opens the full editor", () => {
  const view = plus(rule(guarded, 3, tap("smoke_catch"), [tap("smoke_roots")], []), ["smoke_catch", "smoke_roots"]);
  const r = rig(view);
  r.tab.open(view, { lane: "smoke", rule: 3 });
  expect("its fallback is drawn in the full editor", q(one(r.root, ".cond"), ".cond-else-row").length, 1);
});

check("27 a new rule opens simple, with its Or else behind More options", () => {
  const r = rig(base);
  one(r.root, ".rules-new").click();
  const cond = one(r.root, ".cond");
  expect("hidden before a task is chosen and More options is opened", one(cond, ".cond-else").hidden, true);
  one(cond, ".cond-task[data-card=\"gather\"]").click();
  expect("still behind More options", one(cond, ".cond-else").hidden, true);
  one(cond, ".cond-more").click();
  expect("open with it", one(cond, ".cond-else").hidden, false);
});

check("28 saving a changed rule keeps its guards and its fallbacks", () => {
  const r = rig(plus(guarded, ["smoke_catch", "smoke_roots"]));
  const cond = openRule(r, 3);
  one(cond, ".cond-store[data-store=\"catch\"]").click();   // the condition is what changes
  save(cond);
  const was = guarded.orders[3]!;
  expect("guards and fallback as they were", [sentOrders(r)[3]!.unless, sentOrders(r)[3]!.or_else], [was.unless, was.or_else]);
});

check("28 adding a fallback keeps the guards, and removing one keeps the rest", () => {
  const view = plus(guarded, ["smoke_catch", "smoke_roots", "forage"]);
  const r = rig(view);
  const cond = openRule(r, 3);
  one(cond, ".cond-else-drop").click();
  save(one(r.root, ".cond"));
  expect("fallback gone, guards kept", [sentOrders(r)[3]!.or_else, sentOrders(r)[3]!.unless], [[], guarded.orders[3]!.unless]);
});

check("28 two rules that differ only in a fallback are not the same rule", () => {
  const a = base.orders[0]!;
  const b: Order = { ...a, or_else: [mix("Rest")] };
  const view = { ...base, orders: [a, ...base.orders.slice(1)] };
  expect("a rule with a fallback is not its bare twin", ruleExists(view, null, b), false);
  expect("the same rule is", ruleExists(view, null, { ...a }), true);
  expect("fallbacks in another order differ", ruleExists({ ...base, orders: [{ ...a, or_else: [mix("Rest"), mix("Gather by hand")] }] }, null, { ...a, or_else: [mix("Gather by hand"), mix("Rest")] }), false);
});

check("28 an or-else row is worded as the rule's actions are", () => {
  const r = rig(plus(base, ["rest"]));
  const cond = openRule(r, 0);
  offered(cond);
  one(cond, ".cond-else-choice[data-card=\"rest\"]").click();
  expect("the foot's sentence", one(cond, ".cond-sentence").textContent?.endsWith("→ Gather by hand, or else Rest"), true);
});

if (failures.length > 0) throw new Error(`${failures.length} failed:\n${failures.join("\n")}`);
