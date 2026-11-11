// A Next entry whose card a lane is already running (CONTRACT.txt, "Ruled lanes", an answer's one-off): it stays in
// view.queue until the card completes, so Next draws it as under way, with no Remove, since removing it would not stop
// the work. An entry whose card is not running keeps its Remove.
import { install } from "./fake-dom";
import { testContext } from "./context";
import { fixtureStep } from "../fixtures/steps";
import type { QueueEntry, View } from "../src/api/types";
import { nextRows } from "../src/ui/nextlist";
import { StintPlan } from "../src/ui/stintplan";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const ended = fixtureStep("restoffer", 100).view;
const tapOf = (card: string, n: number): QueueEntry => ({
  verb: { kind: "tap_card", card }, until: { kind: "at_least", watched: { kind: "card_count", card }, value: n, release: n },
});
const queue = [tapOf("larder", 1), tapOf("lean_to", 2)];
const running: View = { ...ended, queue,
  lanes: ended.lanes.map((l) => (l.lane === "hands" ? { ...l, running_card: "larder", completes_at: 400 } : l)) };

{  // control: with the hands free, both entries offer Remove
  const { ctx } = testContext();
  const rows = nextRows(ctx, { ...ended, queue }, new StintPlan(ctx, () => {}));
  expect("both removable", rows.map((r) => r.textContent), ["Next", "LarderRemove", "Lean-toRemove"]);
}

{  // the head's card is on the hands: it reads under way and has no Remove; the entry behind it keeps its own
  const { ctx } = testContext();
  const rows = nextRows(ctx, running, new StintPlan(ctx, () => {}));
  expect("under way, no Remove", rows.map((r) => r.textContent), ["Next", "Larderunder way", "Lean-toRemove"]);
  expect("no button on the running entry", rows[1]!.querySelectorAll("button").length, 0);
}
