// A ledger row a rule watches (ui/ledger.ts; docs/design/opening-screen.md, "Ledger and rules"): the quiet mark, a
// small button to that rule in the Rules tab (the whole row taps through to it), and, when the rule covers the line and
// the store still heads where the rule does not want it, why: empty by the forecast while a rule "under n" wants it
// held, or full with more coming in while a rule "n or more" wants it taken.
import type { LedgerLine, View } from "../api/types";
import type { Catalog } from "../game/catalog";
import { coveredLine, watches } from "../game/cover";
import { emptyAt } from "../game/forecast";
import { actionWords, ruleWords } from "../game/orders";
import { fullAndFed } from "../game/shown";
import { UI } from "../game/text";
import { el, tapFeedback } from "./dom";
import { whyOff } from "./rulewhy";

/** Why rule `index` cannot keep this line where it wants it at `t`: its task can't keep up, or, when it is off, the
 * Rules tab's own reason; null when it can, or when it does not cover the line. */
export function behindWords(catalog: Catalog, view: View, line: LedgerLine, index: number, t: number): string | null {
  const order = view.orders[index];
  if (!order) return null;
  const held = watches(order, line.store, "at_most") && coveredLine(line, view) && emptyAt(view, line.store, t) !== null;
  const taken = watches(order, line.store, "at_least") && fullAndFed(line, t);
  if (!held && !taken) return null;
  const state = view.order_states[index];
  if (state === "outranked" || state === "passed_over") return whyOff(catalog, view, index, t);
  return catalog.text.fill(UI.ledgerBehind, { task: actionWords(catalog, order.then) });
}

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
