// The Book (docs/design/redesign.md, "Book"): one place holding the Chronicle, the Journal and Done, each a page, with
// one way between them: the row of pages beside its title. The Map joins as the last page once it exists. Where it opens
// is the frame's (ui/partseat.ts seats it): a view in the middle and the right on a desktop or a landscape phone, like
// Town, and a sheet from the bottom on a phone. It opens on the chronicle; a page whose button is hidden is not offered,
// and the row shows only while more than one page is.
import type { Catalog } from "../game/catalog";
import { UI } from "../game/text";
import { el } from "./dom";

/** A page of the Book. */
export interface BookPage {
  /** Its button's `data-page`: what a lesson points at. */
  readonly id: string;
  readonly label: string;
  readonly root: HTMLElement;
  /** Controls for the actions row while the page is open, after Close. */
  readonly actions?: readonly HTMLElement[];
  /** A class the sheet takes while the page is open (the journal's full-height page). */
  readonly frame?: string;
  /** The page is shown: the Book opened on it, or it was turned to. */
  turnedTo?(): void;
  /** The page is no longer shown: turned from, or the Book closed. */
  turnedFrom?(): void;
  key?(e: KeyboardEvent): void;
}

export class Book {
  /** Its tab (ui/tabs.ts): a sheet on a phone, a view elsewhere. */
  readonly tab = el("button", "tab");
  readonly sheet = el("dialog", "sheet book-sheet");
  /** The view's panel, among the card area's (ui/screen.ts). */
  readonly view = el("section", "book-tab");
  private readonly body = el("div", "book");
  private readonly row = el("div", "book-pages");
  private readonly actions = el("div", "sheet-actions");
  private readonly close = el("button", "quiet");
  private readonly pages: Array<{ page: BookPage; button: HTMLButtonElement }> = [];
  private open: BookPage | null = null;
  private asView = false;

  /** `left`: the view was left by the Book itself (a link out of it): the screen shows Tasks. */
  constructor(catalog: Catalog, first: BookPage, private readonly left: () => void = () => undefined) {
    this.tab.type = "button";
    this.tab.textContent = catalog.text.get(UI.tabBook);
    this.tab.dataset.tab = "book";
    this.close.type = "button";
    this.close.textContent = catalog.text.get(UI.close);
    this.close.autofocus = true;   // the sheet opens on Close, not on a page
    this.close.addEventListener("click", () => this.shut());
    this.actions.append(this.close);
    this.row.setAttribute("role", "group");
    const head = el("div", "book-head");
    head.append(el("h2", "view-title", catalog.text.get(UI.tabBook)), this.row);
    this.body.append(head, this.actions);
    this.page(first);
    this.sheet.append(this.body);
    this.sheet.addEventListener("click", (e) => { if (e.target === this.sheet) this.shut(); });
    this.sheet.addEventListener("close", () => this.turnTo(null));
    this.body.addEventListener("keydown", (e) => this.open?.key?.(e));
  }

  /** A page joins the row after the others; its button, which the caller hides while the page has nothing. */
  page(page: BookPage): HTMLButtonElement {
    const button = el("button", "book-page", page.label);
    button.type = "button";
    button.dataset.page = page.id;
    button.addEventListener("click", () => this.turnTo(page));
    page.root.hidden = true;
    for (const n of page.actions ?? []) n.hidden = true;
    this.pages.push({ page, button });
    this.row.append(button);
    this.actions.before(page.root);
    this.actions.append(...(page.actions ?? []));
    return button;
  }

  /** Whether it opens as a view (a desktop, a landscape phone) rather than a sheet. */
  get inView(): boolean {
    return this.asView;
  }

  /** Whether a page of it is on screen. */
  get shown(): boolean {
    return this.open !== null;
  }

  /** Opened from its tab, on the chronicle: as the sheet on a phone; the view's panel is the screen's to show. */
  opened(): void {
    this.turnTo(this.pages[0]!.page);
    if (!this.asView && !this.sheet.open) this.sheet.showModal();
  }

  /** The view was left for another tab. */
  closed(): void {
    if (this.asView) this.turnTo(null);
  }

  /** Out of the Book by one of its own links: the sheet closes, the view gives way to Tasks. */
  leave(): void {
    if (this.asView) this.left();
    else this.shut();
  }

  /** The sheet closed by its Close or the backdrop (Escape closes it without either: its close event). */
  private shut(): void {
    this.sheet.close();
    this.turnTo(null);
  }

  /** Where it opens: the view (true) or the sheet. Moving while open closes it there. */
  seat(asView: boolean): void {
    if (this.shown) this.leave();
    this.asView = asView;
    this.close.hidden = asView;
    (asView ? this.view : this.sheet).append(this.body);
  }

  /** Page `page` shown (null: none, the Book is closed), the others hidden. */
  private turnTo(page: BookPage | null): void {
    const was = this.open;
    if (was !== page) was?.turnedFrom?.();
    this.open = page;
    for (const p of this.pages) {
      const on = p.page === page;
      p.page.root.hidden = !on;
      for (const n of p.page.actions ?? []) n.hidden = !on;
      p.button.setAttribute("aria-pressed", String(on));
      if (p.page.frame) this.sheet.classList.toggle(p.page.frame, on);
    }
    if (page && was !== page) page.turnedTo?.();
  }
}
