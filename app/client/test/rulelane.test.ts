// A ruled lane's section of the Rules tab (CONTRACT.txt, "A lane run by rules"): the rules that tap a card on that
// lane, under the lane's label, in view.orders order, an always rule worded as ui.rule.always, a passed-over one-off
// still listed; a new rule on that lane placed just before the lane's first always rule; "outranked by" worded from
// orders[LaneBar.order] (with the always words when that is an always rule). And the words for a rule or a queue entry
// that answers an offer (CONTRACT.txt, "Offers").
import { fakeDocument, type FakeEl, install } from "./fake-dom";
import { testContext } from "./context";
import { fixtureContent, Q } from "../fixtures/content";
import { dayTwoStep } from "../fixtures/daytwo";
import type { Order, View } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { actionWords, ruleDecisions } from "../src/game/orders";
import { RulesTab } from "../src/ui/rules";
import { whyOff } from "../src/ui/rulewhy";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

function mounted(root: HTMLElement): FakeEl {
  document.body.replaceChildren(root);
  const node = fakeDocument.body.firstElementChild;
  if (!node) throw new Error("nothing mounted");
  return node;
}

const catalog = new Catalog(fixtureContent);
const ruled = dayTwoStep("ruled", 100).view;   // hands 0, 1; fetch always (passed over) 2, haul when low 3, chop always 4 (running), haul always 5

{  // the lane's section: its label, then its rules in order, the always ones in the always words, the passed-over one kept
  const { ctx } = testContext();
  const tab = new RulesTab(ctx);
  const root = mounted(tab.root);
  tab.update(ruled);
  const sections = root.querySelectorAll(".rules-lane");
  const helper = sections.find((s) => s.querySelector(".panel-heading")?.textContent === "Helper");
  if (!helper) throw new Error("no section under the lane's label");
  expect("its rules, in view.orders order", helper.querySelectorAll(".rules-row").map((r) => r.querySelector(".rule-cond-text")?.textContent),
    ["Fetch once, always", "Under 3 Dead wood, until 8", "Chop logs, always", "Haul water, always"]);
  expect("the passed-over one-off says so", helper.querySelectorAll(".rule-why").map((n) => n.textContent)[0], "passed over · a task it runs is done");
  expect("the one outranked says by what", helper.querySelectorAll(".rule-why").map((n) => n.textContent).at(-1), "outranked by Chop logs, always");
}

{  // outranked by a store rule the lane runs now: that rule's condition
  const low: View = { ...ruled, lanes: ruled.lanes.map((l) => (l.lane === "helper" ? { ...l, running_card: "haul", order: 3 } : l)),
    order_states: ruled.order_states.map((s, i) => (i === 3 ? "on" : i === 4 ? "outranked" : s)) };
  expect("outranked by the store rule's words", whyOff(catalog, low, 4, 100), "outranked by Under 3 Dead wood, until 8");
}

{  // a store rule holding the hands whose release cannot be reached says which store is out; unfed is a write-time line only
  const hands = ruled.orders.findIndex((o) => o.then.kind === "switch_mix" && o.when.kind === "at_most");
  if (hands < 0) throw new Error("control: the fixture has an at_most mix rule");
  const dry = (holding: boolean): View => ({ ...ruled, order_states: ruled.order_states.map((s, i) => (i === hands ? "on" : s)),
    order_dry: ruled.orders.map((_, i) => (i === hands ? { store: "wood", holding } : null)) });
  expect("holding: can't reach", whyOff(catalog, dry(true), hands, 100), "can't reach 20: out of Dead wood");
  expect("not holding: the row stays quiet", whyOff(catalog, dry(false), hands, 100), null);
}

{  // a new rule on the lane goes just before its first always rule; a hands rule still goes last
  const rule: Order = { when: { kind: "at_least", watched: { kind: "store_value", store: "wood" }, value: 20 * Q, release: 10 * Q }, then: { kind: "tap_card", card: "chop" } };
  const sent = ruleDecisions(ruled, catalog, null, rule)[0];
  const orders = sent?.kind === "set_orders" ? sent.orders : [];
  expect("placed before the lane's first always rule", orders.findIndex((o) => JSON.stringify(o) === JSON.stringify(rule)), 2);
  expect("nothing else moved", orders.filter((o) => o !== rule), ruled.orders);
  const bench: Order = { ...rule, then: { kind: "tap_card", card: "shelter" } };
  const other = ruleDecisions(ruled, catalog, null, bench)[0];
  expect("a rule on a lane not ruled: at the end", other?.kind === "set_orders" ? other.orders.at(-1) : null, bench);
}

{  // a rule or a queue entry that answers an offer has words of its own, in the Rules tab and in Next
  expect("an answer's words", actionWords(catalog, { kind: "answer_offer", offer: "ask", answer: "go" }), "Answer: Go now");
  const answers: View = { ...ruled, queue: [{ verb: { kind: "answer_offer", offer: "ask", answer: "wait" }, until: { kind: "at_least", watched: { kind: "card_count", card: "haul" }, value: 1, release: 1 } }] };
  const { ctx } = testContext();
  const tab = new RulesTab(ctx);
  const root = mounted(tab.root);
  tab.update(answers);
  expect("Next names the answer", root.querySelector(".next-row .rule-action")?.textContent, "Answer: Wait");
}
