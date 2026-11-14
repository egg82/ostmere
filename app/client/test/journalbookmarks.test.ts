// The journal's sections and bookmarks (CONTRACT.txt, "JOURNAL", THE CLIENT MAY), run against the rendered sheet on the
// fixture pages: D is a days page (no sketch), A and C are creatures pages, B is a places page; content order is B, A, C, D.
import { catalog, expect, fire, requests, rig, text } from "./journalrig";
import { NOTE_B, NOTE_C, NOTES_A, NOTES_D } from "../fixtures/journal";

const EVERY = [...NOTES_D, ...NOTES_A, NOTE_C, NOTE_B];
type Rig = ReturnType<typeof rig>;
const bookmarks = (r: Rig): HTMLElement[] => [...r.sheet().querySelectorAll<HTMLElement>(".journal-bookmarks button")];
const labels = (r: Rig): string[] => bookmarks(r).map((b) => b.textContent ?? "");
const current = (r: Rig): string[] => bookmarks(r).filter((b) => b.getAttribute("aria-current") === "true").map((b) => b.textContent ?? "");
const open = (r: Rig): Rig => { r.open(); return r; };

{  // one bookmark per section that has a written page, in the order days, creatures, places, worded by the section's key
  expect("all three sections written", labels(open(rig({ notes: EVERY }))), [text("ui.journal.days"), text("ui.journal.creatures"), text("ui.journal.places")]);
  expect("the words come from the text keys", labels(open(rig({ notes: EVERY }))), ["Days", "Creatures", "Places"]);
  expect("a section with no page written has no bookmark", labels(open(rig({ notes: [...NOTES_D, NOTE_B] }))), [text("ui.journal.days"), text("ui.journal.places")]);
  expect("only creatures written", labels(open(rig({ notes: NOTES_A }))), [text("ui.journal.creatures")]);
}

{  // the bookmarks are real buttons a keyboard reaches, in a labelled group
  const r = open(rig({ notes: EVERY }));
  expect("buttons", bookmarks(r).map((b) => b.tagName.toLowerCase()), ["button", "button", "button"]);
  expect("none is taken out of the tab order", bookmarks(r).map((b) => b.getAttribute("tabindex")), [null, null, null]);
  const group = r.sheet().querySelector<HTMLElement>(".journal-bookmarks")!;
  expect("the group is a labelled navigation", [group.tagName.toLowerCase(), group.getAttribute("aria-label")], ["nav", text("ui.journal.heading")]);
}

{  // pages run days, creatures, places whatever the content order; Prev and Next cross sections one page at a time
  const r = open(rig({ notes: EVERY, read: EVERY }));   // all read: it opens on the page last shown, else the first
  expect("opens on the first page: the days page", r.words(), NOTES_D.map(text));
  const seen: string[][] = [r.words()];
  for (let i = 0; i < 3; i += 1) { r.next().click(); seen.push(r.words()); }
  expect("days, creatures twice, places", seen, [NOTES_D.map(text), NOTES_A.map(text), [text(NOTE_C)], [text(NOTE_B)]]);
  expect("Next is off on the last page, across sections", r.next().disabled, true);
}

{  // the open page's section's bookmark is the current one, and the mark follows the pages
  const r = open(rig({ notes: EVERY, read: EVERY }));
  expect("on a days page: Days", current(r), [text("ui.journal.days")]);
  r.next().click();
  expect("turned into creatures", current(r), [text("ui.journal.creatures")]);
  r.next().click();
  expect("still creatures", current(r), [text("ui.journal.creatures")]);
  r.next().click();
  expect("turned into places", current(r), [text("ui.journal.places")]);
  r.prev().click();
  expect("and back", current(r), [text("ui.journal.creatures")]);
}

{  // a bookmark opens its section's first page holding an unread note, else its latest page
  const none = open(rig({ notes: EVERY, read: [...NOTES_D, ...NOTES_A, NOTE_C, NOTE_B] }));
  bookmarks(none)[1]!.click();
  expect("all read: the section's latest page, the last in content order", none.words(), [text(NOTE_C)]);
  bookmarks(none)[0]!.click();
  expect("the days bookmark, one page: that page", none.words(), NOTES_D.map(text));
  bookmarks(none)[2]!.click();
  expect("the places bookmark", none.words(), [text(NOTE_B)]);

  const unread = open(rig({ notes: EVERY, read: [...NOTES_D, NOTE_B, NOTE_C] }));   // creatures: A unread, C read
  expect("it opens on the first page with an unread note", unread.words(), NOTES_A.map(text));
  bookmarks(unread)[0]!.click();
  expect("away from creatures", unread.words(), NOTES_D.map(text));
  bookmarks(unread)[1]!.click();
  expect("back to creatures: the unread page, not the latest", unread.words(), NOTES_A.map(text));

  const second = open(rig({ notes: EVERY, read: [...NOTES_D, ...NOTES_A, NOTE_B] }));   // creatures: A read, C unread
  bookmarks(second)[1]!.click();
  expect("the first unread in the section is the later page when the earlier is read", second.words(), [text(NOTE_C)]);
  expect("and the mark is on its section", current(second), [text("ui.journal.creatures")]);
}

{  // turning to a bookmark causes no write until the sheet closes; the page opened on and each page turned to count as read (C was not turned to)
  const r = rig({ notes: EVERY, read: [] });
  r.sent.length = 0;
  requests.length = 0;
  r.open();
  bookmarks(r)[2]!.click();
  bookmarks(r)[1]!.click();
  expect("nothing sent from a bookmark", [r.sent.length, r.asked, requests.length], [0, { decided: 0, dry: 0 }, 0]);
  r.close().click();
  expect("one write; the pages turned to are read", [r.sent.length, [...(r.sent[0]?.journal_read ?? [])].sort()], [1, [...NOTES_D, ...NOTES_A, NOTE_B].sort()]);
}

{  // a section's first page written while the sheet is open adds its bookmark in order
  const r = open(rig({ notes: NOTES_A, read: NOTES_A }));
  expect("creatures alone", labels(r), [text("ui.journal.creatures")]);
  r.show([...NOTES_A, ...NOTES_D]);
  expect("a days page is written: its bookmark comes first", labels(r), [text("ui.journal.days"), text("ui.journal.creatures")]);
  expect("the open page keeps the mark", current(r), [text("ui.journal.creatures")]);
  fire(r.sheet(), "close");
  expect("the catalogue holds the section words", catalog.text.get("ui.journal.places"), "Places");
}
