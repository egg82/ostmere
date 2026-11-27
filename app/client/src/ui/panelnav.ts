// Which tab the panel shows and which editor has the screen, and where closing each goes (screen.ts holds the parts;
// back.ts turns the back gesture into closing the top layer). A rule's editor returns to what opened it: the person's
// page, or the tab the player was on; opened from the Rules list, it returns to the list.
import type { Condition, View } from "../api/types";
import type { Keeps } from "../game/account/keeps";
import { Layer } from "./back";
import type { Book } from "./book/book";
import { revealBelow } from "./dom";
import type { MixEditor } from "./mixes/editor";
import type { GlowWhile } from "./feedback/fresh";
import type { Hands } from "./hands/hands";
import { PHONE } from "./layout";
import type { RuleTarget } from "./part";
import type { RulesTab } from "./rules/rules";
import type { PanelTabs, Tab } from "./tabs";

/** What the navigation drives: the screen's parts and the nodes it seats. */
export interface PanelSeats {
  tabs: PanelTabs; rules: RulesTab; editor: MixEditor; hands: Hands; book: Book; keeps: Keeps; rulesGlow: GlowWhile;
  panels: Record<Exclude<Tab, "rules" | "book">, HTMLElement>;
  root: HTMLElement; panel: HTMLElement; area: HTMLElement; pinned: HTMLElement;
  view(): View | null;
  /** The Rules tab has been shown this page session. */
  rulesShown(): void;
}

export class PanelNav {
  /** Back closes, in the order they opened: a tab off Tasks, then a mix editor or a person's page (the Rules tab's editors have their own). */
  private readonly tabLayer = new Layer(() => this.pick("cards"));
  private readonly mixLayer = new Layer(() => this.seats.editor.close());
  private readonly pageLayer = new Layer(() => this.seats.hands.lanes.closeEditors());
  /** Where a rule's editor was opened from when that was not the Rules list: closing the editor returns there. */
  private opener: { tab: Tab; lane: string | null } | null = null;

  constructor(private readonly seats: PanelSeats) {}

  /** The Rules tab, on rule `rule`'s editor when given (the shortcuts from the strip and the ledger). */
  openRules(rule: RuleTarget, offered?: Condition): void {
    const { tabs, rules, hands } = this.seats;
    const view = this.seats.view();
    if (!view) return;
    const lane = hands.lanes.openLane;
    this.opener = rule !== null && (tabs.on !== "rules" || lane !== null) ? { tab: tabs.on, lane } : null;
    this.closeEditors();
    this.seats.keeps.keepRulesOpened();
    this.seats.rulesGlow.used();
    this.seats.rulesShown();
    tabs.rules.style.visibility = "";
    tabs.on = "rules";
    this.tabLayer.set(true);   // under the editor it opens
    rules.open(view, rule, offered);
    this.showTab();
    const { root, panel, area, pinned } = this.seats;
    revealBelow(tabs.root.parentElement === panel && !window.matchMedia(PHONE).matches ? tabs.root : area, pinned, [root, panel]);
  }

  openEditor(mixId: string | null, fresh = false, forRule: number | null = null): void {
    const view = this.seats.view();
    if (!view) return;
    if (fresh) this.seats.editor.showNew(view, forRule);
    else this.seats.editor.show(view, mixId);
    this.seats.hands.editorOpened();
    this.showTab();
  }

  /** A rule's editor closed: back to the tab, and the person's page, it was opened from. */
  returnToOpener(): void {
    const from = this.opener;
    this.opener = null;
    if (!from) return;
    this.seats.tabs.on = from.tab;
    if (from.lane !== null) this.seats.hands.lanes.reopen(from.lane);
    this.showTab();
  }

  closeEditors(): void {
    this.seats.rules.leave();
    if (this.seats.editor.open) this.seats.editor.close();
    this.seats.hands.lanes.closeEditors();
  }

  showTab(): void {
    const { tabs, editor, hands, book, rules, root } = this.seats;
    const editing = editor.open || hands.lanes.editing;
    this.tabLayer.set(tabs.on !== "cards");
    this.mixLayer.set(editor.open);
    this.pageLayer.set(hands.lanes.editing);
    root.classList.toggle("editing", editing);
    if (tabs.on !== "book") book.closed();
    tabs.show(editing, { ...this.seats.panels, rules: rules.root, book: book.view }, root);
  }

  /** The tab a tap chose (Rules opens on its own way in). On a phone a panel scrolled under the pinned stage starts at
   * its top again. */
  pick(tab: Tab): void {
    const { tabs, book } = this.seats;
    if (tab === "rules") { this.openRules(null); return; }
    if (tab === "book" && !book.inView) { book.opened(); return; }   // a phone's sheet: the tab on stays
    this.closeEditors();   // an editor is its tab's: it does not follow a tap to another
    tabs.on = tab;
    this.showTab();
    if (tab === "book") book.opened();
    if (window.matchMedia(PHONE).matches) revealBelow(this.seats.area, this.seats.pinned, [this.seats.root, this.seats.panel]);
  }
}
