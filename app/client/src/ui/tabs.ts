// The panel's tabs: a row of buttons, each with its words from the catalog, that tells `select` which tab a tap chose
// and shows which one is on.
import type { Catalog } from "../game/catalog";
import { UI } from "../game/text";
import { el, tapFeedback } from "./dom";
import { unmark } from "./fresh";

export type Tab = "cards" | "completed" | "rules";

export class PanelTabs {
  readonly root = el("div", "tabs");
  readonly cards = el("button", "tab");
  readonly completed = el("button", "tab");
  readonly rules = el("button", "tab");
  /** The tab whose panel shows. */
  on: Tab = "cards";

  constructor(catalog: Catalog, select: (tab: Tab) => void) {
    for (const [button, key, tab] of [[this.cards, UI.tabCards, "cards"], [this.completed, UI.tabCompleted, "completed"], [this.rules, UI.ordersHeading, "rules"]] as const) {
      button.type = "button";
      button.textContent = catalog.text.get(key);
      button.dataset.tab = tab;   // a lesson's mark of the way to a tab
      button.addEventListener("click", () => {
        tapFeedback();
        select(tab);
      });
    }
    this.rules.style.visibility = "hidden";
    this.root.append(this.cards, this.completed, this.rules);
  }

  /** The tab `on`'s panel shown and its button pressed, the others hidden and not; while the editor is open (`editing`)
   * no panel shows and the row keeps its room unseen. */
  show(editing: boolean, panels: Readonly<Record<Tab, HTMLElement>>): void {
    this.root.style.visibility = editing ? "hidden" : "";
    for (const [button, tab] of [[this.cards, "cards"], [this.completed, "completed"], [this.rules, "rules"]] as const) {
      const panel = panels[tab];
      panel.hidden = editing || this.on !== tab;
      if (!panel.hidden) unmark(button);   // a card that arrived while another tab was open dotted this one (screen.ts)
      button.classList.toggle("on", this.on === tab);
      button.setAttribute("aria-pressed", String(this.on === tab));
    }
  }
}
