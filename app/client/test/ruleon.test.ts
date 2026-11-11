// The fixture's rule-lesson path (fixtures/steps.ts "ruleoffer", then "ruleon" once a rule is set) reaches the rule
// lesson's last step: a rule at work shows the mark that step points at (ui/rules.ts), which the lesson's own target finds.
import { install } from "./fake-dom";
import { testContext } from "./context";
import { fixtureStep } from "../fixtures/steps";
import { FIRST_RULE, LESSONS } from "../src/game/lessons";
import { RulesTab } from "../src/ui/rules";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const lesson = LESSONS.find((l) => l.id === FIRST_RULE);
const last = lesson?.steps.at(-1);
if (!last) throw new Error("no rule lesson");
const offer = fixtureStep("ruleoffer", 100).view;
expect("the offer's phase has no rules yet", offer.orders.length, 0);

const set = fixtureStep("restrule", 100).view.orders.slice(0, 1);   // any rule, as the page would send it
const on = fixtureStep("ruleon", 100, { orders: set }).view;
expect("the rule set is at work", on.orders_on, [true]);

const { ctx } = testContext();
ctx.keeps.keepRuleSeen();
const tab = new RulesTab(ctx);
document.body.replaceChildren(tab.root);
tab.update(on);
tab.open(on, null);
expect("the last step's target finds the rule at work", tab.root.querySelectorAll(last.target({ task: "gather" })).length, 1);
