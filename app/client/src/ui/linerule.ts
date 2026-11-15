// A ledger row a rule watches (ui/ledger.ts; docs/design/opening-screen.md, "Ledger and rules"): the quiet mark, a
// small button to that rule in the Rules tab (the whole row taps through to it).
import type { View } from "../api/types";
import type { Catalog } from "../game/catalog";
import { ruleWords } from "../game/orders";
import { el, tapFeedback } from "./dom";

/** The mark, hidden until a rule is set on it (setRuleMark); the row `box` taps through to rule `rule()` (none while
 * -1) by `open`, and Edit mix keeps its own tap. */
export function ruleMark(box: HTMLElement, rule: () => number, open: (index: number) => void): HTMLButtonElement {
  const mark = el("button", "line-rule");
  mark.type = "button";
  mark.hidden = true;
  box.addEventListener("click", (e) => {
    const index = rule();
    if (index < 0 || (e.target as Element | null)?.closest(".line-edit")) return;
    tapFeedback();
    open(index);
  });
  return mark;
}

/** Shows the mark for rule `index` (-1: none), read aloud as the rule's sentence. */
export function setRuleMark(mark: HTMLButtonElement, catalog: Catalog, view: View, index: number): void {
  const order = view.orders[index];
  const words = order ? ruleWords(catalog, order) : null;
  mark.hidden = !order;
  mark.setAttribute("aria-label", words ? `${words.when} → ${words.action}` : "");
}
