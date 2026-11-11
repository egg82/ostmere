// The full Log, newest last, in a sheet over the page (docs/design/opening-screen.md, "The story strip"): a sticky
// heading, then one stretch per visit (game/loggroups.ts), the newest open and the older folded to a line of counts.
// An open stretch reads as the story, full size; the other kinds of line are small under the story line they follow,
// behind the stretch's counts.
import { agoWords } from "../game/ago";
import type { Catalog } from "../game/catalog";
import type { Keeps } from "../game/keeps";
import { isStory, stretches, tally, type LogEntry, type Stretch } from "../game/loggroups";
import { awayTitle, kindCount } from "../game/logwords";
import { UI } from "../game/text";
import { el } from "./dom";

const KEEP = 200;
const START = -1;

export class LogSheet {
  readonly root = el("dialog", "sheet log-sheet");
  private readonly list = el("ol", "log-all");
  private readonly entries: LogEntry[] = [];
  /** The latest game second the page has seen: the stretch's "now". */
  private now = 0;
  /** Stretches the player opened or folded by hand, by id: a stretch drawn again keeps its state. */
  private readonly handled = new Map<number, boolean>();
  /** Stretches whose small lines the player opened, by id. */
  private readonly shown = new Set<number>();

  constructor(private readonly catalog: Catalog, private readonly keeps: Keeps) {
    const close = el("button", "quiet", catalog.text.get(UI.close));
    close.type = "button";
    close.autofocus = true;   // the sheet opens on Close, not on the first stretch's title
    close.addEventListener("click", () => this.root.close());
    const row = el("div", "sheet-actions");
    row.append(close);
    this.root.append(el("h2", "panel-heading", catalog.text.get(UI.log)), this.list, row);
    this.root.addEventListener("click", (e) => { if (e.target === this.root) this.root.close(); });
  }

  show(): void {
    this.draw();
    this.root.showModal();
    this.list.scrollTop = this.list.scrollHeight;
  }

  /** A line joins the Log; while the Log is open the view follows only if it was at the bottom. */
  add(entry: LogEntry): void {
    this.now = Math.max(this.now, entry.at);
    this.entries.push(entry);
    if (this.entries.length > KEEP) this.entries.shift();
    if (!this.root.open) return;
    const { scrollTop, clientHeight, scrollHeight } = this.list;
    const atBottom = scrollHeight - scrollTop - clientHeight <= 4;
    this.draw();
    if (atBottom) this.list.scrollTop = this.list.scrollHeight;
  }

  /** The page's latest game second, so a stretch's "ago" reads against it. */
  seen(at: number): void {
    this.now = Math.max(this.now, at);
  }

  private draw(): void {
    for (const d of this.list.querySelectorAll<HTMLDetailsElement>("details")) this.handled.set(Number(d.dataset["id"]), d.open);
    const all = stretches(this.entries, this.keeps.visits());
    this.list.replaceChildren(...all.map((s, i) => this.stretch(s, i === all.length - 1)));
  }

  private stretch(s: Stretch, newest: boolean): HTMLElement {
    const { text } = this.catalog;
    const id = s.visit?.left ?? START;
    const item = el("li", newest ? "log-visit newest" : "log-visit");
    const box = el("details");
    box.dataset["id"] = String(id);
    box.open = this.handled.get(id) ?? newest;
    const title = s.visit ? awayTitle(text, s.visit.back - s.visit.left) : text.get(newest ? UI.logNow : UI.logEarlier);
    const ago = s.visit ? agoWords(text, s.visit.back * 1000, this.now * 1000) : "";
    const kinds = tally(s.lines);
    const counts = kinds.filter(([kind]) => !isStory(kind)).map(([kind, n]) => kindCount(text, kind, n));
    const head = el("summary");
    head.append(el("span", "v-title", title), el("span", "v-ago", ago), el("span", "v-sum", kinds.map(([kind, n]) => kindCount(text, kind, n)).join(" · ")));
    box.append(head, this.body(id, s.lines, counts));
    item.append(box);
    return item;
  }

  private body(id: number, lines: LogEntry[], counts: string[]): HTMLElement {
    const body = el("div", "v-body");
    const small = lines.map((l) => (isStory(l.kind) ? el("p", "log-story", l.text) : el("p", `log-small ${l.kind}`, l.text)));
    const reveal = (open: boolean): void => { for (const p of small) if (p.classList.contains("log-small")) p.hidden = !open; };
    reveal(this.shown.has(id));
    body.append(...small);
    if (counts.length === 0) return body;
    const tallyRow = el("button", "log-tally");
    tallyRow.type = "button";
    tallyRow.setAttribute("aria-expanded", String(this.shown.has(id)));
    tallyRow.append(...counts.map((c) => el("span", "log-chip", c)));
    tallyRow.addEventListener("click", () => {
      const open = tallyRow.getAttribute("aria-expanded") !== "true";
      if (open) this.shown.add(id); else this.shown.delete(id);
      tallyRow.setAttribute("aria-expanded", String(open));
      reveal(open);
    });
    const foot = el("div", "log-foot");
    foot.append(tallyRow);
    body.append(foot);
    return body;
  }
}
