// The Rules tab's town section (docs/design/opening-screen.md, "The town"): the rules whose switch_mix names a town mix,
// in order, under the town's heading, drawn as the hands' rules are (the tab's own row: ≡ with its menu and drag, ●,
// the condition, → the mix) and a new town rule under them, once the town has a second mix to switch to: with one, a
// town rule has nothing to do, so neither the section nor its New rule is drawn (the always rule stays in the engine).
// The town's always rule reads as ui.rule.town_always (it has no condition to edit); a rule whose mix is greyed is
// dimmed and says why, as a hands rule does. The mix itself is changed from the town's strip.
import type { View } from "../api/types";
import { ruleActions } from "../game/guardwords";
import { mixLabel } from "../game/orders";
import { townCanSwitch, townRules } from "../game/town";
import { UI } from "../game/text";
import { el } from "./dom";
import type { PartContext } from "./part";
import { whyLine } from "./rulewhy";

/** What the town's section takes from the Rules tab, so its rows are the hands' rows. */
export interface TownRows {
  /** Rule `index`'s condition button. */
  cond(index: number): HTMLElement;
  /** Rule `index` as the tab draws a rule: `body` after its ●, the rule's own lines and menu around it. */
  row(index: number, body: HTMLElement[]): HTMLElement[];
  /** The new-rule control, or nothing while writing rules is not open or the rules are full. */
  add(): HTMLElement[];
}

/** The town's rules under the town's heading; none (no section) before a town mix has a rule or while the town has
 * one mix. */
export function townSection(ctx: PartContext, view: View, rows: TownRows): HTMLElement[] {
  const { catalog } = ctx;
  const rules = townRules(catalog, view);
  if (rules.length === 0 || !townCanSwitch(catalog, view)) return [];
  const section = el("section", "rules-lane rules-town");
  section.append(el("h2", "panel-heading", catalog.text.get(UI.townTitle)), ...rules.flatMap((i) => rows.row(i, townBody(ctx, view, i, rows.cond))), ...rows.add());
  return [section];
}

function townBody(ctx: PartContext, view: View, index: number, cond: (index: number) => HTMLElement): HTMLElement[] {
  const { catalog } = ctx;
  const order = view.orders[index]!;
  const mixId = order.then.kind === "switch_mix" ? order.then.mix_id : "";
  if (order.when.kind === "after_time" && order.when.at === 0) return [el("span", "rule-when", catalog.text.fill(UI.ruleTownAlways, { mix: mixLabel(catalog, mixId) }))];
  return [cond(index), el("span", "rule-arrow", "→"), el("span", order.or_else.length > 0 ? "rule-slot-name has-else" : "rule-slot-name", ruleActions(catalog, order))];
}
