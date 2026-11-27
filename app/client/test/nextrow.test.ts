// Next as a row among the hands' rules (game/nextrow.ts, ui/rules.ts; contract/endpoints.txt, "Next's row"): the row is drawn
// where the rules' below_next puts it, moves like a rule (its ≡ menu, arrow keys), and a rule moved past it changes
// side; every set_orders keeps the rules under Next a run to the end. A rule under Next that waits says so.
import { install } from "./fake-dom";
import { fixtureStep } from "../fixtures/steps";
import type { Decision, QueueEntry, RuleRun, View } from "../src/api/types";
import { NEXT, nextItems, placeItems, reorderedItems, steppedItems, unplacedKey } from "../src/game/nextrow";
import { moveRule, setRule } from "../src/game/orders";
import { RulesTab } from "../src/ui/rules/rules";
import { shownRuns } from "../src/ui/rules/rulelately";
import { testContext } from "./context";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const base = fixtureStep("rulestab", 100).view;   // hands rules wood (0), warmth (1), tired (2); the bench task rule (3)
const under = (view: View, from: number): View => ({ ...view, orders: view.orders.map((o, i) => ({ ...o, below_next: i >= from })) });
const flags = (d: Decision | null): boolean[] | null => (d?.kind === "set_orders" ? d.orders.map((o) => o.below_next) : null);
const whens = (d: Decision | null): string[] => (d?.kind === "set_orders" ? d.orders.map((o) => JSON.stringify(o.when)) : []);
const hands = [0, 1, 2];
const larder: QueueEntry = { verb: { kind: "tap_card", card: "larder" }, until: { kind: "at_least", watched: { kind: "card_count", card: "larder" }, value: 1, release: 1, value_of_cap: false, release_of_cap: false } };

// Where the row sits: before the first rule under it, else at the bottom.
expect("at the bottom", nextItems(base, hands), [0, 1, 2, NEXT]);
expect("between warmth and tired", nextItems(under(base, 2), hands), [0, 1, NEXT, 2]);

// Next one place up: tired goes under it, the bench task rule after it too (a run to the end), nothing moves slot.
{
  const d = placeItems(base, hands, steppedItems(nextItems(base, hands), NEXT, -1)!);
  expect("Next up past tired", flags(d), [false, false, true, true]);
  expect("rules keep their slots", whens(d), base.orders.map((o) => JSON.stringify(o.when)));
}

// A rule moved down past Next keeps its slot and goes under it; moved to the bottom, the rule under it moves up a slot.
{
  const view = under(base, 2);
  const items = nextItems(view, hands);
  expect("warmth down past Next", flags(placeItems(view, hands, steppedItems(items, 1, 1)!)), [false, true, true, true]);
  const d = placeItems(view, hands, reorderedItems(items, 1, 2)!);
  expect("warmth to the bottom: tired takes its slot, above nothing changes", flags(d), [false, true, true, true]);
  expect("warmth now third", whens(d)[2], JSON.stringify(view.orders[1]!.when));
  expect("Next at the top of the list cannot go up", steppedItems([NEXT, 0], NEXT, -1), null);
}

// An edited rule keeps its side of Next, whatever the editor built.
expect("edited in place, still under Next", flags(setRule(under(base, 1), 1, { ...base.orders[1]!, below_next: false })), [false, true, true, true]);

// A plain reorder of two rules (moveRule, the town's way) leaves Next on the slot boundary it had.
expect("swap across the line keeps the line", flags(moveRule(under(base, 1), 0, 1, hands)), [false, true, true, true]);

// The Rules tab draws the row between warmth and tired, and its menu moves it down a place.
{
  const view: View = { ...under(base, 2), queue: [larder] };
  const { ctx, got } = testContext();
  const tab = new RulesTab(ctx);
  document.body.replaceChildren(tab.root);
  tab.update(view);
  const rows = [...tab.root.querySelectorAll<HTMLElement>(".rules-list > .rules-row")].map((r) => r.dataset.rule ?? r.className);
  expect("Next's row between warmth and tired", rows.slice(0, 5), ["0", "1", String(NEXT), "rules-row next-row", "2"]);
  tab.root.querySelector<HTMLElement>(`.rule-handle[data-rule="${NEXT}"]`)!.click();
  const down = [...tab.root.querySelectorAll<HTMLButtonElement>(".rule-menu button")];
  expect("Move up, Move down, no Remove", down.map((b) => b.textContent), ["Move up", "Move down"]);
  down[1]!.click();
  expect("down past tired: Next back at the bottom", flags(got.decided[0] ?? null), [false, false, false, false]);
}

// A rule under Next while the queue has the hands says what the queue runs.
{
  const view: View = { ...under(base, 2), queue: [larder], order_states: ["waiting", "waiting", "behind_next", "on"] };
  const tab = new RulesTab(testContext().ctx);
  document.body.replaceChildren(tab.root);
  tab.update(view);
  const why = tab.root.querySelector<HTMLElement>('.rule-why[data-rule="2"]')?.textContent;
  expect("names Next and its task", why, "outranked by Next · Larder");
}

// Lately: a rule_run's order is served without the row, and still finds its rule under Next.
{
  const view = under(base, 0);
  const run: RuleRun = { order: { ...view.orders[2]!, below_next: false }, starts: 1, on_at: 5, on_level: null, off_at: null, off_level: null, ended: null, made: [] };
  expect("matched unplaced", shownRuns(view, [run]).length, 1);
  expect("the key drops only the row", unplacedKey(view.orders[2]!) === unplacedKey({ ...view.orders[2]!, below_next: false }), true);
}
