// An Unless guard on hurt and the full editor's When list read hurt the way its chip does (#220): whole items rounded
// up. "Unless hurt is 2 or more" holds whenever the chip reads 2 or more, and the When list shows the level beside Hurt.
import { fakeDocument, FakeEl, FakeEvent, install } from "./fake-dom";
import { testContext } from "./context";
import { fixtureContent, Q } from "../fixtures/content";
import { fightsStep, withHurtChip } from "../fixtures/fights";
import type { Decision, View } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { RulesTab } from "../src/ui/rules";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}
const one = (root: FakeEl, sel: string, n = 0): FakeEl => {
  const found = root.querySelectorAll(sel)[n];
  if (!found) throw new Error(`no ${sel} [${n}]`);
  return found;
};

const catalog = new Catalog(withHurtChip(fixtureContent));
const hurt: View = fightsStep("fighthurt", 100).view;   // 1.5 hurt, its chip drawn, a cap of three items

/** A new full-editor rule "make a poultice", its When list drawn. */
function fullEditor(): { cond: FakeEl; decided: Decision[] } {
  const { ctx, got } = testContext(undefined, catalog);
  ctx.keeps.keepRuleSeen();
  const tab = new RulesTab(ctx);
  document.body.replaceChildren(tab.root);
  const root = fakeDocument.body.firstElementChild;
  if (!root) throw new Error("nothing mounted");
  tab.update(hurt);
  one(root, ".rules-new").click();
  const cond = one(root, ".cond");
  one(cond, ".cond-task[data-card=\"poultice\"]").click();
  one(cond, ".cond-more").click();
  return { cond, decided: got.decided };
}

{
  const { cond } = fullEditor();
  expect("the When list shows hurt's level as its chip does: 1.5 hurt reads 2", one(cond, ".cond-stores .cond-store[data-store=\"hurt\"] .cond-amount").textContent, "2");
}

{
  const { cond, decided } = fullEditor();
  one(cond, ".cond-guard-add").click();
  one(cond, ".cond-guard-what .cond-store[data-store=\"hurt\"]").click();
  expect("a hurt guard starts at the cap in whole items", one(cond, ".cond-guard-pick .cond-guard-words").textContent, "Hurt is 3 or more");
  one(cond, ".cond-guard-pick [data-form=\"items\"] [role=\"slider\"]").dispatchEvent(Object.assign(new FakeEvent("keydown"), { key: "ArrowLeft" }));
  one(cond, ".cond-guard-done").click();
  expect("it is worded in the items its chip shows", one(cond, ".cond-guards .cond-guard .cond-guard-words").textContent, "Hurt is 2 or more");
  one(cond, ".cond-actions .primary").click();
  const set = decided.find((d) => d.kind === "set_orders");
  const guard = set?.kind === "set_orders" ? set.orders.at(-1)?.unless[0] : undefined;
  expect("it holds while the chip reads 2 or more (above one item), and lets go above none", guard?.kind === "at_least" ? [guard.value, guard.release, guard.value_of_cap] : null, [Q + 1, 1, false]);
}
