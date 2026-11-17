// Next as a row among the hands' rules (CONTRACT.txt, "Next's row"): the rules under it carry below_next, a run to the end
// of the orders. The hands' list is moved as items, each rule's index and NEXT for the row, so a rule moved past Next
// changes side and Next moved past a rule moves the line; every set_orders keeps the line where the player put it.
import type { Decision, Order, View } from "../api/types";

/** Next's row in a list of rule indexes. */
export const NEXT = -1;

/** The orders' index of the first rule under Next, or the orders' length when Next is at the bottom. */
export function nextUnder(orders: readonly Order[]): number {
  const at = orders.findIndex((o) => o.below_next === true);
  return at < 0 ? orders.length : at;
}

/** `orders` with the rules from index `at` on under Next and those before it above. */
export function withNextAt(orders: readonly Order[], at: number): Order[] {
  return orders.map((o, i) => ({ ...o, below_next: i >= at }));
}

/** The hands' rules `group` (orders' indexes, in order) with NEXT where it sits: before the first one under it. */
export function nextItems(view: View, group: readonly number[]): number[] {
  const at = group.findIndex((i) => view.orders[i]?.below_next === true);
  return at < 0 ? [...group, NEXT] : [...group.slice(0, at), NEXT, ...group.slice(at)];
}

/** The rules of `items` put into the slots of `group` in that order, the rules outside the group keeping their places:
 * with NEXT among them, the rules after it are under Next; without (the town's rules), Next keeps its slot. */
export function placeItems(view: View, group: readonly number[], items: readonly number[]): Decision {
  const rules = items.filter((i) => i !== NEXT);
  const slot = new Map(group.map((g, n) => [g, view.orders[rules[n]!]!]));
  const above = items.indexOf(NEXT);
  const at = above < 0 ? nextUnder(view.orders) : above >= group.length ? view.orders.length : group[above]!;
  return { kind: "set_orders", orders: withNextAt(view.orders.map((o, i) => slot.get(i) ?? o), at) };
}

/** `items` with `item` (a rule's index or NEXT) one place up (-1) or down (+1); null at an end. */
export function steppedItems(items: readonly number[], item: number, step: -1 | 1): number[] | null {
  const from = items.indexOf(item), to = from + step;
  if (from < 0 || to < 0 || to >= items.length) return null;
  const moved = [...items];
  [moved[from], moved[to]] = [moved[to]!, moved[from]!];
  return moved;
}

/** `items` with `item` moved to where `to` stands, those between shifting one place; null when nothing moves. */
export function reorderedItems(items: readonly number[], item: number, to: number): number[] | null {
  const from = items.indexOf(item), at = items.indexOf(to);
  if (from < 0 || at < 0 || from === at) return null;
  const moved = [...items];
  moved.splice(from, 1);
  moved.splice(at, 0, item);
  return moved;
}

/** Where each drawn row comes from once the hands' items are `moved` (ui/ruleslide.ts): a rule's new slot in `group` ->
 * the slot it had (its index now), and NEXT -> NEXT. */
export function itemShift(group: readonly number[], moved: readonly number[]): Map<number, number> {
  const shift = new Map<number, number>([[NEXT, NEXT]]);
  moved.filter((i) => i !== NEXT).forEach((rule, n) => shift.set(group[n]!, rule));
  return shift;
}

/** A rule's words for matching it with a rule_run's `order`, which is served without the row (below_next false). */
export function unplacedKey(order: Order): string {
  const { below_next: _placed, ...rule } = order;
  return JSON.stringify(rule);
}
