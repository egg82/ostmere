// The answer rule's builder in the Rules tab's answers section (CONTRACT.txt, "Offers"): for each offer kind with an
// offer answered, a row with that offer's question, the answer it was given, and one button per role for the offers of
// the kind still to come, worded by the answer that offer gave under it. A tap sets the kind's rule to that role (the pressed button is the rule's role; Remove is on the rule's own row).
import type { View } from "../api/types";
import { answeredKinds, givenLabelKey, kindRuleAt, kindText, roleChoices } from "../game/kindrule";
import { setKindRule } from "../game/lanes";
import { UI } from "../game/text";
import { el, tapFeedback } from "./dom";
import type { PartContext } from "./part";

/** The builder rows, in content order of the kinds; none until an offer of a kind has been answered. */
export function kindRows(ctx: PartContext, view: View): HTMLElement[] {
  const { catalog } = ctx;
  return answeredKinds(catalog, view).map((kind) => {
    const row = el("div", "rules-row kind-rule");
    row.dataset.kind = kind;
    const at = kindRuleAt(view, kind);
    const set = at < 0 ? null : view.orders[at]!.then;
    const given = catalog.text.fill(UI.ruleAnswered, { answer: catalog.label(givenLabelKey(catalog, view, kind)) });
    row.append(el("p", "kind-asked", kindText(catalog, view, kind)), el("p", "kind-answered", given),
      el("p", "kind-lead", catalog.text.get(UI.ruleAnswerNext)));
    for (const c of roleChoices(catalog, view, kind)) {
      const b = el("button", "cond-task", catalog.label(c.label_key));
      b.type = "button";
      b.dataset.role = c.role;
      b.setAttribute("aria-pressed", String(set?.kind === "answer_kind" && set.role === c.role));
      b.addEventListener("click", () => { tapFeedback(); ctx.actions.decide(setKindRule(view, kind, c.role)); });
      row.append(b);
    }
    return row;
  });
}
