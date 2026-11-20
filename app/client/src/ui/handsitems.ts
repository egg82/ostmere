// The Rules tab's rows that move together (ui/rules.ts): the hands' rules with Next's row among them while it is drawn
// (game/nextrow.ts). A move of those rows becomes the set_orders, its slide and where the moved row lands.
import type { Decision, View } from "../api/types";
import { NEXT, itemShift, nextItems, placeItems } from "../game/nextrow";
import { mixRules } from "../game/orders";

/** Next's row is off the bottom of the hands' list (the player moved it). */
export function nextKept(items: readonly number[]): boolean {
  return items[items.length - 1] !== NEXT;
}

/** The rows moved together with `index` (a rule's, or NEXT), in order: the hands' rules with Next's row among them while
 * it is drawn (`listed`: the queue or Plan has a line; or it is off the bottom); none for neither. */
export function itemsOf(view: View, index: number, listed: boolean): number[] {
  const hands = mixRules(view);
  const items = nextItems(view, hands);
  const drawn = listed || nextKept(items) ? items : hands;
  return drawn.includes(index) ? drawn : [];
}

/** The rows moved with `item` (itemsOf) now `moved`, `item` among them: the set_orders (rules into their slots, those
 * after Next under it), its slide (ui/ruleslide.ts) and the index `item`'s row has after the redraw; null when it did
 * not move. */
export function itemsMoved(view: View, item: number, moved: number[] | null): { decision: Decision; shift: Map<number, number>; lands: number } | null {
  if (moved === null) return null;
  const hands = mixRules(view);
  const decision = placeItems(view, hands, moved);
  const lands = item === NEXT ? NEXT : hands[moved.filter((i) => i !== NEXT).indexOf(item)]!;
  return { decision, shift: itemShift(hands, moved), lands };
}
