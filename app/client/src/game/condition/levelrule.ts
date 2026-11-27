// Where a new store rule starts in the quick add (condition.ts): defaultRule's, except on a store a lost fight adds to
// (Catalog.isLevel), in the whole items its chip shows; for one the task takes, its cure is done when the level is gone.
import type { OrderVerb, View } from "../../api/types";
import type { Catalog } from "../page/catalog";
import { ruleCards } from "./ruleoffers";
import { defaultRule, itemsRule, valid, type StoreRule, type Test } from "./storerule";

/** What one run of the task takes of `store`, in whole items rounded up (as View.levels reads; a take of any size reads
 * as 1 at least, a drain's included, which Card.needs no longer lists); 0 when it takes none. */
function take(catalog: Catalog, view: View, then: OrderVerb | null, store: string): number {
  const cards = ruleCards(view, then).filter((c) => catalog.cards.get(c)?.takes.includes(store));
  const quantities = view.cards.filter((c) => cards.includes(c.card)).flatMap((c) => c.needs.filter((n) => n.store === store).map((n) => n.quantity));
  return cards.length === 0 ? 0 : Math.max(1, Math.ceil(Math.max(0, ...quantities) / catalog.content.scales.quantity_per_item));
}

/** The rule a store starts as: a level the task takes ("reaches") starts at the smallest rule the page builds at or above
 * one run's take, until empty; any other level, `itemsRule`. A level is always whole items, as its chip shows it. Any
 * other store's is `defaultRule`. */
export function startRule(catalog: Catalog, view: View | null, then: OrderVerb | null, store: string, test: Test, cap: number): StoreRule {
  if (!catalog.isLevel(store)) return defaultRule(store, test, cap);
  const from = view && test === "reaches" ? take(catalog, view, then, store) : 0;
  for (let items = from; from > 0 && items <= cap; items++) {
    const rule: StoreRule = { store, test, n: { items }, m: { items: 1 } };
    if (valid(rule, cap, catalog.risesInSteps(store))) return rule;
  }
  return itemsRule(store, test, cap);
}
