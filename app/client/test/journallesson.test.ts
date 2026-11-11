// The journal's lesson on pages with and without numbers (CONTRACT.txt, "JOURNAL", THE CLIENT MAY): the numbers step runs
// only on a page that shows numbers; on a page with none the lesson ends, kept, after its notes step, and the numbers
// step is a lesson of its own the first time a page with numbers is open. A step that waits on numbers never holds the
// lessons after it. And the rule offer that follows the book at its first showing is not held back by the journal lesson.
import { install } from "./fake-dom";
import { testContext } from "./context";
import { catalog, expect, KEPT, rig, stepWith, text } from "./journalrig";
import { NOTES_A, NOTES_D } from "../fixtures/journal";
import { fixtureStep } from "../fixtures/steps";
import type { LedgerLine, View } from "../src/api/types";
import { CLOCK, FIRST_MIX, FIRST_RULE, JOURNAL, JOURNAL_NUMBERS } from "../src/game/lessons";
import { Glow } from "../src/ui/fresh";
import { Ledger } from "../src/ui/ledger";
import { Lessons } from "../src/ui/lessons";
import { keepsOf, NEW_FLAT, type Flat } from "./kept";

install();
const RECT = { left: 10, top: 10, width: 80, height: 30, right: 90, bottom: 40 };
const NONE = { left: 0, top: 0, width: 0, height: 0, right: 0, bottom: 0 };
const LATER = 60_000;
let clock = 0;

/** The strip and sheet with the lesson runner beside them, on an account whose kept lessons are `lessons`. */
function walk(lessons: string[], notes: string[]) {
  const r = rig({ lessons: [...KEPT, JOURNAL, JOURNAL_NUMBERS], notes });   // the screen's own runner stays idle
  const sent: Flat[] = [];
  const keeps = keepsOf({ ...NEW_FLAT, lessons }, sent);
  const runner = new Lessons({ catalog, glow: new Glow(), keeps }, document.body, () => undefined, document, () => clock);
  runner.update(stepWith(notes.slice(0, 1), 500).view);   // the book as it first shows: one page written
  const line = (): string => (runner.root.hidden ? "" : runner.root.querySelector(".lesson-line")?.textContent ?? "");
  const tick = (t: number): void => {
    for (const sel of ['[data-teach="journal"]', '[data-teach="clock"]', '.journal-sheet [data-teach="journal-note"]', ".journal-sheet .journal-numbers"])
      for (const n of document.querySelectorAll(sel)) Object.assign(n, { rect: (n as HTMLElement).hidden ? NONE : RECT });   // the fake DOM lays nothing out
    clock = t;
    runner.tick();
  };
  /** A tap on the note's Got it: a read step ends. */
  const got = (): void => runner.root.querySelector<HTMLElement>(".lesson-next")?.click();
  return { r, runner, keeps, sent, line, tick, got };
}

{  // a days page has no numbers: the lesson ends kept after its notes step, and the later lessons run
  const w = walk(KEPT, [...NOTES_D, ...NOTES_A]);
  w.tick(0);
  expect("starts on the button", w.line(), text("ui.lesson.journal_open"));
  w.r.button()!.click();
  w.tick(1);
  expect("then the page's last note", w.line(), text("ui.lesson.journal_notes"));
  w.got();
  w.tick(LATER);
  expect("ended after the notes step: kept", [w.runner.current, w.keeps.lessonKept(JOURNAL), w.keeps.lessonKept(JOURNAL_NUMBERS)], [null, true, false]);
  expect("the record counts it done", w.sent.at(-1)?.lesson_ends?.at(-1)?.skipped, false);
  const clockTrigger = document.createElement("div");
  clockTrigger.dataset["teach"] = "clock";
  document.body.append(clockTrigger);
  w.tick(LATER + 1);
  expect("a later lesson is not held by the numbers step", w.runner.current, CLOCK);
}

{  // the numbers step is a lesson of its own the first time a page with numbers is open
  const w = walk(KEPT, [...NOTES_D, ...NOTES_A]);
  w.tick(0);
  w.r.button()!.click();
  w.tick(1);
  w.got();
  w.tick(LATER);
  w.tick(LATER + 1);
  expect("no numbers on the page: nothing running", w.runner.current, null);
  w.r.next().click();   // the creatures page names a fight
  w.tick(LATER + 2);
  expect("its own lesson starts on the page's numbers", [w.runner.current, w.line()], [JOURNAL_NUMBERS, text("ui.lesson.journal_numbers")]);
  w.got();
  w.tick(LATER + 2 + LATER);
  expect("and is kept", [w.runner.current, w.keeps.lessonKept(JOURNAL_NUMBERS)], [null, true]);
  w.r.prev().click();
  w.r.next().click();
  w.tick(3 * LATER);
  expect("never again", w.runner.current, null);
}

{  // opened first on a page with numbers: the three lines run in turn, as before
  const w = walk(KEPT, NOTES_A);
  w.tick(0);
  w.r.button()!.click();
  w.tick(1);
  expect("notes", w.line(), text("ui.lesson.journal_notes"));
  w.got();
  w.tick(LATER);
  w.tick(LATER + 1);
  expect("then the numbers", [w.runner.current, w.line()], [JOURNAL_NUMBERS, text("ui.lesson.journal_numbers")]);
  w.got();
  w.tick(LATER + 1 + LATER);
  expect("both kept", [w.keeps.lessonKept(JOURNAL), w.keeps.lessonKept(JOURNAL_NUMBERS), w.runner.current], [true, true, null]);
}

/** A red wood line, so the ledger offers the wood card as a rule (lessonhold.test.ts). */
const red: LedgerLine = {
  store: "wood", segment: { start: 100, start_value: 14_000, rate: -120_000, limit: 0 }, net_per_hour: -120_000,
  contributions: [{ runner: "tend", per_hour: -120_000 }], empties_at: null, fills_at: null, falling: true, covered: false, starved: false, cap: 40_000,
};

{  // the book shows first, the rule offer follows: the journal lesson does not hold it back; the rule's lesson comes first
  document.body.replaceChildren();
  const { ctx } = testContext();
  const mid = fixtureStep("mid", 100).view;
  const calm: View = { ...mid, orders: [], orders_on: [] };
  const redView: View = { ...calm, ledger: [red, ...calm.ledger.filter((l) => l.store !== "wood")] };
  const keeps = keepsOf({ ...NEW_FLAT, lessons: [FIRST_MIX] });
  const lessons = new Lessons({ catalog: ctx.catalog, glow: ctx.glow, keeps }, document.body, () => ledger.update(view, null), document, () => clock);
  const ledger = new Ledger({ ...ctx, keeps, lesson: () => lessons.holding, lessonSubject: () => lessons.subject });
  let view = calm;
  document.body.append(ledger.root);
  const book = document.createElement("button");
  book.dataset["teach"] = "journal";
  Object.assign(book, { rect: RECT });
  document.body.append(book);
  lessons.update(calm);
  ledger.update(calm, null);
  clock = 0;
  lessons.tick();
  expect("the book's lesson is under way", lessons.current, JOURNAL);
  view = redView;
  lessons.update(redView);
  ledger.update(redView, null);
  const offers = (): HTMLElement[] => [...document.querySelectorAll<HTMLElement>(`[data-teach="rule-offer"]`)];
  expect("the rule offer is on show, not waiting", offers().length, 1);
  for (const n of offers()) Object.assign(n, { rect: RECT });
  clock = 1;
  lessons.tick();
  expect("the rule's lesson runs first", lessons.current, FIRST_RULE);
  expect("the book's lesson was not kept: it comes back", keeps.lessonKept(JOURNAL), false);
}

{  // a journal lesson the player has begun (the book tapped) is not cut off: the offer waits for it, as for any lesson
  document.body.replaceChildren();
  const { ctx } = testContext();
  const mid = fixtureStep("mid", 100).view;
  const calm: View = { ...mid, orders: [], orders_on: [] };
  const redView: View = { ...calm, ledger: [red, ...calm.ledger.filter((l) => l.store !== "wood")] };
  const keeps = keepsOf({ ...NEW_FLAT, lessons: [FIRST_MIX] });
  const lessons = new Lessons({ catalog: ctx.catalog, glow: ctx.glow, keeps }, document.body, () => ledger.update(redView, null), document, () => clock);
  const ledger = new Ledger({ ...ctx, keeps, lesson: () => lessons.holding, lessonSubject: () => lessons.subject });
  document.body.append(ledger.root);
  const book = document.createElement("button");
  book.dataset["teach"] = "journal";
  Object.assign(book, { rect: RECT });
  document.body.append(book);
  lessons.update(calm);
  ledger.update(calm, null);
  clock = 0;
  lessons.tick();
  book.click();
  lessons.update(redView);
  ledger.update(redView, null);
  clock = 1;
  lessons.tick();
  expect("begun: it still runs, and the offer waits", [lessons.current, document.querySelectorAll(`[data-teach="rule-offer"]`).length], [JOURNAL, 0]);
}
console.log("journallesson: ok");
