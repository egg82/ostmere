// Why a rule is off (docs/design/opening-screen.md, "The Rules tab"; ui/rulewhy.ts): the quiet line under a rule the
// server says is off (View.order_states), in the ledger's grammar. A waiting store rule names its level and the store's
// amount now, which moves with the clock; an outranked one names the rule with the hands; a passed-over one says so; a
// rule that is on, and a waiting chip's rule, carry no line. Task rules on a side lane get the same line.
import { install } from "./fake-dom";
import { fixtureStep } from "../fixtures/steps";
import { Q } from "../fixtures/content";
import type { LedgerLine, Order, OrderState, View } from "../src/api/types";
import { RulesTab } from "../src/ui/rules";
import { testContext } from "./context";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const base = fixtureStep("rulestab", 100).view;   // wood (0), warmth (1), tired (2, its mix runs), bench task (3)
const at = base.at;
/** The store holding `items` at the view's time, changing by `perSecond` items a second. */
const holding = (line: LedgerLine, items: number, perSecond = 0): LedgerLine =>
  ({ ...line, segment: { start: at, start_value: items * Q, rate: perSecond * Q, limit: null } });
const amounts = (view: View, items: Record<string, [number, number?]>): View =>
  ({ ...view, ledger: view.ledger.map((l) => (items[l.store] ? holding(l, ...items[l.store]!) : l)) });

function draw(view: View): { tab: RulesTab; root: HTMLElement; why: () => Record<string, string | null> } {
  const tab = new RulesTab(testContext().ctx);
  document.body.replaceChildren(tab.root);
  tab.update(view);
  const why = () => Object.fromEntries([...tab.root.querySelectorAll<HTMLElement>(".rule-why")].map((n) => [n.dataset.rule!, n.textContent]));
  return { tab, root: tab.root, why };
}

const states = (...s: OrderState[]): OrderState[] => s;

// Waiting store rules: their level and what the store holds now; the rule that is on and the task rule that is on, none.
{
  const view = amounts({ ...base, order_states: states("waiting", "waiting", "on", "on") }, { wood: [14], warmth: [52] });
  const { why } = draw(view);
  expect("waiting rules say what they need and what there is", why(), { 0: "needs under 10 Dead wood · now 14", 1: "needs under 40 Warmth · now 52" });
}

// The amount moves with the clock between steps: the line follows it on the frame.
{
  const view = amounts({ ...base, order_states: states("waiting", "on", "on", "on") }, { wood: [14, -1] });
  const { tab, why } = draw(view);
  tab.tick(at + 3);
  expect("now is sampled at the frame's time", why()["0"], "needs under 10 Dead wood · now 11");
}

// An "n or more" rule words its level the same way.
{
  const reaches: Order = { when: { kind: "at_least", watched: { kind: "store_value", store: "wood" }, value: 30 * Q, release: 12 * Q }, then: base.orders[0]!.then };
  const view = amounts({ ...base, orders: [reaches, ...base.orders.slice(1)], order_states: states("waiting", "on", "on", "on") }, { wood: [14] });
  expect("a reaches rule", draw(view).why()["0"], "needs 30 or more Dead wood · now 14");
}

// Outranked: its condition holds, and the rule whose mix runs (mix_order) is named by its condition.
{
  const view = { ...base, order_states: states("outranked", "waiting", "on", "on") };
  expect("outranked by the rule with the hands", draw(amounts(view, { warmth: [52] })).why()["0"], "outranked by While tired");
}

// Passed over: its mix is greyed, whatever its condition; a waiting chip's rule shows no number and so no line, even
// with its store's line in the view.
{
  const energy = { ...base.ledger.find((l) => l.store === "wood")!, store: "energy" };
  const view = amounts({ ...base, ledger: [...base.ledger, energy], mix_order: null, order_states: states("passed_over", "on", "waiting", "on") }, { energy: [9] });
  expect("passed over, and no line for the chip's rule", draw(view).why(), { 0: "passed over · a task it runs is done" });
}

// A side lane's task rule that is waiting carries its line under its own row.
{
  const view = amounts({ ...base, order_states: states("on", "on", "on", "waiting") }, { stone: [5] });
  const { root, why } = draw(view);
  expect("the task rule's why", why(), { 3: "needs under 2 Flint · now 5" });
  expect("drawn in its lane", root.querySelectorAll(".rules-lane .rule-why").length, 1);
}

// A step that changes only where the rules stand redraws the lines.
{
  const { tab, why } = draw(amounts({ ...base, order_states: states("on", "on", "on", "on") }, { wood: [14] }));
  tab.update(amounts({ ...base, order_states: states("waiting", "on", "on", "on") }, { wood: [14] }));
  expect("a new state draws its line", why(), { 0: "needs under 10 Dead wood · now 14" });
}
