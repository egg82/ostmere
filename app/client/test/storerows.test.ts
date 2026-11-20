// The editors' store rows (ui/storetimes.ts; CONTRACT.txt, "Store rows"): a row per store the edit's cards touch or whose
// rate or heading the dry run changes, net per minute now → after, with where it heads under it; the heading is marked
// only when its direction turns.
import { install } from "./fake-dom";
import { fixtureStep } from "../fixtures/steps";
import { Catalog } from "../src/game/catalog";
import { fixtureContent } from "../fixtures/content";
import type { StoreRow, View } from "../src/api/types";
import { storeRows } from "../src/ui/storetimes";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const catalog = new Catalog(fixtureContent);
const R = fixtureContent.scales.rate_per_item_hour;
const base = fixtureStep("rulestab", 100, { orders: [], extra: [] }).view;
const row = (store: string, per: number, heading: StoreRow["heading"], at: number | null, mixed = false): StoreRow =>
  ({ store, per_hour: per * R, heading, at, mixed });
const at = (rows: StoreRow[]): View => ({ ...base, store_rows: rows });
const out = (els: HTMLElement[]): { text: string[]; turned: string[] } => ({
  text: els.map((e) => e.textContent ?? ""),
  turned: els.filter((e) => e.className.includes("heading-turned")).map((e) => e.textContent ?? ""),
});

expect("no answer yet", storeRows(catalog, at([row("wood", 60, "steady", null)]), null, "after").length, 0);
expect("nothing moved, nothing mixed", storeRows(catalog, at([row("wood", 60, "steady", null)]), at([row("wood", 60, "steady", null)]), "after").length, 0);

// a store the edit's cards touch is listed though its rate holds; one the edit moves is listed; the rest stay out
{
  const now = at([row("wood", 60, "fills", 100 + 3600), row("stone", 10, "steady", null), row("flint", 5, "steady", null)]);
  const then = at([row("wood", 60, "fills", 100 + 3600, true), row("stone", -20, "empties", 100 + 1800), row("flint", 5, "steady", null)]);
  const got = out(storeRows(catalog, now, then, "after"));
  expect("head, wood, its heading, stone, its heading", got.text,
    ["per minutenow→after", "Dead wood+1/min→+1/min", "full in 1 h", "Flint+0.16/min→-0.33/min", "30 m 0 s left"]);
  expect("only the turned heading is marked", got.turned, ["30 m 0 s left"]);
}

// a store already at 0 and falling reads empty, and the camp's own store is never listed
{
  const now = at([row("wood", 0, "steady", null), { ...row(catalog.campStore, 0, "steady", null) }]);
  const then = at([row("wood", -30, "empties", 100), row(catalog.campStore, -5, "empties", 200)]);
  expect("empty now, no camp row", out(storeRows(catalog, now, then, "if run")).text, ["per minutenow→if run", "Dead wood0/min→-0.5/min", "empty"]);
}
