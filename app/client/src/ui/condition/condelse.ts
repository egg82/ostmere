// The full editor's "Or else" (docs/design/rule-guards.md, "How the page words it"; behind More options): the rule's
// fallbacks as words, each with a remove, and an add that picks what to do instead. Only what the first action's lane
// or layer allows is offered (game/condition/elsechoices.ts), up to Content.limits.max_or_else, none twice.
import type { OrderVerb, View } from "../../api/types";
import { choiceVerb, elseChoices, keepElse } from "../../game/condition/elsechoices";
import { actionWords } from "../../game/rules/orders";
import { UI } from "../../game/page/text";
import { choiceButtons } from "./condrows";
import { bringIntoView, el, tapFeedback } from "../dom";
import type { PartContext } from "../part";

function button(cls: string, label: string, click: () => void): HTMLButtonElement {
  const b = el("button", cls, label);
  b.type = "button";
  b.addEventListener("click", () => { tapFeedback(); click(); });
  return b;
}

export class ElseEditor {
  readonly root = el("div", "cond-else");
  private adding = false;

  constructor(private readonly ctx: PartContext, private readonly change: (orElse: OrderVerb[]) => void) {}

  /** The fallbacks as they stand after `then`, drawn while `show` (the full editor is open) and `then` is chosen. Ones
   * `then` no longer allows (another lane or layer, or itself) are dropped through `change`. */
  draw(view: View, then: OrderVerb | null, orElse: OrderVerb[], show: boolean): void {
    const { catalog } = this.ctx;
    const kept = keepElse(catalog, view, then, orElse);
    if (kept.length !== orElse.length) { this.change(kept); return; }
    const { text } = catalog;
    const offer = elseChoices(catalog, view, then, orElse);
    const room = orElse.length < catalog.content.limits.max_or_else && offer.length > 0;
    this.root.hidden = !show || then === null || (orElse.length === 0 && offer.length === 0);
    const head = el("div", "cond-else-head");
    head.append(el("span", "rules-label", text.get(UI.ruleElseLabel)), el("span", "cond-else-hint", text.get(UI.ruleElseHint)));
    const held = orElse.map((v, i) => {
      const row = el("div", "cond-else-row");
      const words = actionWords(catalog, view, v);
      const drop = button("quiet cond-else-drop", text.get(UI.orderRemove), () => { this.adding = false; this.change(orElse.filter((_, j) => j !== i)); });
      drop.setAttribute("aria-label", `${text.get(UI.orderRemove)} ${words}`);
      row.append(el("span", "cond-else-words", words), drop);
      return row;
    });
    const add = button("quiet cond-else-add", text.get(UI.ruleElseAdd), () => { this.adding = !this.adding; this.draw(view, then, orElse, show); this.reveal(); });
    add.hidden = !room;
    add.setAttribute("aria-expanded", String(this.adding && room));
    const pick = el("div", "cond-else-pick");
    if (this.adding && room) {
      pick.append(...choiceButtons(catalog, view, offer, () => "quiet cond-else-choice", (c) => { tapFeedback(); this.add(choiceVerb(c), orElse); }));
    }
    this.root.replaceChildren(head, ...held, add, ...(this.adding && room ? [pick] : []));
  }

  private add(verb: OrderVerb, orElse: OrderVerb[]): void {
    this.adding = false;
    this.change([...orElse, verb]);
  }

  private reveal(): void {
    const pick = this.root.querySelector<HTMLElement>(".cond-else-pick");
    if (pick) bringIntoView(document, pick);
  }
}
