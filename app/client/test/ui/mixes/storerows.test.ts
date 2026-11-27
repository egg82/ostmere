// The editors' store rows (ui/mixes/storetimes.ts; contract/store-rows.txt, "Store rows"): a row per store the edit's cards touch or whose
// rate or heading the dry run changes, net per minute now → after, with what it holds of its cap and where it heads under
// it; the heading is marked only when its direction turns.
import { install } from "../../fake-dom";
import { fixtureStep } from "../../../fixtures/steps";
import { Catalog } from "../../../src/game/page/catalog";
import { fixtureContent } from "../../../fixtures/content";
import type { StoreRow, View } from "../../../src/api/types";
import { storeRows } from "../../../src/ui/mixes/storetimes";

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
  expect("head, wood, what it holds and its heading, stone, the same", got.text,
    ["per minutenow→after", "Dead wood+1/min→+1/min", "14 / 40 · full in 1 h", "Flint+0.16/min→-0.33/min", "3 / 20 · 30 m 0 s left"]);
  expect("only the turned heading is marked", got.turned, ["3 / 20 · 30 m 0 s left"]);
  const unlisted = { ...now, ledger: now.ledger.filter((l) => l.store !== "wood") };
  expect("a store with no ledger line shows its heading alone", out(storeRows(catalog, unlisted, then, "after")).text[2], "full in 1 h");
}

// a store already at 0 and falling reads empty, and the camp's own store is never listed
{
  const camp = catalog.campStore;
  if (camp === null) throw new Error("the fixture content has no camp store");
  const now = { ...at([row("wood", 0, "steady", null), row(camp, 0, "steady", null)]), ledger: [] };
  const then = at([row("wood", -30, "empties", 100), row(camp, -5, "empties", 200)]);
  expect("empty now, no camp row", out(storeRows(catalog, now, then, "if run")).text, ["per minutenow→if run", "Dead wood0/min→-0.5/min", "empty"]);
}
