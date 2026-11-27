// Finding a page in a long journal (docs/design/opening-screen/journal.md, "The journal"): Prev and Next stay in a section and say
// where they go at its edge, a section's contents lists its pages by title, and the sheet shows the place in the section.
// The logic runs on synthetic pages (many sections, a book far longer than any shipped); the sheet on the fixture pages:
// D is a days page, A and C are creatures pages, B is a places page, so the pages run D, A, C, B.
import { Catalog } from "../src/game/catalog";
import { contentsOf, pagesOf, placeOf, SECTIONS, turnOf, type Page, type Reading, type Section } from "../src/game/journal";
import { fixtureContent } from "../fixtures/content";
import { journalStep, LONG_CREATURES, LONG_DAYS, LONG_DAYS_N, LONG_PLACES, LONG_READ, LONG_READ_TO, NOTE_B, NOTE_C, NOTES_A, NOTES_D, withJournal, withLongBook } from "../fixtures/journal";
import { expect, fire, rig, text } from "./journalrig";

const EVERY = [...NOTES_D, ...NOTES_A, NOTE_C, NOTE_B];
type Rig = ReturnType<typeof rig>;
const open = (r: Rig): Rig => { r.open(); return r; };
const label = (b: HTMLElement): string => b.textContent ?? "";
const rows = (r: Rig): string[] => [...r.sheet().querySelectorAll<HTMLElement>(".journal-entry-title")].map(label);
const rowButtons = (r: Rig): HTMLElement[] => [...r.sheet().querySelectorAll<HTMLElement>(".journal-entry")];
const bookmarks = (r: Rig): HTMLElement[] => [...r.sheet().querySelectorAll<HTMLElement>(".journal-bookmarks button")];
const place = (r: Rig): string => r.sheet().querySelector(".journal-place")!.textContent ?? "";

const page = (id: string, section: string): Page => ({ id, section: section as Section, title: `${id}.t`, sketch: null, runners: [], notes: [{ id: `${id}.n`, key: `${id}.k`, hand: "ink", sketch: null, day: null, count: null }] });
const unreadAll: Reading = { note: () => false, newestDay: null };

{  // a turn stays in the section; past its end it names the section it crosses into; the book's ends turn nowhere
  const pages = [page("a", "s1"), page("b", "s1"), page("c", "s2"), page("d", "s3"), page("e", "s3")];
  expect("within a section", turnOf(pages, 0, 1), { to: 1, crossing: null });
  expect("past a section's end", turnOf(pages, 1, 1), { to: 2, crossing: "s2" });
  expect("a one-page section both ways", [turnOf(pages, 2, -1), turnOf(pages, 2, 1)], [{ to: 1, crossing: "s1" }, { to: 3, crossing: "s3" }]);
  expect("back into a section", turnOf(pages, 3, -1), { to: 2, crossing: "s2" });
  expect("the first page has no Prev, the last no Next", [turnOf(pages, 0, -1), turnOf(pages, 4, 1)], [null, null]);
  expect("place in the section", [placeOf(pages, 1), placeOf(pages, 2), placeOf(pages, 4)], [{ n: 2, of: 2 }, { n: 1, of: 1 }, { n: 2, of: 2 }]);
}

{  // a book of eight sections and seventy pages: every page is reachable by Next alone, crossing exactly at each section's end, and a section's contents lists exactly its pages
  const names = Array.from({ length: 8 }, (_, i) => `s${i}`);
  const pages = names.flatMap((s, i) => Array.from({ length: 5 + i * 2 }, (_, k) => page(`${s}.${k}`, s)));
  expect("a long book", pages.length, 5 + 7 + 9 + 11 + 13 + 15 + 17 + 19);
  let at = 0;
  const crossings: string[] = [];
  for (let t = turnOf(pages, at, 1); t; t = turnOf(pages, at, 1)) { at = t.to; if (t.crossing) crossings.push(t.crossing); }
  expect("Next alone walks the whole book, crossing at each section's end", [at, crossings], [pages.length - 1, names.slice(1)]);
  const cat = new Catalog({ ...fixtureContent, text_entries: [...fixtureContent.text_entries, ...pages.map((p) => ({ key: `${p.id}.k`, text: p.id }))] });
  const listed = names.flatMap((s) => contentsOf(cat, pages, s as Section, unreadAll, 0).map((r) => r.index));
  expect("the contents together list every page once, in order", listed, pages.map((_, i) => i));
}

{  // the contents' rows: a days page by its first day, an entry by its first note's words; unread and the open page marked
  const cat = new Catalog(withJournal(fixtureContent));
  const step = journalStep("journal", 1);
  const pages = pagesOf(cat, { ...step.view, unlocked: [...step.view.unlocked, { category: "entry", id: "page_c" }, { category: "note", id: NOTE_C }] }, step.journal_days);
  const seen: Reading = { note: (n) => NOTES_A.includes(n), newestDay: null };
  const creatures = contentsOf(cat, pages, "creatures", seen, 0);   // no days written: page 0 is the first creatures page
  expect("an entry's title is its own, not its first note's words", creatures.map((r) => r.title), [cat.text.get("title_page_a"), cat.text.get("title_page_c")]);
  expect("unread is per page; the open page is marked", creatures.map((r) => [r.unread, r.current]), [[false, true], [true, false]]);
}

{  // the long synthetic book: more pages than any shipped save, and its contents lists days by day
  const cat = new Catalog(withLongBook(withJournal(fixtureContent)));
  const step = journalStep("journalbook", 1);
  const pages = pagesOf(cat, step.view, LONG_DAYS);
  const days = pages.filter((p) => p.section === "days").length;
  expect("the long book's sections", [days > 20, pages.filter((p) => p.section === "creatures").length, pages.filter((p) => p.section === "places").length], [true, LONG_CREATURES, LONG_PLACES]);
  expect("sixty pages and more", pages.length > 60, true);
  const read: Reading = { note: (n) => LONG_READ.includes(n), newestDay: LONG_READ_TO };
  const list = contentsOf(cat, pages, "days", read, 0);
  expect("every days page is a row, the first headed Day 1", [list.length, list[0]!.title], [days, "Day 1"]);
  expect("only pages past the newest day read are unread", list.map((r) => r.unread).join(), pages.filter((p) => p.section === "days").map((p) => p.notes.some((n) => n.day! > LONG_READ_TO)).join());
  expect("the days run to the last day", LONG_DAYS.length, LONG_DAYS_N);
}

{  // on the sheet, Prev and Next name the section they cross into, and the place reads in the section
  const r = open(rig({ notes: EVERY, read: EVERY }));   // all read: it opens on the first page, the days page
  expect("on the days page, Next names creatures", label(r.next()), `${text("ui.journal.creatures")} ›`);
  expect("Prev is off at the book's start", [r.prev().disabled, place(r)], [true, "1 / 1"]);
  r.next().click();
  expect("first creatures page: Prev names days, Next stays", [label(r.prev()), label(r.next()), place(r)], [`‹ ${text("ui.journal.days")}`, `${text("ui.journal.next")} ›`, "1 / 2"]);
  r.next().click();
  expect("last creatures page: Next names places", [label(r.prev()), label(r.next()), place(r)], [`‹ ${text("ui.journal.prev")}`, `${text("ui.journal.places")} ›`, "2 / 2"]);
  r.next().click();
  expect("the last page: Next is off", [r.next().disabled, label(r.prev())], [true, `‹ ${text("ui.journal.creatures")}`]);
}

{  // Contents swaps the page for its section's list; a row turns to its page; the list reads nothing
  const r = open(rig({ notes: EVERY, read: [] }));   // nothing read: it opens on the days page
  r.sent.length = 0;
  r.next().click();
  expect("on the first creatures page", r.words(), NOTES_A.map(text));
  r.contents().click();
  expect("the list: both creatures pages, by title", rows(r), [text("title_page_a"), text("title_page_c")]);
  expect("the open page's row is marked", rowButtons(r).map((b) => b.getAttribute("aria-current")), ["page", null]);
  expect("the spread is out of the way", [r.sheet().querySelector<HTMLElement>(".journal-spread")!.hidden, r.contents().getAttribute("aria-pressed")], [true, "true"]);
  expect("the page not yet turned to is dotted", rowButtons(r).map((b) => b.querySelector(".new-dot") !== null), [false, true]);
  rowButtons(r)[1]!.click();
  expect("a row turns to its page and the list goes", [r.words(), r.sheet().querySelector<HTMLElement>(".journal-contents")!.hidden, r.sheet().querySelector<HTMLElement>(".journal-spread")!.hidden], [[text(NOTE_C)], true, false]);
  r.contents().click();
  r.contents().click();
  expect("the button puts the page back", [r.words(), r.contents().getAttribute("aria-pressed")], [[text(NOTE_C)], "false"]);
}

{  // while listed, a bookmark lists its section and no page is turned to; arrows turn nothing; closing keeps only the pages turned to
  const r = open(rig({ notes: EVERY, read: [] }));
  r.sent.length = 0;
  r.contents().click();
  expect("the days list, one page", rows(r), ["Day 1"]);
  bookmarks(r)[2]!.click();
  expect("the places bookmark lists places", [rows(r), bookmarks(r).map((b) => b.getAttribute("aria-current") === "true")], [[text("title_page_b")], [false, false, true]]);
  fire(r.sheet(), "keydown");
  r.screen.root.dispatchEvent(Object.assign(new Event("keydown"), { key: "ArrowRight" }));
  expect("still the list", rows(r), [text("title_page_b")]);
  r.close().click();
  expect("only the page opened on is read: the day, and no book note", [r.sent.flatMap((s) => [...(s.journal_read ?? [])]), r.sent.at(-1)?.newest_day_read], [[], 0]);
}

{  // Contents is a real button after Close, a tap away on a phone and on a desktop
  const phone = open(rig({ notes: EVERY }));
  const desk = open(rig({ notes: EVERY, phone: false }));
  expect("the control is a button worded by its key", [phone, desk].map((r) => [r.contents().tagName.toLowerCase(), label(r.contents())]), [["button", "Contents"], ["button", "Contents"]]);
  expect("the key is in the content", SECTIONS.length > 0 && text("ui.journal.contents"), "Contents");
}
