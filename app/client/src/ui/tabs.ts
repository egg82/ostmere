// The panel's tabs: one row of buttons, each with its words from the catalog, that tells `select` which tab a tap chose
// and shows which one is on. On a wider screen it is the row over the cards (Tasks, Completed, Rules); on a phone the same
// row is the bottom bar (game.css: Tasks, Town, Rules, Book), where Completed is the Book's Done page instead. Book is
// the chronicle's button (the Story owns it): it opens a sheet, so it is never the tab on.
import type { Catalog } from "../game/catalog";
import { UI } from "../game/text";
import { el, tapFeedback } from "./dom";
import { unmark } from "./fresh";

export type Tab = "cards" | "completed" | "town" | "rules";

export class PanelTabs {
  readonly root = el("div", "tabs");
  readonly cards = el("button", "tab");
  readonly completed = el("button", "tab");
  readonly town = el("button", "tab");
  readonly rules = el("button", "tab");
  /** The tab whose panel shows. */
  on: Tab = "cards";

  constructor(catalog: Catalog, book: HTMLButtonElement, select: (tab: Tab) => void) {
    const tabs = [[this.cards, UI.tabCards, "cards"], [this.completed, UI.tabCompleted, "completed"], [this.town, UI.tabTown, "town"], [this.rules, UI.ordersHeading, "rules"]] as const;
    for (const [button, key, tab] of tabs) {
      button.type = "button";
      button.textContent = catalog.text.get(key);
      button.dataset.tab = tab;   // a lesson's mark of the way to a tab
      button.addEventListener("click", () => {
        tapFeedback();
        select(tab);
      });
    }
    this.rules.style.visibility = this.town.style.visibility = "hidden";
    this.root.append(this.cards, this.completed, this.town, this.rules, book);
  }

  /** The tab `on`'s panel shown and its button pressed, the others hidden and not; while the editor is open (`editing`)
   * no panel shows and the row keeps its room unseen. */
  show(editing: boolean, panels: Readonly<Record<Tab, HTMLElement>>): void {
    this.root.style.visibility = editing ? "hidden" : "";
    for (const [button, tab] of [[this.cards, "cards"], [this.completed, "completed"], [this.town, "town"], [this.rules, "rules"]] as const) {
      const panel = panels[tab];
      panel.hidden = editing || this.on !== tab;
      if (!panel.hidden) unmark(button);   // a card that arrived while another tab was open dotted this one (screen.ts)
      button.classList.toggle("on", this.on === tab);
      button.setAttribute("aria-pressed", String(this.on === tab));
    }
  }
}
