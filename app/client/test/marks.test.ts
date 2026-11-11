// The new-dot rules: a new task gets a dot; touching it, joining it to a mix, or it being at work clears it; plain
// text never gets one (markNew is only ever called for a control).
import { fixtureStep } from "../fixtures/steps";
import { inUse, NewMarks } from "../src/game/marks";

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const idle = fixtureStep("firstmix", 100).view;
const running = fixtureStep("mid", 100).view;
const inMix = running.cards.filter((c) => c.run !== null).map((c) => c.card);
const heldBy = running.mixes.flatMap((m) => m.components.flatMap((c) => (c.kind === "card_share" ? [c.card] : [])));
if (inMix.length === 0 || heldBy.length === 0) throw new Error("fixture mid should have a running mix");

expect("nothing at work before a mix", [...inUse(idle)], []);

const fresh = new NewMarks();
fresh.add("card-a");
expect("a new task has a dot", fresh.has("card-a"), true);
fresh.sync(idle);
expect("a card not at work keeps its dot", fresh.has("card-a"), true);
fresh.clear("card-a");
expect("touching or joining clears it", fresh.has("card-a"), false);

for (const card of new Set([...inMix, ...heldBy])) {
  const m = new NewMarks();
  m.add(card);
  m.sync(running);
  expect(`${card} in a running mix has no dot`, m.has(card), false);
}

const ruled = { ...idle, orders: [{ ...fixtureStep("covered", 100).view.orders[0]! }] };
const named = ruled.orders.flatMap((o) => (o.then.kind === "tap_card" ? [o.then.card] : []));
for (const card of named) {
  const m = new NewMarks();
  m.add(card);
  m.sync(ruled);
  expect(`${card} named by a rule has no dot`, m.has(card), false);
}
