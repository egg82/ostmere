// The Rules tab's side lanes (docs/design/opening-screen.md, "The Rules tab"): each side lane's task rules under the
// lane's label, one line each: ●, the condition (a button that opens the condition editor), → the task, and Remove. A
// ruled lane's always rule reads as its words alone (ui.rule.always: the task is in them); a passed-over one-off stays
// until removed. The rules that answer an offer come last, under their own heading.
import type { View } from "../api/types";
import type { Catalog } from "../game/catalog";
import { isAlways, ruledLaneOf } from "../game/lanes";
import { actionWords, removeRule, taskRules } from "../game/orders";
import { UI } from "../game/text";
import { noteOrderRemoved } from "../telemetry";
import { el, pulse, tapFeedback } from "./dom";
import type { PartContext } from "./part";
import { kindRows } from "./kindrules";
import { whyLine } from "./rulewhy";

/** A rule's ● while it is on (empty while off, so the line keeps its shape). */
export function ruleDot(catalog: Catalog, on: boolean): HTMLElement {
  const dot = el("span", "selector-dot", on ? "●" : "");
  if (on) dot.setAttribute("aria-label", catalog.text.get(UI.ruleOn));
  return dot;
}

/** The group of the rules that answer an offer: no lane's. */
const ANSWERS = "";

/** Each side lane's task rules, under the lane's label. `cond` draws rule `index`'s condition button. */
export function laneSections(ctx: PartContext, view: View, cond: (index: number) => HTMLElement): HTMLElement[] {
  const { catalog } = ctx;
  const byLane = new Map<string, number[]>();
  for (const i of taskRules(view)) {
    const then = view.orders[i]!.then;
    const lane = then.kind === "tap_card" ? catalog.laneOf(then.card) : ANSWERS;
    byLane.set(lane, [...(byLane.get(lane) ?? []), i]);
  }
  const builders = kindRows(ctx, view);
  if (builders.length > 0 && !byLane.has(ANSWERS)) byLane.set(ANSWERS, []);
  const lanes = [...byLane].sort(([a], [b]) => Number(a === ANSWERS) - Number(b === ANSWERS));
  return lanes.map(([lane, rules]) => {
    const section = el("section", "rules-lane");
    const heading = lane === ANSWERS ? catalog.text.get(UI.ruleAnswers) : catalog.laneLabel(lane, view);
    section.append(el("h2", "panel-heading", heading), ...rules.flatMap((i) => [taskRow(ctx, view, i, cond), ...whyLine(catalog, view, i, view.at)]), ...(lane === ANSWERS ? builders : []));
    return section;
  });
}

function taskRow(ctx: PartContext, view: View, index: number, cond: (index: number) => HTMLElement): HTMLElement {
  const { catalog } = ctx;
  const order = view.orders[index]!;
  const row = el("div", "rules-row task-rule");
  const hue = order.then.kind === "tap_card" ? catalog.rank(order.then.card) % 6 : 5;
  const remove = el("button", "quiet", catalog.text.get(UI.orderRemove));
  remove.type = "button";
  remove.addEventListener("click", () => { tapFeedback(); noteOrderRemoved(); ctx.actions.decide(removeRule(view, index)); });
  const does = isAlways(order) ? [] : [el("span", "rule-arrow", "→"), el("b", `rule-action hue-${hue}`, actionWords(catalog, order.then))];
  const lane = ruledLaneOf(catalog, order);   // on a ruled lane, ● is the rule whose task it runs now, as on the hands
  const on = lane === null ? view.orders_on[index] === true : view.lanes.find((l) => l.lane === lane)?.order === index;
  row.append(ruleDot(catalog, on), cond(index), ...does, remove);
  if (order.then.kind === "tap_card" && ctx.fires.fresh.includes(order.then.card)) ctx.arrivals.effect(row, "card", () => pulse(row, "fired"));
  return row;
}
