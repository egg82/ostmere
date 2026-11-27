// "Until done" on a staged card a tap started (CONTRACT.txt, "UNTIL DONE"): the running tap becomes the plan it would
// have been had the player planned it first, its work kept. On the hands (or any lane that is not ruled), a queue entry
// tapping it until its cap, at Next's front (where it would stand, running), or the running When ready entry held on to
// the cap; on a ruled lane, where the queue may not go, an always rule tapping it, placed as a new lane rule goes.
// Either re-taps it at each landing and lets go at the cap (engine design/, "Orders", "Ruled lane").
import type { Card, Decision, Order, View } from "../api/types";
import type { Catalog } from "./catalog";
import { ALWAYS, newRuleAt } from "./lanes";
import { ruleExists, rulesFull } from "./orders";
import { queueFull, tapUntil } from "./queue";

/** The decision that runs card `id` on to its cap, or null when not offered: the card is not running, a rule started
 * it, or the running tap is its last. */
export function untilDone(catalog: Catalog, view: View, id: string): Decision | null {
  const card = view.cards.find((c) => c.card === id);
  const bar = view.lanes.find((l) => l.running_card === id);
  if (card === undefined || bar === undefined || bar.order !== null || card.cap === null || card.cap - card.completions < 2) return null;
  return catalog.ruled(id) ? laneRule(catalog, view, id) : queueEntry(catalog, view, card, card.cap);
}

function queueEntry(catalog: Catalog, view: View, card: Card, cap: number): Decision | null {
  if (view.ended_at === null) return null;
  const at = view.queue.findIndex((q) => q.verb.kind === "tap_card" && q.verb.card === card.card);
  if (at < 0) return queueFull(catalog, view) ? null : { kind: "set_queue", entries: [tapUntil(card.card, cap), ...view.queue] };
  const until = view.queue[at]!.until;
  if (until.kind === "at_least" && until.value >= cap) return null;
  return { kind: "set_queue", entries: view.queue.map((q, i) => (i === at ? tapUntil(card.card, cap) : q)) };
}

function laneRule(catalog: Catalog, view: View, card: string): Decision | null {
  const order: Order = { when: ALWAYS, then: { kind: "tap_card", card }, unless: [], or_else: [], below_next: false };
  if (rulesFull(catalog, view) || ruleExists(view, null, order)) return null;
  const at = newRuleAt(catalog, view, order) ?? view.orders.length;
  return { kind: "set_orders", orders: [...view.orders.slice(0, at), order, ...view.orders.slice(at)] };
}
