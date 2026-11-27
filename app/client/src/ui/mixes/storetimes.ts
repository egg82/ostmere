// The editors' store rows (contract/store-rows.txt, "Store rows"): each store a card of the edit makes or costs, or whose rate or
// heading the dry run changes, net per minute now → after, and under it what it holds of its cap now (the ledger's line)
// and where it heads. Read off view.store_rows, the same dry run as the goal rows; the page computes no rate or time.
import type { StoreRow, View } from "../../api/types";
import type { Catalog } from "../../game/page/catalog";
import { UI } from "../../game/page/text";
import { sample } from "../../game/page/clock";
import { el } from "../dom";

/** The rows, or none until the dry run answers. `afterHead` names the second column ("after", "if run"). `touched`: the
 * stores the edit's cards make or cost, for an edit StoreRow.mixed does not describe (a person's split, which is the town's
 * mix, where mixed is the hands'). */
export function storeRows(catalog: Catalog, view: View, after: View | null, afterHead: string, touched?: ReadonlySet<string>): HTMLElement[] {
  if (after === null) return [];
  const was = new Map(view.store_rows.map((r) => [r.store, r]));
  const shown = after.store_rows.flatMap((r) => {
    const before = was.get(r.store);
    return r.store !== catalog.campStore && before && ((touched ? touched.has(r.store) : r.mixed) || before.per_hour !== r.per_hour || before.heading !== r.heading)
      ? [{ r, before }] : [];
  });
  if (shown.length === 0) return [];
  const { text, format } = catalog;
  const head = el("div", "totals-row totals-head store-head");
  head.append(el("span", "", text.get(UI.perMinuteHead)), el("span", "", text.get(UI.now)), el("span", "", "→"), el("span", "", afterHead));
  return [head, ...shown.flatMap(({ r, before }) => {
    const row = el("div", "totals-row store-row");
    row.append(el("span", "totals-store", catalog.storeTitle(r.store)), el("span", "", format.perMinute(before.per_hour)),
      el("span", "totals-arrow", "→"), el("span", r.per_hour !== before.per_hour ? "totals-after changed" : "totals-after", format.perMinute(r.per_hour)));
    const held = heldWords(catalog, view, r.store);
    const where = headingWords(catalog, r, after.at);
    return [row, el("div", r.heading === before.heading ? "goal-binds" : `goal-binds heading-turned ${r.heading}`, held ? `${held} · ${where}` : where)];
  })];
}

/** The stores these cards make or cost, for storeRows' `touched`. */
export function touchedBy(catalog: Catalog, cards: Iterable<string>): Set<string> {
  return new Set([...cards].flatMap((card) => [...(catalog.cards.get(card)?.makes ?? []), ...(catalog.cards.get(card)?.takes ?? [])]));
}

/** What the store holds of its cap at the view's time ("18 / 18"), as its ledger line reads; empty with no line. */
export function heldWords(catalog: Catalog, view: View, store: string): string {
  const line = view.ledger.find((l) => l.store === store);
  return line ? catalog.format.amount(sample(line.segment, view.at), line.cap) : "";
}

/** Where the store heads: empty in / full in the time left, or steady. */
export function headingWords(catalog: Catalog, r: StoreRow, at: number): string {
  const { text, format } = catalog;
  if (r.heading === "steady" || r.at === null) return text.get(UI.storeSteady);
  if (r.heading === "empties") return r.at <= at ? text.get(UI.storeEmpty) : text.fill(UI.empties, { d: format.duration(r.at - at) });
  return text.fill(UI.fills, { d: format.duration(r.at - at) });
}
