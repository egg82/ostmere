// The condition editor's foot (condition.ts), pinned under the choices: the watched store now (condstore.ts), the rule as
// it reads, the note when the same rule already exists, the dry run's line, then Remove, Copy rule and Save.
import type { Order, OrderVerb, View } from "../../api/types";
import { UI } from "../../game/text";
import { DryNote } from "./conddry";
import { watchedWords } from "./condstore";
import { footRow } from "./condrows";
import { el, setText } from "../dom";
import type { PartContext } from "../part";

export class CondFoot {
  readonly root = el("div", "cond-foot");
  readonly sentence = el("p", "rule-sentence cond-sentence");
  private readonly watched = el("p", "cond-watched");
  private readonly note = el("p", "editor-note cond-note");
  private readonly dry: DryNote;
  private readonly remove = el("button", "quiet danger");
  private readonly copy = el("button", "quiet cond-copy");
  private readonly save = el("button", "primary");
  /** What the quick add's parts in the sentence show now (condquick.quickParts); "" while the sentence is words. */
  private quickKey = "";

  constructor(private readonly ctx: PartContext, drop: () => void, commit: () => void, copy: () => void) {
    const { text } = ctx.catalog;
    this.dry = new DryNote(ctx);
    for (const [b, key] of [[this.remove, UI.orderRemove], [this.copy, UI.ruleCopy], [this.save, UI.save]] as const) {
      b.type = "button";
      setText(b, text.get(key));
    }
    this.remove.addEventListener("click", drop);
    this.save.addEventListener("click", commit);
    this.copy.addEventListener("click", copy);
    const actions = el("div", "sheet-actions cond-actions");
    actions.append(this.remove, this.copy, this.save);
    this.root.append(this.watched, this.sentence, this.note, this.dry.root, actions);
  }

  /** A new rule (`index` null) is added; a rule being changed is saved, can be removed, and can be copied when
   * `copyable` (not a chip's), while the rules have room (`full`: they do not). */
  start(index: number | null, copyable: boolean, full: boolean): void {
    this.save.textContent = this.ctx.catalog.text.get(index === null ? UI.orderAdd : UI.save);
    this.remove.hidden = index === null;
    this.copy.hidden = index === null || !copyable;
    this.copy.disabled = full;
  }

  /** The note and Save for `order` as Save would set it, and the sentence: the quick add's parts when given (rebuilt
   * only when their key changes, so an open picker stays open), else the rule's words (footRow); over it, `store` as it
   * stands (null: none to state). */
  draw(view: View, index: number | null, then: OrderVerb | null, order: Order | null, quick: { key: string; parts: () => HTMLElement[] } | null, store: string | null = null): void {
    setText(this.watched, watchedWords(this.ctx.catalog, view, store));
    this.watched.hidden = this.watched.textContent === "";
    footRow(this.ctx.catalog, view, index, then, order, { sentence: quick ? null : this.sentence, note: this.note, save: this.save });
    if (quick && quick.key !== this.quickKey) this.sentence.replaceChildren(...quick.parts());
    this.quickKey = quick?.key ?? "";
  }

  /** The dry run's line for `order` (conddry.ts). */
  showDry(view: View | null, index: number | null, order: Order | null): void {
    void this.dry.show(view, index, order);
  }
}
