// Next's "+ Plan" (CONTRACT.txt, "Goal stints"; docs/design/opening-screen.md, "The Rules tab"): the two kinds of entry
// the queue holds. The cards "When ready" takes, ready now ones included, each picked through the card's own
// path (game/queue.whenReady), and the steps it would take but for what they wait on, off, each saying what in its
// face's words (game/needwords.ts, which the face draws from too), together under the Tasks page's section headings; then the saved hands mixes: a mix picked lists the goals it would run to (the dry run of
// switching to it, or the live view's when it already runs), and a goal picked queues the stint at the end of Next.
import type { Card, View } from "../api/types";
import { sectioned } from "../game/cardsections";
import { planCards, queueFull, queueStint, whenReady } from "../game/queue";
import { isTownMix } from "../game/town";
import { UI } from "../game/text";
import { waitWords } from "../game/needwords";
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
    const { now, waiting } = planCards(this.ctx.catalog, view);
    return JSON.stringify([now.map((c) => c.card), this.step === null ? null : waiting.map((c) => waitWords(this.ctx.catalog, view, c))]);
  }

  /** The Plan button, or while a plan is under way its picker; nothing when no card or mix could be queued. */
  rows(view: View): HTMLElement[] {
    const { catalog } = this.ctx;
    const mixes = view.mixes.filter((m) => !view.greyed_mix_ids.includes(m.id) && !isTownMix(catalog, view, m));
    const cards = planCards(catalog, view);
    if (this.step === null) {
      if (!this.ctx.keeps.ruleSeen() || queueFull(catalog, view) || (mixes.length === 0 && cards.now.length === 0)) return [];
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
      const offered = [...cards.now.map((c) => ({ c, words: null })), ...cards.waiting.flatMap((c) => { const words = waitWords(catalog, view, c); return words === null ? [] : [{ c, words }]; })];
      const cardRows = sectioned(catalog, offered, (o) => o.c.card, view).flatMap((g) => [...sectionHead(g.heading), ...g.items.map((o) => this.cardRow(view, o.c, o.words))]);
      return [head, ...cardRows, ...mixes.map((m) => this.mixButton(view, m.id))];
    }
    return after === null ? [head] : [head, goalPicker(catalog, after, (until) => {
      tapFeedback();
      this.step = null;
      this.ctx.actions.decide(queueStint(view, mix, until));
      this.redraw();
    })];
  }

  /** A card's row: When ready, picked through the card's own path; or, with what it waits on, off. */
  private cardRow(view: View, card: Card, waits: string | null): HTMLElement {
    const { catalog } = this.ctx;
    const b = el("button", "selector-run plan-card");
    b.type = "button";
    b.disabled = waits !== null;
    b.append(el("span", "selector-name", catalog.cardLabel(card.card)), ...(catalog.ruled(card.card) ? [el("span", "plan-lane", catalog.laneLabel(catalog.laneOf(card.card), view))] : []),
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
