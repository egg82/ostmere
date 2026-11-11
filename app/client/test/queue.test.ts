// When ready and Next (game/queue.ts; ui/whenready.ts, ui/nextlist.ts, the strip's note in ui/hands.ts): offered on a
// step after the end while it waits on something with a ready time, never on work done again and again; one tap of it
// appended to the queue, held until that tap completes; the button stays as "in Next" once queued, takes the one glow
// the first time only; Next lists the queue between the hands rules and Otherwise with Remove; the strip names the head.
import { install } from "./fake-dom";
import { testContext } from "./context";
import { fixtureContent, Q } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { Card, QueueEntry, View } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { canQueue, nextCard, queuedCards, queueTap, unqueue } from "../src/game/queue";
import { Hands } from "../src/ui/hands";
import { nextRows } from "../src/ui/nextlist";
import { StintPlan } from "../src/ui/stintplan";
import { RulesTab } from "../src/ui/rules";
import { WhenReady } from "../src/ui/whenready";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const catalog = new Catalog(fixtureContent);
const still = (v = 0) => ({ start: 100, start_value: v, rate: 0, limit: null });
const waiting = (id: string, readyAt: number | null, over: Partial<Card> = {}): Card => ({
  card: id, completions: 0, cap: 1, bar: still(), bar_total: 20, by: null, completes_at: null, share_bp: 0, run: null, cuts_in: false, spent_store: null, gained: [], tap_s: 20,
  blocker: { condition: { kind: "at_least", watched: { kind: "store_value", store: "stone" }, value: 12 * Q, release: 12 * Q }, ready_at: readyAt },
  needs: [{ store: "stone", quantity: 12 * Q, segment: still(3 * Q), gate: null, makers: [], spent: false }], ...over,
});
const ended = fixtureStep("restoffer", 100).view;   // the end ten minutes back
const at = (cards: Card[], queue: QueueEntry[] = [], over: Partial<View> = {}): View => ({ ...ended, cards: [...ended.cards, ...cards], queue, ...over });
const larder = waiting("larder", 400);
const tapOf = (card: string, n: number): QueueEntry => ({
  verb: { kind: "tap_card", card }, until: { kind: "at_least", watched: { kind: "card_count", card }, value: n, release: n },
});

// Which cards offer it.
expect("a step waiting on a known time", canQueue(catalog, at([larder]), larder), true);
expect("not before the end", canQueue(catalog, at([larder], [], { ended_at: null }), larder), false);
expect("not when it will not turn ready by itself", canQueue(catalog, at([waiting("larder", null)]), waiting("larder", null)), false);
expect("not when ready now", canQueue(catalog, at([{ ...larder, blocker: null }]), { ...larder, blocker: null }), false);
expect("not on work done again and again", canQueue(catalog, at([waiting("gather", 400)]), waiting("gather", 400, { cap: null })), false);
expect("a narrative step too", canQueue(catalog, at([waiting("take_stock", 400)]), waiting("take_stock", 400)), true);
expect("not at its cap", canQueue(catalog, at([larder]), { ...larder, completions: 1 }), false);
expect("an uncapped step may be", canQueue(catalog, at([larder]), { ...larder, cap: null, completions: 4 }), true);
expect("not twice", canQueue(catalog, at([larder], [tapOf("larder", 1)]), larder), false);

// What it sends: the queue as it stands plus one tap, held until the next completion.
const lean = waiting("lean_to", 300, { cap: 2, completions: 1 });
expect("appended, until completion n+1", queueTap(at([lean], [tapOf("larder", 1)]), lean),
  { kind: "set_queue", entries: [tapOf("larder", 1), tapOf("lean_to", 2)] });
expect("Remove sends the rest", unqueue(at([], [tapOf("larder", 1), tapOf("lean_to", 2)]), 0), { kind: "set_queue", entries: [tapOf("lean_to", 2)] });
expect("the head's card", nextCard(at([], [tapOf("larder", 1), tapOf("lean_to", 2)])), "larder");
expect("a mix switch at the head names no card", nextCard(at([], [{ verb: { kind: "switch_mix", mix_id: "M" }, until: tapOf("x", 1).until }])), null);
expect("queued cards in order", queuedCards(at([], [tapOf("larder", 1), tapOf("lean_to", 2)])), ["larder", "lean_to"]);

// The button: hidden until offered; When ready, the glow once; a click queues and flies the card; then "in Next".
{
  const { ctx, got } = testContext();
  const w = new WhenReady(ctx);
  const node = document.createElement("div");
  const b = w.make("larder", node);
  const other = w.make("lean_to", node);
  document.body.replaceChildren(node);
  node.append(b, other);
  expect("hidden at first", b.hidden, true);
  w.sync(b, waiting("larder", null), at([waiting("larder", null)]));
  expect("hidden while it will not turn ready", b.hidden, true);
  const view = at([larder, lean]);
  w.sync(b, larder, view);
  expect("offered", [b.hidden, b.disabled, b.textContent], [false, false, "When ready"]);
  expect("the glow, the first time", b.classList.contains("glow"), true);
  b.click();
  expect("one tap queued", got.decided, [{ kind: "set_queue", entries: [tapOf("larder", 1)] }]);
  expect("the card flies", got.sent.length === 1 && got.sent[0] === node, true);
  expect("the glow goes with the click", b.classList.contains("glow"), false);
  const queued = at([larder, lean], [tapOf("larder", 1)]);
  w.sync(b, larder, queued);
  expect("queued: a quiet mark, off", [b.hidden, b.disabled, b.textContent, b.classList.contains("queued")], [false, true, "in Next", true]);
  w.sync(other, lean, queued);
  expect("the next card offered gets no glow", other.classList.contains("glow"), false);
  w.sync(b, undefined, queued);
  expect("hidden on a finished card", b.hidden, true);
  b.click();
  expect("a hidden button sends nothing", got.decided.length, 1);
}

// A card already queued (a reload) shows its mark and takes no glow.
{
  const w = new WhenReady(testContext().ctx);
  const b = w.make("larder", document.createElement("div"));
  document.body.replaceChildren(b);
  w.sync(b, larder, at([larder], [tapOf("larder", 1)]));
  expect("queued on arrival: no glow", b.classList.contains("glow"), false);
}

// Next: a heading and a line per entry, Remove sends the rest; nothing for an empty queue.
{
  const { ctx, got } = testContext();
  const view = at([], [tapOf("larder", 1), tapOf("lean_to", 2)]);
  expect("empty: nothing", nextRows(ctx, at([]), new StintPlan(ctx, () => {})).length, 0);
  const rows = nextRows(ctx, view, new StintPlan(ctx, () => {}));
  expect("heading and two lines", rows.map((r) => r.textContent), ["Next", "LarderRemove", "Lean-toRemove"]);
  rows[2]!.querySelector<HTMLElement>(".quiet")?.click();
  expect("Remove the second", got.decided, [{ kind: "set_queue", entries: [tapOf("larder", 1)] }]);
}

// In the Rules tab, Next sits after the hands rules and before Otherwise.
{
  const tab = new RulesTab(testContext().ctx);
  document.body.replaceChildren(tab.root);
  const rules = fixtureStep("rulestab", 100).view;
  tab.update({ ...rules, queue: [tapOf("larder", 1)] });
  const order = [...tab.root.querySelector(".rules-list")!.children].map((n) => (["next-row", "otherwise"].find((c) => n.classList.contains(c)) ?? n.className.split(" ")[0]));
  expect("rules (each off one with its why), Next, Otherwise", order, ["rules-row", "rule-why", "rules-row", "rule-why", "rules-row", "rules-next", "next-row", "otherwise"]);
}

// The strip names the head, in whichever row shows, and drops it when the queue empties.
{
  const hands = new Hands(testContext().ctx);
  document.body.replaceChildren(hands.root);
  hands.update(at([], [tapOf("larder", 1)], { active_mix_id: null, running_mix_id: null }));
  const note = hands.root.querySelector<HTMLElement>(".hands-next")!;
  expect("no mix: in the hands row", [note.hidden, note.textContent, note.parentElement?.className], [false, "next: Larder", "hands-row"]);
  hands.update(at([], [tapOf("larder", 1)]));
  expect("a mix: in its meta row, before Edit", [note.parentElement?.className, note.nextElementSibling?.className], ["hands-meta", "hands-edit"]);
  hands.update(at([]));
  expect("empty: hidden", note.hidden, true);
}
