// A rule's guards ("unless") and fallbacks ("or else") as the page words them (docs/design/rule-guards.md, "How the
// page words it"). A rule reads as one sentence: its condition, then ", unless {guard}" and ", and unless {guard}" for
// each further guard; its actions read "{first}, or else {next}". A guard is stored as the condition that blocks the
// rule and is worded as a state ("smoked is full"); its one-item band is never in the sentence. While a guard holds,
// the paused line names where it lets go (View.order_guards[i][j].lets_go) and what the store holds now.
import type { Condition, Order, OrderVerb, View } from "../api/types";
import type { Catalog } from "./catalog";
import { sample } from "./clock";
import { actionWords, chipOf, conditionWords } from "./orders";
import { BP, isShare, levelWords, readRule } from "./storerule";
import { readSubject, subjectName } from "./subjectrule";
import { UI } from "./text";

/** A rule's actions in the order it tries them: `then`, then `or_else`. */
export const actionsOf = (order: Order): OrderVerb[] => [order.then, ...order.or_else];

/** A guard as a state: a chip's label ("tired"), "Forage is done 5 times", "Foraging is level 3 or more", or a store's
 * "smoked is full", "is empty", "is 10 or more", "is under 10", "is half or more", "is a quarter or less"; null for a
 * condition the page does not draw. */
export function guardWords(catalog: Catalog, guard: Condition): string | null {
  const { text, format } = catalog;
  const chip = chipOf(catalog, guard);
  if (chip) return catalog.label(chip.label_key);
  const subject = readSubject(catalog, guard);
  if (subject?.kind === "count") return text.fill(subject.n === 1 ? UI.guardDoneOnce : UI.guardDone, { card: catalog.cardLabel(subject.card), n: format.count(subject.n) });
  if (subject) return text.fill(UI.guardLevel, { name: subjectName(catalog, subject), n: format.count(subject.n) });
  const rule = readRule(guard, catalog.content.scales.quantity_per_item, (s) => catalog.isLevel(s));
  if (!rule) return null;
  const store = catalog.storeLabel(rule.store);
  const below = rule.test === "below";
  if (isShare(rule.n) && rule.n.share === (below ? 0 : BP)) return text.fill(below ? UI.guardEmpty : UI.guardFull, { store });
  const key = isShare(rule.n) ? (below ? UI.guardDownTo : UI.guardUpTo) : (below ? UI.guardBelow : UI.guardReaches);
  return text.fill(key, { store, n: levelWords(catalog, rule.n) });
}

/** A rule's condition with its guards: "13 or more catch, until under 1, unless smoked is full, and unless tired". A
 * rule with no guard reads as its condition alone (orders.conditionWords). */
export function ruleCondition(catalog: Catalog, order: Order): string | null {
  const when = conditionWords(catalog, order.when);
  if (when === null) return null;
  return order.unless.reduce((condition, g, j) => {
    const guard = guardWords(catalog, g);
    return guard === null ? condition : catalog.text.fill(j === 0 ? UI.ruleUnless : UI.ruleAndUnless, { rule: condition, when: guard });
  }, when);
}

/** What a rule does: "Smoke the catch, or else Smoke roots"; a rule with no fallback reads as its one action. */
export function ruleActions(catalog: Catalog, order: Order): string {
  return order.or_else.reduce((first, verb) => catalog.text.fill(UI.ruleOrElse, { a: first, b: actionWords(catalog, verb) }), actionWords(catalog, order.then));
}

/** The why line of a paused rule at `t`: "paused until smoked is under 19 · now 20", "paused while tired", one clause
 * per guard that holds, joined by ", and". Null when no guard holds. */
export function pausedWords(catalog: Catalog, view: View, index: number, t: number): string | null {
  const order = view.orders[index];
  const guards = view.order_guards[index] ?? [];
  const clauses = (order?.unless ?? []).flatMap((g, j) => (guards[j]?.on ? [guardClause(catalog, view, g, guards[j]!.lets_go, t)] : []));
  if (clauses.length === 0) return null;
  const why = clauses.reduce((a, b) => catalog.text.fill(UI.ruleAnd, { a, b }));
  return catalog.text.fill(UI.rulePaused, { until: why });
}

/** One held guard: on a store with a ledger line, where it lets go in whole items and the amount now; else "while
 * {guard}". The level is the served `letsGo`, never worked out from the guard: "n or more" lets go under the whole
 * items at or below it, "under n" at the first whole item past it, so the shown amount never looks past the level
 * while the rule is still paused. */
function guardClause(catalog: Catalog, view: View, guard: Condition, letsGo: number | null, t: number): string {
  const q = catalog.content.scales.quantity_per_item;
  const rule = chipOf(catalog, guard) || readSubject(catalog, guard) ? null : readRule(guard, q);
  const line = rule ? view.ledger.find((l) => l.store === rule.store) : undefined;
  if (!rule || !line || letsGo === null) return catalog.text.fill(UI.guardWhile, { when: guardWords(catalog, guard) ?? "" });
  const below = rule.test === "below";
  const n = below ? Math.floor(letsGo / q) + 1 : Math.floor(letsGo / q);
  const slots = { store: catalog.storeLabel(rule.store), n: catalog.format.count(n), have: catalog.format.items(sample(line.segment, t)) };
  return catalog.text.fill(below ? UI.guardUntilReaches : UI.guardUntilUnder, slots);
}
