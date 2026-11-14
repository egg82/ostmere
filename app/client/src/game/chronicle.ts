// The chronicle's routing and grouping (docs/decisions.md, "The chronicle and unwrap, as built"): every kind of entry
// has one filter, the story strip shows the story filter's kinds and nothing else, and the entries fall into stretches,
// one per return after a long time away (Visit, kept by the page, game/session.ts), each running from the second the
// player left to the second they next left. Pure; the sheet (ui/chroniclesheet.ts) draws them.
import type { Content, Visit } from "../api/types";

/** How a content line is set (opening/line_kinds.py), authored beside its text. */
export type LineKind = Content["line_infos"][number]["kind"];

/** Every kind of entry: the content's line kinds, a rule coming on or letting go (game/rulerows.ts), and the town's
 * talk, which the living world will write. */
export type EntryKind = LineKind | "rule" | "talk";

export type Filter = "story" | "finds" | "levels" | "rules" | "fights" | "talk";

/** One home per kind: the filter that holds it. */
export const ROUTES: Readonly<Record<EntryKind, Filter>> = {
  story: "story", tap: "story", body: "story",
  find: "finds", level: "levels", rule: "rules", fight: "fights", talk: "talk",
};

/** The filters in the order the chronicle offers them. */
export const FILTERS: readonly Filter[] = ["story", "finds", "levels", "rules", "fights", "talk"];

/** The story strip on the main screen holds the story filter's kinds alone. */
export function inStrip(kind: EntryKind): boolean {
  return ROUTES[kind] === "story";
}

/** A line already written: its key and the game second it landed at (a save's history, `PastLine`). */
export interface Past {
  key: string;
  at: number;
}

/** One entry: its words, the game second it landed at, its kind, and what caused it in words (null: nothing to say).
 * `person`: it tells someone joining or leaving, by their own line or a day's mention (CONTRACT.txt, "PEOPLE"). */
export interface Entry {
  text: string;
  at: number;
  kind: EntryKind;
  cause: string | null;
  person?: boolean;
}

/** Game seconds away that make a return a visit. */
export const AWAY_MIN_S = 1800;
/** The returns a save keeps, newest: the chronicle holds KEEP entries a filter, so an older return opens no stretch (the API's MAX_VISITS). */
export const MAX_VISITS = 200;
/** The entries the chronicle keeps of each filter, so a busy kind never pushes out a quiet one's. */
export const KEEP = 200;

/** `entries` with `entry` in its place by game second (after any at the same second), and the oldest of its filter
 * dropped past KEEP. */
export function added(entries: readonly Entry[], entry: Entry): Entry[] {
  let at = entries.length;
  while (at > 0 && entries[at - 1]!.at > entry.at) at -= 1;
  const out = [...entries.slice(0, at), entry, ...entries.slice(at)];
  const same = out.filter((e) => ROUTES[e.kind] === ROUTES[entry.kind]);
  return same.length > KEEP ? out.filter((e) => e !== same[0]) : out;
}

/** The entries one filter holds (null: every entry). */
export function held(entries: readonly Entry[], filter: Filter | null): Entry[] {
  return filter === null ? [...entries] : entries.filter((e) => ROUTES[e.kind] === filter);
}

/** The filters that hold an entry, in FILTERS order. */
export function filtersOf(entries: readonly Entry[]): Filter[] {
  return FILTERS.filter((f) => entries.some((e) => ROUTES[e.kind] === f));
}

/** One stretch: the return that opened it (null: the lines before the first return kept) and its entries in order. */
export interface Stretch {
  visit: Visit | null;
  lines: Entry[];
}

/** `lines` (oldest first) split at each visit's `left`: a line belongs to the last visit whose `left` it is past. A
 * visit with no line after it opens no stretch, and with no visit at all every line is one stretch. */
export function stretches(lines: readonly Entry[], visits: Visit[]): Stretch[] {
  const sorted = [...visits].sort((a, b) => a.left - b.left);
  const out: Stretch[] = [];
  for (const line of lines) {
    const visit = sorted.filter((v) => v.left < line.at).at(-1) ?? null;
    const last = out.at(-1);
    if (last && last.visit === visit) last.lines.push(line);
    else out.push({ visit, lines: [line] });
  }
  return out;
}

/** How many entries each filter holds of `lines`, in FILTERS order, those with none left out. */
export function tally(lines: readonly Entry[]): Array<[Filter, number]> {
  return FILTERS.map((f): [Filter, number] => [f, held(lines, f).length]).filter(([, n]) => n > 0);
}
