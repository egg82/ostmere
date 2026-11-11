// The condition editor's line beside Save about the rule as Save would write it (CONTRACT.txt, "Dry rules"): what the
// server says in View.order_dry from a dry run of those decisions, never kept, never blocking Save.
import type { Order, View } from "../api/types";
import { newRuleAt } from "../game/lanes";
import { ruleDecisions, ruleExists } from "../game/orders";
import { el, setText } from "./dom";
import type { PartContext } from "./part";
import { dryWords } from "./rulewhy";

export class DryNote {
  readonly root = el("p", "editor-note cond-note cond-dry");
  private seq = 0;

  constructor(private readonly ctx: PartContext) {}

  /** The line for `order` at `index` (null: a new rule) of `view`, or nothing: only a rule that lets go as a store rises
   * can say, a town rule is set by a rule alone, and a rule that already exists is not written. */
  async show(view: View | null, index: number | null, order: Order | null, town: boolean): Promise<void> {
    const seq = ++this.seq;
    const { catalog, actions } = this.ctx;
    if (!view || !order || town || order.when.kind !== "at_most" || ruleExists(view, index, order)) { setText(this.root, ""); return; }
    const at = index ?? newRuleAt(catalog, view, order) ?? view.orders.length;
    const after = await actions.dryRun(ruleDecisions(view, catalog, index, order));
    if (seq === this.seq) setText(this.root, (after && dryWords(catalog, order, after.order_dry[at] ?? null)) ?? "");
  }
}
