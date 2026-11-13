// The chronicle, newest first, in a sheet over the page (docs/design/opening-screen.md, "The chronicle"): a heading, a
// row of filters once more than one kind has an entry (game/chronicle.ts routes each kind to one), then the newest
// return's "Since you left" chapter (ui/chapter.ts) and one stretch per earlier visit, folded to a line of counts (the
// newest open when there is no chapter). Lines run oldest first within each. Each line carries its cause beneath it.
// Under Story, a stretch ends with how many entries it holds of each other filter, and each count opens that filter.
import { agoWords } from "../game/ago";
import type { Visit } from "../api/types";
import type { Catalog } from "../game/catalog";
import { added, filtersOf, held, inStrip, stretches, tally, type Entry, type Filter, type Stretch } from "../game/chronicle";
import { awayTitle, filterCount, filterLabel } from "../game/chronwords";
import type { Keeps } from "../game/keeps";
import { UI } from "../game/text";
import { chapterNode, type ChapterView } from "./chapter";
import { el } from "./dom";

const START = -1;

export class ChronicleSheet {
  readonly root = el("dialog", "sheet chronicle");
  private readonly filters = el("div", "chron-filters");
  private readonly list = el("ol", "chron-all");
  private entries: Entry[] = [];
  /** The filter shown; null: every entry. */
  private filter: Filter | null = "story";
  /** The latest game second the page has seen: the stretch's "now". */
  private now = 0;
  /** Stretches the player opened or folded by hand, by id: a stretch drawn again, under any filter, keeps its state. */
  private readonly handled = new Map<number, boolean>();
  /** How many asks wait now: the chapter's waiting row. */
  private asks = 0;

  /** `showWaiting`: what the chapter's waiting count opens (the asks on the page). */
  constructor(private readonly catalog: Catalog, private readonly keeps: Keeps, private readonly showWaiting: () => void) {
    const close = el("button", "quiet", catalog.text.get(UI.close));
    close.type = "button";
    close.autofocus = true;   // the sheet opens on Close, not on the first filter
    close.addEventListener("click", () => this.root.close());
    const row = el("div", "sheet-actions");
    row.append(close);
    this.filters.setAttribute("role", "group");
    this.root.append(el("h2", "panel-heading", catalog.text.get(UI.chronicle)), this.filters, this.list, row);
    this.root.addEventListener("click", (e) => { if (e.target === this.root) this.root.close(); });
  }

  show(): void {
    this.draw();
    this.root.showModal();
    this.list.scrollTop = 0;
  }

  /** An entry joins the chronicle in its place by time; while it is open the view stays where it was. */
  add(entry: Entry): void {
    this.now = Math.max(this.now, entry.at);
    this.entries = added(this.entries, entry);
    if (!this.root.open) return;
    const { scrollTop } = this.list;
    this.draw();
    this.list.scrollTop = scrollTop;
  }

  /** How many asks wait now; drawn the next time the sheet draws. */
  waiting(n: number): void {
    this.asks = n;
  }

  /** The page's latest game second, so a stretch's "ago" reads against it. */
  seen(at: number): void {
    this.now = Math.max(this.now, at);
  }

  /** The stretches are cut from every entry, so a stretch keeps its title and state whatever the filter; the filter
   * picks their lines, and a stretch with none of them is not drawn. The newest return's stretch is the chapter, drawn
   * under Story and All even with no line; with no return kept, the newest drawn opens unless folded by hand. */
  private draw(): void {
    const offered = filtersOf(this.entries);
    if (this.filter !== null && !offered.includes(this.filter)) this.filter = offered[0] ?? "story";
    this.drawFilters(offered);
    const all = stretches(this.entries, this.keeps.visits());
    const chapter = this.chapter(all);
    const last = chapter ? null : all.at(-1);
    const drawn = all.filter((s) => held(s.lines, this.filter).length > 0).reverse();
    const top = chapter && (this.filter === "story" || this.filter === null || held(chapter.lines, this.filter).length > 0)
      ? [chapterNode(this.catalog, chapter, this.filter, { line: (l) => this.line(l), pick: (f) => this.pick(f), showWaiting: () => this.waitingShown() })] : [];
    this.list.replaceChildren(...top, ...drawn.map((s, i) => this.stretch(s, s === last, top.length === 0 && i === 0)));
  }

  /** The newest return's chapter, its stretch taken out of `all`; null with no return kept. */
  private chapter(all: Stretch[]): ChapterView | null {
    const visit = this.keeps.visits().reduce<Visit | null>((n, v) => (n === null || v.left > n.left ? v : n), null);
    if (visit === null) return null;
    const lines = all.at(-1)?.visit?.left === visit.left ? all.pop()!.lines : [];
    const figures = this.keeps.chapter();
    return { visit, lines, figures: figures?.left === visit.left ? figures : null, waiting: this.asks };
  }

  private waitingShown(): void {
    this.root.close();
    this.showWaiting();
  }

  private drawFilters(offered: Filter[]): void {
    this.filters.hidden = offered.length < 2;
    const choices: Array<Filter | null> = [...offered, null];
    this.filters.replaceChildren(...choices.map((f) => {
      const b = el("button", "chron-filter", filterLabel(this.catalog.text, f ?? "all"));
      b.type = "button";
      b.dataset["filter"] = f ?? "all";
      b.setAttribute("aria-pressed", String(f === this.filter));
      b.addEventListener("click", () => this.pick(f));
      return b;
    }));
  }

  private pick(filter: Filter | null): void {
    this.filter = filter;
    this.draw();
    this.list.scrollTop = 0;
  }

  /** `newest`: the chronicle's last stretch (its title is "Now" when no return opened it). `open`: drawn open unless
   * the player folded it. */
  private stretch(s: Stretch, newest: boolean, open: boolean): HTMLElement {
    const { text } = this.catalog;
    const id = s.visit?.left ?? START;
    const item = el("li", newest ? "chron-stretch newest" : "chron-stretch");
    const box = el("details");
    box.dataset["id"] = String(id);
    box.open = this.handled.get(id) ?? open;
    const title = s.visit ? awayTitle(text, s.visit.back - s.visit.left) : text.get(newest ? UI.chronNow : UI.chronEarlier);
    const ago = s.visit ? agoWords(text, s.visit.back * 1000, this.now * 1000) : "";
    const head = el("summary");
    head.append(el("span", "v-title", title), el("span", "v-ago", ago),
      el("span", "v-sum", tally(s.lines).map(([f, n]) => filterCount(text, f, n)).join(" · ")));
    head.addEventListener("click", () => this.handled.set(id, !box.open));   // the click toggles it after this
    box.append(head, this.body(s.lines));
    item.append(box);
    return item;
  }

  private body(lines: Entry[]): HTMLElement {
    const body = el("div", "v-body");
    body.append(...held(lines, this.filter).map((l) => this.line(l)));
    if (this.filter !== "story") return body;
    const others = tally(lines).filter(([f]) => f !== "story");
    if (others.length === 0) return body;
    const foot = el("div", "chron-foot");
    foot.append(...others.map(([f, n]) => {
      const b = el("button", "chron-count", filterCount(this.catalog.text, f, n));
      b.type = "button";
      b.dataset["filter"] = f;
      b.addEventListener("click", () => this.pick(f));
      return b;
    }));
    body.append(foot);
    return body;
  }

  private line(l: Entry): HTMLElement {
    const row = el("div", inStrip(l.kind) ? "chron-line story" : "chron-line");
    row.dataset["kind"] = l.kind;
    row.append(el("p", "chron-text", l.text));
    if (l.cause) row.append(el("p", "chron-cause", l.cause));
    return row;
  }
}
