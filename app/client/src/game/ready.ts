// When a card waiting on a store will turn ready by itself, as far as the page can see the promise kept
// (docs/design/opening-screen.md, "When ready"). The engine's ready_at holds under the current rates; a rule on that
// store that is on and lets go below the need stops it short (the rule's own release, from view.orders), so no
// countdown or When ready is drawn for it. A card waiting on its store's whole cap turns ready when the store fills,
// so its time is the forecast's fill, which plays out the rules that take the hands from the mix; ready_at, under
// the current rates, would come late by every tap they make. Never a countdown the engine's time cannot keep.
import type { Card, View } from "../api/types";
import { fullAt } from "./forecast";

/** The card's ready time, or null: none from the engine, a rule on its store stops the store short of the need, or
 * it waits on a full store the forecast does not fill by its horizon. */
export function keptReadyAt(view: View, card: Card): number | null {
  const at = card.blocker?.ready_at ?? null;
  if (at === null || stopsShort(view, card)) return null;
  const full = fullStore(view, card);
  return full === null ? at : fullAt(view, full, view.at);
}

/** The store the card's blocker waits on when it asks for the store's whole cap, or null. */
function fullStore(view: View, card: Card): string | null {
  const when = card.blocker?.condition;
  if (when?.kind !== "at_least" || when.watched.kind !== "store_value") return null;
  const { store } = when.watched;
  const line = view.ledger.find((l) => l.store === store);
  return line !== undefined && when.value >= line.cap ? store : null;
}

/** The card waits on a store the player has never been shown (the night): its countdown is all the page draws of it,
 * with no have/need and no When ready (CONTRACT.txt, "The client may"; docs/design/opening-screen.md, "When ready"). */
export function waitsOnUnseen(view: View, card: Card): boolean {
  const when = card.blocker?.condition;
  if (when?.kind !== "at_least" || when.watched.kind !== "store_value") return false;
  const { store } = when.watched;
  return !view.unlocked.some((u) => u.category === "store" && u.id === store);
}

/** An "under x, until y" rule on the blocker's store that is on now lets go (past y) before the store reaches the need. */
function stopsShort(view: View, card: Card): boolean {
  const when = card.blocker?.condition;
  if (when?.kind !== "at_least" || when.watched.kind !== "store_value") return false;
  const { store } = when.watched;
  const need = when.value;
  return view.orders.some((o, i) => view.orders_on[i] === true && o.when.kind === "at_most"
    && o.when.watched.kind === "store_value" && o.when.watched.store === store && o.when.release + 1 < need);
}
