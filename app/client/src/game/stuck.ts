// A person with nothing to do (issue 467): every card holding a share of their time is stopped, paused or spent
// (CONTRACT.txt, "SPENT"), and no tap holds their lane, so the split they set runs nothing and moving it between those
// cards cannot help. The page says so and offers the tasks they could run now; it never picks one (the game does not
// choose for the player). All of it is read off the view: Card.run, spent_store, full_store and the needs it serves.
import type { Card, View } from "../api/types";
import type { Catalog } from "./catalog";
import { sample } from "./clock";

/** A stopped card and why: spent on a store nothing makes again, paused with no room in a store it fills, or paused
 * waiting on a store it needs (the first need short now; null when none reads short). */
export interface Stopped { card: string; why: "spent" | "full" | "dry"; store: string | null }

function stopped(card: Card): boolean {
  return card.run === "paused" || card.run === "spent";
}

/** The first of the card's needs the store falls short of now. */
function shortNeed(card: Card, at: number): string | null {
  return card.needs.find((n) => sample(n.segment, at) < n.quantity)?.store ?? null;
}

/** Why each held card of `lane` is stopped, in view order; null unless the lane holds a share, every card holding one is
 * paused or spent, and no tap holds the lane. */
export function stuckOf(catalog: Catalog, view: View, lane: string): Stopped[] | null {
  if (view.lanes.find((l) => l.lane === lane)?.running_card) return null;
  const held = view.cards.filter((c) => c.share_bp > 0 && catalog.laneOf(c.card) === lane);
  if (held.length === 0 || !held.every(stopped)) return null;
  return held.map((c) => (c.run === "spent" ? { card: c.card, why: "spent", store: c.spent_store }
    : c.full_store !== null ? { card: c.card, why: "full", store: c.full_store } : { card: c.card, why: "dry", store: shortNeed(c, view.at) }));
}

/** The tasks of `lane` that could run now and hold no share yet: open (no blocker), uncapped (the town's mix holds no
 * capped card), not stopped, every need met now. In view order. */
export function runnableFor(catalog: Catalog, view: View, lane: string): string[] {
  return view.cards.filter((c) => catalog.laneOf(c.card) === lane && c.share_bp === 0 && c.cap === null && c.blocker === null
    && !stopped(c) && shortNeed(c, view.at) === null).map((c) => c.card);
}
