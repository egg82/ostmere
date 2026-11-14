// The Book's Done page (ui/book.ts), offered once something is finished: view.completed, dimmed, each with its cap reached, or marked retired when a newer card replaced it
// (a `retired` unlock); a ruled lane's are left out. Plain panels, not buttons: nothing here can be tapped.
import type { View } from "../api/types";
import { panelView } from "../game/lanes";
import { UI } from "../game/text";
import type { Book } from "./book";
import { el, keyed, setText } from "./dom";
import type { Part, PartContext } from "./part";

export class Completed implements Part {
  readonly id = "done";
  readonly label: string;
  readonly root = el("section", "completed");
  private readonly list = el("div", "card-list");
  private rows = new Map<string, { node: HTMLElement; count: HTMLElement }>();
  private readonly button: HTMLButtonElement;

  constructor(private readonly ctx: PartContext, book: Book) {
    this.label = ctx.catalog.text.get(UI.bookDone);
    this.root.append(this.list);
    this.button = book.page(this);
  }

  update(full: View): void {
    const { catalog } = this.ctx;
    this.button.hidden = full.completed.length === 0;
    const view = panelView(catalog, full);   // a ruled lane's done tasks are never cards here
    this.rows = keyed(this.list, view.completed, (c) => c.card, this.rows, (c) => {
      const node = el("div", "card done");
      node.dataset.lane = catalog.laneOf(c.card);
      const count = el("span", "card-count");
      const head = el("span", "card-head");
      head.append(el("span", "card-title", catalog.cardLabel(c.card)), count);
      node.append(head);
      return { node, count };
    });
    for (const c of view.completed) {
      const row = this.rows.get(c.card);
      if (!row) continue;
      const retired = catalog.retired(view, c.card);
      row.node.classList.toggle("retired", retired);
      setText(row.count, retired ? catalog.text.get(UI.retired) : catalog.format.completions(c.completions, c.completions));
    }
  }

  tick(): void {}
}
