// OrderFires against the fixture's covered view with a task rule on "gather": the hands start it with no tap (the rule,
// while its condition holds) or with one (the player's); a queue entry, or a rule that is not on, is not the rule.
import { fixtureContent } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { LaneBar, View } from "../src/api/types";
import { OrderFires } from "../src/ui/fires";

const card = fixtureContent.order_cards[0]!;
const base: View = { ...fixtureStep("covered", 100).view, orders: [{ when: card.when, then: card.then }], orders_on: [true] };
const idle: LaneBar = { lane: "hands", running_card: null, completes_at: null, order: null };
const running: LaneBar = { ...idle, running_card: "gather" };
const before: View = { ...base, lanes: [idle] };
const after: View = { ...base, lanes: [running] };

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

if (card.then.kind !== "tap_card") throw new Error("fixture card should tap a card");

const a = new OrderFires();
a.observe(after, before);
expect("order start", a.fresh, ["gather"]);
expect("order start running", [...a.running], ["gather"]);
a.observe(after, after);
expect("still running keeps the marker", [...a.running], ["gather"]);
a.observe(before, after);
expect("run ended", [...a.running], []);

const b = new OrderFires();
b.tap("gather");
b.observe(after, before);
expect("a tap is not an order", b.fresh, []);

const c = new OrderFires();
c.observe(after, { ...before, queue: [{ verb: card.then, until: card.when }] });
expect("a queued start is not an order", c.fresh, []);

const d = new OrderFires();
d.observe({ ...after, orders: [] }, before);
expect("no order, no marker", d.fresh, []);

const e = new OrderFires();
e.observe({ ...after, orders_on: [false] }, before);
expect("a rule whose condition does not hold did not start it", e.fresh, []);
