// The condition editor's quick add (docs/design/opening-screen/rules-tab.md, "The condition editor"): with a task chosen, When
// offers the stores relevant to it (game/relevant.ts), what it makes then what it takes, and More options every store
// with those first.
import { install } from "./fake-dom";
import { testContext } from "./context";
import { dayOneStep } from "../fixtures/dayone";
import type { Decision, View } from "../src/api/types";
import { fixtureContent } from "../fixtures/content";
import { Catalog } from "../src/game/page/catalog";
import { RulesTab } from "../src/ui/rules/rules";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const q = (root: ParentNode, sel: string): HTMLButtonElement[] => Array.from(root.querySelectorAll<HTMLButtonElement>(sel));
const one = (root: ParentNode, sel: string): HTMLButtonElement => {
  const found = q(root, sel)[0];
  if (!found) throw new Error(`no ${sel}`);
  return found;
};

function newRule(view: View): { cond: HTMLElement; decided: Decision[] } {
  const { ctx, got } = testContext();
  ctx.keeps.keepRuleSeen();
  const tab = new RulesTab(ctx);
  document.body.replaceChildren(tab.root);
  tab.update(view);
  one(tab.root, ".rules-new").click();
  return { cond: one(tab.root, ".cond"), decided: got.decided };
}

const rising = dayOneStep("rising", 100).view;   // the smoke lane open: catch, smoked and roots have lines
const stores = (cond: HTMLElement) => q(cond, ".cond-stores .cond-store[data-store]").map((b) => b.dataset.store);

// Smoking the catch: the store it makes, then the one it takes; nothing else until More options, which lists every
// store with those two first.
{
  const { cond } = newRule(rising);
  one(cond, ".cond-task[data-card=\"smoke_catch\"]").click();
  expect("simple: what it makes, then what it takes", stores(cond), ["smoked", "catch"]);
  one(cond, ".cond-more").click();
  const all = stores(cond);
  expect("full: the same two first", all.slice(0, 2), ["smoked", "catch"]);
  expect("full: then every other store, each once", all.length > 2 && new Set(all).size === all.length && all.includes("wood"), true);
}

/** The sentence as it reads: each part's words, the text between them as written. */
const reads = (cond: HTMLElement): string => Array.from(one(cond, ".cond-sentence").children).map((c) =>
  (c.classList.contains("quick-part") ? c.querySelector(".quick-word")?.textContent : c.textContent) ?? "").join("");
const select = (cond: HTMLElement, part: string): HTMLSelectElement => {
  const found = cond.querySelector<HTMLSelectElement>(`.cond-sentence .quick-${part} select`);
  if (!found) throw new Error(`no ${part} part`);
  return found;
};
function choose(cond: HTMLElement, part: string, value: string): void {
  const s = select(cond, part);
  s.value = value;
  s.dispatchEvent(new Event("change"));
}
const options = (cond: HTMLElement, part: string): string[] => q(select(cond, part), "option").map((o) => `${o.textContent}${o.disabled ? " (off)" : ""}`);
const sent = (decided: Decision[]) => { const d = decided.at(-1); return d?.kind === "set_orders" ? d.orders.at(-1)?.when : undefined; };

// The quick add reads as one sentence with the default levels, each part a choice in place: a store the task makes
// starts "falls to a quarter, until three quarters"; one it takes, "reaches full, until down to half".
{
  const { cond, decided } = newRule(rising);
  one(cond, ".cond-task[data-card=\"smoke_catch\"]").click();
  one(cond, ".cond-store[data-store=\"smoked\"]").click();
  expect("a store it makes", reads(cond), "When Smoked falls to a quarter, Smoke the catch until three quarters");
  expect("no levels fold in the quick add", one(cond, ".cond-levels").hidden, true);
  expect("the store part offers the When row's stores", options(cond, "store"), ["Smoked", "Catch"]);
  expect("the level parts offer the named shares", options(cond, "n"), ["empty", "a quarter", "half", "three quarters (off)", "full (off)"]);
  choose(cond, "store", "catch");
  expect("a store it takes", reads(cond), "When Catch reaches full, Smoke the catch until down to half");
  choose(cond, "test", "below");
  expect("the test, in place: its own defaults", reads(cond), "When Catch falls to a quarter, Smoke the catch until three quarters");
  choose(cond, "m", "s10000");
  expect("a level, in place", reads(cond), "When Catch falls to a quarter, Smoke the catch until full");
  one(cond, ".cond-actions .primary").click();
  expect("saved as read", sent(decided), { kind: "at_most", watched: { kind: "store_value", store: "catch" }, value: 2500, release: 10000, value_of_cap: true, release_of_cap: true });
}

// More options keeps the uncommon: the levels open there, with exact numbers, and the foot reads as before.
{
  const { cond } = newRule(rising);
  one(cond, ".cond-task[data-card=\"smoke_catch\"]").click();
  one(cond, ".cond-store[data-store=\"smoked\"]").click();
  one(cond, ".cond-more").click();
  expect("full: the levels shown", one(cond, ".cond-levels").hidden, false);
  expect("full: no quick parts", q(cond, ".cond-sentence .quick-part").length, 0);
}

// Copy rule: a rule being changed starts a new rule from it, the same task and condition, Save off until it differs;
// one with share levels on a relevant store opens in the quick add, one with exact numbers in the full editor.
function editRule(view: View, index: number, catalog?: Catalog): { cond: HTMLElement; decided: Decision[] } {
  const { ctx, got } = testContext(undefined, catalog);
  ctx.keeps.keepRuleSeen();
  const tab = new RulesTab(ctx);
  document.body.replaceChildren(tab.root);
  tab.update(view);
  q(tab.root, ".rules .rule-cond")[index]!.click();
  return { cond: one(tab.root, ".cond"), decided: got.decided };
}
const woodRule = rising.orders.findIndex((o) => o.when.kind === "at_most" && o.when.watched.kind === "store_value" && o.when.watched.store === "wood");
const shared: View = { ...rising, orders: rising.orders.map((o, i) => (i === woodRule && o.when.kind === "at_most" ? { ...o, when: { ...o.when, value: 2500, release: 7500, value_of_cap: true, release_of_cap: true } } : o)) };
{
  const { cond, decided } = editRule(shared, woodRule);
  expect("control: the wood rule is open", one(cond, ".cond-heading").textContent?.startsWith("Run "), true);
  one(cond, ".cond-copy").click();
  expect("a new rule", [one(cond, ".cond-heading").textContent, one(cond, ".cond-actions .primary").textContent], ["New rule", "Add rule"]);
  expect("the same rule: Save off, and why", [one(cond, ".cond-actions .primary").disabled, one(cond, ".cond-note").textContent], [true, "a rule already does this"]);
  expect("no Remove or Copy on the copy", [one(cond, ".cond-actions .danger").hidden, one(cond, ".cond-copy").hidden], [true, true]);
  expect("shares on a store the task makes: the quick add", reads(cond), "When Dead wood falls to a quarter, Gather by hand until three quarters");
  choose(cond, "n", "s5000");
  one(cond, ".cond-actions .primary").click();
  const set = decided.at(-1);
  expect("added beside the first: two rules doing the same", set?.kind === "set_orders" ? [set.orders.length, set.orders.at(-1)?.then] : null,
    [shared.orders.length + 1, shared.orders[woodRule]!.then]);
}
{
  const { cond } = editRule(rising, woodRule);
  one(cond, ".cond-copy").click();
  expect("exact numbers: the copy opens in the full editor", [one(cond, ".cond-heading").textContent, one(cond, ".cond-levels").hidden], ["New rule", false]);
}
{
  const chipRule = rising.orders.findIndex((o) => o.then.kind === "switch_mix" && o.then.mix_id === "Rest");
  const { cond } = editRule(rising, chipRule);
  expect("control: a chip's rule is open", one(cond, ".cond-heading").textContent, "While tired");
  expect("a chip's rule has no copy: its condition can't change", one(cond, ".cond-copy").hidden, true);
}
{
  const full = new Catalog({ ...fixtureContent, limits: { ...fixtureContent.limits, max_orders: rising.orders.length } });
  const { cond } = editRule(rising, woodRule, full);
  expect("no room for another rule: Copy rule is off", [one(cond, ".cond-copy").hidden, one(cond, ".cond-copy").disabled], [false, true]);
}
{
  const { cond } = newRule(rising);
  one(cond, ".cond-task[data-card=\"smoke_catch\"]").click();
  one(cond, ".cond-store[data-store=\"smoked\"]").click();
  choose(cond, "action", "smoke_roots");
  expect("the task, in place: smoking roots makes smoked too, so the store stays", reads(cond), "When Smoked falls to a quarter, Smoke roots until three quarters");
}
{
  // A new view while a part's picker may be open (the page's next step) keeps the parts as they are: rebuilding would
  // close the picker under the player's thumb. A change that moves the sentence rebuilds it.
  const { ctx } = testContext();
  ctx.keeps.keepRuleSeen();
  const tab = new RulesTab(ctx);
  document.body.replaceChildren(tab.root);
  tab.update(rising);
  one(tab.root, ".rules-new").click();
  const cond = one(tab.root, ".cond");
  one(cond, ".cond-task[data-card=\"smoke_catch\"]").click();
  one(cond, ".cond-store[data-store=\"smoked\"]").click();
  const before = select(cond, "n");
  tab.update({ ...rising, at: rising.at + 5 });
  expect("the same sentence: the same select", select(cond, "n") === before, true);
  choose(cond, "n", "s0");
  expect("a pick redraws it", [select(cond, "n") === before, reads(cond)], [false, "When Smoked falls to empty, Smoke the catch until three quarters"]);
}
