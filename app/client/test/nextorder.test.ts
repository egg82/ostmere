// Next's entries are put in the player's order (ui/nextorder.ts, game/queue.ts "moveQueued"): the ≡ in a row's
// handle gap, dragged or moved by the arrow keys, sends one set_queue holding the same entries in the new order.
// An entry a lane already runs has no ≡, is not a drop place, and keeps its index.
import { fakeDocument, type FakeEl, FakeEvent, install, pointer } from "./fake-dom";
import { testContext } from "./context";
import { fixtureStep } from "../fixtures/steps";
import type { Decision, QueueEntry, View } from "../src/api/types";
import { RulesTab } from "../src/ui/rules";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const ended = fixtureStep("restoffer", 100).view;
const tapOf = (card: string, n: number): QueueEntry => ({
  verb: { kind: "tap_card", card }, until: { kind: "at_least", watched: { kind: "card_count", card }, value: n, release: n, value_of_cap: false, release_of_cap: false },
});
const [A, B, C] = [tapOf("larder", 1), tapOf("lean_to", 2), tapOf("larder", 3)] as [QueueEntry, QueueEntry, QueueEntry];
const withQueue = (queue: QueueEntry[], running: string | null = null): View => ({
  ...ended, queue, lanes: ended.lanes.map((l) => (l.lane === "hands" ? { ...l, running_card: running, completes_at: running ? 400 : null } : l)),
});
const queueOf = (d: Decision | undefined): QueueEntry[] | null => (d?.kind === "set_queue" ? d.entries : null);

function rig(view: View): { root: FakeEl; decided: Decision[]; handles: () => FakeEl[]; rows: () => FakeEl[] } {
  const { ctx, got } = testContext();
  const tab = new RulesTab(ctx);
  document.body.replaceChildren(tab.root);
  const root = fakeDocument.body.firstElementChild as FakeEl;
  tab.update(view);
  const rows = (): FakeEl[] => root.querySelectorAll(".next-row");
  rows().forEach((row, i) => { row.rect = { left: 0, top: i * 50, width: 300, height: 48, right: 300, bottom: i * 50 + 48 }; });
  return { root, decided: got.decided, handles: () => root.querySelectorAll(".next-row .rule-handle"), rows };
}

{  // the keyboard: ArrowDown on the first entry's ≡ swaps it with the second; ArrowUp on the first goes nowhere
  const r = rig(withQueue([A, B]));
  expect("each entry has a ≡", r.handles().length, 2);
  r.handles()[0]!.dispatchEvent(new FakeEvent("keydown", { key: "ArrowUp" }));
  expect("up from the top sends nothing", r.decided.length, 0);
  r.handles()[0]!.dispatchEvent(new FakeEvent("keydown", { key: "ArrowDown" }));
  expect("ArrowDown sends the entries swapped, each unchanged", queueOf(r.decided[0]), [B, A]);
}

{  // a drag: the ghost lifts past the threshold, the drop mark shows where it lands, and letting go sends the order
  const r = rig(withQueue([A, B, C]));
  const handle = r.handles()[0]!;
  handle.dispatchEvent(pointer("pointerdown", 10, 10));
  handle.dispatchEvent(pointer("pointermove", 10, 120));
  expect("mid-drag: a ghost follows", fakeDocument.querySelectorAll(".drag-ghost").length, 1);
  expect("mid-drag: the drop mark is after the last", r.rows().map((n) => n.classList.contains("drop-after")), [false, false, true]);
  handle.dispatchEvent(pointer("pointerup", 10, 120));
  expect("the drop sends the first entry last", queueOf(r.decided[0]), [B, C, A]);
  expect("the ghost is gone", fakeDocument.querySelectorAll(".drag-ghost").length, 0);
}

{  // an entry a lane runs stays put: no ≡ on it, and the others move among themselves around it
  const r = rig(withQueue([A, B, tapOf("stool", 1)], "larder"));   // A taps the card the hands run
  expect("the entry under way has no ≡, the others do", r.rows().map((n) => n.querySelectorAll(".rule-handle").length), [0, 1, 1]);
  const lone = rig(withQueue([A, B], "larder"));
  expect("one movable entry has nothing to move past", lone.handles().length, 0);
  const mid = rig(withQueue([B, A, tapOf("stool", 1)], "larder"));
  expect("the entries around the one under way", mid.handles().length, 2);
  mid.handles()[0]!.dispatchEvent(new FakeEvent("keydown", { key: "ArrowDown" }));
  expect("the one under way keeps its place", queueOf(mid.decided[0])?.map((e) => (e.verb.kind === "tap_card" ? e.verb.card : e.verb.kind)), ["stool", "larder", "lean_to"]);
}
