// What the page works out about fights (CONTRACT.txt, "FIGHTS"); every number it shows is the engine's, served: the
// odds' words, the strengths' entries, and which fights of a window the log calls lost. It rolls nothing that changes
// a number: a window's labels are placed by a seeded shuffle of the engine's exact lost count.
import type { Fight, Strength, View } from "../api/types";
import { UI, type Text } from "./text";

/** The feature that switches the page's fight parts on. */
export const COMBAT = "combat";

/** The odds as a whole "j in n" (n at most 20) when exact, else a percentage: one decimal under 10%. */
export type Odds = { kind: "pair"; lost: number; of: number } | { kind: "pct"; pct: string };

const MOST_OF = 20;

export function oddsOf(lossBp: number, bp: number): Odds {
  for (let of = 1; of <= MOST_OF; of++) {
    if ((lossBp * of) % bp === 0) return { kind: "pair", lost: (lossBp * of) / bp, of };
  }
  const pct = lossBp / (bp / 100);
  return { kind: "pct", pct: pct < 10 ? pct.toFixed(1) : String(Math.round(pct)) };
}

/** A fight's odds in the card's words: unknown until fought, else "j in n lost", else a percentage. */
export function oddsWords(text: Text, fight: Fight, bp: number): string {
  if (fight.fought === 0) return text.get(UI.fightOddsUnknown);
  const odds = oddsOf(fight.loss_bp, bp);
  return odds.kind === "pair" ? text.fill(UI.fightOdds, { lost: String(odds.lost), of: String(odds.of) }) : text.fill(UI.fightOddsPct, { pct: odds.pct });
}

/** A window of fights since the last view: `fought` of them from the count `start`, of which `lost` were lost;
 * `lostBefore` were lost before it. */
export interface Window {
  runner: string;
  start: number;
  fought: number;
  lost: number;
  lostBefore: number;
}

/** Each fight runner's window between two views (none on the first view). Counts only rise; a runner new in `now`
 * starts from none. The lost count is held to the window's fights. */
export function windows(prev: View | null, now: View): Window[] {
  if (!prev) return [];
  const was = new Map(prev.fights.map((f) => [f.runner, f]));
  const out: Window[] = [];
  for (const f of now.fights) {
    const before = was.get(f.runner);
    const fought = f.fought - (before?.fought ?? 0);
    if (fought <= 0) continue;
    const lostBefore = before?.lost ?? 0;
    out.push({ runner: f.runner, start: before?.fought ?? 0, fought, lost: Math.min(fought, Math.max(0, f.lost - lostBefore)), lostBefore });
  }
  return out;
}

/** A 32-bit FNV-1a hash of the draw's key seeds a mulberry32 generator. */
export function seeded(key: string): () => number {
  let h = 0x811c9dc5;
  for (let i = 0; i < key.length; i++) h = Math.imul(h ^ key.charCodeAt(i), 0x01000193);
  let a = h >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/** The window's fights in order, true where one reads as lost: a bag of `lost` losses and the rest wins, shuffled by a
 * draw keyed by the save, the runner and the fought count the window starts at, so the same window reads the same on
 * every call and every device. */
export function labels(save: number, w: Window): boolean[] {
  return shuffled(Array.from({ length: w.fought }, (_, i) => i < w.lost), seeded(`${save}|${w.runner}|${w.start}`));
}

/** A Fisher-Yates shuffle of a copy, by `next`. */
function shuffled<T>(xs: T[], next: () => number): T[] {
  const bag = [...xs];
  for (let i = bag.length - 1; i > 0; i--) {
    const j = Math.floor(next() * (i + 1));
    [bag[i], bag[j]] = [bag[j] as T, bag[i] as T];
  }
  return bag;
}

/** The k-th draw of a shuffle bag: `pool` shuffled by a draw keyed by `key` and the round floor(k / n), so each item
 * comes once before any repeats, the same on every device. */
export function bagged(key: string, pool: readonly string[], k: number): string {
  const round = Math.floor(k / pool.length);
  return shuffled([...pool], seeded(`${key}|${round}`))[k % pool.length] ?? "";
}

/** The pool's line for the runner's k-th fight of a kind (won or lost, counted from 0 since it first ran): a shuffle
 * bag keyed by the save, the runner and the kind. */
export function poolLine(save: number, runner: string, kind: "won" | "lost", pool: readonly string[], k: number): string {
  return bagged(`${save}|${runner}|${kind}`, pool, k);
}

/** Past this many fights in one window the arrival queue shows one summary line instead of one per fight. */
export const MOST_ENTRIES = 3;

/** A runner's fight in the view: its odds, strengths and tally. */
export function fightOf(view: View, runner: string): Fight | undefined {
  return view.fights.find((f) => f.runner === runner);
}

export interface StrengthRow {
  source: string | null;
  /** The share of its lane's time a held entry has now; null on a permanent entry and on a whole share. */
  share: string | null;
  amount: string;
}

/** A strength's entries as rows, the base first as served: the base as the number it is, a sum as a signed
 * percentage, a factor as a multiple. `name` words a source id; `change` words a signed change in basis points; `share`
 * words a share in basis points. */
export function strengthRows(s: Strength, bp: number, name: (source: string) => string, change: (bp: number) => string, share: (bp: number) => string): StrengthRow[] {
  return s.sources.map((e) => ({
    source: e.source === null ? null : name(e.source),
    share: e.share_bp === null || e.share_bp >= bp ? null : share(e.share_bp),
    amount: e.form === "base" ? String(e.amount_bp) : e.form === "add_bp" ? change(e.amount_bp) : `×${Number((e.amount_bp / bp).toFixed(2))}`,
  }));
}

/** The words an arrival-queue entry is written in: one fight won or lost, the runner's k-th of that kind (counted
 * from 0 since it first ran, for its pool: poolLine), and a long window's summary. */
export interface EntryWords {
  won(runner: string, k: number): string;
  lost(runner: string, k: number): string;
  since(w: Window): string;
}

/** The arrival queue's fight entries between two views, in runner order: for a window of k fights with j lost, k
 * entries of which exactly j read as lost (labels), or past MOST_ENTRIES one summary line of the exact counts. */
export function entries(save: number, prev: View | null, now: View, words: EntryWords): string[] {
  return windows(prev, now).flatMap((w) => {
    if (w.fought > MOST_ENTRIES) return [words.since(w)];
    let won = w.start - w.lostBefore;
    let lost = w.lostBefore;
    return labels(save, w).map((isLost) => (isLost ? words.lost(w.runner, lost++) : words.won(w.runner, won++)));
  });
}
