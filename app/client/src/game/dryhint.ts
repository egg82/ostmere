// The first dry store (docs/design/opening-screen.md, the hands strip, "Hint: the first dry store"): read off the view and
// the content only. A card of the running mix has stopped on a store that ran dry, nothing covers that store, and a hands
// card in play that makes it could join the mix: added, it takes the stopped card's share while the store refills
// (CONTRACT.txt, "SPENT"). The ledger marks that line with the quiet dot and the dry store's lesson starts from it
// (game/lessons.ts, DRY_STORE); nothing is built and the mix is never edited for the player.
import type { Mix, View } from "../api/types";
import type { Catalog } from "./catalog";
import { holdsCard, runningMix } from "./mix";
import { editShown } from "./shown";

/** The lesson's subject: the dry store, the mix card stopped on it, and a card in play that makes it. */
export interface DryCue {
  store: string;
  card: string;
  maker: string;
}

/** A hands card among `makers` (Need.makers) that is ready, in play, and not in the running mix (the editor's Add row
 * offers it). */
function makerFor(catalog: Catalog, view: View, mix: Mix, makers: readonly string[]): string | null {
  const maker = view.cards.find((c) => makers.includes(c.card) && catalog.mixable(c.card) && c.blocker === null && c.share_bp === 0 && !holdsCard(mix, c.card));
  return maker?.card ?? null;
}

/** The first card of the running mix, in the view's order, stopped on a starved line nothing covers that a card in play
 * could refill; null when none is, or the strip's Edit has not come. */
export function dryCue(catalog: Catalog, view: View): DryCue | null {
  const mix = runningMix(view);
  if (mix === null || !editShown(catalog, view)) return null;
  const lines = new Map(view.ledger.map((l) => [l.store, l]));
  for (const card of view.cards) {
    if (card.run !== "paused" || card.share_bp === 0 || !catalog.mixable(card.card)) continue;
    for (const need of card.needs) {
      const line = lines.get(need.store);
      if (!line?.starved || line.covered || line.store === catalog.campStore || catalog.stores.get(line.store)?.hidden) continue;
      const maker = makerFor(catalog, view, mix, need.makers);
      if (maker !== null) return { store: need.store, card: card.card, maker };
    }
  }
  return null;
}

/** Some saved mix already holds a card in play and a maker of one of its needs (Need.makers): the save has done what the
 * lesson teaches. */
export function anySelfFedMix(view: View): boolean {
  return view.mixes.some((mix) => view.cards.some((c) => holdsCard(mix, c.card)
    && c.needs.some((n) => n.makers.some((m) => m !== c.card && holdsCard(mix, m)))));
}
