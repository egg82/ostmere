// A store guard as the editor builds it (docs/design/rule-guards.md, "Guards"): one level and one test, stored as the
// condition that blocks the rule. "Unless smoked is 10 or more" blocks from 10 and lets go one item past, under 9;
// "unless smoked is under 10" blocks under 10 and lets go from 11. A share keeps the same share for both levels, which
// the engine widens to a band of one item (contract/endpoints.txt, "Share levels"). The page words a guard in guardwords.ts.
import type { Condition } from "../api/types";
import { BP, crossing, isShare, SHARE_STEP, type Level, type Test } from "./storerule";

export interface Guard {
  store: string;
  /** "reaches": blocks at the level or more; "below": blocks under it. */
  test: Test;
  level: Level;
}

/** The condition the guard saves. `q`: Scales.quantity_per_item; `level`: the store is a level (Catalog.isLevel), whose
 * whole items cross on its chip's reading (storerule.ts). */
export function buildGuard(g: Guard, q: number, level = false): Condition {
  const watched = { kind: "store_value" as const, store: g.store };
  const share = isShare(g.level);
  const n = isShare(g.level) ? g.level.share : g.level.items;
  const below = g.test === "below";
  const at = (items: number): number => (share ? n : crossing(items, below, q, level));
  return { kind: below ? "at_most" : "at_least", watched, value: at(n), release: at(below ? n + 1 : n - 1), value_of_cap: share, release_of_cap: share };
}

/** Whether the page builds the guard on a store of `cap` whole items: a share inside 0..BP that is neither always on
 * ("or more" of empty, "under" full), whole items whose release stays inside the store (2..cap "or more", 1..cap-1
 * "under"). */
export function guardValid(g: Guard, cap: number): boolean {
  if (cap < 2) return false;
  if (isShare(g.level)) return g.level.share >= 0 && g.level.share <= BP && (g.test === "reaches" ? g.level.share > 0 : g.level.share < BP);
  return g.test === "reaches" ? g.level.items >= 2 && g.level.items <= cap : g.level.items >= 1 && g.level.items <= cap - 1;
}

/** Where a new guard starts: "unless {store} is full"; on a level store (`cap` its whole items, else null) its levels are
 * whole items only, so it starts at the cap. */
export const defaultGuard = (store: string, cap: number | null = null): Guard => ({ store, test: "reaches", level: cap === null ? { share: BP } : { items: cap } });

/** The guard's level in the other form, standing about where it reads now. */
export function otherForm(g: Guard, cap: number): Level {
  if (isShare(g.level)) return { items: Math.round((g.level.share * cap) / BP) };
  return { share: Math.min(BP, Math.max(0, Math.round((g.level.items * BP) / Math.max(1, cap) / SHARE_STEP) * SHARE_STEP)) };
}

/** The guard with its test changed: its level stays when the page builds it so, else it moves to where a new guard of
 * that test starts (full for "or more", a quarter for "under"; in whole items on a level store, `items`). */
export function withTest(g: Guard, test: Test, cap: number, items = false): Guard {
  const next = { ...g, test };
  if (guardValid(next, cap)) return next;
  const share = test === "reaches" ? BP : 2500;
  return { ...next, level: items ? { items: test === "reaches" ? cap : Math.max(1, Math.ceil(cap / 4)) } : { share } };
}
