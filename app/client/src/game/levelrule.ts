// Where a new store rule starts in the quick add (condition.ts): defaultRule's, except on a store a lost fight adds to
// (Catalog.isLevel) that the task takes, whose cure is done when the level is gone.
import type { OrderVerb, View } from "../api/types";
import type { Catalog } from "./catalog";
import { ruleCards } from "./ruleoffers";
import { defaultRule, switchForm, tryRule, valid, type StoreRule, type Test } from "./storerule";

/** What one run of the task takes of `store`, in whole items rounded up (as View.levels reads); 0 when it takes none. */
function take(catalog: Catalog, view: View, then: OrderVerb | null, store: string): number {
  const cards = ruleCards(view, then);
  const quantities = view.cards.filter((c) => cards.includes(c.card)).flatMap((c) => c.needs.filter((n) => n.store === store).map((n) => n.quantity));
  return Math.ceil(Math.max(0, ...quantities) / catalog.content.scales.quantity_per_item);
}

/** The rule a store starts as: for a level the task takes ("reaches"), the smallest rule the page builds at or above one
 * run's take, until empty, its start as the share nearest that many items (the quick add reads shares); any other
 * store's, `defaultRule`. */
export function startRule(catalog: Catalog, view: View | null, then: OrderVerb | null, store: string, test: Test, cap: number): StoreRule {
  const from = view && catalog.isLevel(store) && test === "reaches" ? take(catalog, view, then, store) : 0;
  for (let items = from; from > 0 && items <= cap; items++) {
    if (!valid({ store, test, n: { items }, m: { share: 0 } }, cap)) continue;
    const rule = tryRule({ store, test, n: switchForm({ items }, test, "on", cap), m: { share: 0 } }, cap);
    if (rule) return rule;
  }
  return defaultRule(store, test, cap);
}
