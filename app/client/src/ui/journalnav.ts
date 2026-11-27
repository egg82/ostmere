// The Journal's controls for finding a page (docs/design/opening-screen/journal.md, "The journal"): Prev and Next, which stay in
// a section and name the section they cross into, the page's place in its section, and the contents button with the
// list of a section's pages that it swaps for the spread. Held here so the sheet (ui/journal.ts) only says which page.
import { bookmarksOf, contentsOf, placeOf, SECTIONS, turnOf, type Page, type Reading, type Section } from "../game/journal";
import type { Catalog } from "../game/catalog";
import { UI } from "../game/text";
import { el, tapFeedback } from "./dom";

/** What the sheet does when a control is used. */
export interface NavHandlers {
  turn(by: -1 | 1): void;
  toggle(): void;
  pick(index: number): void;
  mark(section: Section): void;
}

export class JournalNav {
  readonly prev = el("button", "quiet");
  readonly next = el("button", "quiet");
  readonly place = el("span", "journal-place");
  /** One bookmark for each section that has a page written, in the book's order. */
  readonly marks = el("nav", "tabs journal-bookmarks");
  readonly button = el("button", "quiet");
  /** The actions row's controls after Close. */
  readonly actions: readonly HTMLElement[] = [this.button, this.prev, this.place, this.next];
  /** The list of a section's pages, shown in place of the spread while `listed` names the section. */
  readonly list = el("nav", "journal-contents");
  listed: Section | null = null;
  private key = "";
  private sections = "";

  constructor(private readonly catalog: Catalog, private readonly on: NavHandlers) {
    for (const [b, by] of [[this.prev, -1], [this.next, 1]] as const) {
      b.type = "button";
      b.addEventListener("click", () => { tapFeedback(); this.on.turn(by); });
    }
    this.button.type = "button";
    this.button.textContent = catalog.text.get(UI.journalContents);
    this.button.addEventListener("click", () => { tapFeedback(); this.on.toggle(); });
    this.place.setAttribute("aria-hidden", "true");
    this.marks.setAttribute("aria-label", catalog.text.get(UI.journalHeading));
    this.list.setAttribute("aria-label", catalog.text.get(UI.journalContents));
    this.list.hidden = true;
    this.list.addEventListener("click", (e) => {
      const row = (e.target as HTMLElement).closest<HTMLElement>("[data-index]");
      if (row) { tapFeedback(); this.on.pick(Number(row.dataset["index"])); }
    });
  }

  /** Lists `section`, or the page again for null; the next draw rebuilds the list and scrolls to the open page. */
  show(section: Section | null): void {
    this.listed = section;
    this.key = "";
  }

  /** Prev and Next say where they go once it is another section, and are off at the book's ends; the place reads "3 / 9"
   * in the section. */
  drawTurns(pages: Page[], at: number): void {
    const { text } = this.catalog;
    for (const [b, by, key] of [[this.prev, -1, UI.journalPrev], [this.next, 1, UI.journalNext]] as const) {
      const turn = turnOf(pages, at, by);
      const into = turn?.crossing ? SECTIONS.find((s) => s.section === turn.crossing)?.key : undefined;
      const word = text.get(into ?? key);
      b.disabled = turn === null;
      b.textContent = by < 0 ? `‹ ${word}` : `${word} ›`;
    }
    const { n, of } = placeOf(pages, at);
    this.place.textContent = `${n} / ${of}`;
  }

  /** The list while a section is listed: rows that are buttons, the open page's marked, the unread ones dotted. */
  drawList(pages: Page[], at: number, read: Reading): void {
    const open = this.listed;
    this.list.hidden = open === null;
    this.button.setAttribute("aria-pressed", String(open !== null));
    this.place.hidden = open !== null;
    if (open === null) return;
    const rows = contentsOf(this.catalog, pages, open, read, at);
    const key = JSON.stringify([open, rows]);
    if (key === this.key) return;
    this.key = key;
    this.list.replaceChildren(...rows.map((r, n) => {
      const b = el("button", "journal-entry", "");
      b.type = "button";
      b.dataset["index"] = String(r.index);
      b.classList.toggle("on", r.current);
      if (r.current) b.setAttribute("aria-current", "page");
      b.append(el("span", "journal-entry-n", String(n + 1)), el("span", "journal-entry-title", r.title));
      if (r.unread) b.append(el("i", "new-dot"));
      return b;
    }));
    const here = this.list.querySelector<HTMLElement>(".on");
    if (here) here.scrollIntoView({ block: "center" });
    else this.list.scrollTop = 0;
  }

  /** The bookmarks of the sections written, `shown` marked as the current one and scrolled to when the row overflows. */
  drawMarks(pages: Page[], shown: Section): void {
    const sections = bookmarksOf(pages);
    const key = sections.map((m) => m.section).join();
    if (key !== this.sections) {
      this.sections = key;
      this.marks.replaceChildren(...sections.map((m) => this.bookmark(m.section, m.key)));
    }
    for (const b of Array.from(this.marks.children) as HTMLElement[]) {
      const on = b.dataset["section"] === shown;
      b.classList.toggle("on", on);
      if (on) { b.setAttribute("aria-current", "true"); this.marks.scrollLeft = Math.max(0, b.offsetLeft - (this.marks.clientWidth - b.offsetWidth) / 2); }
      else b.removeAttribute("aria-current");
    }
  }

  private bookmark(section: Section, key: string): HTMLButtonElement {
    const b = el("button", "tab", this.catalog.text.get(key));
    b.type = "button";
    b.dataset["section"] = section;
    b.addEventListener("click", () => { tapFeedback(); this.on.mark(section); });
    return b;
  }
}
