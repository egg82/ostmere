// What the Rules tab's redraw depends on.
import type { RuleRun, View } from "../api/types";

/** What a redraw depends on: a view that changes none of it leaves the tab alone (a press or a focus survives). */
export function shape(view: View, fired: readonly string[], ruleSeen: boolean, runs: readonly RuleRun[], plan: string): string {
  return JSON.stringify([plan, view.orders, view.queue, view.orders_on, view.order_states, view.order_guards, view.order_doing, view.order_dry, view.mixes.map((m) => m.id), view.greyed_mix_ids, view.active_mix_id, view.mix_order, view.town_mix_order, ruleSeen, fired, runs]);
}
