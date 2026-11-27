// The Rules page's two sides (docs/decisions/mixes.md, "Mine and Camp"): a rule is on Camp when its action runs on another
// person's lane (a task on a ruled lane) or on the town's layer (a mix `town.isTownMix` names, the client's reading of
// the engine's `mix_layer`); every other rule is the player's own. Read off the rule's action, never its wording.
import type { Decision, View } from "../../api/types";
import type { Catalog } from "../page/catalog";
import { isTownMix, people } from "../town/town";

export type RuleSide = "mine" | "camp";

/** The side rule `index` is on. */
export function ruleSideOf(catalog: Catalog, view: View, index: number): RuleSide {
  const then = view.orders[index]?.then;
  if (then?.kind === "tap_card") return catalog.ruled(then.card) ? "camp" : "mine";
  const mix = then?.kind === "switch_mix" ? view.mixes.find((m) => m.id === then.mix_id) : undefined;
  return mix !== undefined && isTownMix(catalog, view, mix) ? "camp" : "mine";
}

/** The side of the first rule `d` adds or changes, null for a decision that sets none. */
export function landedSide(catalog: Catalog, view: View, d: Decision): RuleSide | null {
  if (d.kind !== "set_orders") return null;
  const was = new Set(view.orders.map((o) => JSON.stringify(o)));
  const at = d.orders.findIndex((o) => !was.has(JSON.stringify(o)));
  return at < 0 ? null : ruleSideOf(catalog, { ...view, orders: d.orders }, at);
}

/** The switch is drawn once a second person has hands; before that the page is one list. */
export function sideSwitchShown(catalog: Catalog, view: View): boolean {
  return people(catalog, view).length > 0;
}
