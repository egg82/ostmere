// Until done (contract/until-done.txt, "UNTIL DONE"; game/cards/untildone.ts, ui/cards/whenready.ts): a staged card a tap started can be run
// on to its cap from its own face while it runs. On the hands it becomes the queue entry it would have been had it
// been queued first (tap until its cap, at Next's front, or a running When ready entry held on to the cap); on a
// person's lane an always rule where a new lane rule goes. Not offered on the last stage, on a rule's tap, or idle.
import { fakeDocument, type FakeEl, install } from "./fake-dom";
import { testContext } from "./context";
import { fixtureContent } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import { townStep } from "../fixtures/town";
import type { Card, Order, QueueEntry, View } from "../src/api/types";
import { Catalog } from "../src/game/page/catalog";
import { tapUntil } from "../src/game/mixes/queue";
import { untilDone } from "../src/game/cards/untildone";
import { Cards } from "../src/ui/cards/cards";
import { NewMarks } from "../src/game/lessons/marks";
import { pageRig } from "./personrig";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const catalog = new Catalog(fixtureContent);
const ended = fixtureStep("restoffer", 100).view;
const lean: Card = {
  card: "lean_to", completions: 0, cap: 4, bar: { start: 100, start_value: 0, rate: 0, limit: null }, bar_total: 300, by: null, completes_at: null,
  share_bp: 0, run: null, cuts_in: false, spent_store: null, full_store: null, gained: [], crew: null, tap_s: 300, speed: 1, blocker: null, needs: [],
};
/** The hands running `card` (a tap: order null, or a rule's `order`), at `completions` of `cap`. */
function running(card: Card, completions: number, cap: number | null, queue: QueueEntry[] = [], order: number | null = null): View {
  const ends = ended.at + 300;
  const c: Card = { ...card, completions, cap, by: "tap", completes_at: ends, blocker: null };
  return {
    ...ended, queue, cards: [...ended.cards, c],
    lanes: ended.lanes.map((l) => (l.lane === "hands" ? { ...l, running_card: card.card, completes_at: ends, order } : l)),
  };
}
const other = tapUntil("larder", 1);

// The hands: what it sends.
expect("a hand tap: the entry until the cap, at Next's front", untilDone(catalog, running(lean, 1, 4, [other]), "lean_to"),
  { kind: "set_queue", entries: [tapUntil("lean_to", 4), other] });
expect("a running When ready entry: held on to the cap, in its place", untilDone(catalog, running(lean, 1, 4, [other, tapUntil("lean_to", 2)]), "lean_to"),
  { kind: "set_queue", entries: [other, tapUntil("lean_to", 4)] });
expect("already until done: nothing", untilDone(catalog, running(lean, 1, 4, [tapUntil("lean_to", 4)]), "lean_to"), null);
expect("the last stage running: nothing", untilDone(catalog, running(lean, 3, 4), "lean_to"), null);
expect("work done again and again: nothing", untilDone(catalog, running(lean, 3, null), "lean_to"), null);
expect("a rule's tap: nothing", untilDone(catalog, running(lean, 1, 4, [], 0), "lean_to"), null);
expect("before the end: nothing", untilDone(catalog, { ...running(lean, 1, 4), ended_at: null }, "lean_to"), null);
expect("not running: nothing", untilDone(catalog, { ...ended, cards: [...ended.cards, { ...lean, completions: 1 }] }, "lean_to"), null);
const full = Array.from({ length: fixtureContent.limits.max_queue }, (_, i) => tapUntil(`x${i}`, 1));
expect("Next full: nothing", untilDone(catalog, running(lean, 1, 4, full), "lean_to"), null);

// The hands: the card panel's face shows it on the running card, and a tap sends it.
{
  const { ctx, got } = testContext();
  const cards = new Cards(ctx, new NewMarks());
  document.body.replaceChildren(cards.root);
  const view = running(lean, 1, 4);
  cards.update(view, null);
  const node = (fakeDocument.body.firstElementChild as FakeEl).querySelectorAll(".card").find((n) => n.dataset.card === "lean_to")!;
  const button = node.querySelector(".card-ready") as FakeEl;
  expect("on the running tapped card: Until done, on", [button.hidden, button.disabled, button.textContent], [false, false, "Until done"]);
  button.click();
  expect("its tap sends the entry", got.decided, [{ kind: "set_queue", entries: [tapUntil("lean_to", 4)] }]);
  cards.update({ ...view, queue: [tapUntil("lean_to", 4)] }, null);
  expect("then the quiet mark", [button.hidden, button.disabled, button.textContent], [false, true, "in Next"]);
  cards.update(running(lean, 3, 4), null);
  expect("the last stage: hidden", button.hidden, true);
}

// A person's lane: an always rule where a new lane rule goes; the face on their page offers it while their one-off runs.
{
  const both = townStep("town").view;
  const capped = { ...both, cards: both.cards.map((c) => (c.card === "carve" ? { ...c, cap: 3, share_bp: 0 } : c)),
    mixes: both.mixes.map((m) => ({ ...m, components: m.components.filter((c) => c.kind !== "card_share" || c.card !== "carve") })) };
  const ends = capped.at + 600;
  const held: View = {
    ...capped,
    lanes: capped.lanes.map((l) => (l.lane === "mason" ? { ...l, running_card: "carve", completes_at: ends, order: null } : l)),
    cards: capped.cards.map((c) => (c.card === "carve" ? { ...c, completions: 1, by: "tap" as const, completes_at: ends } : c)),
  };
  const always: Order = { when: { kind: "after_time", at: 0 }, then: { kind: "tap_card", card: "carve" }, unless: [], or_else: [], below_next: false };
  const first = held.orders.findIndex((o) => o.when.kind === "after_time" && o.then.kind === "tap_card" && catalog.laneOf(o.then.card) === "mason");
  const want = first < 0 ? [...held.orders, always] : [...held.orders.slice(0, first), always, ...held.orders.slice(first)];
  expect("the rule, placed as a new lane rule", untilDone(catalog, held, "carve"), { kind: "set_orders", orders: want });
  const { open, face, got } = pageRig(held);
  open(1);
  const button = face("carve").querySelector(".card-ready") as FakeEl;
  expect("on the person's running one-off: Until done, on", [button?.hidden, button?.disabled, button?.textContent], [false, false, "Until done"]);
  button.click();
  expect("its tap sends the rule", got.decided, [{ kind: "set_orders", orders: want }]);
  expect("a rule's tap there: nothing", untilDone(catalog, { ...held, lanes: held.lanes.map((l) => (l.lane === "mason" ? { ...l, order: 0 } : l)) }, "carve"), null);
}
