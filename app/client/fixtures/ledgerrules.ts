// FIXTURE, never shipped: ledger rows a rule watches (ui/ledger.ts), on mid's screen with the lessons behind.
// spendrule: a rule smoking the catch while there is some, until under one, is on and draws the catch down; mid's wood
// still falls with no rule on it. behindrule: a rule keeping wood stocked whose mix makes wood, and the forecast still
// empties it; the smoke rule on with the catch full and more coming in.
import type { LedgerLine, Mix, Order, Step, View } from "../src/api/types";
import { BP, Q, R } from "./content";
import { fixtureStep, type Kept } from "./steps";

export type LedgerPhase = "spendrule" | "behindrule";
export const isLedgerRules = (phase: string): phase is LedgerPhase => phase === "spendrule" || phase === "behindrule";

const SMOKE: Order = { when: { kind: "at_least", watched: { kind: "store_value", store: "catch" }, value: 2 * Q, release: Q }, then: { kind: "tap_card", card: "smoke_catch" } };
const KEEP_WOOD: Order = { when: { kind: "at_most", watched: { kind: "store_value", store: "wood" }, value: 10 * Q - 1, release: 20 * Q - 1 }, then: { kind: "switch_mix", mix_id: "Gather by hand" } };
const GATHER: Mix = { id: "Gather by hand", components: [{ kind: "card_share", card: "gather", share_bp: BP }] };

function catchLine(at: number, items: number, by: Array<[string, number]>): LedgerLine {
  const net = by.reduce((a, [, n]) => a + n * R, 0);
  const full = items >= 6 && net > 0;
  return {
    store: "catch", segment: { start: at, start_value: items * Q, rate: full ? 0 : net, limit: net < 0 ? 0 : 6 * Q },
    net_per_hour: net, contributions: by.map(([runner, n]) => ({ runner, per_hour: n * R })),
    empties_at: null, fills_at: null, falling: net < 0, covered: false, starved: false, cap: 6 * Q,
  };
}

export function ledgerRulesStep(phase: LedgerPhase, at: number, kept: Kept = {}, decisions = 0): Step {
  const base = fixtureStep("mid", at, kept, decisions);
  const mid = base.view;
  const spend = phase === "spendrule";
  const wood = mid.ledger.find((l) => l.store === "wood")!;
  const orders = spend ? [SMOKE] : [KEEP_WOOD, SMOKE];
  const catchNow = spend ? catchLine(at, 5, [["smoke_catch", -120]]) : catchLine(at, 6, [["gather", 180], ["smoke_catch", -120]]);
  const view: View = {
    ...mid,
    orders, orders_on: spend ? [true] : [false, true], order_states: spend ? ["on"] : ["waiting", "on"], order_dry: orders.map(() => null),
    mixes: [...mid.mixes, GATHER],
    unlocked: [...mid.unlocked, { category: "card", id: "smoke_catch" }, { category: "store", id: "catch" }],
    ledger: [...mid.ledger.map((l) => (l.store === "wood" && !spend ? { ...wood, covered: true } : l)), catchNow],
  };
  return { ...base, view };
}
