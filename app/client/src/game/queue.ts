// The player's queue as the page builds it (docs/systems.md, "Standing orders and the queue"; engine DESIGN.txt,
// "Orders"): "When ready" lines up one tap of a step that is not ready yet but will be by itself (its blocker has a
// ready time), held until that tap's completion. The engine starts the head the moment it turns ready and never passes
// it over; while it waits the mix runs on. Every edit sends the whole list back (set_queue replaces it).
import type { Card, Condition, Decision, GoalRow, QueueEntry, View } from "../api/types";
import type { Catalog } from "./catalog";
import { keptReadyAt, waitsOnUnseen } from "./ready";

/** The cards the queue taps, in its order. */
export function queuedCards(view: View): string[] {
  return view.queue.flatMap((q) => (q.verb.kind === "tap_card" ? [q.verb.card] : []));
}

/** "When ready" is offered on a step (not work done again and again, which is the mix's) after the end, while it is
 * unready with a ready time the page can see kept (game/ready.ts), not at its cap and not already queued, and not
 * waiting on a store the player has never seen (a clock: what it opens must open in front of the player). */
export function canQueue(catalog: Catalog, view: View, card: Card): boolean {
  return !queueFull(catalog, view) && queueable(catalog, view, card);
}

/** The queue holds Content.limits.max_queue entries: no more are offered. */
export function queueFull(catalog: Catalog, view: View): boolean {
  return view.queue.length >= catalog.content.limits.max_queue;
}

/** Whether `card` would be offered "When ready" if the queue had room. */
export function queueable(catalog: Catalog, view: View, card: Card): boolean {
  return view.ended_at !== null && catalog.cards.get(card.card)?.presentation !== "action" && keptReadyAt(view, card) !== null
    && !waitsOnUnseen(view, card)
    && (card.cap === null || card.completions < card.cap) && !queuedCards(view).includes(card.card);
}

/** The queue with one more tap of `card` at its end, held until that tap completes. */
export function queueTap(view: View, card: Card): Decision {
  const n = card.completions + 1;
  const entry: QueueEntry = {
    verb: { kind: "tap_card", card: card.card },
    until: { kind: "at_least", watched: { kind: "card_count", card: card.card }, value: n, release: n },
  };
  return { kind: "set_queue", entries: [...view.queue, entry] };
}

/** The queue less entry `index`. */
export function unqueue(view: View, index: number): Decision {
  return { kind: "set_queue", entries: view.queue.filter((_, i) => i !== index) };
}

/** The card the queue's head taps, or null (an empty queue, or a head that switches a mix). */
export function nextCard(view: View): string | null {
  const head = view.queue[0]?.verb;
  return head?.kind === "tap_card" ? head.card : null;
}

/** The queue with a goal stint at its end: `mix` runs over the player's own until `row`'s goal lands (CONTRACT.txt,
 * "Goal stints"). */
export function queueStint(view: View, mix: string, row: GoalRow): Decision {
  return { kind: "set_queue", entries: [...view.queue, { verb: { kind: "switch_mix", mix_id: mix }, until: row.until }] };
}

/** The goal row whose `until` is `until`, or null (no row: the goal left view.goal_rows, or another client wrote it). */
export function stintRow(view: View, until: Condition): GoalRow | null {
  return view.goal_rows.find((r) => sameUntil(r.until, until)) ?? null;
}

function sameUntil(a: Condition, b: Condition): boolean {
  if (a.kind !== "at_least" || b.kind !== "at_least" || a.value !== b.value || a.release !== b.release) return false;
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
