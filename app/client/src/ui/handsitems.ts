// The Rules tab's rows that move together (ui/rules.ts): the hands' rules with Next's row among them while it is drawn
// (game/nextrow.ts), or the town's rules. A move of the hands' rows becomes the set_orders, its slide and where the moved
// row lands.
import type { Decision, View } from "../api/types";
import type { Catalog } from "../game/catalog";
import { NEXT, itemShift, nextItems, placeItems } from "../game/nextrow";
import { mixRules } from "../game/orders";
import { townRules } from "../game/town";

/** The rules drawn together with rule `index`, in order: the town's rules, or the hands' (none when it is neither). */
export function groupOf(catalog: Catalog, view: View, index: number): number[] {
  const town = townRules(catalog, view);
  const group = town.includes(index) ? town : mixRules(view).filter((i) => !town.includes(i));
  return group.includes(index) ? group : [];
}

/** The hands' rules, those not the town's, in order. */
export function handsGroup(catalog: Catalog, view: View): number[] {
  const town = townRules(catalog, view);
  return mixRules(view).filter((i) => !town.includes(i));
}

/** Next's row is off the bottom of the hands' list (the player moved it). */
export function nextKept(items: readonly number[]): boolean {
  return items[items.length - 1] !== NEXT;
}

/** The rows moved together with `index` (a rule's, or NEXT), in order: the hands' rules with Next's row among them while
 * it is drawn (`listed`: the queue or Plan has a line; or it is off the bottom), or the town's rules; none for neither. */
export function itemsOf(catalog: Catalog, view: View, index: number, listed: boolean): number[] {
  const hands = handsGroup(catalog, view);
  if (index !== NEXT && !hands.includes(index)) return groupOf(catalog, view, index);
  const items = nextItems(view, hands);
  const drawn = listed || nextKept(items) ? items : hands;
  return drawn.includes(index) ? drawn : [];
}

/** The rows moved with `item` (itemsOf) now `moved`, `item` among them: the set_orders (rules into their slots, those
 * after Next under it), its slide (ui/ruleslide.ts) and the index `item`'s row has after the redraw; null when it did
 * not move. */
export function itemsMoved(catalog: Catalog, view: View, item: number, moved: number[] | null): { decision: Decision; shift: Map<number, number>; lands: number } | null {
  if (moved === null) return null;
  const hands = handsGroup(catalog, view);
  const slots = item === NEXT || hands.includes(item) ? hands : groupOf(catalog, view, item);
  const decision = placeItems(view, slots, moved);
  const lands = item === NEXT ? NEXT : slots[moved.filter((i) => i !== NEXT).indexOf(item)]!;
  return { decision, shift: itemShift(slots, moved), lands };
}
