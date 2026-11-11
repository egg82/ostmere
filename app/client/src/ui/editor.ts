// The mix editor (docs/design/opening-screen.md, "The mix editor"): a name, Save, the split bar, then what the edit
// does: live totals for what it changes (editortotals.ts) and the goals it moves (goaltimes.ts), so a drag of the bar
// shows its effect without scrolling; one row per entry with what it does at its share; the cards that can join, folded
// behind one "+ Add" that stays open until tapped again, as cards to tap or drag in; Save as new and Delete at the foot. Save commits and never changes which mix runs (game/mix.ts); ✕ leaves without a
// change. A card joins with a real share (an equal slice from the others) and leaves by its ✕ or by being dragged off
// the bar.
// The "after" numbers are the engine's own: the edit is sent as a dry run (Actions.dryRun) and its view read, never
// kept, so the page computes no rate; an edit still holding a retired or completed card is previewed without it, as
// Save will need it gone. Rates are facts: nothing here says balanced, efficient or better.
import type { GoalRow, Mix, View } from "../api/types";
import { cardShares, dropComponent, holdsCard, joinCard, mixesFull, runningMix, saveDecisions, withShares } from "../game/mix";
import { freeName, repointRule } from "../game/orders";
import { queueFull, queueStint } from "../game/queue";
import { UI } from "../game/text";
import { el, setText, tapFeedback } from "./dom";
import type { NewMarks } from "../game/marks";
import { segmentSpecs } from "./hands";
import type { PartContext } from "./part";
import { deleteParts } from "./editordelete";
import { AddFold } from "./editoradds";
import { entryRows } from "./editorrows";
import { afterHead, totalsRows } from "./editortotals";
import { goalRows } from "./goaltimes";
import { ShareBar } from "./sharebar";
import { stintParts } from "./stint";

const PREVIEW_MS = 150;

export class MixEditor {
  readonly root = el("section", "editor");
  private readonly nameInput = el("input", "editor-name");
  private readonly save = el("button", "primary");
  private readonly saveNew = el("button", "quiet");
  private readonly bar: ShareBar;
  private readonly entries = el("div", "editor-entries");
  private readonly totals = el("div", "editor-totals");
  private readonly adds: AddFold;
  private readonly danger = el("div", "editor-delete");
  private readonly stint = el("div", "editor-stint");
  private picking = false;
  private view: View | null = null;
  private after: View | null = null;
  private from: string | null = null;
  /** A new mix made for this rule (a rule slot's picker in the Rules tab): saving points the rule at it. */
  private forRule: number | null = null;
  private local: Mix | null = null;
  private seq = 0;
  private timer = 0;
  private asking = false;

  constructor(
    private readonly ctx: PartContext, private readonly closed: () => void, private readonly marks: NewMarks,
  ) {
    const { catalog } = ctx;
    const { text } = catalog;
    this.root.hidden = true;
    this.bar = new ShareBar("large", catalog.content.scales.bp, (bp) => catalog.format.share(bp), {
      moving: (shares, d) => {
        this.setShares(shares);
        this.ctx.actions.highlight(d < 0 ? null : this.local?.components.slice(d, d + 2).flatMap((c) => (c.kind === "card_share" ? [c.card] : [])) ?? null);
      },
      commit: (shares) => { this.ctx.actions.highlight(null); this.setShares(shares); },
      remove: (i) => this.drop(i),
    });
    this.adds = new AddFold(catalog, this.marks, () => this.bar.root, (card) => this.join(card));
    const label = el("label", "editor-label");
    label.append(el("span", "", text.get(UI.name)), this.nameInput);
    this.nameInput.maxLength = 40;
    this.nameInput.addEventListener("input", () => { this.drawButtons(); this.schedule(); });
    for (const [b, key] of [[this.save, UI.save], [this.saveNew, UI.saveNew]] as const) {
      b.type = "button";
      setText(b, text.get(key));
    }
    this.save.addEventListener("click", () => this.commit(false));
    this.saveNew.addEventListener("click", () => this.commit(true));
    const close = el("button", "editor-close", "✕");
    close.type = "button";
    close.setAttribute("aria-label", text.get(UI.close));
    close.addEventListener("click", () => this.close());
    const head = el("div", "editor-head");
    const buttons = el("div", "editor-buttons");
    buttons.append(this.save, close);
    head.append(label, buttons);
    const foot = el("div", "editor-foot"); foot.append(this.saveNew, this.danger);   // Save as new, then Delete
    this.root.append(head, this.bar.root, this.totals, this.stint, this.entries, this.adds.root, foot);   // the results sit under the bar, so a drag shows its effect in view
  }

  get open(): boolean {
    return !this.root.hidden;
  }

  /** Opens on a saved mix (the running one when null). */
  show(view: View, mixId: string | null): void {
    const mix = (mixId ? view.mixes.find((m) => m.id === mixId) : runningMix(view)) ?? null;
    if (mix) this.openOn(view, mix, mix.id, null);
  }

  /** Opens on a mix with no cards and a name no saved mix has; Save waits for a card. With `forRule`, saving points
   * that rule at the new mix instead of running it. */
  showNew(view: View, forRule: number | null = null): void {
    this.openOn(view, { id: freeName(view, this.ctx.catalog.text.get(view.mixes.length === 0 ? UI.defaultMix : UI.newMix)), components: [] }, null, forRule);
  }

  private openOn(view: View, mix: Mix, from: string | null, forRule: number | null): void {
    this.view = view;
    this.from = from;
    this.forRule = forRule;
    this.local = structuredClone(mix);
    this.nameInput.value = mix.id;
    this.asking = this.picking = false;
    this.adds.reset();
    this.after = view;
    this.root.hidden = false;
    this.draw();
    this.schedule();
  }

  close(): void {
    this.root.hidden = true;
    this.local = null;
    this.ctx.actions.highlight(null);
    this.closed();
  }

  /** A new view while open: the "now" column and the cards that can join follow it; the edit stays as it is. */
  update(view: View): void {
    this.view = view;
    if (!this.open || !this.local) return;
    if (this.from !== null && !view.mixes.some((m) => m.id === this.from)) { this.close(); return; }   // deleted
    this.draw();
  }

  private setShares(shares: number[]): void {
    if (!this.local) return;
    this.local = withShares(this.local, shares);
    this.drawEntries();
    this.schedule();
  }

  private join(card: string): void {
    if (!this.local || holdsCard(this.local, card)) return;
    this.marks.clear(card);
    tapFeedback();
    this.local = joinCard(this.local, card, this.ctx.catalog.content.scales.bp);
    this.draw();
    this.schedule();
  }

  private drop(i: number): void {
    if (!this.local || this.local.components.length < 2) return;
    tapFeedback();
    this.local = dropComponent(this.local, i, this.ctx.catalog.content.scales.bp);
    this.draw();
    this.schedule();
  }

  private edited(): Mix | null {
    const name = this.nameInput.value.trim();
    return this.local && name ? { ...this.local, id: name } : null;
  }

  /** The edit holds a card no longer in play (retired or completed): it must leave before the mix can run again. */
  private holdsGone(): boolean {
    const view = this.view;
    return !!this.local && !!view && cardShares(this.local).some((c) => this.gone(view, c.card));
  }

  private gone(view: View, card: string): boolean {
    return !view.cards.some((v) => v.card === card);
  }

  /** The edit as Save will have to send it: without the cards no longer in play, their shares back to the rest. */
  private runnable(mix: Mix, view: View): Mix | null {
    let out = mix;
    for (let i = out.components.length - 1; i >= 0; i--) {
      const c = out.components[i];
      if (c?.kind === "card_share" && this.gone(view, c.card)) {
        if (out.components.length < 2) return null;
        out = dropComponent(out, i, this.ctx.catalog.content.scales.bp);
      }
    }
    return out;
  }

  private commit(asNew: boolean): void {
    const view = this.view;
    const mix = this.edited();
    if (!view || !mix || mix.components.length === 0 || this.holdsGone()) return;
    tapFeedback();
    const decisions = this.forRule !== null && this.from === null
      ? [{ kind: "save_mix" as const, mix }, repointRule(view, this.forRule, mix.id)]
      : saveDecisions(view, mix, this.from, asNew);
    for (const d of decisions) this.ctx.actions.decide(d);
    this.close();
  }

  /** Saves the edit when it differs from the saved mix, then queues it until `row`'s goal (CONTRACT.txt, "Goal stints"). */
  private runUntil(row: GoalRow): void {
    const view = this.view;
    const mix = this.edited();
    if (!view || !mix || this.save.disabled) return;
    tapFeedback();
    const saved = view.mixes.find((m) => m.id === mix.id);
    const decisions = saved && JSON.stringify(saved) === JSON.stringify(mix) ? [] : saveDecisions(view, mix, this.from, false);
    for (const d of [...decisions, queueStint(view, mix.id, row)]) this.ctx.actions.decide(d);
    this.close();
  }

  private schedule(): void {
    window.clearTimeout(this.timer);
    this.timer = window.setTimeout(() => void this.preview(), PREVIEW_MS);
  }

  private async preview(): Promise<void> {
    const view = this.view;
    const edited = this.edited();
    const mix = edited && view ? this.runnable(edited, view) : null;
    if (!view || !mix || mix.components.length === 0 || !this.open) return;
    const seq = ++this.seq;
    const runs = mix.id === view.running_mix_id || mix.id === view.active_mix_id;   // the same rule as saveDecisions' switch
    const decisions = runs ? [{ kind: "save_mix" as const, mix }] : [{ kind: "save_mix" as const, mix }, { kind: "switch_mix" as const, mix_id: mix.id }];
    const after = await this.ctx.actions.dryRun(decisions);
    if (seq !== this.seq || !this.open) return;
    this.after = after;
    this.drawEntries();
    this.drawTotals();
  }

  private draw(): void {
    const mix = this.local;
    if (!mix || !this.view) return;
    this.bar.set(segmentSpecs(this.ctx, mix, this.view), mix.components.map((c) => c.share_bp));
    this.drawEntries();
    this.drawTotals();
    this.adds.draw(this.view, mix);
    this.drawButtons();
    this.drawDelete();
  }

  private drawButtons(): void {
    const view = this.view;
    const name = this.nameInput.value.trim();
    const taken = !!view && view.mixes.some((m) => m.id === name);
    const empty = (this.local?.components.length ?? 0) === 0;
    const full = !!view && mixesFull(this.ctx.catalog, view);
    this.save.disabled = !name || empty || this.holdsGone() || (this.from === null && taken) || (full && !taken);
    this.saveNew.hidden = this.from === null;
    this.saveNew.disabled = !name || empty || this.holdsGone() || taken || full;
  }

  private drawEntries(): void {
    const mix = this.local;
    const view = this.view;
    if (!mix || !view) return;
    this.entries.replaceChildren(...entryRows(this.ctx, mix, view, this.after, (i) => this.drop(i)));
  }

  private drawTotals(): void {
    const { view, after, from } = this;
    if (!view) return;
    const { catalog } = this.ctx;
    this.totals.replaceChildren(...totalsRows(catalog, view, after, from), ...goalRows(catalog, view, after, afterHead(catalog, view, from)));
    const off = this.save.disabled || queueFull(catalog, view);
    this.stint.hidden = this.forRule !== null;
    this.stint.replaceChildren(...stintParts(catalog, after, this.picking, off, () => { this.picking = !this.picking; this.drawTotals(); }, (r) => this.runUntil(r)));
  }

  /** Delete asks once, in place (editordelete.ts). */
  private drawDelete(): void {
    const { view, from } = this;
    const ask = (on: boolean): void => { this.asking = on; this.drawDelete(); };
    this.danger.replaceChildren(...(view && from !== null ? deleteParts(this.ctx, view, from, this.asking, ask, () => this.close()) : []));
  }
}
