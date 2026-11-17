// A rule's condition on the Rules tab: a button with an edit mark that opens the condition editor (a ruled lane's always
// rule: its words, opening the lane's task editor). Never gated.
import type { View } from "../api/types";
import { alwaysWords, ruledLaneOf } from "../game/lanes";
import { chipOf } from "../game/orders";
import { ruleCondition } from "../game/guardwords";
import { el, tapFeedback } from "./dom";
import type { PartContext } from "./part";

/** What the button opens: a lane's task editor, or rule `index`'s condition editor. */
export interface CondOpens {
  lane(lane: string, index: number): void;
  edit(index: number): void;
}

export function condButton(ctx: PartContext, view: View, index: number, opens: CondOpens): HTMLElement {
  const order = view.orders[index]!;
  const lane = ruledLaneOf(ctx.catalog, order);
  const always = alwaysWords(ctx.catalog, order);
  const b = el("button", "rule-cond");
  b.type = "button";
  if (view.orders_on[index] === true) b.dataset.teach = "rule-on";   // a lesson's mark of a rule at work
  b.classList.toggle("chip-rule", chipOf(ctx.catalog, order.when) !== undefined);
  b.append(el("span", "rule-cond-text", always ?? ruleCondition(ctx.catalog, view, order) ?? ""), el("span", "rule-edit-mark", "✎"));
  b.querySelector(".rule-edit-mark")?.setAttribute("aria-hidden", "true");
  b.addEventListener("click", () => {
    tapFeedback();
    if (always !== null && lane !== null) opens.lane(lane, index);
    else opens.edit(index);
  });
  return b;
}
