// The town editor (docs/design/opening-screen.md, "The town"): the town's mix, one split per person, each person's own
// parts of 100% and the rest idle. A card holds a share in steps (the smallest is the mix editor's smallest), joins from
// the Add row with half of what is free and leaves by its ✕; only that person's own cards, without a cap, are offered.
// Nothing moves a share from one person to another or adds them across people. Save sends the mix, and for a new one the
// town's always rule pointed at it (game/town.ts); ✕ at the top leaves without a change. It takes the card area's place,
// as the mix editor does.
import type { Mix, View } from "../api/types";
import { MIN_SHARE_BP } from "../game/mix";
import { UI } from "../game/text";
import { dropTownCard, given, joinTownCard, newTownMix, people, townMixToEdit, townSaveDecisions, townTasks, withTownShare, TOWN_STEP_BP } from "../game/town";
import { el, setText, tapFeedback } from "./dom";
import type { PartContext } from "./part";
import { splitOf, type Part as Share } from "./townsplit";

export class TownEditor {
  readonly root = el("section", "editor town-editor");
  private readonly save = el("button", "primary");
  private readonly body = el("div", "town-split");
  private view: View | null = null;
  private local: Mix | null = null;
  private isNew = false;

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
    if (this.open && this.local) this.draw();
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
    const parts: Share[] = [];
    for (const c of mix.components) {
      if (c.kind !== "card_share" || catalog.laneOf(c.card) !== lane) continue;
      parts.push({ text: `${catalog.cardLabel(c.card)} ${catalog.format.share(c.share_bp)}`, bp: c.share_bp, hue: catalog.rank(c.card) % 6, idle: false });
      rows.append(this.cardRow(c.card, c.share_bp, mix));
    }
    if (idle > 0) parts.push({ text: `${catalog.text.fill(UI.townIdle, { person: label })} ${catalog.format.share(idle)}`, bp: idle, hue: 5, idle: true });
    const { bar, key } = splitOf(parts);
    bar.classList.add("town-bar");
    const adds = el("div", "editor-adds");
    adds.append(el("span", "editor-add-label", catalog.text.get(UI.add)));
    for (const card of townTasks(catalog, view, lane).filter((id) => !mix.components.some((c) => c.kind === "card_share" && c.card === id))) {
      const add = el("button", `quiet town-add hue-${catalog.rank(card) % 6}`, catalog.cardLabel(card));
      add.type = "button";
      add.dataset.card = card;
      add.disabled = idle < MIN_SHARE_BP;
      add.addEventListener("click", () => this.edit(joinTownCard(catalog, mix, card)));
      adds.append(add);
    }
    node.append(el("h3", "town-name", label), bar, key, rows, adds);
    return node;
  }

  private cardRow(card: string, bp: number, mix: Mix): HTMLElement {
    const { catalog } = this.ctx;
    const row = el("div", "town-card");
    row.dataset.card = card;
    const step = (sign: 1 | -1, glyph: string): HTMLButtonElement => {
      const b = el("button", `quiet town-step town-${sign > 0 ? "plus" : "minus"}`, glyph);
      b.type = "button";
      b.setAttribute("aria-label", `${catalog.cardLabel(card)} ${glyph}`);
      b.disabled = withTownShare(catalog, mix, card, bp + sign * TOWN_STEP_BP) === null;
      b.addEventListener("click", () => this.edit(withTownShare(catalog, mix, card, bp + sign * TOWN_STEP_BP)));
      return b;
    };
    const drop = el("button", "quiet town-drop", "✕");
    drop.type = "button";
    drop.setAttribute("aria-label", `${catalog.cardLabel(card)} ${catalog.text.get(UI.orderRemove)}`);
    drop.addEventListener("click", () => this.edit(dropTownCard(mix, card)));
    row.append(el("span", "town-card-name", catalog.cardLabel(card)), step(-1, "−"), el("span", "town-card-share", catalog.format.share(bp)), step(1, "+"), drop);
    return row;
  }
}
