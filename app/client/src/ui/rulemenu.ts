// A rule's ≡ menu, open under its row: Move up, Move down, Remove (Next's row: no Remove).
import type { Catalog } from "../game/catalog";
import { UI } from "../game/text";
import { el } from "./dom";

export interface RuleMenu {
  first: boolean;
  last: boolean;
  move(step: -1 | 1): void;
  /** Absent for Next's row, which is moved but never removed. */
  remove?: () => void;
}

export function ruleMenu(catalog: Catalog, m: RuleMenu): HTMLElement {
  const tool = (label: string, disabled: boolean, act: () => void, cls = "quiet"): HTMLButtonElement => {
    const b = el("button", cls, label);
    b.type = "button";
    b.disabled = disabled;
    b.addEventListener("click", act);
    return b;
  };
  const menu = el("div", "rule-menu");
  const remove = m.remove;
  menu.append(
    tool(catalog.text.get(UI.ruleUp), m.first, () => m.move(-1)),
    tool(catalog.text.get(UI.ruleDown), m.last, () => m.move(1)),
    ...(remove ? [tool(catalog.text.get(UI.orderRemove), false, () => remove(), "quiet danger")] : []),
  );
  return menu;
}
