// A rule the game removed, in the Rules tab's Lately block (CONTRACT.txt, "RULE RUNS"): an entry with `ended` set is
// drawn, in the server's order, as one line wording the rule and why it ended: the season's turn, or its person leaving
// (the name of the lane of the card the rule taps). It matches no rule in the view and offers nothing to edit.
import { install } from "./fake-dom";
import { fixtureStep } from "../fixtures/steps";
import { Q } from "../fixtures/content";
import type { Order, RuleRun } from "../src/api/types";
import { RulesTab } from "../src/ui/rules";
import { testContext } from "./context";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const base = fixtureStep("rulestab", 100).view;
const at = base.at;
const wood = base.orders[0] as Order;

function lately(runs: RuleRun[]): string[] {
  const tab = new RulesTab({ ...testContext().ctx, ruleRuns: () => runs });
  document.body.replaceChildren(tab.root);
  tab.update(base);
  return [...tab.root.querySelectorAll<HTMLElement>(".lately-line")].map((n) => n.textContent ?? "");
}

const tapping = (card: string): Order => ({ ...wood, then: { kind: "tap_card", card } });
const ended = (card: string, why: "season" | "left"): RuleRun =>
  ({ order: tapping(card), starts: 2, on_at: at - 7200, on_level: 2 * Q, off_at: at - 5, off_level: 20 * Q, ended: why, made: [] });

expect("a season's turn", lately([ended("gather", "season")]), ["Lately", "Under 10 Dead wood, until 20 → Gather by hand · ended with the season"]);
expect("a person leaving, named", lately([ended("hew", "left")]), ["Lately", "Under 10 Dead wood, until 20 → Hew stone · ended when Mason left"]);
expect("in the server's order, beside a live rule", lately([ended("hew", "left"), { order: wood, starts: 1, on_at: at - 60, on_level: Q, off_at: null, off_level: null, ended: null, made: [] }]).length, 4);
