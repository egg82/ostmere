// The mix editor's Add control (editor.ts): one "+ Add" that folds the cards that can join, so the editor does not grow
// with every unlocked card. A tap opens the list in place and a second tap closes it; a pick leaves it open, so several
// cards can join in a row. A lesson step pointing at a chip inside opens it (the "unfold" event, ui/lessons.ts).
import type { View, Mix } from "../api/types";
import type { Catalog } from "../game/catalog";
import type { NewMarks } from "../game/marks";
import { holdsCard } from "../game/mix";
import { UI } from "../game/text";
import { acted, el, setText } from "./dom";
import { dragIn } from "./editordrag";
import { markNew } from "./fresh";

export class AddFold {
  readonly root = el("div", "editor-adds");
  private readonly fold = el("button", "quiet add-fold", "");
  private readonly list = el("div", "add-list");
  private open = false;
  private waiting = false;
  private key = "";

  constructor(
    private readonly catalog: Catalog, private readonly marks: NewMarks,
    private readonly bar: () => HTMLElement, private readonly join: (card: string) => void,
  ) {
    this.fold.type = "button";
    setText(this.fold, catalog.text.get(UI.add));
    this.fold.addEventListener("click", () => this.setOpen(!this.open));
    this.root.addEventListener("unfold", () => this.setOpen(true));
    this.root.append(this.fold, this.list);
    this.reset();
  }

  /** Closed, and the chips drawn afresh at the next `draw`. */
  reset(): void {
    this.key = "-";
    this.setOpen(false);
  }

  /** The cards that can join: on the hands, in play, not in the edit yet; tapped, or dragged onto the bar. */
  draw(view: View, mix: Mix): void {
    const { catalog } = this;
    const free = view.cards.filter((c) => catalog.mixable(c.card) && !holdsCard(mix, c.card));
    const key = free.map((c) => (this.marks.has(c.card) ? `${c.card}*` : c.card)).join("|");
    if (key === this.key) return;   // kept across views, so a card being dragged in stays under the finger
    this.key = key;
    const cards = free.map((c) => {
      const b = el("button", `add-card hue-${catalog.rank(c.card) % 6}`, catalog.cardLabel(c.card));
      b.type = "button"; b.dataset.card = c.card;   // a lesson's step names the card it points at
      if (this.marks.has(c.card)) markNew(b, () => this.marks.clear(c.card));
      const join = (): void => { acted(b); this.join(c.card); };   // told first: joining redraws the row, and no click follows
      b.addEventListener("pointerdown", (e) => dragIn(e, b, this.bar(), join));
      b.addEventListener("click", (e) => { if (e.detail === 0) join(); });   // keyboard
      return b;
    });
    this.list.replaceChildren(...cards);
    this.root.hidden = free.length === 0;
    this.waiting = free.some((c) => this.marks.has(c.card));
    this.markFold();
  }

  /** A new card waits in the folded list: its dot shows on "+ Add" until the list opens. */
  private markFold(): void {
    this.fold.querySelector(":scope > .new-dot")?.remove();
    if (!this.waiting || this.open) return;
    const dot = el("i", "new-dot");
    dot.setAttribute("aria-hidden", "true");
    this.fold.append(dot);
  }

  private setOpen(open: boolean): void {
    this.open = open;
    this.list.hidden = !open;
    this.root.classList.toggle("folded", !open);
    this.fold.setAttribute("aria-expanded", String(open));
    this.markFold();
  }
}
