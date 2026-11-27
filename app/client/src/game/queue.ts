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

/** Whether the card's face would offer "When ready" if the queue had room: a step (not work done again and again, which
 * the mix and Plan take), not queued already, not the card its lane runs (Until done is that one's), and either waiting
 * on a kept ready time or ready while its lane runs another tap. */
export function onFace(catalog: Catalog, view: View, card: Card): boolean {
  if (!queueable(catalog, view, card) || catalog.cards.get(card.card)?.presentation === "action" || queuedCards(view).includes(card.card)) return false;
  if (card.blocker !== null) return keptReadyAt(view, card, catalog.content.scales.quantity_per_item) !== null;
  const running = view.lanes.find((l) => l.lane === catalog.laneOf(card.card))?.running_card ?? null;
  return running !== null && running !== card.card;
}

/** Whether the queue takes a run of `card`, from Plan or its face: after the end, with room under its cap for one more
 * run than those planned (a run past it could never happen), whatever it waits on (an entry is checked when its turn
 * comes: one that cannot run then waits, and one whose card reached its cap is dropped). Not one on a ruled lane (the queue is the hands' plan: the server refuses it, contract/a-lane-run-by-rules.txt, "A LANE RUN BY
 * RULES"). Not one waiting on a store the player has never seen (a clock: what it opens must open in front of the
 * player). */
export function queueable(catalog: Catalog, view: View, card: Card): boolean {
  return view.ended_at !== null && !catalog.ruled(card.card) && (card.cap === null || planned(view, card) < card.cap)
    && (card.blocker === null || !waitsOnUnseen(view, card));
}

/** One run of card `id` at the queue's end, from its face or from Plan, or null when it is not taken. The one way the
 * page puts a card in the queue. */
export function whenReady(catalog: Catalog, view: View, id: string): Decision | null {
  const card = view.cards.find((c) => c.card === id);
  return card !== undefined && !queueFull(catalog, view) && queueable(catalog, view, card) ? queueTap(view, card) : null;
}

/** The cards Plan lists, in the page's order: every card the queue takes. */
export function planCards(catalog: Catalog, view: View): Card[] {
  return queueFull(catalog, view) ? [] : view.cards.filter((c) => queueable(catalog, view, c));
}

/** The queue with one more run of `card` at its end: held until the card's count is one past the runs planned before it,
 * the tap under way and the card's earlier entries (each entry is one run, so a running card's adds one after it). */
export function queueTap(view: View, card: Card): Decision {
  return { kind: "set_queue", entries: [...view.queue, tapUntil(card.card, planned(view, card) + 1)] };
}

/** The card's count once the runs planned for it land: the tap under way and its entries in the queue. */
function planned(view: View, card: Card): number {
  const running = view.lanes.some((l) => l.running_card === card.card) ? 1 : 0;
  return Math.max(card.completions + running, ...runTargets(view.queue, card.card));
}

/** The counts the queue's runs of `card` are held until, in queue order. */
function runTargets(entries: readonly QueueEntry[], card: string): number[] {
  return entries.flatMap((q) => (runOf(q) === card && q.until.kind === "at_least" ? [q.until.value] : []));
}

/** The card a run entry taps (a tap held until a count of that card), or null. */
function runOf(q: QueueEntry): string | null {
  const u = q.until;
  return q.verb.kind === "tap_card" && u.kind === "at_least" && u.watched.kind === "card_count" && u.watched.card === q.verb.card ? q.verb.card : null;
}

/** Each card's run counts in `entries`, the least first. */
function runCounts(entries: readonly QueueEntry[]): Map<string, number[]> {
  const counts = new Map<string, number[]>();
  for (const q of entries) {
    const card = runOf(q);
    if (card !== null && !counts.has(card)) counts.set(card, runTargets(entries, card).sort((a, b) => a - b));
  }
  return counts;
}

/** `entries` with each card's runs held until `counts`' in queue order, the least first: runs of one card are alike, so
 * after a move or a removal the earlier ones keep the earlier counts. */
function renumbered(entries: readonly QueueEntry[], counts: Map<string, number[]>): QueueEntry[] {
  return entries.map((q) => {
    const card = runOf(q);
    const n = card === null ? undefined : counts.get(card)?.shift();
    return card === null || n === undefined ? q : tapUntil(card, n);
  });
}

/** A queue entry tapping `card` until its card_count reaches `n`. */
export function tapUntil(card: string, n: number): QueueEntry {
  return {
    verb: { kind: "tap_card", card },
    until: { kind: "at_least", watched: { kind: "card_count", card }, value: n, release: n, value_of_cap: false, release_of_cap: false },
  };
}

/** The queue less entry `index`: the card's runs left keep its least counts, so they still follow the tap under way. */
export function unqueue(view: View, index: number): Decision {
  return { kind: "set_queue", entries: renumbered(view.queue.filter((_, i) => i !== index), runCounts(view.queue)) };
}

/** How many runs of its card entry `index` adds after those planned before it (the tap under way and the card's earlier
 * entries): 1 for each pick from Plan, more for Until done's entry, 0 for one the tap under way completes; null for an
 * entry that is no run of a card (a stint, an answer). */
export function entryRuns(view: View, index: number): number | null {
  const entry = view.queue[index];
  const card = entry === undefined ? null : runOf(entry);
  if (card === null || entry!.until.kind !== "at_least") return null;
  const before = runTargets(view.queue.slice(0, index), card);
  const running = view.lanes.some((l) => l.running_card === card) ? 1 : 0;
  const done = view.cards.find((c) => c.card === card)?.completions ?? 0;
  return Math.max(0, entry!.until.value - Math.max(done + running, ...before));
}

/** Whether entry `index` is the tap a lane runs: it pops when that tap completes, adding no run after it, so it holds
 * its place and is not offered a Remove. */
export function runsNow(view: View, index: number): boolean {
  const verb = view.queue[index]?.verb;
  return verb?.kind === "tap_card" && view.lanes.some((l) => l.running_card === verb.card) && (entryRuns(view, index) ?? 0) === 0;
}

/** The entries Next lets move, in order: all but those a lane already runs. */
export function movableEntries(view: View): number[] {
  return view.queue.flatMap((_, i) => (runsNow(view, i) ? [] : [i]));
}

/** Next's rows: the queue's entries in order, runs of the same card one after another drawn as one (an entry a lane runs
 * stays a row of its own). */
export function queueRows(view: View): number[][] {
  const rows: number[][] = [];
  view.queue.forEach((q, i) => {
    const last = rows[rows.length - 1];
    const prev = last === undefined ? undefined : view.queue[last[last.length - 1]!];
    const same = prev !== undefined && runOf(q) !== null && runOf(q) === runOf(prev) && !runsNow(view, i) && !runsNow(view, i - 1);
    if (same) last!.push(i); else rows.push([i]);
  });
  return rows;
}

/** Where moving one entry of the row holding `index` one movable row up (-1) or down (+1) puts it: before the row above,
 * or after the row below (an entry index for moveQueued); null at an end. */
export function rowStep(view: View, index: number, step: -1 | 1): number | null {
  const rows = queueRows(view).filter((r) => !runsNow(view, r[0]!));
  const at = rows.findIndex((r) => r.includes(index));
  const next = at < 0 ? undefined : rows[at + step];
  return next === undefined ? null : step < 0 ? next[0]! : next[next.length - 1]!;
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
  return { kind: "set_queue", entries: renumbered(entries, runCounts(entries)) };
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
 * share of a store's cap (contract/goal-stints.txt, "Goal stints"). */
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
