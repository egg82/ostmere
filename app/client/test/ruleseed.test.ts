// A guided rule starts at the offer's levels (condition.ts openNew, given the offered condition): choosing the offer's
// task leaves the sentence at the offer's "Under 10, until 20", not the editor's defaults; without an offer, the defaults.
import { install } from "./fake-dom";
import { testContext } from "./context";
import { fixtureContent } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { Condition } from "../src/api/types";
import { RulesTab } from "../src/ui/rules";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}
const one = (root: ParentNode, sel: string): HTMLButtonElement => {
  const found = root.querySelector<HTMLButtonElement>(sel);
  if (!found) throw new Error(`no ${sel}`);
  return found;
};

const view = fixtureStep("mid", 100).view;
const card = fixtureContent.order_cards.find((c) => c.store === "wood");
if (!card || card.then.kind !== "tap_card") throw new Error("fixture: no wood offer");
const task = card.then.card;

/** The sentence after opening a new rule (given `offered`, or none) and choosing the offer's task. */
function sentence(offered: Condition | undefined): string {
  const { ctx } = testContext();
  ctx.keeps.keepRuleSeen();
  const tab = new RulesTab(ctx);
  document.body.replaceChildren(tab.root);
  tab.update(view);
  tab.open(view, "new", offered);
  one(tab.root, `.cond-task[data-card="${task}"]`).click();
  const stores = Array.from(tab.root.querySelectorAll<HTMLButtonElement>(".cond-stores button")).filter((b) => b.dataset.store === "wood");
  if (offered === undefined) stores[0]?.click();   // from scratch the store is chosen too
  return one(tab.root, ".cond-sentence").textContent ?? "";
}

expect("the offer's levels", sentence(card.when), "Under 10 Dead wood, until 20 → Gather by hand");
expect("from scratch: the editor's defaults differ", sentence(undefined) !== "Under 10 Dead wood, until 20 → Gather by hand", true);
