// The journal as the page reads it (docs/design/opening-screen.md, "The journal"; CONTRACT.txt, "JOURNAL"): which pages
// and notes are written, what is unread, which page the sheet opens on, the numbers rows and the seeded layout. Pure:
// the days pages are the written days the save served (game/days.ts), every other page is Content.journal and
// view.unlocked, the numbers are view.fights, and what has been read is the account's notes and the save's newest day
// (Keeps).
import type { EntryInfo, Fight, Hand, JournalDay, View } from "../api/types";
import type { Catalog } from "./catalog";
import { dayPages } from "./days";
import { fightOf, oddsWords, seeded } from "./fights";
import { UI } from "./text";

/** A note drawn on a page: `id` is a book note's id, or a day's note's day and place; its words are the text `key`. A
 * days page's note names the day it was written on. */
export interface PageNote {
  id: string;
  key: string;
  hand: Hand;
  sketch: string | null;
  day: number | null;
}

/** A page written: a days page (its id the first day on it), or an entry's page with the notes written on it so far,
 * in content order. */
export interface Page {
  id: string;
  section: Section;
  sketch: string | null;
  runners: string[];
  notes: PageNote[];
}

export type Section = "days" | EntryInfo["section"];

/** What the player has read: the account's book notes, and the newest written day turned to in this save. */
export interface Reading {
  note(id: string): boolean;
  newestDay: number | null;
}

/** The book's sections in the order it runs, each with the text key of its bookmark. */
export const SECTIONS: ReadonlyArray<{ section: Section; key: string }> = [
  { section: "days", key: UI.journalDays },
  { section: "creatures", key: UI.journalCreatures },
  { section: "places", key: UI.journalPlaces },
];

/** The days pages, then every entry view.unlocked holds, creatures then places and in content order within one, each
 * with the notes it holds (a note not unlocked keeps no room). */
export function pagesOf(catalog: Catalog, view: View, days: readonly JournalDay[]): Page[] {
  const journal = catalog.content.journal;
  if (!journal) return [];
  const written: Page[] = journal.entries
    .filter((e) => catalog.unlocked(view, "entry", e.entry))
    .map((e) => ({ id: e.entry, section: e.section, sketch: e.sketch, runners: e.runners, notes: e.notes
      .filter((n) => catalog.unlocked(view, "note", n.note))
      .map((n) => ({ id: n.note, key: n.note, hand: n.hand, sketch: n.sketch, day: null })) }));
  return [...daysPages(catalog, days), ...SECTIONS.flatMap(({ section }) => written.filter((p) => p.section === section))];
}

function daysPages(catalog: Catalog, days: readonly JournalDay[]): Page[] {
  return dayPages(days, (key) => catalog.text.get(key)).map((onPage) => ({
    id: `days:${onPage[0]!.day}`, section: "days", sketch: null, runners: [],
    notes: onPage.flatMap((d) => d.day_notes.map((n, i) => ({ id: `${d.day}.${i}`, key: n.key, hand: n.hand, sketch: n.sketch, day: d.day }))),
  }));
}

/** The sections that have a page written, in the book's order: one bookmark each. */
export function bookmarksOf(pages: Page[]): Array<{ section: Section; key: string }> {
  return SECTIONS.filter(({ section }) => pages.some((p) => p.section === section));
}

/** Whether the page holds something unread: a book note not read, or a day after the newest day turned to. */
export function isUnread(page: Page, read: Reading): boolean {
  return page.notes.some((n) => (n.day === null ? !read.note(n.id) : read.newestDay === null || n.day > read.newestDay));
}

/** The page a section's bookmark turns to: its first page holding something unread, else its latest page; -1 for a
 * section with no page. */
export function bookmarkPage(pages: Page[], section: Section, read: Reading): number {
  const own = pages.flatMap((p, i) => (p.section === section ? [i] : []));
  return own.find((i) => isUnread(pages[i]!, read)) ?? own.at(-1) ?? -1;
}

/** The book is a button from its first page on; until then it is the plain text of any feature with a label. */
export function isButton(catalog: Catalog, view: View, pages: Page[]): boolean {
  const journal = catalog.content.journal;
  return journal !== null && catalog.unlocked(view, "feature", journal.feature) && pages.length > 0;
}

/** The page the sheet opens on: the first holding something unread, else the page last shown in this page session,
 * else the first. */
export function openingPage(pages: Page[], read: Reading, last: string | null): number {
  const unread = pages.findIndex((p) => isUnread(p, read));
  if (unread >= 0) return unread;
  return Math.max(0, pages.findIndex((p) => p.id === last));
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

/** The page's numbers, in runners order, one row for each runner view.fights holds (a runner it does not hold draws
 * nothing). Known means fought above 0, read off the view and stored nowhere. */
export function numbersOf(catalog: Catalog, view: View, page: Page): NumbersRow[] {
  return page.runners.flatMap((r) => { const f = fightOf(view, r); return f ? [rowOf(catalog, f)] : []; });
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
