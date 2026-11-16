// The town editor (docs/design/opening-screen.md, "The town"): the town's mix, one split per person, each person's own
// parts of 100% and the rest idle. A person's bar is the hands' ShareBar: its dividers are dragged to trade share between
// neighbours, the last one against the idle rest (never below the mix editor's smallest share, the idle rest down to nothing). A card joins from the
// Add row with half of what is free (an equal slice from the person's cards when nothing is) and leaves by its ✕; only that person's own cards, without a cap, are offered.
// Nothing moves a share from one person to another or adds them across people. Save sends the mix, and for a new one the
// town's always rule pointed at it (game/town.ts); ✕ at the top leaves without a change. It takes the card area's place,
// as the mix editor does.
import type { Mix, View } from "../api/types";
import { UI } from "../game/text";
import { dropTownCard, given, joinTownCard, newTownMix, people, townMixToEdit, townSaveDecisions, townTasks, withTownShares } from "../game/town";
import { el, setText, tapFeedback } from "./dom";
import type { PartContext } from "./part";
import { ShareBar, type SegmentSpec } from "./sharebar";
import { Bonus } from "./bonus";
import { takesNothing } from "./cardneeds";
import { sideStrength } from "./strength";

export class TownEditor {
  readonly root = el("section", "editor town-editor");
  private readonly save = el("button", "primary");
  private readonly body = el("div", "town-split");
  private view: View | null = null;
  private local: Mix | null = null;
  private isNew = false;
  private readonly bars = new Map<string, ShareBar>();
  /** The cards whose bonus line has its strength sheet open: a redraw keeps them open. */
  private readonly bonusOpen = new Set<string>();
  /** A divider is held: a new view waits for the let-go, so the bar under the finger is not rebuilt. */
  private held = false;

  constructor(private readonly ctx: PartContext, private readonly closed: () => void) {
    const { text } = ctx.catalog;
    this.root.hidden = true;
    this.save.type = "button";
    setText(this.save, text.get(UI.save));
    this.save.addEventListener("click", () => this.commit());
    const close = el("button", "editor-close", "✕");
    close.type = "button";
    close.setAttribute("aria-label", text.get(UI.close));
    close.addEventListener("click", () => this.close());
    const buttons = el("div", "editor-buttons");
    buttons.append(this.save, close);
    const head = el("div", "editor-head");
    head.append(el("span", "town-title", text.get(UI.townTitle)), buttons);
    this.root.append(head, this.body);
  }

  get open(): boolean {
    return !this.root.hidden;
  }

  /** Opens on the town's mix (the running one, else the first always rule's), else on a new one. */
  show(view: View): void {
    const mix = townMixToEdit(this.ctx.catalog, view);
    this.view = view;
    this.isNew = mix === null;
    this.local = structuredClone(mix ?? newTownMix(view, this.ctx.catalog.text.get(UI.townTitle)));
    this.local.components = this.local.components.filter((c) => c.kind !== "card_share" || view.cards.some((v) => v.card === c.card));   // a gone card leaves; Save mends the mix
    this.root.hidden = false;
    this.draw();
  }

  close(): void {
    this.root.hidden = true;
    this.local = null;
    this.closed();
  }

  /** A new view while open: the cards that can join follow it; the edit stays as it is. */
  update(view: View): void {
    this.view = view;
    if (!this.held && this.open && this.local) this.draw();
  }

  private commit(): void {
    if (!this.view || !this.local) return;
    tapFeedback();
    for (const d of townSaveDecisions(this.view, this.local, this.isNew)) this.ctx.actions.decide(d);
    this.close();
  }

  private edit(next: Mix | null): void {
    if (!next) return;
    tapFeedback();
    this.local = next;
    this.draw();
  }

  private draw(): void {
    const { view, local } = this;
    if (!view || !local) return;
    const { catalog } = this.ctx;
    this.save.disabled = local.components.length === 0;
    this.body.replaceChildren(...people(catalog, view).map((lane) => this.person(lane, view, local)));
  }

  private person(lane: string, view: View, mix: Mix): HTMLElement {
    const { catalog } = this.ctx;
    const label = catalog.laneLabel(lane, view);
    const taken = given(catalog, mix, lane);
    const idle = catalog.content.scales.bp - taken;
    const node = el("section", "town-person");
    node.dataset.lane = lane;
    const rows = el("div", "town-cards");
    const cards = mix.components.flatMap((c) => (c.kind === "card_share" && catalog.laneOf(c.card) === lane ? [c] : []));
    const specs: SegmentSpec[] = cards.map((c) => ({ key: c.card, label: catalog.cardLabel(c.card), hue: catalog.rank(c.card) }));
    const shares = cards.map((c) => c.share_bp);
    specs.push({ key: `idle:${lane}`, label: catalog.text.fill(UI.townIdle, { person: label }), hue: 5, idle: true });   // always there, so a full person has a divider to drag down
    shares.push(idle);
    const bar = this.barOf(lane);
    bar.set(specs, shares);
    this.cardRows(rows, lane, mix);
    const adds = el("div", "editor-adds");
    adds.append(el("span", "editor-add-label", catalog.text.get(UI.add)));
    for (const card of townTasks(catalog, view, lane).filter((id) => !mix.components.some((c) => c.kind === "card_share" && c.card === id))) {
      const add = el("button", `quiet town-add hue-${catalog.rank(card) % 6}`);
      add.append(el("span", "town-card-name", catalog.cardLabel(card)), ...this.upside(card), ...this.nothing(card));
      add.type = "button";
      add.dataset.card = card;
      add.addEventListener("click", () => this.edit(joinTownCard(catalog, mix, card)));
      adds.append(add);
    }
    node.append(el("h3", "town-name", label), bar.root, rows, adds);
    return node;
  }

  /** The person's bar, kept across redraws; moving a divider edits the mix at once, and letting go redraws. */
  private barOf(lane: string): ShareBar {
    const kept = this.bars.get(lane);
    if (kept) return kept;
    const { catalog } = this.ctx;
    const at = (shares: number[]): void => {
      if (this.local) this.local = withTownShares(catalog, this.local, lane, shares);
    };
    const bar = new ShareBar("large town-bar", catalog.content.scales.bp, (bp) => catalog.format.share(bp), {
      moving: (shares, d) => {
        at(shares);
        const row = this.body.querySelector<HTMLElement>(`.town-person[data-lane="${lane}"] .town-cards`);
        if (this.local && row) this.cardRows(row, lane, this.local);
        if (d >= 0) this.held = true;
        else this.release();
      },
      commit: (shares) => { at(shares); this.release(); },
    });
    this.bars.set(lane, bar);
    return bar;
  }

  private release(): void {
    this.held = false;
    if (this.open && this.local) this.draw();
  }

  private cardRows(rows: HTMLElement, lane: string, mix: Mix): void {
    const { catalog } = this.ctx;
    rows.replaceChildren(...mix.components.flatMap((c) => (c.kind === "card_share" && catalog.laneOf(c.card) === lane ? [this.cardRow(c.card, c.share_bp, mix)] : [])));
  }

  /** The card's upside: on a row at its share, and on its Add button, which has no share yet, at the full figure. A row's
   * upside that feeds a side leads to that side's strength (bonus.ts). */
  private upside(card: string, shareBp?: number): HTMLElement[] {
    const { catalog } = this.ctx;
    const info = catalog.cards.get(card);
    if (!info?.upside_key) return [];
    const words = catalog.text.fill(info.upside_key, (shareBp === undefined ? catalog.format.figures(info.change_bp) : catalog.format.figuresAt(info, shareBp)));
    const side = info.kept.find((k) => k.side !== null)?.side;
    if (shareBp === undefined || !side || !this.view) return [el("span", "card-upside town-card-upside", words)];
    const bonus = new Bonus(catalog, side, "card-upside town-card-upside", (open) => { if (open) this.bonusOpen.add(card); else this.bonusOpen.delete(card); }, this.bonusOpen.has(card));
    bonus.draw(words, sideStrength(catalog, this.view, side));
    return [bonus.line];
  }

  private nothing(card: string): HTMLElement[] {
    const line = takesNothing(this.ctx.catalog, card);
    return line ? [line] : [];
  }

  private cardRow(card: string, bp: number, mix: Mix): HTMLElement {
    const { catalog } = this.ctx;
    const row = el("div", "town-card");
    row.dataset.card = card;
    const drop = el("button", "quiet town-drop", "✕");
    drop.type = "button";
    drop.setAttribute("aria-label", `${catalog.cardLabel(card)} ${catalog.text.get(UI.orderRemove)}`);
    drop.addEventListener("click", () => this.edit(dropTownCard(mix, card)));
    const what = el("span", "town-card-what");   // the card, and what it is for when it says (its upside)
    what.append(el("span", "town-card-name", catalog.cardLabel(card)));
    what.append(...this.upside(card, bp), ...this.nothing(card));
    row.append(what, el("span", "town-card-share", catalog.format.share(bp)), drop);
    return row;
  }
}
