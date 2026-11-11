// A card's hint marks (game/hints.ts): the quiet dot where the player's mix could take a card they keep tapping, and the
// second mix's lesson's trigger on the card it starts from (game/lessons.ts, SECOND_MIX), which stays once the dot is
// touched, while the detection holds.
import type { Catalog } from "../game/catalog";
import { cardHints, secondMixCard } from "../game/hints";
import type { Keeps } from "../game/keeps";
import type { RepeatedTap, View } from "../api/types";
import { markNew, unmark } from "./fresh";

/** What a card panel's update marks: the cards that get the dot, and the one the second mix's lesson starts from. */
export interface CardHints { dots: ReadonlySet<string>; lesson: string | null }

export function cardHintsNow(catalog: Catalog, view: View, keeps: Keeps, lesson: string | null, taps: readonly RepeatedTap[]): CardHints {
  return { dots: new Set(cardHints(catalog, view, keeps, lesson, taps)), lesson: secondMixCard(catalog, view, keeps, taps) };
}

/** The card's dot (kept once touched, by `keep`) and its lesson trigger; a dot that is another mark's (`marked`) stays. */
export function hintCard(node: HTMLElement, card: string, hints: CardHints, keep: () => void, marked: boolean): void {
  if (hints.dots.has(card)) markNew(node, keep);
  else if (!marked) unmark(node);
  if (hints.lesson === card) node.dataset.teach = "mix-hint";   // the card node carries its data-card (cards.ts)
  else if (node.dataset.teach === "mix-hint") delete node.dataset.teach;
}
