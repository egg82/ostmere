// The Asks list (CONTRACT.txt, "OFFERS"; docs/design/redesign.md, "Asks"): every open offer, and their one home on the
// page. It takes no room until an ask is open. Under its heading the first open ask in content order is drawn
// (ui/asknode.ts) in a slot of fixed height, so a season bringing several moves nothing under it, and "{n} more"
// opens the whole list in a sheet. On a phone the slot is one row (who, the question, how many wait), and a tap
// anywhere on it opens the sheet, so a season's asks never push the cards from under the thumb. A new ask arrives through the arrival queue after the last of its lines in this
// Step, or at once when the Step holds none of them (it showed before the page's last view); one that arrives already
// answered is never drawn. The shown ask holds the ember outline, and takes the one glow when it is free: a lesson's
// step keeps it first, and the ask waits for it (GlowWhile) until answered.
import type { View } from "../api/types";
import { openAsks } from "../game/asks";
import { UI } from "../game/text";
import { askNode, type AskNode } from "./asknode";
import { AskRuns } from "./askruns";
import { bringIntoView, el, setText, tapFeedback } from "./dom";
import { GlowWhile } from "./fresh";
import { PHONE } from "./layout";
import type { Part, PartContext } from "./part";

export class Asks implements Part {
  readonly root = el("section", "asks");
  private readonly more = el("button", "asks-more");
  private readonly slot = el("div", "asks-slot");
  /** A phone's way into the sheet: laid over the whole row, how many wait at its end. */
  private readonly opener = el("button", "asks-open");
  private readonly sheet = el("dialog", "sheet asks-sheet");
  private readonly sheetList = el("div", "asks-all");
  private readonly runs: AskRuns;
  private front: { offer: string; ask: AskNode; glow: GlowWhile } | null = null;
  private listed = new Map<string, AskNode>();
  private view: View | null = null;
  /** The offers drawn so far this page session: one new to the page arrives through the queue. */
  private readonly seen = new Set<string>();

  constructor(private readonly ctx: PartContext) {
    const { text } = ctx.catalog;
    this.runs = new AskRuns(ctx, () => { if (this.view) this.update(this.view); });
    this.more.type = "button";
    this.opener.type = "button";
    for (const b of [this.more, this.opener]) b.addEventListener("click", () => { tapFeedback(); this.openList(); });
    const head = el("div", "asks-head");
    head.append(el("span", "panel-heading", text.get(UI.asks)), this.more);
    this.root.append(head, this.slot);
    const close = el("button", "quiet", text.get(UI.close));
    close.type = "button";
    close.autofocus = true;
    close.addEventListener("click", () => this.sheet.close());
    const row = el("div", "sheet-actions");
    row.append(close);
    this.sheet.append(el("h2", "panel-heading", text.get(UI.asks)), this.sheetList, row);
    this.sheet.addEventListener("click", (e) => { if (e.target === this.sheet) this.sheet.close(); });
    this.root.append(this.sheet);
    this.root.hidden = true;
  }

  update(view: View): void {
    this.view = view;
    const open = openAsks(view);
    if (open[0] !== undefined && !this.seen.has(open[0])) this.arrive(open[0]);
    for (const id of open) this.seen.add(id);
    this.root.hidden = open.length === 0;
    this.drawFront(view, open[0] ?? null);
    setText(this.more, open.length > 1 ? this.ctx.catalog.text.fill(UI.asksMore, { n: this.ctx.catalog.format.count(open.length - 1) }) : "");
    this.more.hidden = open.length < 2;
    setText(this.opener, this.ctx.catalog.format.count(open.length));
    this.opener.setAttribute("aria-label", `${this.ctx.catalog.text.get(UI.asks)} ${this.opener.textContent ?? ""}`);
    if (this.sheet.open) this.drawList(view, open);
  }

  tick(): void {
    this.front?.glow.tick();
  }

  /** The waiting asks brought into view (the chronicle's "waiting" row): the list when several wait or on a phone, else
   * the one shown below the pinned parts, its first answer focused. */
  show(): void {
    if (this.more.hidden && !window.matchMedia(PHONE).matches) {
      bringIntoView(document, this.slot);
      this.slot.querySelector<HTMLButtonElement>("button")?.focus({ preventScroll: true });
    } else this.openList();
  }

  /** A new ask to be shown: the slot waits for its lines when this Step holds them. One that joins behind the shown ask
   * only moves the count. */
  private arrive(offer: string): void {
    const keys = new Set(this.ctx.catalog.offers.get(offer)?.line_keys ?? []);
    if (this.ctx.lines().some((l) => keys.has(l.key))) this.ctx.arrivals.arrive(this.slot, "chip", `offer:${offer}`);
  }

  private drawFront(view: View, offer: string | null): void {
    if (this.front?.offer !== offer) {
      this.front?.glow.used();
      this.front = null;
      this.slot.replaceChildren();
      if (offer !== null) {
        const ask = askNode(this.ctx, offer);
        this.slot.append(ask.node, this.opener);
        this.front = { offer, ask, glow: new GlowWhile(this.ctx.glow, ask.node) };
        this.front.glow.update(true);   // after the arrival has held the slot: the glow comes when it shows
      }
    }
    if (this.front) this.front.ask.refresh(view, this.runs.figures(view, this.front.offer));
  }

  private openList(): void {
    if (!this.view) return;
    this.drawList(this.view, openAsks(this.view));
    this.sheet.showModal();
  }

  private drawList(view: View, open: string[]): void {
    const next = new Map<string, AskNode>();
    for (const id of open) next.set(id, this.listed.get(id) ?? askNode(this.ctx, id));
    this.listed = next;
    this.sheetList.replaceChildren(...[...next.values()].map((a) => a.node));
    for (const [id, ask] of next) ask.refresh(view, this.runs.figures(view, id));
    if (open.length === 0) this.sheet.close();
  }
}
