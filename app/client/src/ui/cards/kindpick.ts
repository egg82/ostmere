// The kind picker on a card that stands for several kinds (game/variants.ts): the other kinds' rows are hidden, and the
// shown one carries a row of buttons, one per kind in view, the shown kind pressed and a kind at work marked. A kind not
// yet in front of the player carries the quiet dot on its button. Which kind is picked is kept per device.
import type { View } from "../../api/types";
import { kindLabel, kindsByLead, shownKind, variantOf } from "../../game/variants";
import { el, tapFeedback } from "../dom";
import { markNew } from "../feedback/fresh";
import type { PartContext } from "../part";

/** What the picker needs of a card's row. */
export interface KindRow {
  node: HTMLElement;
}

/** Marks a kind not yet in front of the player: has it, and clears it. */
export interface KindMarks {
  has(card: string): boolean;
  clear(card: string): void;
}

const KEY = "ostmere.kind.";

function kept(lead: string): string | null {
  try {
    return localStorage.getItem(KEY + lead);
  } catch {
    return null;
  }
}

function keep(lead: string, card: string): void {
  try {
    localStorage.setItem(KEY + lead, card);
  } catch {
    // a convenience: without storage the pick lasts the page
  }
}

export class KindPicks {
  private readonly picked = new Map<string, string>();
  private readonly pickers = new Map<string, HTMLElement>();

  /** `changed`: a pick was made, so the rows are applied again. */
  constructor(private readonly ctx: PartContext, private readonly marks: KindMarks, private readonly changed: () => void) {}

  /** A kind that just arrived is the one shown, so it is in front of the player with its dot. */
  arrived(card: string): void {
    const lead = variantOf(this.ctx.catalog, card);
    if (lead !== null) this.picked.set(lead, card);
  }

  /** Every kind but each lead's shown one hidden, the picker seated at the top of the shown one. */
  apply(rows: ReadonlyMap<string, KindRow>, view: View): void {
    const { catalog } = this.ctx;
    const leads = kindsByLead(catalog, view.cards);
    for (const [id, row] of rows) {
      const lead = variantOf(catalog, id);
      if (lead === null || !leads.has(lead)) row.node.hidden = false;
    }
    for (const [lead, kinds] of leads) {
      const shown = shownKind(view, kinds, this.picked.get(lead) ?? kept(lead));
      for (const k of kinds) {
        const row = rows.get(k.card);
        if (row) row.node.hidden = k.card !== shown;
      }
      const row = shown === null ? undefined : rows.get(shown);
      if (row && shown !== null) row.node.prepend(this.draw(lead, kinds.map((k) => k.card), shown, view));
    }
    for (const [lead, node] of this.pickers) if (!leads.has(lead)) node.remove();
  }

  private draw(lead: string, kinds: string[], shown: string, view: View): HTMLElement {
    const { catalog } = this.ctx;
    let node = this.pickers.get(lead);
    if (!node) {
      node = el("div", "variant-pick");
      node.setAttribute("role", "group");
      this.pickers.set(lead, node);
    }
    const running = new Set(view.lanes.flatMap((l) => (l.running_card ? [l.running_card] : [])));
    const mixed = new Set(view.cards.filter((c) => c.by !== null).map((c) => c.card));
    node.replaceChildren(...kinds.map((card) => {
      const b = el("button", "variant-option", kindLabel(catalog, card));
      b.type = "button";
      b.dataset.card = card;
      b.setAttribute("aria-pressed", String(card === shown));
      b.classList.toggle("at-work", running.has(card) || mixed.has(card));
      b.addEventListener("click", () => {
        tapFeedback();
        this.picked.set(lead, card);
        keep(lead, card);
        this.changed();
      });
      if (card !== shown && this.marks.has(card)) markNew(b, () => this.marks.clear(card));
      return b;
    }));
    return node;
  }
}
