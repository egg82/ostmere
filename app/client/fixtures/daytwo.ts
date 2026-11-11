// FIXTURE, never shipped: day two's shapes (CONTRACT.txt, "A lane run by rules" and "Offers"), with placeholder ids,
// built on the rest rule's ended camp (steps.ts, restrule).
//   ruled:    a lane run by rules at work: its always rule taps Chop logs; a one-off rule passed over, a store rule
//             waiting, and a second always rule outranked by the first; its cards stay out of Tasks and Completed.
//   offered:  the same lane free, and an offer shown in this step with its line (its row comes after the line);
//   bank:     an offer whose answers install modifiers and put a store in, open (their costs state the amounts);
//   answered: the offer answered ("wait"); answering again is refused (422) and the page asks again.
import type { Card, LaneBar, Offer, Order, OrderState, Step, View } from "../src/api/types";
import { BP, Q } from "./content";
import { fixtureStep, type Kept } from "./steps";

export type DayTwoPhase = "ruled" | "offered" | "bank" | "answered";
export const DAY_TWO: readonly DayTwoPhase[] = ["ruled", "offered", "bank", "answered"];

export function isDayTwo(phase: string): phase is DayTwoPhase {
  return (DAY_TWO as readonly string[]).includes(phase);
}

const always = (card: string): Order => ({ when: { kind: "after_time", at: 0 }, then: { kind: "tap_card", card } });
const HAUL_LOW: Order = { when: { kind: "at_most", watched: { kind: "store_value", store: "wood" }, value: 3 * Q, release: 8 * Q }, then: { kind: "tap_card", card: "haul" } };
/** The lane's rules after the hands' own: a done one-off, a store rule, the always rule at work, one it outranks. */
export const LANE_RULES: Order[] = [always("fetch"), HAUL_LOW, always("chop"), always("haul")];

function laneCard(at: number, id: string, running: boolean): Card {
  return {
    card: id, completions: running ? 2 : 0, cap: null, bar: { start: at, start_value: running ? 4 * BP : 0, rate: running ? BP : 0, limit: null },
    bar_total: 12 * BP, by: running ? "tap" : null, completes_at: running ? at + 8 : null, share_bp: 0, run: null, blocker: null, cuts_in: false, spent_store: null, gained: [], tap_s: 12, needs: [],
  };
}

function offerOf(phase: DayTwoPhase): Offer[] {
  if (phase === "ruled") return [];
  if (phase === "bank") return [{ offer: "bank", answer: null, answers: [{ answer: "hers", card: null, takes_s: null }, { answer: "his", card: null, takes_s: null }] }];
  return [{ offer: "ask", answer: phase === "answered" ? "wait" : null, answers: [{ answer: "wait", card: null, takes_s: null }, { answer: "go", card: "haul", takes_s: 750 }] }];
}

const same = (a: Order, b: Order): boolean => JSON.stringify(a) === JSON.stringify(b);

function dayTwo(phase: DayTwoPhase, v: View, at: number, kept: Kept): View {
  const busy = phase === "ruled";
  const orders = kept.orders ?? [...v.orders, ...LANE_RULES];
  const chopAt = orders.findIndex((o) => same(o, always("chop")));
  const order = busy && chopAt >= 0 ? chopAt : null;
  const own = (o: Order): number => v.orders.findIndex((p) => same(o, p));   // the hands' rules stand as restrule has them
  const state = (o: Order, i: number): OrderState => (o.then.kind === "switch_mix" ? v.order_states[own(o)] ?? "waiting"
    : o.then.kind === "tap_card" && o.then.card === "fetch" ? "passed_over" : o.when.kind !== "after_time" ? "waiting"
      : order !== null && order < i ? "outranked" : "on");
  const on = (o: Order): boolean => (o.then.kind === "switch_mix" ? v.orders_on[own(o)] ?? false : o.when.kind === "after_time");
  const lane: LaneBar = { lane: "helper", running_card: busy ? "chop" : null, completes_at: busy ? at + 8 : null, order };
  return {
    ...v, orders, orders_on: orders.map(on), order_states: orders.map(state),
    lanes: [...v.lanes, lane], cards: [...v.cards, laneCard(at, "chop", busy), laneCard(at, "haul", false)],
    completed: [...v.completed, { card: "fetch", completions: 1 }], offers: offerOf(phase),
    unlocked: [...v.unlocked, ...["chop", "haul", "fetch"].map((id) => ({ category: "card" as const, id })), ...(phase === "ruled" ? [] : [{ category: "feature" as const, id: "yard" }])],
  };
}

export function dayTwoStep(phase: DayTwoPhase, at: number, kept: Kept = {}, decisions = 0): Step {
  const base = fixtureStep("restrule", at, { ...kept, orders: undefined }, decisions);
  const lines = phase === "offered" ? [{ at, seq: 0, key: "line.offer", card: null }] : phase === "answered" ? [{ at, seq: 0, key: "line.4", card: null }] : [];
  return { ...base, view: dayTwo(phase, base.view, at, kept), lines };
}
