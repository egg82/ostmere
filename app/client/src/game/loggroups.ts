// How the Log's lines fall into stretches: one per return after a long time away (Visit, kept by the page,
// game/session.ts), each running from the second the player left to the second they next left. Pure; the sheet
// (ui/logsheet.ts) draws a stretch's title and its lines.
import type { Content, Visit } from "../api/types";

/** How a line is set (opening/line_kinds.py), authored beside its text. */
export type LineKind = Content["line_infos"][number]["kind"];

/** A line already written: its key and the game second it landed at (a save's history, `PastLine`). */
export interface Past {
  key: string;
  at: number;
}

/** One line of the Log: its words, the game second it landed at, and its kind. */
export interface LogEntry {
  text: string;
  at: number;
  kind: LineKind;
}

/** Game seconds away that make a return a visit. */
export const AWAY_MIN_S = 1800;
/** The returns a save keeps, newest: the Log holds ui/story.ts KEEP lines, so an older return opens no stretch (the API's MAX_VISITS). */
export const MAX_VISITS = 200;

/** The kinds the Log sets at full size; every other kind is a small line under them. */
export function isStory(kind: LineKind): boolean {
  return kind === "story";
}

/** One stretch: the return that opened it (null: the lines before the first return kept) and its lines in order. */
export interface Stretch {
  visit: Visit | null;
  lines: LogEntry[];
}

/** `lines` (oldest first) split at each visit's `left`: a line belongs to the last visit whose `left` it is past. A
 * visit with no line after it opens no stretch, and with no visit at all every line is one stretch. */
export function stretches(lines: LogEntry[], visits: Visit[]): Stretch[] {
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

const ORDER: LineKind[] = ["story", "tap", "find", "level", "body", "fight"];

/** How many lines of each kind that appears, the story's first. */
export function tally(lines: LogEntry[]): Array<[LineKind, number]> {
  return ORDER.map((kind): [LineKind, number] => [kind, lines.filter((l) => l.kind === kind).length]).filter(([, n]) => n > 0);
}
