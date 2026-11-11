// A rising line's card whose task is a hands build (an at_least on a store the build takes, staged builds run by a
// standing order): marked on its line like a side lane's; nothing is built from the line. The side lane's case (lineoffers.test.ts) and a red line's are unchanged.
import { install } from "./fake-dom";
import { testContext } from "./context";
import { fixtureContent, Q } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { LedgerLine, OrderCard, View } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { risingCard } from "../src/game/cues";
import { Ledger } from "../src/ui/ledger";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const BUILD: OrderCard = {
  store: "stone", when: { kind: "at_least", watched: { kind: "store_value", store: "stone" }, value: 6 * Q, release: 6 * Q },
  then: { kind: "tap_card", card: "lean_to" }, offered_after: null, chip: null, after_end: false,
};
const catalog = new Catalog({ ...fixtureContent, order_cards: [...fixtureContent.order_cards, BUILD] });
const base = fixtureStep("covered", 100).view;
const view = (line: LedgerLine): View => ({ ...base, unlocked: [...base.unlocked, { category: "feature", id: "ledger" }], ledger: [...base.ledger, line] });

function stoneLine(items: number, perHour: number): LedgerLine {
  return {
    store: "stone", segment: { start: 100, start_value: items * Q, rate: perHour * 1000, limit: perHour > 0 ? 6 * Q : null },
    net_per_hour: perHour * 1000, contributions: [], empties_at: null, fills_at: null, falling: perHour < 0, covered: false, starved: false, cap: 6 * Q,
  };
}

function rig(): { ledger: Ledger; root: HTMLElement; decided: unknown[] } {
  const { ctx, got } = testContext(undefined, catalog);
  const ledger = new Ledger(ctx);
  document.body.replaceChildren(ledger.root);
  return { ledger, root: ledger.root, decided: got.decided };
}
const offers = (root: HTMLElement): string[] => [...root.querySelectorAll(".line-order")].map((n) => n.textContent ?? "");
const marks = (root: HTMLElement): number => root.querySelectorAll(".new-dot").length;

expect("a hands build taking the store is a rising card", risingCard(catalog, BUILD), true);
expect("a hands task that takes other stores is not", risingCard(catalog, { ...BUILD, store: "warmth" }), false);

{
  const r = rig();
  r.ledger.update(view(stoneLine(1, 0)), null);
  expect("flat and not full: no mark", marks(r.root), 0);
  r.ledger.update(view(stoneLine(6, 0)), null);
  expect("full: the line is marked, with no row and nothing built", [marks(r.root), offers(r.root), r.decided], [1, [], []]);
}
