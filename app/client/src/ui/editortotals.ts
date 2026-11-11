// The mix editor's live totals (editor.ts): per minute, now → after, for each store the edit changes, and how long the
// mix runs. "after" is the engine's own dry run of the edit, null until it lands. Rates are facts, never a verdict.
import type { View } from "../api/types";
import type { Catalog } from "../game/catalog";
import { UI } from "../game/text";
import { el } from "./dom";

/** The table's rows, or none when the edit changes nothing yet. `from` is the saved mix being edited (null for a new
 * one): when it runs, Save leaves it running and the second column is "after"; otherwise it is "if run". */
export function totalsRows(catalog: Catalog, view: View, after: View | null, from: string | null): HTMLElement[] {
  const { text, format } = catalog;
  const net = (v: View | null, store: string) => v?.ledger.find((l) => l.store === store)?.net_per_hour ?? 0;
  const stores = [...new Set([...view.ledger, ...(after?.ledger ?? [])].map((l) => l.store))]
    .filter((s) => s !== catalog.campStore && after !== null && net(view, s) !== net(after, s));
  const runsNow = format.runs(view.runs_out_at, view.at), runsAfter = after ? format.runs(after.runs_out_at, after.at) : runsNow;
  if (stores.length === 0 && runsNow === runsAfter) return [];
  const head = el("div", "totals-row totals-head");
  head.append(el("span", "", text.get(UI.perMinuteHead)), el("span", "", text.get(UI.now)), el("span", "", "→"), el("span", "", afterHead(catalog, view, from)));
  const rows = stores.map((s) => {
    const row = el("div", "totals-row");
    row.append(el("span", "totals-store", catalog.storeTitle(s)), el("span", "", format.perMinute(net(view, s))), el("span", "totals-arrow", "→"),
      el("span", "totals-after changed", format.perMinute(net(after, s))));
    return row;
  });
  const runsRow = el("div", "totals-row totals-runs");
  runsRow.append(el("span", "", ""), el("span", "", runsNow), el("span", "totals-arrow", "→"), el("span", "", runsAfter));
  return [head, ...rows, runsRow];
}

/** The second column's head: "after" when Save leaves the edited mix running, else "if run". */
export function afterHead(catalog: Catalog, view: View, from: string | null): string {
  const runs = from !== null && (from === view.running_mix_id || from === view.active_mix_id);
  return catalog.text.get(runs ? UI.after : UI.ifRun);
}
