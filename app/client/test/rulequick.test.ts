// The condition editor's quick add (docs/design/opening-screen.md, "The condition editor"): with a task chosen, When
// offers the stores relevant to it (game/relevant.ts), what it makes then what it takes, and More options every store
// with those first.
import { install } from "./fake-dom";
import { testContext } from "./context";
import { dayOneStep } from "../fixtures/dayone";
import type { Decision, View } from "../src/api/types";
import { RulesTab } from "../src/ui/rules";

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
