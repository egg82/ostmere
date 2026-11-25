// "When 1 or more hurt, until under 1" can be built (owner: "it's '2 or more' which I then forget to check before
// tapping a project card, so I'm always 15% slower"). A store rule needs a band of an item so it never flips at one
// level on a flow; a store only events raise (StoreInfo.rises_in_steps: nothing that runs makes it) cannot flip that way,
// so a rule on it may let go where it came on. The owner's case: hurt, raised only by a lost fight, cured by the poultice.
import { install } from "./fake-dom";
import { testContext } from "./context";
import { fixtureContent } from "../fixtures/content";
import { fightsStep, withHurtChip } from "../fixtures/fights";
import type { Decision, View } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { tryRule } from "../src/game/storerule";
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
const hurt: View = fightsStep("fighthurt", 100).view;

expect("control: hurt rises only in steps, wood does not", [catalog.risesInSteps("hurt"), catalog.risesInSteps("wood")], [true, false]);
expect("reaches 1, until under 1, on hurt", tryRule({ store: "hurt", test: "reaches", n: { items: 1 }, m: { items: 1 } }, 3, true), { store: "hurt", test: "reaches", n: { items: 1 }, m: { items: 1 } });
expect("control: not on a store a flow raises", tryRule({ store: "wood", test: "reaches", n: { items: 1 }, m: { items: 1 } }, 40, false), null);

// The quick add: When hurt reaches 1, Make a poultice until down to empty, saved as on above none and off at none.
{
  const { ctx, got } = testContext(undefined, catalog);
  ctx.keeps.keepRuleSeen();
  const tab = new RulesTab(ctx);
  document.body.replaceChildren(tab.root);
  tab.update(hurt);
  one(tab.root, ".rules-new").click();
  const cond = one(tab.root, ".cond");
  one(cond, ".cond-task[data-card=\"poultice\"]").click();
  one(cond, ".cond-store[data-store=\"hurt\"]").click();
  const options = (cls: string) => q(one(cond, `.cond-sentence .${cls}`), "option").map((o) => `${o.textContent}${(o as HTMLOptionElement).disabled ? "-" : ""}`);
  expect("when: 1 is offered", options("quick-n"), ["empty-", "1", "2", "3"]);
  const read = Array.from(one(cond, ".cond-sentence").children).map((c) => (c.classList.contains("quick-part") ? c.querySelector(".quick-word")?.textContent : c.textContent) ?? "").join("");
  expect("it starts at one run's take, 1, until empty", read, "When hurt reaches 1, Make a poultice until down to empty");
  one(cond, ".cond-actions .primary").click();
  const set = (got.decided as Decision[]).at(-1);
  const when = set?.kind === "set_orders" ? set.orders.at(-1)?.when : undefined;
  expect("on above no hurt, off at none", when?.kind === "at_least" ? [when.value, when.release, when.value_of_cap, when.release_of_cap] : null, [1, 1, false, false]);
}
