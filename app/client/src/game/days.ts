// The daily journal's written days as the page reads them (docs/design/journal.md, "What the page draws"; CONTRACT.txt,
// "JOURNAL", "The written days"): every day Opened and the Steps carried, and the days pages they fill. Pure: the pages
// come from the days and their words alone, never the window, so the same days are the same pages on every device and
// width.
import type { JournalDay } from "../api/types";

/** One written day per day number, oldest first: `more` joined into `held` (a day already held stays as it is). */
export function joinDays(held: readonly JournalDay[], more: readonly JournalDay[]): JournalDay[] {
  const have = new Set(held.map((d) => d.day));
  const fresh = more.filter((d) => !have.has(d.day) && have.add(d.day));
  return fresh.length === 0 ? [...held] : [...held, ...fresh].sort((a, b) => a.day - b.day);
}

/** The page's measure, in rows of the hand as the desktop page draws them (1440 by 900: the room under a page's padding
 * is about 23.6 rows of 28px, each row about 50 characters): a fixed number, so paging never reads the window. */
export const PAGE_ROWS = 22;
/** Characters of the hand in one row, and in one beside a note's drawing (the words take about half the width). */
export const ROW_CHARS = 46;
export const BESIDE_SKETCH_CHARS = 24;
/** A note's drawing is at most 8rem tall: about five rows. */
export const SKETCH_ROWS = 5;
/** The space under each note and above each day after a page's first. */
export const NOTE_GAP = 0.25;
export const DAY_GAP = 0.5;
/** A day's heading takes one row. */
export const HEADING_ROWS = 1;

/** How many rows a note of `chars` characters takes, with its drawing beside it or not. */
export function noteRows(chars: number, sketch: boolean): number {
  const words = Math.max(1, Math.ceil(chars / (sketch ? BESIDE_SKETCH_CHARS : ROW_CHARS)));
  return (sketch ? Math.max(words, SKETCH_ROWS) : words) + NOTE_GAP;
}

/** How many rows `day` takes: its heading and its notes, `words` giving each note's words. */
export function dayRows(day: JournalDay, words: (key: string) => string): number {
  return HEADING_ROWS + day.day_notes.reduce((n, note) => n + noteRows(words(note.key).length, note.sketch !== null), 0);
}

/** The days pages: days run on down a page until the next would not fit, which starts a new page. A day is never split,
 * so one longer than a page has a page of its own. A page, once a later one is begun, never changes. */
export function dayPages(days: readonly JournalDay[], words: (key: string) => string): JournalDay[][] {
  const pages: JournalDay[][] = [];
  let used = 0;
  for (const day of days) {
    const page = pages.at(-1);
    const rows = dayRows(day, words);
    if (page && used + DAY_GAP + rows <= PAGE_ROWS) {
      page.push(day);
      used += DAY_GAP + rows;
    } else {
      pages.push([day]);
      used = rows;
    }
  }
  return pages;
}
