// The player's queue as the page builds it (docs/systems.md, "Standing orders and the queue"; engine DESIGN.txt,
// "Orders"): "When ready" lines up one tap of any step the player could not simply tap now, held until that tap's
// completion. The engine starts the head the moment it turns ready and passes over only an entry nothing will make
// ready (DESIGN.txt, "Never ready"); while it waits the mix runs on. Every edit sends the whole list back (set_queue
// replaces it).
import type { Card, Condition, Decision, GoalRow, QueueEntry, View } from "../api/types";
import type { Catalog } from "./catalog";
import { keptReadyAt, waitsOnUnseen } from "./ready";

/** The cards the queue taps, in its order. */
export function queuedCards(view: View): string[] {
  return view.queue.flatMap((q) => (q.verb.kind === "tap_card" ? [q.verb.card] : []));
}

/** The card's own "When ready" button is offered while the queue has room on a card Plan takes (queueable) that the
 * player cannot simply tap now: one unready with a ready time, or one ready now whose lane runs another tap (so it
 * runs after that task). Plan takes the rest too; the face promises only what it can keep. */
export function canQueue(catalog: Catalog, view: View, card: Card): boolean {
  return !queueFull(catalog, view) && onFace(catalog, view, card);
}

/** The queue holds Content.limits.max_queue entries: no more are offered. */
export function queueFull(catalog: Catalog, view: View): boolean {
  return view.queue.length >= catalog.content.limits.max_queue;
}

/** Whether the card's face would offer "When ready" if the queue had room. */
export function onFace(catalog: Catalog, view: View, card: Card): boolean {
  if (!queueable(catalog, view, card)) return false;
  if (card.blocker !== null) return keptReadyAt(view, card, catalog.content.scales.quantity_per_item) !== null;
  return (view.lanes.find((l) => l.lane === catalog.laneOf(card.card))?.running_card ?? null) !== null;
}

/** Whether "When ready" takes `card`, from Plan or its face: a step (not work done again and again, which is the mix's)
 * after the end, not at its cap, not already queued and not running (its entry would pop at that landing and add
 * nothing: Until done is the running card's own), whatever it waits on: an entry that cannot run yet waits. Not one on a
 * ruled lane (the queue is the hands' plan: the server refuses it, CONTRACT.txt, "A LANE RUN BY RULES"). Not one
 * waiting on a store the player has never seen (a clock: what it opens must open in front of the player). */
export function queueable(catalog: Catalog, view: View, card: Card): boolean {
  return view.ended_at !== null && catalog.cards.get(card.card)?.presentation !== "action" && !catalog.ruled(card.card)
    && !view.lanes.some((l) => l.running_card === card.card)
    && (card.cap === null || card.completions < card.cap) && !queuedCards(view).includes(card.card)
    && (card.blocker === null || !waitsOnUnseen(view, card));
}

/** "When ready" on card `id`, from its face or from Plan: the queue with one tap of it at the end, or null when it is
 * not taken. The one way the page puts a card in the queue. */
export function whenReady(catalog: Catalog, view: View, id: string): Decision | null {
  const card = view.cards.find((c) => c.card === id);
  return card !== undefined && !queueFull(catalog, view) && queueable(catalog, view, card) ? queueTap(view, card) : null;
}

/** The cards Plan lists, in the page's order: every step "When ready" takes. */
export function planCards(catalog: Catalog, view: View): Card[] {
  return queueFull(catalog, view) ? [] : view.cards.filter((c) => queueable(catalog, view, c));
}

/** The queue with one more tap of `card` at its end, held until that tap completes. */
export function queueTap(view: View, card: Card): Decision {
  return { kind: "set_queue", entries: [...view.queue, tapUntil(card.card, card.completions + 1)] };
}

/** A queue entry tapping `card` until its card_count reaches `n`. */
export function tapUntil(card: string, n: number): QueueEntry {
  return {
    verb: { kind: "tap_card", card },
    until: { kind: "at_least", watched: { kind: "card_count", card }, value: n, release: n, value_of_cap: false, release_of_cap: false },
  };
}

/** The queue less entry `index`. */
export function unqueue(view: View, index: number): Decision {
  return { kind: "set_queue", entries: view.queue.filter((_, i) => i !== index) };
}

/** Whether a lane is running the card the entry taps: the entry stays queued until that tap completes, so it holds its
 * place and is not offered a Remove. */
export function runsNow(view: View, entry: QueueEntry): boolean {
  const verb = entry.verb;
  return verb.kind === "tap_card" && view.lanes.some((l) => l.running_card === verb.card);
}

/** The entries Next lets move, in order: all but those a lane already runs. */
export function movableEntries(view: View): number[] {
  return view.queue.flatMap((e, i) => (runsNow(view, e) ? [] : [i]));
}

/** The queue with entry `from` moved to entry `to`'s place among the movable ones; the entries a lane runs keep their
 * places. Null when either is not movable or they are the same. */
export function moveQueued(view: View, from: number, to: number): Decision | null {
  const slots = movableEntries(view);
  const a = slots.indexOf(from), b = slots.indexOf(to);
  if (a < 0 || b < 0 || a === b) return null;
  const order = slots.map((i) => view.queue[i]!);
  order.splice(b, 0, ...order.splice(a, 1));
  const entries = [...view.queue];
  slots.forEach((slot, k) => { entries[slot] = order[k]!; });
  return { kind: "set_queue", entries };
}

/** The card the queue taps next: its head's, or, while the head's card already runs on the hands, the entry's after
 * it; null when that entry is missing or switches a mix. */
export function nextCard(view: View): string | null {
  const running = view.lanes.find((l) => l.lane === "hands")?.running_card ?? null;
  const head = view.queue[0]?.verb;
  const next = head?.kind === "tap_card" && head.card === running ? view.queue[1]?.verb : head;
  return next?.kind === "tap_card" ? next.card : null;
}

/** The queue with a goal stint at its end: `mix` runs over the player's own until `until` holds, a goal row's or a
 * share of a store's cap (CONTRACT.txt, "Goal stints"). */
export function queueStint(view: View, mix: string, until: Condition): Decision {
  return { kind: "set_queue", entries: [...view.queue, { verb: { kind: "switch_mix", mix_id: mix }, until }] };
}

/** A stint's `until` at a share of `store`'s cap, in basis points: it holds once the store's whole items reach it. */
export function shareUntil(store: string, share: number): Condition {
  return { kind: "at_least", watched: { kind: "store_value", store }, value: share, release: share, value_of_cap: true, release_of_cap: true };
}

/** The goal row whose `until` is `until`, or null (no row: the goal left view.goal_rows, or another client wrote it). */
export function stintRow(view: View, until: Condition): GoalRow | null {
  return view.goal_rows.find((r) => sameUntil(r.until, until)) ?? null;
}

function sameUntil(a: Condition, b: Condition): boolean {
  if (a.kind !== "at_least" || b.kind !== "at_least" || a.value !== b.value || a.release !== b.release) return false;
  if ((a.value_of_cap ?? false) !== (b.value_of_cap ?? false) || (a.release_of_cap ?? false) !== (b.release_of_cap ?? false)) return false;
  const [x, y] = [a.watched, b.watched];
  if (x.kind === "store_value" && y.kind === "store_value") return x.store === y.store;
  return x.kind === "skill_level" && y.kind === "skill_level" && x.skill === y.skill;
}

/** The index of the entry that controls: the first whose verb is not dead (a switch to a greyed mix, a tap of a
 * completed card); null when every entry is. */
export function controllingEntry(view: View): number | null {
  const done = new Set(view.completed.map((c) => c.card));
  const i = view.queue.findIndex((q) => (q.verb.kind === "switch_mix" ? !view.greyed_mix_ids.includes(q.verb.mix_id)
    : q.verb.kind !== "tap_card" || !done.has(q.verb.card)));
  return i < 0 ? null : i;
}
