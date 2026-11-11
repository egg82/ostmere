// A rule's condition on a store, as the page builds, reads and words it (CONTRACT.txt, "a store rule"). Two tests, each
// a latch with a band so a rule never flips at one level: "under n, until m" (at_most) and "n or more, until under m"
// (at_least). The words put the number before the store and use no verb, so they read whatever the label's number. Levels are whole items; the ±1 conventions put each crossing on the amount the page shows. A rule
// the page builds always has a band of at least one item and is never always true; one read back with no band (an
// order card without a release) is worded without "until".
import type { Condition } from "../api/types";
import type { Catalog } from "./catalog";
import { UI } from "./text";

export type Test = "below" | "reaches";

export interface StoreRule {
  store: string;
  test: Test;
  /** The level it comes on at, in whole items. */
  n: number;
  /** The level it lets go at, in whole items; null when it has no band (it lets go where it came on). */
  m: number | null;
}

/** The store rule a condition is, or null for any other condition. `q`: Scales.quantity_per_item. */
export function readRule(when: Condition, q: number): StoreRule | null {
  if (when.kind === "after_time" || when.watched.kind !== "store_value") return null;
  const store = when.watched.store;
  if (when.kind === "at_most") {
    const n = Math.floor((when.value + 1) / q), m = Math.floor((when.release + 1) / q);
    return { store, test: "below", n, m: m > n ? m : null };
  }
  const n = Math.floor(when.value / q), m = Math.floor(when.release / q);
  return { store, test: "reaches", n, m: m < n ? m : null };
}

/** The condition for a store rule. A rule with no band builds as a plain threshold (only content makes those). */
export function buildRule(rule: StoreRule, q: number): Condition {
  const watched = { kind: "store_value" as const, store: rule.store };
  if (rule.test === "below") {
    const value = rule.n * q - 1;
    return { kind: "at_most", watched, value, release: rule.m === null ? value : rule.m * q - 1 };
  }
  const value = rule.n * q;
  return { kind: "at_least", watched, value, release: rule.m === null ? value : rule.m * q };
}

/** The levels a store with `cap` whole items allows: [lo, hi] for n, and for m given n. Null when the store is too
 * small for a band (under two items). */
export function bounds(test: Test, cap: number, n: number): { n: [number, number]; m: [number, number] } | null {
  if (cap < 2) return null;
  return test === "below" ? { n: [1, cap - 1], m: [n + 1, cap] } : { n: [2, cap], m: [1, n - 1] };
}

const clamp = (v: number, [lo, hi]: [number, number]): number => Math.min(hi, Math.max(lo, v));

/** The rule held inside what the store allows: n first, then m for that n (a missing m gets the default). */
export function clampRule(rule: StoreRule, cap: number): StoreRule {
  const first = bounds(rule.test, cap, rule.n);
  if (first === null) return rule;
  const n = clamp(rule.n, first.n);
  const m = clamp(rule.m ?? defaultUntil(rule.test, n, cap), bounds(rule.test, cap, n)!.m);
  return { ...rule, n, m };
}

/** Where a new rule starts: below a quarter, until halfway to full; or at full, until below half. */
export function defaultRule(store: string, test: Test, cap: number): StoreRule {
  const n = test === "below" ? Math.ceil(cap / 4) : cap;
  return clampRule({ store, test, n, m: defaultUntil(test, n, cap) }, cap);
}

function defaultUntil(test: Test, n: number, cap: number): number {
  return test === "below" ? Math.ceil((n + cap) / 2) : Math.max(1, Math.floor(n / 2));
}

/** The condition in the player's words: "Under {n} {store}, until {m}" and its three siblings. */
export function ruleWhen(catalog: Catalog, rule: StoreRule): string {
  const slots = { store: catalog.storeLabel(rule.store), n: catalog.format.count(rule.n), m: rule.m === null ? "" : catalog.format.count(rule.m) };
  const key = rule.test === "below" ? (rule.m === null ? UI.ruleBelow : UI.ruleBelowUntil) : (rule.m === null ? UI.ruleReaches : UI.ruleReachesUntil);
  return catalog.text.fill(key, slots);
}

/** What the hands strip says while the rule's mix or task runs: until it lets go, or, with no band, while under. */
export function ruleUntil(catalog: Catalog, rule: StoreRule): string {
  const store = catalog.storeLabel(rule.store);
  if (rule.m === null) return rule.test === "below" ? catalog.text.fill(UI.handsByRule, { store, n: catalog.format.count(rule.n) }) : "";
  return catalog.text.fill(rule.test === "below" ? UI.handsUntilUp : UI.handsUntilDown, { store, m: catalog.format.count(rule.m) });
}
