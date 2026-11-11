// Ledger offers beyond a red line (game/cues.ts; ui/ledger.ts): a later order card for a store supersedes the earlier
// once offered (the earlier stays on offer until then); a rising line's card (an at_least on a task's input) is
// marked once its line is full or rising, kept through a dip until a rule is set. A line is marked, never offered a build.
import { install } from "./fake-dom";
import { testContext } from "./context";
import { fixtureContent, Q } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { Decision, LedgerLine, Order, OrderCard, View } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { offeredCard, risingCard, risingLine } from "../src/game/cues";
import { Ledger } from "../src/ui/ledger";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const catalog = new Catalog(fixtureContent);
const card = (store: string, n = 0): OrderCard => fixtureContent.order_cards.filter((c) => c.store === store)[n]!;
const [WOOD, WOOD_RETUNE, CATCH] = [card("wood"), card("wood", 1), card("catch")];
const base = fixtureStep("covered", 100).view;   // the wood rule (at_most 10, until 20) set; every line white
const withLedger = (v: View): View => ({ ...v, unlocked: [...v.unlocked, { category: "feature", id: "ledger" }] });
const unlock = (v: View, category: "feature" | "card", id: string): View => ({ ...v, unlocked: [...v.unlocked, { category, id }] });

function catchLine(items: number, perHour: number): LedgerLine {
  return {
    store: "catch", segment: { start: 100, start_value: items * Q, rate: perHour * 1000, limit: perHour > 0 ? 6 * Q : null },
    net_per_hour: perHour * 1000, contributions: [], empties_at: null, fills_at: null, falling: perHour < 0, covered: false, starved: false, cap: 6 * Q,
  };
}

// Which card is on offer: the later one supersedes, but only once its own offered_after holds.
expect("before its unlock, the shipped card", offeredCard(catalog, base, "wood"), WOOD);
expect("after it, the later card", offeredCard(catalog, unlock(base, "feature", "stock"), "wood"), WOOD_RETUNE);
expect("the rising card waits for its task", offeredCard(catalog, base, "catch"), undefined);

// The rising card's shape and its line.
expect("an at_least on a side lane's input is a rising card", risingCard(catalog, CATCH), true);
expect("an at_most is not", risingCard(catalog, { ...CATCH, when: { kind: "at_most", watched: { kind: "store_value", store: "catch" }, value: 4 * Q, release: 4 * Q } }), false);
expect("a hands task taking from the store is (handsrising.test.ts)", risingCard(catalog, { ...CATCH, store: "wood", then: { kind: "tap_card", card: "lean_to" } }), true);
expect("a side lane task that takes other stores is not", risingCard(catalog, { ...CATCH, store: "wood" }), false);
expect("rising", risingLine(catchLine(2, 3), 100), true);
expect("full, flat", risingLine(catchLine(6, 0), 100), true);
expect("full by its time, sampled", risingLine({ ...catchLine(5, 0), segment: { start: 0, start_value: 5 * Q, rate: Q / 100, limit: 6 * Q } }, 100), true);
expect("flat below full", risingLine(catchLine(3, 0), 100), false);
expect("falling", risingLine(catchLine(5, -2), 100), false);

function rig(): { ledger: Ledger; root: HTMLElement; decided: Decision[] } {
  const { ctx, got } = testContext();
  const ledger = new Ledger(ctx);
  document.body.replaceChildren(ledger.root);
  return { ledger, root: ledger.root, decided: got.decided };
}
const offers = (root: HTMLElement): string[] => [...root.querySelectorAll(".line-order")].map((n) => n.textContent ?? "");
const marks = (root: HTMLElement): number => root.querySelectorAll(".new-dot").length;   // the quiet mark on a line a rule could answer

// The rising offer: drawn under a rising line, calm (not the alarm's), kept through a dip, gone once set.
{
  const smoking = withLedger(unlock(base, "card", "smoke_catch"));
  const at = (line: LedgerLine, orders: Order[] = smoking.orders): View => ({ ...smoking, orders, orders_on: orders.map(() => false), ledger: [...smoking.ledger, line] });
  const r = rig();
  r.ledger.update(at(catchLine(1, 0)), null);
  expect("flat and not full: no mark", marks(r.root), 0);
  r.ledger.update(at(catchLine(2, 3)), null);
  expect("rising: the line is marked, with no row and nothing built", [marks(r.root), offers(r.root), r.decided], [1, [], []]);
  r.ledger.update(at(catchLine(1, -4)), null);
  expect("kept through a dip", marks(r.root), 1);
  const set = [...smoking.orders, { when: CATCH.when, then: CATCH.then }];
  r.ledger.update(at(catchLine(2, 3), set), null);
  expect("gone once its rule is set", marks(r.root), 0);
  r.ledger.update(at(catchLine(1, 0)), null);
  expect("the rule removed with the line flat: not kept from before", marks(r.root), 0);
}

// A red line is offered its card whatever draws it down, the hands' own tap included: shown.drawnDown decides only when
// a line with no offer joins. The pacing simulator takes her first rule on this (tests/daytwo/policy.her_first_rule).
{
  const tapped = (by: string | null): View => ({
    ...withLedger(base), orders: [], orders_on: [],
    lanes: base.lanes.map((l) => (l.lane === "hands" ? { ...l, running_card: "gather" } : l)),
    ledger: [...base.ledger.filter((l) => l.store !== "wood"), {
      store: "wood", segment: { start: 100, start_value: 14 * Q, rate: by === null ? 0 : -120_000, limit: by === null ? null : 0 },
      net_per_hour: by === null ? 0 : -120_000,
      contributions: by === null ? [] : [{ runner: by, per_hour: -120_000 }], empties_at: null, fills_at: null,
      falling: by !== null, covered: false, starved: false, cap: 40 * Q,
    }],
  });
  const r = rig();
  r.ledger.update(tapped("gather"), null);
  expect("drawn down only by the hands' tap: marked", marks(r.root), 1);
  const flat = rig();
  flat.ledger.update(tapped(null), null);
  expect("not falling: no mark", marks(flat.root), 0);
}

// Not offered before its task exists, however the line rises.
{
  const r = rig();
  r.ledger.update({ ...withLedger(base), ledger: [...base.ledger, catchLine(6, 3)] }, null);
  expect("no task, no mark", marks(r.root), 0);
}
