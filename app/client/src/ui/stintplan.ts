// Next's "+ Plan" (CONTRACT.txt, "Goal stints"): pick a saved hands mix, then a goal from the goals the mix would run to (the
// dry run of switching to it, or the live view's when it already runs); the pick queues the stint at the end of Next.
import type { View } from "../api/types";
import { queueFull, queueStint } from "../game/queue";
import { isTownMix } from "../game/town";
import { UI } from "../game/text";
import { el, tapFeedback } from "./dom";
import type { PartContext } from "./part";
import { goalPicker } from "./stint";

type Step = { mix: string | null; after: View | null };

export class StintPlan {
  private step: Step | null = null;
  private seq = 0;

  constructor(private readonly ctx: PartContext, private readonly redraw: () => void) {}

  /** The Plan button, or while a plan is under way its picker; nothing when no mix could be queued. */
  rows(view: View): HTMLElement[] {
    const { catalog } = this.ctx;
    const mixes = view.mixes.filter((m) => !view.greyed_mix_ids.includes(m.id) && !isTownMix(catalog, view, m));
    if (this.step === null) {
      if (!this.ctx.keeps.ruleSeen() || queueFull(catalog, view) || mixes.length === 0) return [];
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
    if (mix === null) return [head, ...mixes.map((m) => this.mixButton(view, m.id))];
    return after === null ? [head] : [head, goalPicker(catalog, after, (row) => {
      tapFeedback();
      this.step = null;
      this.ctx.actions.decide(queueStint(view, mix, row));
      this.redraw();
    })];
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
