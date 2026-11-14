// A lane run by rules (CONTRACT.txt, "A lane run by rules"; docs/design/opening-screen.md, the hands strip's lane
// rows): a row under the hands strip per ruled lane, its label (the last later label whose unlock is held), what it
// does (the running card, or idle) and Change, which opens the rule editor's simple view scoped to that lane on
// orders[LaneBar.order], else the lane's first always rule not passed over, else a new always rule. Saving there
// changes that rule's tap_card in place, or appends a new always rule.
import { fakeDocument, type FakeEl, install } from "./fake-dom";
import { testContext } from "./context";
import { dayTwoStep, LANE_RULES } from "../fixtures/daytwo";
import type { Decision, Order, View } from "../src/api/types";
import { LaneRows } from "../src/ui/lanerows";
import { RulesTab } from "../src/ui/rules";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

function mounted(root: HTMLElement): FakeEl {
  document.body.replaceChildren(root);
  const node = fakeDocument.body.firstElementChild;
  if (!node) throw new Error("nothing mounted");
  return node;
}

const ruled = dayTwoStep("ruled", 100).view;   // hands rules 0, 1; then fetch (passed over), haul when low, chop always (running), haul always
const offered = dayTwoStep("offered", 100).view;   // the same rules, the lane free, `yard` open
const CHOP = 4;
const sentOrders = (d: Decision | undefined): Order[] | null => (d?.kind === "set_orders" ? d.orders : null);

{  // the row: the lane's label, what it does, its Change; nothing for a lane that is not ruled
  const { ctx } = testContext();
  const rows = new LaneRows(ctx);
  const root = mounted(rows.root);
  rows.update(ruled);
  expect("one row, for the ruled lane only", root.querySelectorAll(".lane-row").length, 1);
  expect("its label", root.querySelector(".lane-row .town-name")?.textContent, "Helper");
  expect("what it does", root.querySelector(".lane-row .town-doing")?.textContent, "Chop logs");
  rows.update(offered);
  expect("a later label once its unlock is held", root.querySelector(".lane-row .town-name")?.textContent, "Helper, settled");
  expect("free: idle", root.querySelector(".lane-row .town-doing")?.textContent, "idle");
}

/** What Change asks for on this view. */
function changeOf(view: View): unknown {
  const { ctx, got } = testContext();
  const rows = new LaneRows(ctx);
  const root = mounted(rows.root);
  rows.update(view);
  root.querySelector(".lane-change")?.click();
  return got.opened[0];
}

expect("Change: the rule the lane runs now", changeOf(ruled), { lane: "helper", rule: CHOP });
expect("Change, the lane free: its first always rule not passed over", changeOf(offered), { lane: "helper", rule: CHOP });
const lowRuns = { ...ruled, lanes: ruled.lanes.map((l) => (l.lane === "helper" ? { ...l, running_card: "haul", order: 3 } : l)) };
expect("Change: a store rule the lane runs now", changeOf(lowRuns), { lane: "helper", rule: 3 });
const noAlways = { ...offered, orders: offered.orders.slice(0, 4), orders_on: offered.orders_on.slice(0, 4), order_states: offered.order_states.slice(0, 4) };
expect("Change, no always rule left to act: a new one", changeOf(noAlways), { lane: "helper", rule: null });

/** The Rules tab opened on the lane's simple view; pick `card`, Save; what was sent. */
function saved(view: View, rule: number | null, card: string): { orders: Order[] | null; tasks: string[] } {
  const { ctx, got } = testContext();
  const tab = new RulesTab(ctx);
  const root = mounted(tab.root);
  tab.update(view);
  tab.open(view, { lane: "helper", rule });
  const tasks = root.querySelectorAll(".cond-task").map((b) => b.dataset.card ?? "");
  root.querySelector(`.cond-task[data-card="${card}"]`)?.click();
  root.querySelector(".cond-actions .primary")?.click();
  return { orders: sentOrders(got.decided[0]), tasks };
}

{  // the simple view offers the lane's own cards; Save changes the rule's task in place
  const got = saved(ruled, CHOP, "haul");
  expect("the lane's tasks, and only those", got.tasks, ["chop", "haul"]);
  expect("its tap_card changed in place", got.orders, ruled.orders.map((o, i) => (i === CHOP ? { ...o, then: { kind: "tap_card", card: "haul" } } : o)));
  const low = saved(ruled, 3, "chop");
  expect("a store rule keeps its condition", low.orders?.[3], { ...LANE_RULES[1], then: { kind: "tap_card", card: "chop" } });
  const fresh = saved(noAlways, null, "chop");
  expect("a new always rule, appended", fresh.orders, [...noAlways.orders, { when: { kind: "after_time", at: 0 }, then: { kind: "tap_card", card: "chop" } }]);
}
