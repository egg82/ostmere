// The condition editor's draft and the pure choices it makes from one (condition.ts draws and sends).
import type { Condition, Order, OrderVerb, View } from "../api/types";
import type { Catalog } from "../game/catalog";
import { actionWords, chipOf, conditionWords, savedVerb, storeRule } from "../game/orders";
import { bounds, buildRule, clampRule, defaultRule, type StoreRule } from "../game/storerule";
import { buildSubject, readSubject, type SubjectRule } from "../game/subjectrule";
import { UI } from "../game/text";
import { isTownMix } from "../game/town";

export interface Draft {
  /** The rule being changed, or null for a new one. */
  index: number | null;
  /** What it does; null on a new rule until chosen. */
  then: OrderVerb | null;
  rule: StoreRule;
  /** The edited rule's own condition and the levels it opened at: while the draft keeps those levels, the condition
   * stays exactly as it was (a chip's still reads as the chip, and Save changes nothing). */
  opened?: { rule: StoreRule; when: Condition };
  /** The edited rule is a chip's: only what it does can change. */
  chip?: boolean;
  /** A rule on the town: it does a town mix and nothing else. */
  town?: boolean;
  /** A count, a level or a task running, in place of `rule` (whose store is then ""). */
  subject?: SubjectRule;
}

export function sameRule(a: StoreRule, b: StoreRule): boolean {
  return a.store === b.store && a.test === b.test && a.n === b.n && a.m === b.m;
}

/** The condition a draft at `rule` saves: the edited rule's own while its levels are as it opened (a chip's stays the
 * chip's, a content card's keeps its exact threshold), else built from the levels. `q`: Scales.quantity_per_item. */
export function draftWhen(rule: StoreRule, opened: Draft["opened"], q: number): Condition {
  return opened && sameRule(rule, opened.rule) ? opened.when : buildRule(rule, q);
}

/** The cap of a store in whole items, from its ledger line (caps can grow), else its StoreInfo. */
export function storeCap(catalog: Catalog, view: View | null, store: string): number {
  const q = catalog.content.scales.quantity_per_item;
  const line = view?.ledger.find((l) => l.store === store);
  return Math.floor((line?.cap ?? catalog.stores.get(store)?.cap ?? 0) / q);
}

/** The rule as Save would set it, its verb as saved (a hands task as its solo mix when one exists); null while
 * something is still to choose. `chip`: the draft's condition is a chip's exactly. */
export function draftOrder(catalog: Catalog, view: View | null, draft: Draft | null, chip: boolean): Order | null {
  if (!draft?.then || !view) return null;
  const then = savedVerb(view, catalog, draft.then);
  if ((draft.chip || chip) && draft.opened) return { when: draft.opened.when, then };
  if (draft.subject) return { when: buildSubject(catalog, draft.subject), then };
  if (bounds(draft.rule.test, storeCap(catalog, view, draft.rule.store), draft.rule.n) === null) return null;
  return { when: draftWhen(draft.rule, draft.opened, catalog.content.scales.quantity_per_item), then };
}

/** The draft rule `index` opens on: a subject rule as set; a store rule at its levels as set, a chip's as the chip, one
 * with no band with "until" at the default. Null for a rule the editor does not open. */
export function editDraft(catalog: Catalog, view: View, index: number): Draft | null {
  const order = view.orders[index];
  if (!order) return null;
  const { then } = order;
  const town = then.kind === "switch_mix" && view.mixes.some((m) => m.id === then.mix_id && isTownMix(catalog, view, m));
  const subject = readSubject(catalog, order.when);
  if (subject) return { index, then, rule: defaultRule("", "below", 0), subject, town };
  const rule = storeRule(catalog, order);
  if (!rule) return null;
  const chip = chipOf(catalog, order.when) !== undefined;
  const clamped = chip ? rule : clampRule(rule, storeCap(catalog, view, rule.store));
  const opened = sameRule(clamped, rule) ? { rule, when: order.when } : undefined;
  return { index, then, rule: clamped, opened, chip, town };
}

/** The editor's heading: a chip's rule as the chip, a rule being changed by what it runs, else "New rule". */
export function headingWords(catalog: Catalog, draft: Draft): string {
  return draft.chip && draft.opened ? conditionWords(catalog, draft.opened.when) ?? ""
    : draft.index !== null && draft.then ? catalog.text.fill(UI.ruleHeading, { mix: actionWords(catalog, draft.then) })
      : catalog.text.get(UI.ruleNew);
}
