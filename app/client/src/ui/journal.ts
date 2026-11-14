// The Journal (docs/design/opening-screen.md, "The journal"; CONTRACT.txt, "JOURNAL"): a page of the Book (ui/book.ts)
// from the first entry on, its button and the Book's tab dotted while a note is unread, one journal page per entry
// written. A journal page is the entry's sketch, its notes in their hand and, under them, the numbers of the fights it
// names, in the fight card's words. The draws are seeded (game/journal.ts) and the numbers are View.fights'. Turning to
// it and turning its pages send nothing; the notes of every page turned to are kept as read in one write when it is left.
import type { View } from "../api/types";
import { bookmarkPage, bookmarksOf, isButton, layoutOf, numbersOf, openingPage, pagesOf, unreadOf, type NumbersRow, type Page, type Section } from "../game/journal";
import { UI } from "../game/text";
import { reportError } from "../telemetry";
import type { BookPage } from "./book";
import { el, tapFeedback } from "./dom";
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
  /** One bookmark for each section that has a page written, in the book's order. */
  private readonly marks = el("nav", "tabs journal-bookmarks");
  private readonly prev = el("button", "quiet");
  private readonly next = el("button", "quiet");
  private view: View | null = null;
  private pages: Page[] = [];
  /** The entry on the open page, and the one last shown in this page session. */
  private current: string | null = null;
  private last: string | null = null;
  /** The notes of the pages turned to since the sheet opened: sent as read when it closes. */
  private readonly turned = new Set<string>();
  private drawn = { entry: "", notes: 0, numbers: "", sections: "" };
  private isOpen = false;
  private readonly failed = new Set<string>();

  /** `tab`: the Book's tab, which carries the dot and the lesson's mark while the journal shows. */
  constructor(private readonly ctx: Pick<PartContext, "catalog" | "keeps">, private readonly tab: HTMLElement) {
    const { catalog } = ctx;
    this.label = catalog.text.get(UI.journalHeading);
    for (const d of this.dots) d.setAttribute("aria-hidden", "true");
    for (const [b, key, by] of [[this.prev, UI.journalPrev, -1], [this.next, UI.journalNext, 1]] as const) {
      b.type = "button";
      b.textContent = catalog.text.get(key);
      b.addEventListener("click", () => { tapFeedback(); this.turn(by); });
    }
    this.actions = [this.prev, this.next];
    this.left.append(this.sketch);
    this.marks.setAttribute("aria-label", catalog.text.get(UI.journalHeading));
    const right = el("div", "journal-page journal-right");
    right.append(this.notes, this.numbers);
    this.spread.append(this.left, right);
    this.root.append(this.marks, this.spread);
  }

  /** Its button in the Book's row: hidden until the journal shows, and dotted with it. */
  seat(button: HTMLElement): void {
    this.button = button;
    this.sync();
  }

  key(e: KeyboardEvent): void {
    if (e.key === "ArrowLeft") this.turn(-1);
    else if (e.key === "ArrowRight") this.turn(1);
  }

  /** Whether the journal is in the Book now (an entry is written and the feature is on). */
  get shown(): boolean {
    return this.view !== null && isButton(this.ctx.catalog, this.view, this.pages);
  }

  /** Redrawn from each view: the dots, and an open page's notes and numbers. */
  update(view: View): void {
    this.view = view;
    this.pages = pagesOf(this.ctx.catalog, view);
    this.sync();
    if (this.isOpen) this.draw(false);
  }

  /** Its button shows with the journal, the Book's tab is its lesson's mark, and the dots show while a note is written
   * and unread, at no other time. */
  private sync(): void {
    const shown = this.shown;
    if (this.button) this.button.hidden = !shown;
    if (shown) this.tab.dataset["teach"] = "journal";
    const unread = unreadOf(this.pages, (n) => this.ctx.keeps.journalRead(n)).length > 0;
    for (const [d, on] of [[this.dots[0]!, this.button], [this.dots[1]!, this.tab]] as const) {
      if (unread && on) on.append(d);
      else d.remove();
    }
  }

  turnedTo(): void {
    if (this.pages.length === 0) return;
    this.turned.clear();
    this.isOpen = true;
    this.go(openingPage(this.pages, (n) => this.ctx.keeps.journalRead(n), this.last), 0);
  }

  private index(): number {
    return Math.max(0, this.pages.findIndex((p) => p.entry.entry === this.current));
  }

  private turn(by: -1 | 1): void {
    const to = this.index() + by;
    if (to >= 0 && to < this.pages.length) this.go(to, by);
  }

  /** Turns to page `i`: its notes written now count as read when the sheet closes. `by` is the side turned toward. */
  private go(i: number, by: number): void {
    const page = this.pages[i];
    if (!page) return;
    this.current = this.last = page.entry.entry;
    for (const n of page.notes) this.turned.add(n.note);
    this.draw(true);
    if (by !== 0) this.slide(by);
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
    this.prev.disabled = at === 0;
    this.next.disabled = at === this.pages.length - 1;
    if (whole || this.drawn.entry !== page.entry.entry) this.drawPage(page);
    else this.appendNotes(page);
    this.drawNumbers(page);
    this.drawMarks(page);
  }

  /** The bookmarks of the sections written, the open page's section marked as the current one. */
  private drawMarks(page: Page): void {
    const sections = bookmarksOf(this.pages);
    const key = sections.map((m) => m.section).join();
    if (key !== this.drawn.sections) {
      this.drawn.sections = key;
      this.marks.replaceChildren(...sections.map((m) => this.bookmark(m.section, m.key)));
    }
    for (const b of Array.from(this.marks.children) as HTMLElement[]) {
      const on = b.dataset["section"] === page.entry.section;
      b.classList.toggle("on", on);
      if (on) b.setAttribute("aria-current", "true");
      else b.removeAttribute("aria-current");
    }
  }

  private bookmark(section: Section, key: string): HTMLButtonElement {
    const b = el("button", "tab", this.ctx.catalog.text.get(key));
    b.type = "button";
    b.dataset["section"] = section;
    b.addEventListener("click", () => { tapFeedback(); this.turnTo(section); });
    return b;
  }

  /** A bookmark's page: the section's first with an unread note, else its latest. */
  private turnTo(section: Section): void {
    const to = bookmarkPage(this.pages, section, (n) => this.ctx.keeps.journalRead(n));
    if (to >= 0) this.go(to, Math.sign(to - this.index()));
  }

  private drawPage(page: Page): void {
    const layout = layoutOf(page.entry.entry, page.entry.notes.length);
    const s = this.spread.style;
    s.setProperty("--sk-w", `${layout.sketchWidth.toFixed(1)}%`);
    s.setProperty("--sk-x", layout.sketchX.toFixed(3));
    s.setProperty("--sk-y", layout.sketchY.toFixed(3));
    this.spread.dataset["above"] = String(layout.noteAbove);
    const bare = page.entry.sketch === null;   // no drawing: the page is text alone, with no room kept for one
    this.left.hidden = bare;
    this.spread.dataset["bare"] = String(bare);
    this.sketch.replaceChildren(...(page.entry.sketch === null ? [] : [this.image(page.entry.sketch, "journal-sketch")]));
    this.notes.replaceChildren();
    this.drawn = { ...this.drawn, entry: page.entry.entry, notes: 0 };
    this.appendNotes(page);
  }

  /** Notes only append: one written while the page is open joins it, and no earlier note moves. */
  private appendNotes(page: Page): void {
    const { entry } = page;
    const looks = layoutOf(entry.entry, entry.notes.length).notes;
    for (let i = this.drawn.notes; i < page.notes.length; i++) {
      const info = page.notes[i]!;
      const look = looks[entry.notes.findIndex((n) => n.note === info.note)]!;
      const node = el("div", `journal-note hand-${info.hand}`);
      node.append(el("p", "journal-words", this.ctx.catalog.text.get(info.note)));
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
    const rows = this.view ? numbersOf(this.ctx.catalog, this.view, page.entry) : [];
    const key = JSON.stringify([page.entry.entry, rows]);
    this.numbers.hidden = rows.length === 0;
    if (key === this.drawn.numbers) return;
    this.drawn.numbers = key;
    this.numbers.replaceChildren(...rows.map(rowNode));
  }

  /** Turned from, or the Book closed (its Close, the backdrop, Escape, another tab): one write of what was read, then
   * the dots are redrawn. */
  turnedFrom(): void {
    if (!this.isOpen) return;
    this.isOpen = false;
    this.ctx.keeps.keepJournalRead(this.turned);
    this.turned.clear();
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
