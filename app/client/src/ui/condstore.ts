// The watched store as the rule editor's levels are set (issue 467; condition.ts, condfoot.ts): pinned in the foot over
// the sentence, what it holds of its cap, its net per minute and where it heads, the editors' store rows' words
// (storetimes.ts) read off the view. None for a chip's rule (the store behind a chip is never a number), a count or a
// level, or a store with no ledger line.
import type { View } from "../api/types";
import type { Catalog } from "../game/catalog";
import { headingWords, heldWords } from "./storetimes";

/** "Stones · 17 / 18 · -1.35/min · empty in 13m", or "" when there is nothing to state. */
export function watchedWords(catalog: Catalog, view: View, store: string | null): string {
  const line = store ? view.ledger.find((l) => l.store === store) : undefined;
  if (!store || !line) return "";
  const row = view.store_rows.find((r) => r.store === store);
  const per = catalog.format.perMinute(row?.per_hour ?? line.net_per_hour);
  return [catalog.storeTitle(store), heldWords(catalog, view, store), per, ...(row ? [headingWords(catalog, row, view.at)] : [])].join(" · ");
}
