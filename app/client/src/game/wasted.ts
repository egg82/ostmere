// A card working into full stores (issue 467): it runs on its share (run full) while every store it makes is at its cap,
// so its work is thrown away; a card that draws a store nothing refills stops instead (Card.full_store, contract/full-output.txt,
// "FULL OUTPUT"). Read off the ledger at the view's time; a store with no ledger line is not known full, so neither is the card.
import type { Card, View } from "../api/types";
import type { Catalog } from "./catalog";
import { sample } from "./clock";

/** The first store `card` makes when it runs on a share and every store it makes is full; null otherwise. */
export function wastedOn(catalog: Catalog, view: View, card: Card): string | null {
  const makes = catalog.cards.get(card.card)?.makes ?? [];
  if (card.run !== "full" || card.by !== "mix" || makes.length === 0) return null;
  const full = makes.every((store) => {
    const line = view.ledger.find((l) => l.store === store);
    return line !== undefined && sample(line.segment, view.at) >= line.cap;
  });
  return full ? makes[0]! : null;
}
