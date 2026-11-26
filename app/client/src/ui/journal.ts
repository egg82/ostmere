// The Journal (docs/design/opening-screen.md, "The journal"; docs/design/journal.md, "What the page draws"; CONTRACT.txt,
// "JOURNAL"): a page of the Book (ui/book.ts) from its first page on, its button and the Book's tab dotted while
// something is unread. The days pages hold the written days the save served, each day's notes under its day, as many
// days as fit (game/days.ts); every other page is one entry written. A page is its sketch, its notes in their hand and,
// under them, the numbers of the fights it names, in the fight card's words. The draws are seeded (game/journal.ts) and
// the numbers are View.fights'. Turning to it and turning its pages send nothing; when it is left, the book notes of every
// page turned to are kept as read in one write, and the newest day turned to in another.
import type { JournalDay, View } from "../api/types";
import { sing } from "../audio/cues";
import { joinDays } from "../game/days";
import { bookmarkPage, isButton, isUnread, layoutOf, numbersOf, openingPage, pagesOf, turnOf, type NumbersRow, type Page, type Reading, type Section } from "../game/journal";
import { wantedOf } from "../game/pagemarks";
import { UI } from "../game/text";
import { reportError } from "../telemetry";
import type { BookPage } from "./book";
import { el, tapFeedback } from "./dom";
import { JournalNav } from "./journalnav";
import { PageMarks } from "./pagemarks";
import type { PartContext } from "./part";

const SKETCHES = "/assets/journal/";

export class Journal implements BookPage {
  readonly id = "journal";
  readonly label: string;
  readonly root = el("div", "journal");
  readonly frame = "journal-sheet";
  readonly actions: readonly HTMLElement[];
  /** Its button in the Book's row of pages (seat()), hidden until an entry is written. */
  private button: HTMLElement | null = null;
  /** The dots of the unread notes: on its button, and on the Book's tab. */
  private readonly dots = [el("i", "new-dot"), el("i", "new-dot")];
  private readonly sketch = el("div", "journal-sketch-box");
  private readonly notes = el("div", "journal-notes");
  private readonly numbers = el("div", "journal-numbers");
  private readonly spread = el("div", "journal-spread");
  private readonly left = el("div", "journal-page journal-left");
  private readonly pageMarks = new PageMarks(this.spread);
  private readonly nav: JournalNav;
  private view: View | null = null;
  /** Every written day served so far, oldest first. */
  private days: JournalDay[] = [];
  private pages: Page[] = [];
  /** The open page's id, and the one last shown in this page session. */
  private current: string | null = null;
  private last: string | null = null;
  /** The book notes, and the newest day, of the pages turned to since the sheet opened: kept as read when it closes. */
  private readonly turned = new Set<string>();
  private turnedDay: number | null = null;
  private drawn = { page: "", notes: 0, numbers: "" };
  private isOpen = false;
  private readonly failed = new Set<string>();

  /** `tab`: the Book's tab, which carries the dot and the lesson's mark while the journal shows. */
  constructor(private readonly ctx: Pick<PartContext, "catalog" | "keeps" | "saveId">, private readonly tab: HTMLElement) {
    const { catalog } = ctx;
    this.label = catalog.text.get(UI.journalHeading);
    for (const d of this.dots) d.setAttribute("aria-hidden", "true");
    this.nav = new JournalNav(catalog, { turn: (by) => this.turn(by), toggle: () => this.toggleContents(), pick: (i) => this.turnToIndex(i), mark: (s) => this.turnTo(s) });
    this.actions = this.nav.actions;
    this.left.append(this.sketch);
    const right = el("div", "journal-page journal-right");
    right.append(this.notes, this.numbers, this.pageMarks.layer);
    this.spread.append(this.left, right);
    this.root.append(this.nav.marks, this.spread, this.nav.list);
  }

  /** Its button in the Book's row: hidden until the journal shows, and dotted with it. */
  seat(button: HTMLElement): void {
    this.button = button;
    this.sync();
  }

  key(e: KeyboardEvent): void {
    if (this.nav.listed !== null) return;
    if (e.key === "ArrowLeft") this.turn(-1);
    else if (e.key === "ArrowRight") this.turn(1);
  }

  /** Whether the journal is in the Book now (an entry is written and the feature is on). */
  get shown(): boolean {
    return this.view !== null && isButton(this.ctx.catalog, this.view, this.pages);
  }

  /** Written days a Step or Opened carried, joined to those held; drawn at the next update. */
  written(days: readonly JournalDay[]): void {
    this.days = joinDays(this.days, days);
  }

  /** Every written day held, oldest first: what a redrawn screen restores. */
  get writtenDays(): JournalDay[] {
    return [...this.days];
  }

  /** Redrawn from each view: the dots, and an open page's notes and numbers. */
  update(view: View): void {
    this.view = view;
    this.pages = pagesOf(this.ctx.catalog, view, this.days);
    this.sync();
    if (this.isOpen) this.draw(false);
  }

  private get reading(): Reading {
    const { keeps } = this.ctx;
    return { note: (n) => keeps.journalRead(n), newestDay: keeps.newestDayRead() };
  }

  /** What has been read, with the pages turned to since the sheet opened: the contents' dots go as a page is turned to,
   * though the write waits for the close. */
  private get readNow(): Reading {
    const kept = this.reading;
    return { note: (n) => this.turned.has(n) || kept.note(n), newestDay: this.turnedDay === null ? kept.newestDay : Math.max(this.turnedDay, kept.newestDay ?? -1) };
  }

  /** Its button shows with the journal, the Book's tab is its lesson's mark, and the dots show while something written
   * is unread, at no other time. */
  private sync(): void {
    const shown = this.shown;
    if (this.button) this.button.hidden = !shown;
    if (shown) this.tab.dataset["teach"] = "journal";
    const reading = this.reading;
    const unread = this.pages.some((p) => isUnread(p, reading));
    for (const [d, on] of [[this.dots[0]!, this.button], [this.dots[1]!, this.tab]] as const) {
      if (unread && on) on.append(d);
      else d.remove();
    }
  }

  turnedTo(): void {
    if (this.pages.length === 0) return;
    this.turned.clear();
    this.turnedDay = null;
    this.isOpen = true;
    this.nav.show(null);
    this.go(openingPage(this.pages, this.reading, this.last), 0);
  }

  private index(): number {
    return Math.max(0, this.pages.findIndex((p) => p.id === this.current));
  }

  private turn(by: -1 | 1): void {
    const turn = turnOf(this.pages, this.index(), by);
    if (turn) this.go(turn.to, by);
  }

  /** The contents button swaps the page for its section's list and back; nothing is read by listing. */
  private toggleContents(): void {
    this.nav.show(this.nav.listed === null ? this.pages[this.index()]?.section ?? null : null);
    this.draw(false);
  }

  /** A contents row turns to its page. */
  private turnToIndex(i: number): void {
    const by = Math.sign(i - this.index());
    this.nav.show(null);
    this.go(i, by);
  }

  /** Turns to page `i`: what is written on it now counts as read when the sheet closes. `by` is the side turned toward. */
  private go(i: number, by: number): void {
    const page = this.pages[i];
    if (!page) return;
    this.current = this.last = page.id;
    for (const n of page.notes) {
      if (n.day === null) this.turned.add(n.id);
      else this.turnedDay = Math.max(this.turnedDay ?? n.day, n.day);
    }
    this.draw(true);
    if (by !== 0) {
      this.slide(by);
      sing("page");
    }
  }

  /** A turned page slides in from the side turned toward and fades in (the CSS, off under reduced motion). */
  private slide(by: number): void {
    this.spread.classList.remove("turn-next", "turn-prev");
    void this.spread.offsetWidth;
    this.spread.classList.add(by > 0 ? "turn-next" : "turn-prev");
  }

  private draw(whole: boolean): void {
    const page = this.pages[this.index()];
    if (!page || !this.view) return;
    const at = this.index();
    this.nav.drawTurns(this.pages, at);
    this.nav.drawList(this.pages, at, this.readNow);
    this.spread.hidden = this.nav.listed !== null;
    this.nav.drawMarks(this.pages, this.nav.listed ?? page.section);
    if (this.nav.listed !== null) return;
    if (whole || this.drawn.page !== page.id) this.drawPage(page);
    else this.appendNotes(page);
    this.drawNumbers(page);
    this.pageMarks.show(wantedOf(this.ctx.saveId(), page, this.days));
  }

  /** A bookmark's page: the section's first with an unread note, else its latest. */
  private turnTo(section: Section): void {
    if (this.nav.listed !== null) {
      this.nav.show(section);
      this.draw(false);
      return;
    }
    const to = bookmarkPage(this.pages, section, this.reading);
    if (to >= 0) this.go(to, Math.sign(to - this.index()));
  }

  private drawPage(page: Page): void {
    const layout = layoutOf(page.id, page.notes.length);
    const s = this.spread.style;
    s.setProperty("--sk-w", `${layout.sketchWidth.toFixed(1)}%`);
    s.setProperty("--sk-x", layout.sketchX.toFixed(3));
    s.setProperty("--sk-y", layout.sketchY.toFixed(3));
    this.spread.dataset["above"] = String(layout.noteAbove);
    const bare = page.sketch === null;   // no drawing: the page is text alone, with no room kept for one
    this.left.hidden = bare;
    this.spread.dataset["bare"] = String(bare);
    this.sketch.replaceChildren(...(page.sketch === null ? [] : [this.image(page.sketch, "journal-sketch")]));
    this.notes.replaceChildren();
    this.drawn = { ...this.drawn, page: page.id, notes: 0 };
    this.appendNotes(page);
  }

  /** Notes only append: one written while the page is open joins it, and no earlier note moves. On a days page each
   * day's first note is headed by its day. */
  private appendNotes(page: Page): void {
    const looks = layoutOf(page.id, page.notes.length).notes;
    const { text } = this.ctx.catalog;
    for (let i = this.drawn.notes; i < page.notes.length; i++) {
      const info = page.notes[i]!;
      const look = looks[i]!;
      if (info.day !== null && info.day !== page.notes[i - 1]?.day) {
        this.notes.append(el("p", "journal-day", text.fill(UI.journalDay, { n: String(info.day + 1) })));
      }
      const node = el("div", `journal-note hand-${info.hand}`);
      node.append(el("p", "journal-words", text.get(info.key)));
      if (info.count !== null) node.append(el("span", "journal-count", String(info.count)));   // beside, never inside
      if (info.sketch) node.append(this.image(info.sketch, "journal-note-sketch"));
      node.style.setProperty("--tilt", `${look.tiltDeg.toFixed(2)}deg`);
      node.style.setProperty("--indent", `${look.indentRem.toFixed(2)}rem`);
      this.notes.append(node);
    }
    this.drawn.notes = page.notes.length;
  }

  /** A sketch is loaded when its page is drawn; one that fails leaves its room empty and is reported once. */
  private image(sketch: string, className: string): HTMLImageElement {
    const img = el("img", className);
    img.alt = "";
    img.setAttribute("aria-hidden", "true");
    img.addEventListener("error", () => {
      img.classList.add("missing");
      if (this.failed.has(sketch)) return;
      this.failed.add(sketch);
      reportError("error", `journal sketch failed to load: ${sketch}`, "journal");
    });
    img.src = `${SKETCHES}${sketch}.png`;
    return img;
  }

  /** The numbers under the notes, redrawn at each view while the sheet is open. */
  private drawNumbers(page: Page): void {
    const rows = this.view ? numbersOf(this.ctx.catalog, this.view, page) : [];
    const key = JSON.stringify([page.id, rows]);
    this.numbers.hidden = rows.length === 0;
    if (key === this.drawn.numbers) return;
    this.drawn.numbers = key;
    this.numbers.replaceChildren(...rows.map(rowNode));
  }

  /** Turned from, or the Book closed (its Close, the backdrop, Escape, another tab): a write of the book notes read and
   * one of the newest day turned to, each only when it adds something, then the dots are redrawn. */
  turnedFrom(): void {
    if (!this.isOpen) return;
    this.isOpen = false;
    this.ctx.keeps.keepJournalRead(this.turned);
    this.ctx.keeps.keepDayRead(this.turnedDay);
    this.turned.clear();
    this.turnedDay = null;
    this.sync();
  }
}

function rowNode(r: NumbersRow): HTMLElement {
  const row = el("div", "journal-row");
  const vs = el("span", "journal-vs");
  vs.textContent = r.vs;
  row.append(el("span", "journal-runner", r.label), el("span", "journal-odds", r.odds), vs);
  if (r.tally !== null) row.append(el("span", "journal-tally", r.tally));
  return row;
}
