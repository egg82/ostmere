// Next's "+ Plan" (contract/goal-stints.txt, "Goal stints"; docs/design/opening-screen/rules-tab.md, "The Rules tab"): the two kinds of entry
// the queue holds. Every card "When ready" takes, each picked through the card's own path (game/queue.whenReady); one
// the page cannot promise a ready time for says what it waits on in its face's words (game/needwords.ts, which the
// face draws from too), under the Tasks page's section headings; then the saved hands mixes, under "Run until…": a mix picked lists the
// goals it would run to (the dry run of switching to it, or the live view's when it already runs), and a goal picked
// queues the stint at the end of Next.
import type { Card, View } from "../api/types";
import { sectioned } from "../game/cardsections";
import { planCards, queueFull, queueStint, whenReady } from "../game/queue";
import { isTownMix } from "../game/town";
import { UI } from "../game/text";
import { waitWords } from "../game/needwords";
import { keptReadyAt } from "../game/ready";
import { el, tapFeedback } from "./dom";
import type { PartContext } from "./part";
import { sectionHead } from "./condrows";
import { goalPicker } from "./stint";

type Step = { mix: string | null; after: View | null };

export class StintPlan {
  private step: Step | null = null;
  private seq = 0;

  constructor(private readonly ctx: PartContext, private readonly redraw: () => void) {}

  /** What the rows drawn for `view` depend on beyond the queue and the mixes: the cards Plan offers and what they wait on. */
  shape(view: View): string {
    const cards = planCards(this.ctx.catalog, view);
    return JSON.stringify([cards.map((c) => c.card), this.step === null ? null : cards.map((c) => this.words(view, c))]);
  }

  /** The Plan button, or while a plan is under way its picker; nothing when no card or mix could be queued. */
  rows(view: View): HTMLElement[] {
    const { catalog } = this.ctx;
    const mixes = view.mixes.filter((m) => !view.greyed_mix_ids.includes(m.id) && !isTownMix(catalog, view, m));
    const cards = planCards(catalog, view);
    if (this.step === null) {
      if (!this.ctx.keeps.ruleSeen() || queueFull(catalog, view) || (mixes.length === 0 && cards.length === 0)) return [];
      const b = el("button", "quiet stint-plan", `+ ${catalog.text.get(UI.queuePlan)}`);
      b.type = "button";
      b.addEventListener("click", () => { tapFeedback(); this.step = { mix: null, after: null }; this.redraw(); });
      return [b];
    }
    const { mix, after } = this.step;
    const close = el("button", "editor-close", "✕");
    close.type = "button";
    close.setAttribute("aria-label", catalog.text.get(UI.close));
    close.addEventListener("click", () => { this.step = null; this.seq++; this.redraw(); });
    const head = el("div", "cond-head");
    head.append(el("h3", "rules-next", mix === null ? catalog.text.get(UI.queuePlan) : catalog.text.fill(UI.stintWhich, { mix })), close);
    if (mix === null) {
      const offered = cards.map((c) => ({ c, words: this.words(view, c) }));
      const cardRows = sectioned(catalog, offered, (o) => o.c.card, view).flatMap((g) => [...sectionHead(g.heading), ...g.items.map((o) => this.cardRow(view, o.c, o.words))]);
      const mixHead = sectionHead(mixes.length === 0 ? "" : catalog.text.get(UI.stintRun));   // a mix may bear a card's name
      return [head, ...cardRows, ...mixHead, ...mixes.map((m) => this.mixButton(view, m.id))];
    }
    return after === null ? [head] : [head, goalPicker(catalog, after, (until) => {
      tapFeedback();
      this.step = null;
      this.ctx.actions.decide(queueStint(view, mix, until));
      this.redraw();
    })];
  }

  /** What a card waits on in its face's words, when the page cannot see a ready time kept for it; else null. */
  private words(view: View, card: Card): string | null {
    const { catalog } = this.ctx;
    return card.blocker !== null && keptReadyAt(view, card, catalog.content.scales.quantity_per_item) === null ? waitWords(catalog, view, card) : null;
  }

  /** A card's row, picked through the card's own path (When ready): a waiting entry says what it waits on. */
  private cardRow(view: View, card: Card, waits: string | null): HTMLElement {
    const { catalog } = this.ctx;
    const b = el("button", "selector-run plan-card");
    b.type = "button";
    b.append(el("span", "selector-name", catalog.cardLabel(card.card)),
      el("span", "selector-note", waits ?? catalog.text.get(UI.queueWhenReady)));
    b.addEventListener("click", () => {
      const decision = whenReady(catalog, view, card.card);
      if (decision === null) return;
      tapFeedback();
      this.step = null;
      this.ctx.actions.decide(decision);
      this.redraw();
    });
    return b;
  }

  private mixButton(view: View, id: string): HTMLElement {
    const b = el("button", "selector-run");
    b.type = "button";
    b.append(el("span", "selector-name", id));
    b.addEventListener("click", () => { tapFeedback(); void this.pick(view, id); });
    return b;
  }

  private async pick(view: View, id: string): Promise<void> {
    const seq = ++this.seq;
    this.step = { mix: id, after: null };
    this.redraw();
    const runs = id === view.running_mix_id || id === view.active_mix_id;
    const after = runs ? view : await this.ctx.actions.dryRun([{ kind: "switch_mix", mix_id: id }]);
    if (seq !== this.seq || this.step === null) return;
    this.step = { mix: id, after };
    this.redraw();
  }
}
