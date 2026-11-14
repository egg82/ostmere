// A rule's condition on a store, as the page builds, reads and words it (CONTRACT.txt, "a store rule"). Two tests, each
// a latch with a band so a rule never flips at one level: "under n, until m" (at_most) and "n or more, until under m"
// (at_least). Each level is whole items or a share of the store's cap (CONTRACT.txt, "Share levels"); a share keeps up
// as the cap grows and is worded as one (empty, a quarter, half, three quarters, full, or a percentage). Whole-item
// levels keep the ±1 conventions that put each crossing on the amount the page shows; a share is reached at the share
// itself, from either side ("down to a quarter", "until empty"). A rule the page builds always has a band of at least
// one item and is never always true; one read back with no band (an order card without a release) is worded without
// "until".
import type { Condition } from "../api/types";
import type { Catalog } from "./catalog";
import { UI } from "./text";

export type Test = "below" | "reaches";

/** A level: whole items, or basis points of the store's cap now. */
export type Level = { items: number } | { share: number };

export interface StoreRule {
  store: string;
  test: Test;
  /** The level it comes on at. */
  n: Level;
  /** The level it lets go at; null when it has no band (it lets go where it came on). */
  m: Level | null;
}

export const BP = 10_000;
/** The shares worded by name, each with its text key. */
export const PRESETS: readonly (readonly [number, string])[] = [
  [0, UI.levelEmpty], [2500, UI.levelQuarter], [5000, UI.levelHalf], [7500, UI.levelThreeQuarters], [BP, UI.levelFull]];
/** A share's fine step: five points. */
export const SHARE_STEP = 500;

export const isShare = (l: Level): l is { share: number } => "share" in l;

export function sameLevel(a: Level | null, b: Level | null): boolean {
  if (a === null || b === null) return a === b;
  return isShare(a) ? isShare(b) && a.share === b.share : !isShare(b) && a.items === b.items;
}

/** The store rule a condition is, or null for any other condition. `q`: Scales.quantity_per_item. */
export function readRule(when: Condition, q: number): StoreRule | null {
  if (when.kind === "after_time" || when.watched.kind !== "store_value") return null;
  const below = when.kind === "at_most";
  const off = below ? 1 : 0;
  const n: Level = when.value_of_cap ? { share: when.value } : { items: Math.floor((when.value + off) / q) };
  const m: Level = when.release_of_cap ? { share: when.release } : { items: Math.floor((when.release + off) / q) };
  const banded = isShare(n) || isShare(m) || (below ? m.items > n.items : m.items < n.items);
  return { store: when.watched.store, test: below ? "below" : "reaches", n, m: banded ? m : null };
}

/** The condition for a store rule. A rule with no band builds as a plain threshold (only content makes those). */
export function buildRule(rule: StoreRule, q: number): Condition {
  const watched = { kind: "store_value" as const, store: rule.store };
  const below = rule.test === "below";
  const raw = (l: Level): number => (isShare(l) ? l.share : l.items * q - (below ? 1 : 0));
  const m = rule.m ?? rule.n;
  return { kind: below ? "at_most" : "at_least", watched, value: raw(rule.n), release: raw(m),
    value_of_cap: isShare(rule.n), release_of_cap: isShare(m) };
}

/** Where a level stands among the store's whole items under a cap of `cap` items, as the engine reads it (DESIGN.txt,
 * "SHARE LEVELS"): side "on", the shown amount at or past which the rule holds (at or under for "below", at or over
 * for "reaches"); side "off", the shown amount at which it lets go. */
function shownAt(l: Level, test: Test, side: "on" | "off", cap: number): number {
  const floorSide = (test === "below") === (side === "on");
  if (!isShare(l)) return floorSide ? l.items - 1 : l.items;
  return floorSide ? Math.floor((l.share * cap) / BP) : Math.ceil((l.share * cap) / BP);
}

/** A level as a point on the bar from empty to `cap` items: whole items, or the exact share. */
export function levelAt(l: Level, cap: number): number {
  return isShare(l) ? (l.share * cap) / BP : l.items;
}

const inRange = (l: Level, cap: number): boolean => (isShare(l) ? l.share >= 0 && l.share <= BP : l.items >= 1 && l.items <= cap);

/** The page builds the rule: every level in range, a band of at least one item inside 0..cap, and never always true
 * (CONTRACT.txt, "a store rule"). */
export function valid(rule: StoreRule, cap: number): boolean {
  const m = rule.m;
  if (cap < 2 || m === null || !inRange(rule.n, cap) || !inRange(m, cap)) return false;
  const on = shownAt(rule.n, rule.test, "on", cap), off = shownAt(m, rule.test, "off", cap);
  return rule.test === "below" ? on >= 0 && off >= on + 2 && off <= cap : on <= cap && off >= 0 && off <= on - 2;
}

const clamp = (v: number, lo: number, hi: number): number => Math.min(hi, Math.max(lo, v));

/** The rule held inside what the store allows: an amount `n` inside its range, then an amount `m` brought next to it
 * (a missing m gets the default); a share is never moved. */
export function clampRule(rule: StoreRule, cap: number): StoreRule {
  if (cap < 2) return rule;
  const below = rule.test === "below";
  const n = isShare(rule.n) ? rule.n : { items: below ? clamp(rule.n.items, 1, cap - 1) : clamp(rule.n.items, 2, cap) };
  const m = rule.m ?? defaultUntil(rule.test);
  if (isShare(m)) return { ...rule, n, m };
  const on = shownAt(n, rule.test, "on", cap);
  return { ...rule, n, m: { items: below ? clamp(m.items, on + 2, cap) : clamp(m.items, 1, on - 1) } };
}

/** `rule` held as clampRule holds it, or null when that is still not a rule the page builds. */
export function tryRule(rule: StoreRule, cap: number): StoreRule | null {
  const held = clampRule(rule, cap);
  return valid(held, cap) ? held : null;
}

/** Where a new rule starts, as shares: down to a quarter, until three quarters; or up to full, until half. On a store
 * too small for those to keep a band, in items: under a quarter, until halfway to full; or at full, until under half. */
export function defaultRule(store: string, test: Test, cap: number): StoreRule {
  const shares = { store, test, n: { share: test === "below" ? 2500 : BP }, m: defaultUntil(test) };
  if (valid(shares, cap)) return shares;
  const n = test === "below" ? Math.ceil(cap / 4) : cap;
  return clampRule({ store, test, n: { items: n }, m: { items: test === "below" ? Math.ceil((n + cap) / 2) : Math.max(1, Math.floor(n / 2)) } }, cap);
}

const defaultUntil = (test: Test): Level => ({ share: test === "below" ? 7500 : 5000 });

/** The level in the other form, standing where it reads now under a cap of `cap` items: a share as whole items, whole
 * items as the nearest share step. */
export function switchForm(l: Level, test: Test, side: "on" | "off", cap: number): Level {
  if (!isShare(l)) return { share: clamp(Math.round((l.items * BP) / Math.max(1, cap) / SHARE_STEP) * SHARE_STEP, 0, BP) };
  const shown = shownAt(l, test, side, cap);
  return { items: (test === "below") === (side === "on") ? shown + 1 : shown };
}

/** A level in the player's words: a count, a share's name, or its percentage. */
export function levelWords(catalog: Catalog, l: Level): string {
  if (!isShare(l)) return catalog.format.count(l.items);
  const named = PRESETS.find(([bp]) => bp === l.share);
  return named ? catalog.text.get(named[1]) : catalog.text.fill(UI.levelPct, { pct: String(l.share / 100) });
}

/** The condition in the player's words: "Under {n} {store}, until {m}", "{store} down to {n}, until {m}" and their
 * siblings, by the test and each level's form. */
export function ruleWhen(catalog: Catalog, rule: StoreRule): string {
  const slots = { store: catalog.storeLabel(rule.store), n: levelWords(catalog, rule.n), m: rule.m === null ? "" : levelWords(catalog, rule.m) };
  return catalog.text.fill(whenKey(rule), slots);
}

function whenKey(rule: StoreRule): string {
  const share = isShare(rule.n);
  if (rule.test === "below") return share ? UI.ruleDownToUntil : rule.m === null ? UI.ruleBelow : UI.ruleBelowUntil;
  if (rule.m === null) return UI.ruleReaches;
  if (share) return isShare(rule.m) ? UI.ruleUpToUntil : UI.ruleUpToUntilUnder;
  return isShare(rule.m) ? UI.ruleReachesUntilDown : UI.ruleReachesUntil;
}

/** What the hands strip says while the rule's mix or task runs: until it lets go, or, with no band, while under. */
export function ruleUntil(catalog: Catalog, rule: StoreRule): string {
  const store = catalog.storeLabel(rule.store);
  if (rule.m === null) return rule.test === "below" ? catalog.text.fill(UI.handsByRule, { store, n: levelWords(catalog, rule.n) }) : "";
  const share = isShare(rule.m);
  const key = rule.test === "below" ? (share ? UI.handsUntilUpTo : UI.handsUntilUp) : (share ? UI.handsUntilDownTo : UI.handsUntilDown);
  return catalog.text.fill(key, { store, m: levelWords(catalog, rule.m) });
}

/** The key of why a store rule is off (what it waits for), in the words of its level's form. */
export function needsKey(rule: StoreRule): string {
  if (isShare(rule.n)) return rule.test === "below" ? UI.ruleNeedsDownTo : UI.ruleNeedsUpTo;
  return rule.test === "below" ? UI.ruleNeedsBelow : UI.ruleNeedsReaches;
}

/** The quantity at which an "under" rule on a store whose cap is `capQ` (a quantity) lets go as the store fills: its
 * release plus one, or for a share the whole items it reads, read off the cap. */
export function letGoAt(when: { release: number; release_of_cap: boolean }, capQ: number, q: number): number {
  return when.release_of_cap ? Math.ceil((when.release * Math.floor(capQ / q)) / BP) * q : when.release + 1;
}
