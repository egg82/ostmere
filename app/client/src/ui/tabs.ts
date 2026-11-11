// The panel's tab buttons: each takes its words from the catalog and tells `select` which tab a tap chose; showTabs
// draws which one is on.
import type { Catalog } from "../game/catalog";
import { tapFeedback } from "./dom";
import { unmark } from "./fresh";

export type Tab = "cards" | "completed" | "rules";

export function wireTabs(catalog: Catalog, tabs: ReadonlyArray<readonly [HTMLButtonElement, string, Tab]>, select: (tab: Tab) => void): void {
  for (const [button, key, tab] of tabs) {
    button.type = "button";
    button.textContent = catalog.text.get(key);
    button.dataset.tab = tab;   // a lesson's mark of the way to a tab
    button.addEventListener("click", () => {
      tapFeedback();
      select(tab);
    });
  }
}

/** Tab `on`'s panel shown and its button pressed, the others hidden and not; while the editor is open (`editing`)
 * no panel shows. */
export function showTabs(on: Tab, editing: boolean, tabs: ReadonlyArray<readonly [HTMLButtonElement, HTMLElement, Tab]>): void {
  for (const [button, panel, tab] of tabs) {
    panel.hidden = editing || on !== tab;
    if (!panel.hidden) unmark(button);   // a card that arrived while another tab was open dotted this one (screen.ts)
    button.classList.toggle("on", on === tab);
    button.setAttribute("aria-pressed", String(on === tab));
  }
}
