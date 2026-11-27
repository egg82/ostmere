// The daily journal's days pages (docs/design/journal.md, "What the page draws"; contract/journal.txt, "JOURNAL", "The written
// days"): each day's notes in order under its day, days running on down a page, a note that does not fit beginning the
// next page under its day's heading again, the measure fixed so the same days are the same pages on every device and
// width; a day still being written growing on its page; the dot while a day after the save's newest day read is
// written; the newest day turned to kept as the sheet closes.
import { catalog, expect, rig, text } from "./journalrig";
import { WEEKS } from "../fixtures/journal";
import type { JournalDay } from "../src/api/types";
import { DAY_GAP, dayPages, dayRows, joinDays, noteRows, PAGE_ROWS, ROW_CHARS } from "../src/game/book/days";

const words = (key: string): string => catalog.text.get(key);
const KEY = "wk_rain";   // a one-row note
const day = (n: number, keys: string[], sketch: string | null = null): JournalDay =>
  ({ day: n, day_notes: keys.map((key) => ({ subject: `s_${key}`, slot: "first" as const, key, hand: "ink" as const, sketch, count: null })), marks: [] });
const days = (pages: JournalDay[][]): number[][] => pages.map((p) => p.map((d) => d.day));

{  // the written days held: one per day, oldest first, a day held kept against a copy no longer
  const held = joinDays([day(3, [KEY])], [day(1, [KEY]), day(3, ["wk_roof"])]);
  expect("joined, oldest first, one per day", held.map((d) => d.day), [1, 3]);
  expect("the day held stays", held[1]!.day_notes[0]!.key, KEY);
}

{  // the measure: a note's rows from its words' length, a drawing beside it at least five rows
  expect("one row", noteRows(ROW_CHARS, false), 1.25);
  expect("one more character wraps", noteRows(ROW_CHARS + 1, false), 2.25);
  expect("a drawing is five rows", noteRows(10, true), 5.25);
  expect("a day: its heading and its notes", dayRows(day(0, [KEY, KEY]), words), 1 + 2 * noteRows(words(KEY).length, false));
}

{  // days run on down a page until the next would not fit; that one starts the next page, whole
  const one = dayRows(day(0, [KEY]), words);   // 2.25 rows
  const fit = Math.floor((PAGE_ROWS + DAY_GAP) / (one + DAY_GAP));   // as many one-note days as the page holds
  const run = Array.from({ length: fit + 1 }, (_, i) => day(i, [KEY]));
  const pages = dayPages(run, words);
  expect("a full page, then the day that did not fit on the next", days(pages), [run.slice(0, fit).map((d) => d.day), [fit]]);
  expect("one day fewer: one page", dayPages(run.slice(0, fit), words).length, 1);
  const long = day(50, Array.from({ length: 12 }, () => "wk_roof"));   // longer than a page
  const over = dayPages([day(49, [KEY]), long, day(51, [KEY])], words);
  expect("a day longer than a page runs on over the next, from where the page had room", days(over), [[49, 50], [50], [50, 51]]);
  expect("every note of it once, in order", over.flatMap((p) => p.filter((d) => d.day === 50).flatMap((d) => d.day_notes)).length, 12);
  expect("every day once, in order", days(dayPages(WEEKS, words)).flat(), WEEKS.map((d) => d.day));
  const sized = (key: string): string => "x".repeat(Number(key.slice(1)));   // key "c<n>": n characters
  const tall = day(0, [`c${18 * ROW_CHARS}`]);   // 1 + 18.25 rows
  expect("a day that fills the page exactly still fits", days(dayPages([tall, day(1, ["c1"])], sized)), [[0, 1]]);   // + .5 + 2.25 = 22
  expect("a row more does not", days(dayPages([tall, day(1, [`c${ROW_CHARS + 1}`])], sized)), [[0], [1]]);
}

{  // a page, once a later one is begun, never changes as days are added
  const all = dayPages(WEEKS, words);
  for (let n = 1; n <= WEEKS.length; n += 1) {
    const some = dayPages(WEEKS.slice(0, n), words);
    expect(`after ${n} days the closed pages are the final ones`, days(some.slice(0, -1)), days(all.slice(0, some.length - 1)));
  }
  expect("the fixture's weeks fill more than one page", all.length > 1, true);
}

{  // drawn: each day's heading, then its notes in order, in their hands and with their drawings
  const r = rig({ notes: [], days: WEEKS, newestDay: null });
  r.open();
  const first = dayPages(WEEKS, words)[0]!;
  expect("the first page: each day headed, its notes under it", r.written(),
    first.flatMap((d) => [catalog.text.fill("ui.journal.day", { n: String(d.day + 1) }), ...d.day_notes.map((n) => text(n.key))]));
  const notes = [...r.sheet().querySelectorAll<HTMLElement>(".journal-note")];
  expect("each note in its hand", notes.map((n) => n.className), first.flatMap((d) => d.day_notes.map((n) => `journal-note hand-${n.hand}`)));
  expect("a drawing beside the note that names one", [...r.sheet().querySelectorAll<HTMLImageElement>(".journal-note-sketch")].map((i) => i.src), ["/assets/journal/note_sketch.png"]);
  expect("a days page is text alone", r.sheet().querySelector<HTMLElement>(".journal-spread")?.dataset["bare"], "true");
  r.next().click();
  expect("the next page starts with the day that did not fit", r.written()[0], catalog.text.fill("ui.journal.day", { n: String(dayPages(WEEKS, words)[1]![0]!.day + 1) }));
}

{  // the same days are the same pages on a phone and a desktop
  const pagesOn = (phone: boolean, width: number): string[][] => {
    Object.assign(window, { innerWidth: width, innerHeight: phone ? 844 : 900 });
    const r = rig({ notes: [], days: WEEKS, newestDay: null, phone });
    r.open();
    const seen = [r.written()];
    while (!r.next().disabled) { r.next().click(); seen.push(r.written()); }
    return seen;
  };
  expect("phone and desktop page alike", pagesOn(true, 390), pagesOn(false, 1440));
  Object.assign(window, { innerWidth: 400, innerHeight: 800 });
}

{  // the Journal is a page of the Book from the first written day, with nothing else written
  const r = rig({ notes: [], days: [day(0, [KEY])], newestDay: null });
  expect("a written day alone: the Journal's button", r.button()?.textContent, text("ui.journal.heading"));
  expect("no day written, nothing else: no Journal", rig({ notes: [], days: [], newestDay: null }).button(), null);
}

{  // unread: a day after the newest turned to; the sheet opens on the first page holding one
  const pages = dayPages(WEEKS, words);
  const lastOfFirst = pages[0]!.at(-1)!.day;
  expect("nothing read yet: the dots", ((r) => [r.dotShows(), r.tabDot()])(rig({ notes: [], days: WEEKS, newestDay: null })), [true, true]);
  expect("read to the newest day: no dot", rig({ notes: [], days: WEEKS, newestDay: WEEKS.at(-1)!.day }).dotShows(), false);
  const r = rig({ notes: [], days: WEEKS, newestDay: lastOfFirst });
  expect("read through the first page: the dot", r.dotShows(), true);
  r.open();
  expect("it opens on the second page", r.written()[0], catalog.text.fill("ui.journal.day", { n: String(pages[1]![0]!.day + 1) }));
}

{  // closing keeps the newest day of the pages turned to, in one write, and no book notes; a day written while its page is
  // open joins the page and stays unread
  const r = rig({ notes: [], days: WEEKS.slice(0, 2), newestDay: null });
  r.sent.length = 0;
  r.open();
  r.show([], [WEEKS[2]!]);
  expect("the day written while open joins the page", r.written().includes(text(WEEKS[2]!.day_notes[0]!.key)), true);
  r.close().click();
  expect("one write: the newest day turned to, not the one written since", [r.sent.length, r.sent[0]?.newest_day_read, r.sent[0]?.journal_read], [1, 1, []]);
  expect("the later day keeps the dot", r.dotShows(), true);
  r.open();
  r.close().click();
  expect("turned to again: read, and an older day is never written back", [r.sent.at(-1)?.newest_day_read, r.dotShows()], [2, false]);
  r.open();
  r.close().click();
  expect("nothing new: nothing sent", r.sent.length, 2);
  const back = rig({ notes: [], days: WEEKS, newestDay: WEEKS.at(-1)!.day });   // all read: it opens on the first page
  back.sent.length = 0;
  back.open();
  back.close().click();
  expect("turning to an earlier page takes nothing back", back.sent.length, 0);
}

{  // a day still being written: a later copy carrying more notes replaces the one held, and as it grows past the page its
  // notes so far keep their page and the rest run on to the next, headed again by its day
  const growing = (n: number): JournalDay => day(9, Array.from({ length: n }, () => KEY));
  const held = joinDays([day(8, [KEY]), growing(1)], [growing(3)]);
  expect("the copy with more notes replaces the day held", held.map((d) => d.day_notes.length), [1, 3]);
  expect("a copy with fewer notes leaves it", joinDays(held, [growing(2)]).map((d) => d.day_notes.length), [1, 3]);
  const notesOn = (pages: JournalDay[][]): number[][] => pages.map((p) => p.map((d) => d.day_notes.length));
  const before = [day(7, Array.from({ length: 12 }, () => KEY))];
  let shown = notesOn(dayPages([...before, growing(1)], words));
  for (let n = 2; n <= 16; n += 1) {
    const now = notesOn(dayPages([...before, growing(n)], words));
    for (let i = 0; i < shown.length - 1; i += 1) expect(`${n} notes: page ${i} is as it was`, now[i], shown[i]);
    const last = shown.length - 1;
    expect(`${n} notes: the last page shown keeps every note it had`, now[last]!.slice(0, shown[last]!.length - 1), shown[last]!.slice(0, -1));
    expect(`${n} notes: the day on the last page shown only grows there`, now[last]![shown[last]!.length - 1]! >= shown[last]!.at(-1)!, true);
    expect(`${n} notes: none lost`, now.flat().reduce((a, b) => a + b, 0), 12 + n);
    shown = now;
  }
  expect("the day ran on to a second page", shown.length > 1 && dayPages([...before, growing(16)], words).at(-1)![0]!.day, 9);
}

{  // a day still being written grows on its page while the page is open: its earlier notes stay where they were drawn
  const partial: JournalDay = { ...WEEKS[1]!, day_notes: WEEKS[1]!.day_notes.slice(0, 1) };
  const r = rig({ notes: [], days: [WEEKS[0]!, partial], newestDay: null });
  r.open();
  const before = r.written();
  r.show([], [{ ...partial, day_notes: [...partial.day_notes, { ...partial.day_notes[0]!, key: "wk_roof" }] }]);
  expect("the earlier notes stay as drawn", r.written().slice(0, before.length), before);
  expect("the new note joins the page", r.written().at(-1), text("wk_roof"));
}
