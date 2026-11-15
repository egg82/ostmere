// Why a rule is off (docs/design/opening-screen.md, "The Rules tab"): a quiet line under its row, from the view's
// order_states (CONTRACT.txt), in the ledger's grammar. A waiting store rule names what it waits for and what the store
// holds now, sampled from its ledger line as the ledger samples it; a paused rule names where its guards let go
// (game/guardwords.ts), and a rule with fallbacks that is on names the one it runs past its first.
import type { Order, RuleDry, View } from "../api/types";
import type { Catalog } from "../game/catalog";
import { sample } from "../game/clock";
import { alwaysWords } from "../game/lanes";
import { actionsOf, pausedWords } from "../game/guardwords";
import { actionWords, chipOf, conditionWords, storeRule } from "../game/orders";
import { levelWords, needsKey, readRule } from "../game/storerule";
import { UI } from "../game/text";
import { el, setText } from "./dom";

/** The words for rule `index` at time `t`, or null when it is on or there is nothing to say: a waiting chip's rule
 * (its store is never a number), or a waiting store rule whose store has no ledger line to read. */
export function whyOff(catalog: Catalog, view: View, index: number, t: number): string | null {
  const order = view.orders[index];
  const state = view.order_states[index];
  if (!order || state === undefined) return null;
  if (state === "on") return dryWords(catalog, order, view.order_dry[index]?.holding ? view.order_dry[index] : null) ?? doingWords(catalog, view, index);
  if (state === "passed_over") return catalog.text.get(order.or_else.length > 0 ? UI.rulePassedOverAll : UI.rulePassedOver);
  if (state === "paused") return pausedWords(catalog, view, index, t);
  if (state === "outranked") {
    const by = outrankedBy(catalog, view, index);
    const rule = by ? alwaysWords(catalog, by) ?? conditionWords(catalog, by.when) : null;
    return rule === null ? null : catalog.text.fill(UI.ruleOutranked, { rule });
  }
  if (chipOf(catalog, order.when)) return null;
  const rule = storeRule(catalog, order);
  const line = rule ? view.ledger.find((l) => l.store === rule.store) : undefined;
  if (!rule || !line) return null;
  const slots = { store: catalog.storeLabel(rule.store), n: levelWords(catalog, rule.n), have: catalog.format.items(sample(line.segment, t)) };
  return catalog.text.fill(needsKey(rule), slots);
}

/** What a store rule's `dry` (View.order_dry) says: it holds the hands and cannot let go (stuck), or its mix may stop
 * short (unfed); null for neither. The release is the rule's own. */
export function dryWords(catalog: Catalog, order: Order, dry: RuleDry | null): string | null {
  const rule = dry && readRule(order.when, catalog.content.scales.quantity_per_item);
  if (!dry || !rule) return null;
  const slots = { store: catalog.storeLabel(dry.store), n: levelWords(catalog, rule.m ?? rule.n) };
  return catalog.text.fill(dry.holding ? UI.ruleStuck : UI.ruleUnfed, slots);
}

/** What a rule with fallbacks that is on runs: "on now · {action}" past its first, "on now · nothing it lists can start
 * yet" for none (View.order_doing); null for its first, and for a rule with no fallback. */
function doingWords(catalog: Catalog, view: View, index: number): string | null {
  const order = view.orders[index]!;
  if (order.or_else.length === 0) return null;
  const doing = view.order_doing[index] ?? null;
  if (doing === null) return catalog.text.get(UI.ruleOnNone);
  const action = actionsOf(order)[doing];
  return doing === 0 || !action ? null : catalog.text.fill(UI.ruleOnDoing, { task: actionWords(catalog, action) });
}

/** The earlier rule that has what rule `index` would run: orders[mix_order] for a mix rule, orders[LaneBar.order] of
 * its card's lane for a rule that taps a card (CONTRACT.txt, order_states). */
function outrankedBy(catalog: Catalog, view: View, index: number): Order | undefined {
  const then = view.orders[index]?.then;
  const at = then?.kind === "tap_card" ? view.lanes.find((l) => l.lane === catalog.laneOf(then.card))?.order ?? null : view.mix_order;
  return at === null ? undefined : view.orders[at];
}

/** The quiet line under rule `index`'s row, or nothing while it is on. */
export function whyLine(catalog: Catalog, view: View, index: number, t: number): HTMLElement[] {
  const words = whyOff(catalog, view, index, t);
  if (words === null) return [];
  const line = el("div", "rule-why", words);
  line.dataset.rule = String(index);
  return [line];
}

/** Each drawn line's words at time `t`: the store's amount moves between steps. */
export function retickWhy(catalog: Catalog, view: View, root: ParentNode, t: number): void {
  for (const line of root.querySelectorAll<HTMLElement>(".rule-why")) {
    const words = whyOff(catalog, view, Number(line.dataset.rule), t);
    if (words !== null) setText(line, words);
  }
}
