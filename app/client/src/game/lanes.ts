// A lane run by rules (CONTRACT.txt, "A lane run by rules"): a townsperson's lane, whose task is set by the player's
// rules, never by their tap. Its default task is an always rule (after_time 0, tap_card), which never lets go, so a
// rule below it acts only while its card cannot: a new rule on the lane goes before the lane's first always rule.
import type { Condition, Decision, Order, View } from "../api/types";
import type { Catalog } from "./catalog";
import { kindRuleAt, roleLabelKey } from "./kindrule";
import { UI } from "./text";

export const ALWAYS: Condition = { kind: "after_time", at: 0 };

/** An always rule: on from the moment it is set, never letting go. A lane's tap, or the answer order that answers an
 * offer the instant it shows. */
export function isAlways(order: Order): boolean {
  return order.when.kind === "after_time" && order.when.at === 0 && (order.then.kind === "tap_card" || order.then.kind === "answer_offer" || order.then.kind === "answer_kind");
}

/** An always rule's words, or null for any other rule: ui.rule.always for a lane's tap, ui.rule.answer for an answer. */
export function alwaysWords(catalog: Catalog, order: Order): string | null {
  if (!isAlways(order)) return null;
  return order.then.kind === "answer_offer" || order.then.kind === "answer_kind" ? answerWords(catalog, order.then)
    : order.then.kind === "tap_card" ? catalog.text.fill(UI.ruleAlways, { card: catalog.cardLabel(order.then.card) }) : null;
}

/** The words for a rule or queue entry that answers an offer: the answer's label under ui.rule.answer. */
export function answerWords(catalog: Catalog, then: { kind: "answer_offer"; offer: string; answer: string } | { kind: "answer_kind"; offer_kind: string; role: string }): string {
  const key = then.kind === "answer_kind" ? roleLabelKey(catalog, then.offer_kind, then.role)
    : catalog.offers.get(then.offer)?.answers.find((a) => a.answer === then.answer)?.label_key;
  return catalog.text.fill(UI.ruleAnswer, { answer: catalog.label(key) });
}

/** The lane a rule's task is on, when it taps a card on a ruled lane; else null. */
export function ruledLaneOf(catalog: Catalog, order: Order): string | null {
  return order.then.kind === "tap_card" && catalog.ruled(order.then.card) ? catalog.laneOf(order.then.card) : null;
}

/** The view's lanes whose LaneInfo.ruled is true, in view order. */
export function ruledLanes(catalog: Catalog, view: View): View["lanes"] {
  return view.lanes.filter((l) => catalog.lanes.get(l.lane)?.ruled === true);
}

/** The rule a lane's Change opens: the one whose task the lane runs now, else its first always rule not passed over
 * (the one that acts next); null for a new always rule. */
export function changeTarget(catalog: Catalog, view: View, lane: string): number | null {
  const now = view.lanes.find((l) => l.lane === lane)?.order ?? null;
  if (now !== null && view.orders[now]) return now;
  const next = view.orders.findIndex((o, i) => isAlways(o) && ruledLaneOf(catalog, o) === lane && view.order_states[i] !== "passed_over");
  return next >= 0 ? next : null;
}

/** Rule `index` set to tap `card`, its condition kept; or (null) a new always rule tapping `card`, appended. */
export function laneTask(view: View, index: number | null, card: string): Decision {
  const then = { kind: "tap_card" as const, card };
  if (index === null) return { kind: "set_orders", orders: [...view.orders, { when: ALWAYS, then }] };
  return { kind: "set_orders", orders: view.orders.map((o, i) => (i === index ? { ...o, then } : o)) };
}

/** The decision that makes `kind` answered by `role`: its rule changed in place, or an always rule appended. */
export function setKindRule(view: View, kind: string, role: string): Decision {
  const then = { kind: "answer_kind" as const, offer_kind: kind, role };
  const at = kindRuleAt(view, kind);
  if (at < 0) return { kind: "set_orders", orders: [...view.orders, { when: ALWAYS, then }] };
  return { kind: "set_orders", orders: view.orders.map((o, i) => (i === at ? { ...o, then } : o)) };
}

/** Where a new rule goes: just before the first always rule on its ruled lane, else (null) at the end. */
export function newRuleAt(catalog: Catalog, view: View, order: Order): number | null {
  const lane = ruledLaneOf(catalog, order);
  const first = lane === null ? -1 : view.orders.findIndex((o) => isAlways(o) && ruledLaneOf(catalog, o) === lane);
  return first >= 0 ? first : null;
}

/** The view as the card panel and the Completed tab draw it: without the cards of ruled lanes, which are offered only
 * as those lanes' tasks. */
export function panelView(catalog: Catalog, view: View): View {
  return { ...view, cards: view.cards.filter((c) => !catalog.ruled(c.card)), completed: view.completed.filter((c) => !catalog.ruled(c.card)) };
}
