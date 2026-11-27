// What the Rules tab's redraw depends on.
import type { RuleRun, View } from "../../api/types";
import type { RuleSide } from "../../game/ruleside";

/** What a redraw depends on: a view that changes none of it leaves the tab alone (a press or a focus survives). */
export function shape(view: View, fired: readonly string[], ruleSeen: boolean, runs: readonly RuleRun[], plan: string, side: RuleSide | null): string {
  return JSON.stringify([plan, side, view.orders, view.queue, view.orders_on, view.order_states, view.order_guards, view.order_doing, view.order_dry, view.mixes.map((m) => m.id), view.greyed_mix_ids, view.active_mix_id, view.mix_order, ruleSeen, fired, runs]);
}
