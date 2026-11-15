// FIXTURE, never shipped: rules with guards and fallbacks on rulestab's Rules tab (docs/design/rule-guards.md, "How the
// page words it"), for screenshots. guards: the wood rule waits with a fallback mix; the warmth rule is paused, Smoked
// full and its guard held; the tired rule's mix runs; the smoke lane's rule smokes the catch, or else roots, with a
// guard that does not hold, and runs its fallback.
import type { LedgerLine, Order, Step, View } from "../src/api/types";
import { BP, Q } from "./content";
import { fixtureStep, type Kept } from "./steps";

export type GuardsPhase = "guards";
export const isGuards = (phase: string): phase is GuardsPhase => phase === "guards";

const SMOKED_FULL = { kind: "at_least" as const, watched: { kind: "store_value" as const, store: "smoked" }, value: BP, release: BP, value_of_cap: true, release_of_cap: true };
const WOOD_UNDER_5 = { kind: "at_most" as const, watched: { kind: "store_value" as const, store: "wood" }, value: 5 * Q - 1, release: 6 * Q - 1, value_of_cap: false, release_of_cap: false };
const SMOKE: Order = {
  when: { kind: "at_least", watched: { kind: "store_value", store: "catch" }, value: 2 * Q, release: Q, value_of_cap: false, release_of_cap: false },
  then: { kind: "tap_card", card: "smoke_catch" }, unless: [SMOKED_FULL, WOOD_UNDER_5], or_else: [{ kind: "tap_card", card: "smoke_roots" }],
};

function line(at: number, store: string, items: number, cap: number): LedgerLine {
  return { store, segment: { start: at, start_value: items * Q, rate: 0, limit: null }, net_per_hour: 0, contributions: [], empties_at: null, fills_at: null, falling: false, covered: false, starved: false, cap: cap * Q };
}

export function guardsStep(_phase: GuardsPhase, at: number, kept: Kept = {}, decisions = 0): Step {
  const base = fixtureStep("rulestab", at, kept, decisions);
  const v = base.view;
  const [wood, warmth, tired] = v.orders as [Order, Order, Order, ...Order[]];
  const orders: Order[] = [{ ...wood, or_else: [{ kind: "switch_mix", mix_id: "Rest by the fire" }] }, { ...warmth, unless: [SMOKED_FULL] }, tired, SMOKE];
  const view: View = {
    ...v,
    orders, orders_on: [false, true, true, true], order_states: ["waiting", "paused", "on", "on"], order_dry: orders.map(() => null),
    order_guards: [[], [{ on: true, lets_go: 11 * Q }], [], [{ on: false, lets_go: 11 * Q }, { on: false, lets_go: 6 * Q - 1 }]],
    order_doing: [null, null, 0, 1],
    unlocked: [...v.unlocked, ...["smoke_catch", "smoke_roots"].map((id) => ({ category: "card" as const, id })), ...["catch", "smoked", "roots"].map((id) => ({ category: "store" as const, id }))],
    ledger: [...v.ledger, line(at, "catch", 4, 6), line(at, "smoked", 12, 12), line(at, "roots", 6, 24)],
    lanes: [...v.lanes, { lane: "smoke", running_card: "smoke_roots", completes_at: at + 40, order: 3 }],
  };
  return { ...base, view };
}
