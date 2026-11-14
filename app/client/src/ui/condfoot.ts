// The condition editor's foot (condition.ts), pinned under the choices: the rule as it reads, the note when the same
// rule already exists, the dry run's line, then Remove and Save.
import type { Order, OrderVerb, View } from "../api/types";
import { UI } from "../game/text";
import { DryNote } from "./conddry";
import { footRow } from "./condrows";
import { el, setText } from "./dom";
import type { PartContext } from "./part";

export class CondFoot {
  readonly root = el("div", "cond-foot");
  readonly sentence = el("p", "rule-sentence cond-sentence");
  private readonly note = el("p", "editor-note cond-note");
  private readonly dry: DryNote;
  private readonly remove = el("button", "quiet danger");
  private readonly save = el("button", "primary");

  constructor(private readonly ctx: PartContext, drop: () => void, commit: () => void) {
    const { text } = ctx.catalog;
    this.dry = new DryNote(ctx);
    for (const [b, key] of [[this.remove, UI.orderRemove], [this.save, UI.save]] as const) {
      b.type = "button";
      setText(b, text.get(key));
    }
    this.remove.addEventListener("click", drop);
    this.save.addEventListener("click", commit);
    const actions = el("div", "sheet-actions cond-actions");
    actions.append(this.remove, this.save);
    this.root.append(this.sentence, this.note, this.dry.root, actions);
  }

  /** A new rule (`index` null) is added; a rule being changed is saved, and can be removed. */
  start(index: number | null): void {
    this.save.textContent = this.ctx.catalog.text.get(index === null ? UI.orderAdd : UI.save);
    this.remove.hidden = index === null;
  }

  /** The sentence, the note and Save for `order` as Save would set it (footRow). */
  draw(view: View, index: number | null, then: OrderVerb | null, order: Order | null): void {
    footRow(this.ctx.catalog, view, index, then, order, { sentence: this.sentence, note: this.note, save: this.save });
  }

  /** The dry run's line for `order` (conddry.ts). */
  showDry(view: View | null, index: number | null, order: Order | null, town: boolean): void {
    void this.dry.show(view, index, order, town);
  }
}
