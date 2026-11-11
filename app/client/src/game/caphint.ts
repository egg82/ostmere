// The first full store (docs/design/opening-screen.md, the hands strip, "Hint: the first full store"): read off the view
// and the content only. A new save has no cap rule, so a store the hands fill tops out and what they make past the top
// is lost. The ledger marks that line with the quiet dot and the cap rule's lesson starts from it (game/lessons.ts,
// CAP_RULE); nothing is built.
import type { LedgerLine, Order, View } from "../api/types";
import type { Catalog } from "./catalog";
import { rulesFull } from "./orders";
import { ruleTasks } from "./ruleoffers";
import { fullAndFed } from "./shown";

/** The store a rule watches reach a level (what a cap rule watches), or null. */
function reachesStore(order: Order): string | null {
  return order.when.kind === "at_least" && order.when.watched.kind === "store_value" ? order.when.watched.store : null;
}

/** A rule that comes on when the store reaches a level: what a cap rule watches. */
export function reachesRuleOn(view: View, store: string): boolean {
  return view.orders.some((o) => reachesStore(o) === store);
}

/** The save has a cap rule on any store: the player has written one (nothing installs a rule that watches a store). */
export function anyReachesRule(view: View): boolean {
  return view.orders.some((o) => reachesStore(o) !== null);
}

/** The line is full, a card on the hands still makes it, another hands task could take that time, and no rule
 * watches it reach a level. */
function capped(catalog: Catalog, view: View, line: LedgerLine, tasks: readonly string[]): boolean {
  const makers = new Set(catalog.stores.get(line.store)?.made_by ?? []);
  return fullAndFed(line, view.at)
    && line.contributions.some((c) => c.per_hour > 0 && catalog.mixable(c.runner))
    && tasks.some((t) => !makers.has(t))
    && !reachesRuleOn(view, line.store);
}

/** The store whose line carries the cap hint now: the first in the view's order that is capped, the Camp store and
 * hidden stores excepted; null when none is, or when no rule can be added. */
export function capStore(catalog: Catalog, view: View): string | null {
  if (rulesFull(catalog, view)) return null;
  const tasks = ruleTasks(catalog, view, null).filter((c) => catalog.mixable(c));
  const line = view.ledger.find((l) => l.store !== catalog.campStore && !catalog.stores.get(l.store)?.hidden && capped(catalog, view, l, tasks));
  return line?.store ?? null;
}
