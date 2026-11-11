// The journal as the page reads it (docs/design/opening-screen.md, "The journal"; CONTRACT.txt, "JOURNAL"): which pages
// and notes are written, what is unread, which page the sheet opens on, the numbers rows and the seeded layout. Pure:
// every fact is Content.journal, view.unlocked or view.fights, and what has been read is the account's (Keeps).
import type { EntryInfo, Fight, NoteInfo, View } from "../api/types";
import type { Catalog } from "./catalog";
import { fightOf, oddsWords, seeded } from "./fights";
import { UI } from "./text";

/** A page written: its entry, and the notes written on it so far, in content order. */
export interface Page {
  entry: EntryInfo;
  notes: NoteInfo[];
}

export type Section = EntryInfo["section"];

/** The book's sections in the order it runs, each with the text key of its bookmark. */
export const SECTIONS: ReadonlyArray<{ section: Section; key: string }> = [
  { section: "days", key: UI.journalDays },
  { section: "creatures", key: UI.journalCreatures },
  { section: "places", key: UI.journalPlaces },
];

/** Every entry view.unlocked holds, section by section (days, creatures, places) and in content order within one, each
 * with the notes it holds (a note not unlocked keeps no room). */
export function pagesOf(catalog: Catalog, view: View): Page[] {
  const journal = catalog.content.journal;
  if (!journal) return [];
  const written = journal.entries
    .filter((e) => catalog.unlocked(view, "entry", e.entry))
    .map((entry) => ({ entry, notes: entry.notes.filter((n) => catalog.unlocked(view, "note", n.note)) }));
  return SECTIONS.flatMap(({ section }) => written.filter((p) => p.entry.section === section));
}

/** The sections that have a page written, in the book's order: one bookmark each. */
export function bookmarksOf(pages: Page[]): Array<{ section: Section; key: string }> {
  return SECTIONS.filter(({ section }) => pages.some((p) => p.entry.section === section));
}

/** The page a section's bookmark turns to: its first page holding an unread note, else its latest page; -1 for a
 * section with no page. */
export function bookmarkPage(pages: Page[], section: Section, read: (note: string) => boolean): number {
  const own = pages.flatMap((p, i) => (p.entry.section === section ? [i] : []));
  return own.find((i) => pages[i]!.notes.some((n) => !read(n.note))) ?? own.at(-1) ?? -1;
}

/** The book is a button from the first entry on; until then it is the plain text of any feature with a label. */
export function isButton(catalog: Catalog, view: View, pages: Page[]): boolean {
  const journal = catalog.content.journal;
  return journal !== null && catalog.unlocked(view, "feature", journal.feature) && pages.length > 0;
}

/** The notes written and not yet read, in page order. */
export function unreadOf(pages: Page[], read: (note: string) => boolean): string[] {
  return pages.flatMap((p) => p.notes.map((n) => n.note)).filter((n) => !read(n));
}

/** The page the sheet opens on: the first with an unread note, else the page last shown in this page session, else the
 * first. */
export function openingPage(pages: Page[], read: (note: string) => boolean, last: string | null): number {
  const unread = pages.findIndex((p) => p.notes.some((n) => !read(n.note)));
  if (unread >= 0) return unread;
  return Math.max(0, pages.findIndex((p) => p.entry.entry === last));
}

/** A runner's numbers in the fight card's words (CONTRACT.txt, "FIGHTS"): `odds`, the two strengths named in `vs`, and
 * the tally; a runner never fought has the card's unknowns and no tally. */
export interface NumbersRow {
  runner: string;
  label: string;
  odds: string;
  vs: string;
  tally: string | null;
}

function runnerLabel(catalog: Catalog, runner: string): string {
  if (catalog.cards.has(runner)) return catalog.cardLabel(runner);
  return catalog.label(catalog.content.standing_infos.find((a) => a.action === runner)?.label_key);
}

function rowOf(catalog: Catalog, fight: Fight): NumbersRow {
  const { text, content } = catalog;
  const known = fight.fought > 0;
  const threat = known ? String(fight.threat_strength.value) : text.get(UI.fightThreatUnknown);
  return {
    runner: fight.runner, label: runnerLabel(catalog, fight.runner), odds: oddsWords(text, fight, content.scales.bp),
    vs: text.fill(UI.fightVs, { side_name: catalog.sideLabel(fight.side), power: String(fight.power.value), threat_name: catalog.threatLabel(fight.threat), threat }),
    tally: known ? text.fill(UI.fightTally, { fought: String(fight.fought), lost: String(fight.lost) }) : null,
  };
}

/** The entry's numbers, in runners order, one row for each runner view.fights holds (a runner it does not hold draws
 * nothing). Known means fought above 0, read off the view and stored nowhere. */
export function numbersOf(catalog: Catalog, view: View, entry: EntryInfo): NumbersRow[] {
  return entry.runners.flatMap((r) => { const f = fightOf(view, r); return f ? [rowOf(catalog, f)] : []; });
}

/** One page's seeded draws (opening-screen.md, "Seeded per entry"). */
export interface Layout {
  /** The sketch's width as a share of its box, 86 to 100 per cent. */
  sketchWidth: number;
  /** Where the sketch sits in the room left over, from 0 (start) to 1 (end), across and, on the left page, down. */
  sketchX: number;
  sketchY: number;
  /** On a phone, the first note sits above the sketch (35 per cent of pages). */
  noteAbove: boolean;
  notes: Array<{ tiltDeg: number; indentRem: number }>;
}

const ABOVE_SHARE = 0.35;

/** A draw in [0, 1), keyed by "journal", the entry and the part: never the save, so a page looks the same in every game
 * and on every device and differs from its neighbours. */
export function drawOf(entry: string, part: string): number {
  return seeded(`journal|${entry}|${part}`)();
}

/** The layout of `entry`'s page for `notes` notes. A note's draws are keyed by its index, so a note written later
 * leaves every earlier note's draws alone. */
export function layoutOf(entry: string, notes: number): Layout {
  return {
    sketchWidth: 86 + 14 * drawOf(entry, "sketch-width"), sketchX: drawOf(entry, "sketch-x"), sketchY: drawOf(entry, "sketch-y"),
    noteAbove: drawOf(entry, "note-above") < ABOVE_SHARE,
    notes: Array.from({ length: notes }, (_, i) => noteLayout(entry, i)),
  };
}

/** A note's tilt (-2 to +1 degrees) and indent (0 to 1.5rem, and a rem further for a note written after the first). */
export function noteLayout(entry: string, index: number): { tiltDeg: number; indentRem: number } {
  return { tiltDeg: -2 + 3 * drawOf(entry, `note-${index}-tilt`), indentRem: 1.5 * drawOf(entry, `note-${index}-indent`) + (index > 0 ? 1 : 0) };
}
