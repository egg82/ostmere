// Kinds of one card (CardInfo.variant_of: the pot's stews) are one card on the Tasks page, with a picker of the kinds in
// view (contract/, "Cards"). The card shows the kind the player picked, else one at work, else the first.
import type { Card, View } from "../../api/types";
import type { Catalog } from "../page/catalog";

/** The card `card` is a kind of, or null for a card of its own. */
export function variantOf(catalog: Catalog, card: string): string | null {
  return catalog.cards.get(card)?.variant_of ?? null;
}

/** Each lead's kinds among `cards`, in their order there; a lead with one kind in view is left out (no picker). */
export function kindsByLead(catalog: Catalog, cards: readonly Card[]): Map<string, Card[]> {
  const by = new Map<string, Card[]>();
  for (const c of cards) {
    const lead = variantOf(catalog, c.card);
    if (lead !== null) by.set(lead, [...(by.get(lead) ?? []), c]);
  }
  return new Map([...by].filter(([, kinds]) => kinds.length > 1));
}

/** The kind the one card shows: `picked` while in view, else one a lane runs or a mix holds, else the first. */
export function shownKind(view: View, kinds: readonly Card[], picked: string | null): string | null {
  const running = new Set(view.lanes.flatMap((l) => (l.running_card ? [l.running_card] : [])));
  return (kinds.find((c) => c.card === picked) ?? kinds.find((c) => running.has(c.card) || c.by !== null) ?? kinds[0])?.card ?? null;
}

/** A kind's name on the picker: the store its completions land first (CardInfo.makes). */
export function kindLabel(catalog: Catalog, card: string): string {
  const store = catalog.cards.get(card)?.makes[0];
  return store ? catalog.storeLabel(store) : catalog.cardLabel(card);
}
