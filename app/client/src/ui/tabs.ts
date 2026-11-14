// The panel's tabs: one row of buttons, each with its words from the catalog, that tells `select` which tab a tap chose
// and shows which one is on: Tasks, Town, Rules and Book. game.css gives the one row three forms: the desktop's left rail
// (docs/design/redesign.md, "Desktop frame"), a row over the cards on a landscape phone, and a phone's bottom bar with an
// icon each (ui/partseat.ts seats it). Book is the chronicle's button (the Story owns it): it opens a sheet, so it is
// never the tab on.
import type { Catalog } from "../game/catalog";
import { UI } from "../game/text";
import { el, tapFeedback } from "./dom";
import { unmark } from "./fresh";

export type Tab = "cards" | "town" | "rules";

export class PanelTabs {
  readonly root = el("nav", "tabs");
  readonly cards = el("button", "tab");
  readonly town = el("button", "tab");
  readonly rules = el("button", "tab");
  /** The tab whose panel shows. */
  on: Tab = "cards";

  constructor(catalog: Catalog, book: HTMLButtonElement, select: (tab: Tab) => void) {
    const tabs = [[this.cards, UI.tabCards, "cards"], [this.town, UI.tabTown, "town"], [this.rules, UI.ordersHeading, "rules"]] as const;
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
    this.root.append(this.cards, this.town, this.rules, book);
  }

  /** The tab `on`'s panel shown and its button pressed, the others hidden and not; while the editor is open (`editing`)
   * no panel shows. `root` learns the tab on (game.css: the desktop's Town view takes the middle and the right). */
  show(editing: boolean, panels: Readonly<Record<Tab, HTMLElement>>, root: HTMLElement): void {
    root.dataset.tab = this.on;
    for (const [button, tab] of [[this.cards, "cards"], [this.town, "town"], [this.rules, "rules"]] as const) {
      const panel = panels[tab];
      panel.hidden = editing || this.on !== tab;
      if (!panel.hidden) unmark(button);   // something that arrived while another tab was open dotted this one (screen.ts)
      button.classList.toggle("on", this.on === tab);
      button.setAttribute("aria-pressed", String(this.on === tab));
    }
  }
}
