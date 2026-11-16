// "When hurt, make a poultice" can be built (#171): hurt is a store no ledger line draws and no unlock opens, so the When
// row offered neither its chip nor the store for the poultice, though the poultice takes hurt. A store a lost fight adds
// to is offered once its chip has been drawn, and the quick add reads it as a level, in whole items rounded up.
import { install } from "./fake-dom";
import { testContext } from "./context";
import { fixtureContent } from "../fixtures/content";
import { fightsStep, withHurtChip } from "../fixtures/fights";
import type { Decision, View } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { storeItems } from "../src/game/ruleoffers";
import { RulesTab } from "../src/ui/rules";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const q = (root: ParentNode, sel: string): HTMLElement[] => Array.from(root.querySelectorAll<HTMLElement>(sel));
const one = (root: ParentNode, sel: string): HTMLElement => {
  const found = q(root, sel)[0];
  if (!found) throw new Error(`no ${sel}`);
  return found;
};

const catalog = new Catalog(withHurtChip(fixtureContent));
const hurt: View = fightsStep("fighthurt", 100).view;   // 1.5 hurt, its chip drawn

function newRule(view: View): { cond: HTMLElement; decided: Decision[] } {
  const { ctx, got } = testContext(undefined, catalog);
  ctx.keeps.keepRuleSeen();
  const tab = new RulesTab(ctx);
  document.body.replaceChildren(tab.root);
  tab.update(view);
  one(tab.root, ".rules-new").click();
  return { cond: one(tab.root, ".cond"), decided: got.decided };
}
const chips = (cond: HTMLElement) => q(cond, ".cond-stores .cond-chip").map((b) => b.textContent);
const stores = (cond: HTMLElement) => q(cond, ".cond-stores .cond-store[data-store]").map((b) => b.dataset["store"]);

// The poultice is a task the Do row offers; choosing it offers hurt, the store it takes.
{
  const { cond, decided } = newRule(hurt);
  expect("the poultice is offered as an action", q(cond, ".cond-task").map((b) => b.dataset["card"]).includes("poultice"), true);
  one(cond, ".cond-task[data-card=\"poultice\"]").click();
  expect("hurt is offered once, as the store: a chip's rule carries no level", [chips(cond), stores(cond).includes("hurt")], [[], true]);
  one(cond, ".cond-store[data-store=\"hurt\"]").click();
  expect("the quick add reads hurt as a store the task takes: it reaches", one(cond, ".cond-sentence .quick-test .quick-word").textContent, "reaches");
  const read = Array.from(one(cond, ".cond-sentence").children).map((c) => (c.classList.contains("quick-part") ? c.querySelector(".quick-word")?.textContent : c.textContent) ?? "").join("");
  expect("it starts at 2 of the 3 hurt (one run takes 1, and a band needs two items) and ends empty, not at full", read, "When hurt reaches 65%, Make a poultice until down to empty");
  one(cond, ".cond-actions .primary").click();
  const set = decided.at(-1);
  const when = set?.kind === "set_orders" ? set.orders.at(-1)?.when : undefined;
  expect("saved as a rule that waits on the hurt store, at a level", [when?.kind, when && "watched" in when ? when.watched : null], ["at_least", { kind: "store_value", store: "hurt" }]);
  expect("65% of 3 reads 2 and lets go at none", when?.kind === "at_least" ? [when.value, when.release, when.value_of_cap, when.release_of_cap] : null, [6500, 0, true, true]);
}

// The level a rule reads is the one the chip shows: whole items, rounded up.
expect("1.5 hurt reads 2", storeItems(catalog, hurt, "hurt"), 2);

// Before its chip has been drawn there is nothing to wait on.
{
  const { cond } = newRule({ ...hurt, chips_seen: [] });
  one(cond, ".cond-task[data-card=\"poultice\"]").click();
  expect("no chip drawn: neither offered", [chips(cond), stores(cond).includes("hurt")], [[], false]);
}
