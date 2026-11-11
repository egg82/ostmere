// The rule offers (the ledger's, the strip's chip rest offer, and the repeated-switch offer) stop at the served bound,
// Content.limits.max_orders, as the Rules tab does (test/limits.test.ts): another rule would be refused as a 422.
import { install } from "./fake-dom";
import { testContext } from "./context";
import { fixtureContent, Q } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { LedgerLine, View } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { chipCards } from "../src/game/cues";
import { hintedSwitch } from "../src/game/ruleoffers";
import { Ledger } from "../src/ui/ledger";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const catalog = new Catalog(fixtureContent);
const { max_orders } = fixtureContent.limits;
const rule = fixtureStep("restoffer", 100).view.orders[0]!;
const filled = (v: View, n: number): View =>
  ({ ...v, orders: Array.from({ length: n }, () => rule), orders_on: Array.from({ length: n }, () => false) });

// The strip's chip offer.
const rest = fixtureStep("restoffer", 100).view;
expect("chip: room", chipCards(catalog, filled(rest, max_orders - 1), true)[0]?.store, "energy");
expect("chip: full", chipCards(catalog, filled(rest, max_orders), true)[0], undefined);

// The repeated-switch offer.
const mid = { ...fixtureStep("mid", 100).view, orders: [], orders_on: [] };
const repeat = { chip: "cold", mix_id: mid.active_mix_id as string, count: 3 };
expect("repeat: room", hintedSwitch(catalog, filled(mid, max_orders - 1), [repeat], () => false) !== null, true);
expect("repeat: full", hintedSwitch(catalog, filled(mid, max_orders), [repeat], () => false), null);

// The ledger's offer under a rising line.
const line: LedgerLine = {
  store: "catch", segment: { start: 100, start_value: 2 * Q, rate: 3000, limit: 6 * Q },
  net_per_hour: 3000, contributions: [], empties_at: null, fills_at: null, falling: false, covered: false, starved: false, cap: 6 * Q,
};
const smoking0 = fixtureStep("covered", 100).view;
const smoking: View = { ...smoking0, unlocked: [...smoking0.unlocked, { category: "feature", id: "ledger" }, { category: "card", id: "smoke_catch" }] };
const offers = (v: View): number => {
  const ledger = new Ledger(testContext().ctx);
  document.body.replaceChildren(ledger.root);
  const f = filled(smoking, v.orders.length);
  ledger.update({ ...f, ledger: [...f.ledger, line] }, null);
  return ledger.root.querySelectorAll(".new-dot").length;
};
expect("ledger: room", offers(filled(smoking, max_orders - 1)), 1);
expect("ledger: full", offers(filled(smoking, max_orders)), 0);
