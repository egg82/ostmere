// The Rules tab's mix-slot picker offers only the mixes a player rule may switch to (contract/the-towns-mix.txt, "The town's mix"; docs/decisions/principles.md,
// "Every option offered works as worded"): a town mix is set by a rule on the town, so the server refuses a player's switch to one.
import { fakeDocument, type FakeEl, install } from "./fake-dom";
import { testContext } from "./context";
import { fixtureStep } from "../fixtures/steps";
import type { Mix, View } from "../src/api/types";
import { RulesTab } from "../src/ui/rules/rules";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const base = fixtureStep("rulestab", 100).view;
const gameMade: Mix = { id: "town:main", components: [] };   // the one the game made: a town mix holding no card
const view: View = { ...base, mixes: [...base.mixes, gameMade] };

function picked(slot: string): string[] {
  const { ctx } = testContext();
  const tab = new RulesTab(ctx);
  document.body.replaceChildren(tab.root);
  tab.update(view);
  const root = fakeDocument.body.firstElementChild as FakeEl;
  root.querySelectorAll(slot)[slot.includes("otherwise") ? 0 : 1]?.click();
  return root.querySelectorAll(".rule-picker .selector-run").map((b) => b.querySelector(".selector-name")?.textContent ?? "");
}

expect("the game's own mix is in the view", view.mixes.some((m) => m.id === "town:main"), true);
expect("a hands rule's picker offers the hands' mixes alone", picked(".rule-slot"), base.mixes.map((m) => m.id));
expect("Otherwise offers them too, no town mix", picked(".rules-row.otherwise .rule-slot"), base.mixes.map((m) => m.id));
