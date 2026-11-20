// #storerows (dev-main.ts): View.store_rows for the screenshot fixture, authored, not the engine's. Each card's flows are
// made up: rest makes wood, tend costs wood and makes flint, look costs a little flint.
import type { Mix, StoreRow, View } from "../src/api/types";
import { BP, Q, R } from "./content";

const FLOWS: Record<string, Record<string, number>> = {
  rest: { wood: 60 },
  tend: { wood: -80, stone: 10 },
  look: { stone: -5 },
};
const HELD: Record<string, number> = { wood: 10, stone: 4 };

/** The stores' rows when `mix` runs: each card's items an hour at its share, summed per store. */
export function storeRowsFor(v: View, mix: Mix | undefined): StoreRow[] {
  const net: Record<string, number> = { wood: 0, stone: 0 };
  const mixed = new Set<string>();
  for (const c of mix?.components ?? []) {
    if (c.kind !== "card_share") continue;
    for (const [store, perHour] of Object.entries(FLOWS[c.card] ?? {})) {
      net[store] = (net[store] ?? 0) + perHour * c.share_bp / BP;
      mixed.add(store);
    }
  }
  return Object.entries(net).map(([store, items]) => {
    const cap = (v.ledger.find((l) => l.store === store)?.cap ?? 0) / Q;
    const held = HELD[store] ?? 0;
    const falling = items < 0, rising = items > 0 && held < cap;
    const secs = falling ? Math.ceil(held * 3600 / -items) : rising ? Math.ceil((cap - held) * 3600 / items) : null;
    return { store, per_hour: Math.round(items * R), mixed: mixed.has(store),
      heading: falling ? "empties" : rising ? "fills" : "steady", at: secs === null ? null : v.at + secs };
  });
}

export const runningMixOf = (v: View): Mix | undefined => v.mixes.find((m) => m.id === (v.running_mix_id ?? v.active_mix_id));
