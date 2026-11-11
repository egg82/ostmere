// The condition editor's facts (condition.ts): a store's rate while the rule's mix runs, and the goals running it
// moves (goaltimes.ts), the engine's own numbers from one dry run (the rules cleared, the mix run), never kept. Never a
// verdict.
import type { View } from "../api/types";
import { UI } from "../game/text";
import { el, setText } from "./dom";
import { goalRows } from "./goaltimes";
import type { PartContext } from "./part";

export class RuleFact {
  readonly root = el("div", "cond-facts");
  private readonly line = el("p", "cond-fact");
  private readonly goals = el("div", "editor-totals");
  private after: View | null = null;
  private seq = 0;

  constructor(private readonly ctx: PartContext) {
    this.root.append(this.line, this.goals);
  }

  /** What the rule does changed: the last dry run no longer answers, and one still on its way is dropped. */
  reset(): void {
    this.after = null;
    this.seq += 1;
  }

  /** Dry-runs `mix`, then calls `landed` unless reset meanwhile. */
  async ask(mix: string, landed: () => void): Promise<void> {
    const seq = ++this.seq;
    const after = await this.ctx.actions.dryRun([{ kind: "set_orders", orders: [] }, { kind: "switch_mix", mix_id: mix }]);
    if (seq !== this.seq) return;
    this.after = after;
    landed();
  }

  /** "while {what} runs: {store} {rate}" and the goal rows of the last dry run against `view`, or nothing (no store,
   * or no answer yet). */
  show(store: string | null, what: string, view: View | null): void {
    const { catalog } = this.ctx;
    const line = store === null ? undefined : this.after?.ledger.find((l) => l.store === store);
    const whileRuns = catalog.text.fill(UI.ruleWhileRuns, { mix: what });
    setText(this.line, line ? `${whileRuns}: ${catalog.storeLabel(line.store)} ${catalog.format.perMinute(line.net_per_hour)}` : "");
    this.goals.replaceChildren(...(store !== null && view ? goalRows(catalog, view, this.after, catalog.text.get(UI.ifRun)) : []));
  }
}
