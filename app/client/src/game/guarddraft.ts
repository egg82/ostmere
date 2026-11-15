// A store guard as the editor builds it (docs/design/rule-guards.md, "Guards"): one level and one test, stored as the
// condition that blocks the rule. "Unless smoked is 10 or more" blocks from 10 and lets go one item past, under 9;
// "unless smoked is under 10" blocks under 10 and lets go from 11. A share keeps the same share for both levels, which
// the engine widens to a band of one item (CONTRACT.txt, "Share levels"). The page words a guard in guardwords.ts.
import type { Condition } from "../api/types";
import { BP, isShare, SHARE_STEP, type Level, type Test } from "./storerule";

export interface Guard {
  store: string;
  /** "reaches": blocks at the level or more; "below": blocks under it. */
  test: Test;
  level: Level;
}

/** The condition the guard saves. `q`: Scales.quantity_per_item. */
export function buildGuard(g: Guard, q: number): Condition {
  const watched = { kind: "store_value" as const, store: g.store };
  const share = isShare(g.level);
  const n = isShare(g.level) ? g.level.share : g.level.items;
  if (g.test === "reaches") {
    return { kind: "at_least", watched, value: share ? n : n * q, release: share ? n : (n - 1) * q, value_of_cap: share, release_of_cap: share };
  }
  return { kind: "at_most", watched, value: share ? n : n * q - 1, release: share ? n : (n + 1) * q - 1, value_of_cap: share, release_of_cap: share };
}

/** Whether the page builds the guard on a store of `cap` whole items: a share inside 0..BP that is neither always on
 * ("or more" of empty, "under" full), whole items whose release stays inside the store (2..cap "or more", 1..cap-1
 * "under"). */
export function guardValid(g: Guard, cap: number): boolean {
  if (cap < 2) return false;
  if (isShare(g.level)) return g.level.share >= 0 && g.level.share <= BP && (g.test === "reaches" ? g.level.share > 0 : g.level.share < BP);
  return g.test === "reaches" ? g.level.items >= 2 && g.level.items <= cap : g.level.items >= 1 && g.level.items <= cap - 1;
}

/** Where a new guard starts: "unless {store} is full". */
export const defaultGuard = (store: string): Guard => ({ store, test: "reaches", level: { share: BP } });

/** The guard's level in the other form, standing about where it reads now. */
export function otherForm(g: Guard, cap: number): Level {
  if (isShare(g.level)) return { items: Math.round((g.level.share * cap) / BP) };
  return { share: Math.min(BP, Math.max(0, Math.round((g.level.items * BP) / Math.max(1, cap) / SHARE_STEP) * SHARE_STEP)) };
}

/** The guard with its test changed: its level stays when the page builds it so, else it moves to where a new guard of
 * that test starts (full for "or more", a quarter for "under"). */
export function withTest(g: Guard, test: Test, cap: number): Guard {
  const next = { ...g, test };
  return guardValid(next, cap) ? next : { ...next, level: { share: test === "reaches" ? BP : 2500 } };
}
