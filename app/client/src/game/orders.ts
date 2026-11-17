// The player's rules (standing orders) as the page words and edits them. A rule is "when a store is under or at least a
// level, run a mix" on the hands, or "… do a task" on another lane: a mix is what the hands do, a rule is what waits on
// something happening (docs/decisions.md, "The mix"). Its condition is a store rule (storerule.ts) or a count or a level
// (subjectrule.ts); the page draws no other kind. A rule whose condition is a chip's is worded as the chip ("While tired"), never by its numbers. Every
// edit sends the whole list back (set_orders replaces it).
import type { ChipInfo, Condition, Decision, Mix, Order, OrderCard, OrderVerb, RuleRun, View } from "../api/types";
import type { Catalog } from "./catalog";
import { answerWords, isAlways, newRuleAt } from "./lanes";
import { LEDGER_FEATURE } from "./shown";
import { readRule, ruleUntil, ruleWhen, type StoreRule } from "./storerule";
import { readSubject, subjectWords } from "./subjectrule";
import { nextUnder, withNextAt } from "./nextrow";
import { UI } from "./text";

const same = (a: unknown, b: unknown): boolean => JSON.stringify(a) === JSON.stringify(b);

/** JSON with every object's keys sorted: equal for two values whatever order their fields were written in. */
const canon = (x: unknown): string => JSON.stringify(x, (_, v: unknown) => (v !== null && typeof v === "object" && !Array.isArray(v)
  ? Object.fromEntries(Object.entries(v).sort(([a], [b]) => (a < b ? -1 : a > b ? 1 : 0))) : v));

/** A condition with its share flags written out: one left out is false (CONTRACT.txt, "Share levels"). */
const filled = (c: Condition): Condition => (c.kind === "after_time" ? c
  : { ...c, value_of_cap: c.value_of_cap ?? false, release_of_cap: c.release_of_cap ?? false });

/** The same condition, whatever order its fields were written in. */
export function sameCondition(a: Condition, b: Condition): boolean {
  return canon(filled(a)) === canon(filled(b));
}

/** The chip whose condition `when` is exactly (same test, store and levels), if any. */
export function chipOf(catalog: Catalog, when: Condition): ChipInfo | undefined {
  return catalog.content.chip_infos.find((c) => sameCondition(c.when, when));
}

/** A rule's condition in the player's words: as its chip (ui.rule.chip) when it is a chip's, else as a subject rule
 * (a count or a level), else as a store rule; null for a condition the page does not draw. */
export function conditionWords(catalog: Catalog, when: Condition): string | null {
  const chip = chipOf(catalog, when);
  if (chip) return catalog.text.fill(UI.ruleChip, { chip: catalog.label(chip.label_key) });
  const subject = readSubject(catalog, when);
  if (subject) return subjectWords(catalog, subject);
  const rule = readRule(when, catalog.content.scales.quantity_per_item, (s) => catalog.isLevel(s));
  return rule === null ? null : ruleWhen(catalog, rule);
}

/** What the hands strip says while a rule's mix or task runs: "while {chip}" for a chip's rule, else where its store
 * rule lets go (storerule.ruleUntil); "" for a condition the page does not draw. */
export function ruleRunning(catalog: Catalog, order: Order): string {
  const chip = chipOf(catalog, order.when);
  if (chip) return catalog.text.fill(UI.handsWhileChip, { chip: catalog.label(chip.label_key) });
  const rule = storeRule(catalog, order);
  return rule === null ? "" : ruleUntil(catalog, rule);
}

/** A rule's condition as a store rule, or null for any other (a subject rule's Camp level included). */
export function storeRule(catalog: Catalog, order: Order): StoreRule | null {
  return readSubject(catalog, order.when) ? null : readRule(order.when, catalog.content.scales.quantity_per_item, (s) => catalog.isLevel(s));
}

/** The rule already set on an order card's store and test (whatever its levels, which the player may have changed,
 * and whatever it does), or -1. */
export function ruleFor(view: View, card: OrderCard): number {
  const key = (o: Pick<Order, "when">) => (o.when.kind === "after_time" || o.when.watched.kind !== "store_value" ? null : `${o.when.kind}|${o.when.watched.store}`);
  const want = key(card);
  return want === null ? -1 : view.orders.findIndex((o) => key(o) === want);
}

/** A rule's two halves in the player's words: its condition and what it runs (a mix's name or a task's label). */
export function ruleWords(catalog: Catalog, view: View, order: Order): { when: string; action: string } | null {
  const when = conditionWords(catalog, order.when);
  return when === null ? null : { when, action: actionWords(catalog, view, order.then) };
}

/** A mix as the player reads it: one the game made (Content.game_mix_ids) as the town's title, any other by its name. */
export function mixLabel(catalog: Catalog, view: View, id: string): string {
  return catalog.content.game_mix_ids.includes(id) ? catalog.townTitle(view) : id;
}

export function actionWords(catalog: Catalog, view: View, then: OrderVerb): string {
  if (then.kind === "answer_offer" || then.kind === "answer_kind") return answerWords(catalog, then);   // set by an answer or another client; the page builds none
  return then.kind === "switch_mix" ? mixLabel(catalog, view, then.mix_id) : catalog.cardLabel(then.card);
}

/** The hands' rules, in priority order: each runs a mix (and is drawn as a row of the Rules tab). */
export function mixRules(view: View): number[] {
  return view.orders.flatMap((o, i) => (o.then.kind === "switch_mix" && drawn(o) ? [i] : []));
}

/** The rules that do a task, in order: the side lanes' (a task off the hands cannot be in a mix), a ruled lane's always
 * rules among them, and those that answer an offer. */
export function taskRules(view: View): number[] {
  return view.orders.flatMap((o, i) => ((o.then.kind === "tap_card" || o.then.kind === "answer_offer" || o.then.kind === "answer_kind") && (drawn(o) || isAlways(o)) ? [i] : []));
}

/** The Rules tab has something of this game to list: a rule or a queued tap. */
function rulesListed(view: View): boolean {
  return mixRules(view).length + taskRules(view).length > 0 || view.queue.length > 0;
}

/** The Rules tab is drawn: this game has a rule or a queued tap to list, or writing rules is open for the account
 * (`ruleSeen`, Keeps.ruleSeen) and the ledger is in, so a new rule has a store to watch. A new game's first screen
 * stays without it until then. */
export function rulesTabDrawn(view: View, ruleSeen: boolean): boolean {
  return rulesListed(view) || (ruleSeen && view.unlocked.some((u) => u.category === "feature" && u.id === LEDGER_FEATURE));
}

/** A rule the page draws: its condition is on a store's amount, a count, a level or a task running. */
function drawn(order: Order): boolean {
  return order.when.kind !== "after_time" && ["store_value", "card_count", "skill_level", "running"].includes(order.when.watched.kind);
}

/** The rule whose task the hands are doing now (its first or a fallback), or -1. */
export function handsRule(view: View): number {
  const running = view.lanes.find((l) => l.lane === "hands")?.running_card ?? null;
  return running === null ? -1
    : view.orders.findIndex((o, i) => view.orders_on[i] === true && [o.then, ...o.or_else].some((a) => a.kind === "tap_card" && a.card === running));
}

/** The saved mix of this card alone at the whole share, if one exists. */
function soloMix(view: View, card: string, bp: number): Mix | undefined {
  return view.mixes.find((m) => m.components.length === 1 && same(m.components[0], { kind: "card_share", card, share_bp: bp }));
}

/** A name no saved mix has: `base`, else `base 2`, `base 3`, … (as the editor names a new mix). */
export function freeName(view: View, base: string): string {
  let name = base;
  for (let n = 2; view.mixes.some((m) => m.id === name); n++) name = `${base} ${n}`;
  return name;
}

/**
 * Accepting an order card: the orders as they stand plus one rule on the card's condition. On the hands a rule runs a
 * mix, so a hands task becomes a mix of that card alone (reused when one is saved, else saved under the card's label);
 * a task on another lane is the rule's own task (CONTRACT.txt).
 */
export function addRule(view: View, catalog: Catalog, card: OrderCard): Decision[] {
  return ruleDecisions(view, catalog, null, { when: card.when, then: card.then, unless: [], or_else: [], below_next: false });
}

/** Setting `order`, appended as the lowest priority (`index` null; on a ruled lane, just before its first always rule)
 * or in place of rule `index`. A hands task runs as the saved mix of that task alone: reused when one is saved, else
 * saved first under the task's label. */
export function ruleDecisions(view: View, catalog: Catalog, index: number | null, order: Order): Decision[] {
  const at = index === null ? newRuleAt(catalog, view, order) : null;   // a ruled lane's: before its first always rule
  if (at !== null) return [{ kind: "set_orders", orders: [...view.orders.slice(0, at), order, ...view.orders.slice(at)] }];
  const cards = [...new Set([order.then, ...order.or_else].flatMap((v) => (handsTap(catalog, v) ? [v.card] : [])))];
  const bp = catalog.content.scales.bp;
  const ids = new Map<string, string>();
  const save: Decision[] = [];
  let known = view;
  for (const card of cards) {
    const found = soloMix(known, card, bp);
    const id = found?.id ?? freeName(known, catalog.cardLabel(card));
    ids.set(card, id);
    if (found) continue;
    const mix: Mix = { id, components: [{ kind: "card_share", card, share_bp: bp }] };
    save.push({ kind: "save_mix", mix });
    known = { ...known, mixes: [...known.mixes, mix] };
  }
  const solo = (v: OrderVerb): OrderVerb => (handsTap(catalog, v) ? { kind: "switch_mix", mix_id: ids.get(v.card)! } : v);
  return [...save, setRule(view, index, { ...order, then: solo(order.then), or_else: order.or_else.map(solo) })];
}

/** A tap of a hands task: a rule runs it as its solo mix. */
export function handsTap(catalog: Catalog, v: OrderVerb): v is Extract<OrderVerb, { kind: "tap_card" }> {
  return v.kind === "tap_card" && catalog.cards.get(v.card)?.lane === "hands";
}

/** The verb a rule saves for `then`: a hands task is its saved solo mix when there is one (ruleDecisions saves one
 * otherwise). */
export function savedVerb(view: View, catalog: Catalog, then: OrderVerb): OrderVerb {
  if (then.kind !== "tap_card" || catalog.cards.get(then.card)?.lane !== "hands") return then;
  const found = soloMix(view, then.card, catalog.content.scales.bp);
  return found ? { kind: "switch_mix", mix_id: found.id } : then;
}

/** The task a saved mix is, when it holds one card at the whole share; else null. */
export function soloCard(mix: Mix, bp: number): string | null {
  const only = mix.components.length === 1 ? mix.components[0] : undefined;
  return only?.kind === "card_share" && only.share_bp === bp ? only.card : null;
}

/** The rules as they stand, less the one at `index`. Its mix stays saved. */
export function removeRule(view: View, index: number): Decision {
  return { kind: "set_orders", orders: view.orders.filter((_, i) => i !== index) };
}

/** A rule's mix slot: a hands rule's index, or the player's own mix ("Otherwise"). */
export type RuleSlot = number | "otherwise";

/** The mix a dropped or armed chip names, on `slot`: the decision that makes it so, or null when it already is. */
export function pointSlot(view: View, slot: RuleSlot, mixId: string): Decision | null {
  if (view.greyed_mix_ids.includes(mixId) || !view.mixes.some((m) => m.id === mixId)) return null;
  if (slot === "otherwise") return view.active_mix_id === mixId ? null : { kind: "switch_mix", mix_id: mixId };
  const then = view.orders[slot]?.then;
  if (!then || then.kind !== "switch_mix" || then.mix_id === mixId) return null;
  return repointRule(view, slot, mixId);
}

/** Rule `index` now runs `mixId`. */
export function repointRule(view: View, index: number, mixId: string): Decision {
  return { kind: "set_orders", orders: view.orders.map((o, i) => (i === index ? { ...o, then: { kind: "switch_mix", mix_id: mixId } } : o)) };
}

/** Rule `index` swapped with the rule before it (-1) or after it (+1) in `group` (the rules drawn together, the hands'
 * by default); the rules outside it keep their places, and Next its slot (the hands' list moves past Next by
 * nextrow.ts). Null at an end. */
export function moveRule(view: View, index: number, step: -1 | 1, group: readonly number[] = mixRules(view)): Decision | null {
  const order = group;
  const at = order.indexOf(index);
  const other = at < 0 ? undefined : order[at + step];
  const mine = view.orders[index];
  const theirs = other === undefined ? undefined : view.orders[other];
  if (other === undefined || mine === undefined || theirs === undefined) return null;
  return { kind: "set_orders", orders: withNextAt(view.orders.map((o, i) => (i === index ? theirs : i === other ? mine : o)), nextUnder(view.orders)) };
}

/** Rule `index` moved to where rule `to` stands (both indexes into view.orders, both in `group`, the hands' by default),
 * the rules of the group between shifting one place; the rules outside it keep their places. Null when nothing moves. */
export function reorderRule(view: View, index: number, to: number, group: readonly number[] = mixRules(view)): Decision | null {
  const hands = group;
  const from = hands.indexOf(index), at = hands.indexOf(to);
  if (from < 0 || at < 0 || from === at) return null;
  const moved = hands.map((i) => view.orders[i]!);
  const [mine] = moved.splice(from, 1);
  moved.splice(at, 0, mine!);
  const slot = new Map(hands.map((i, n) => [i, moved[n]!]));
  return { kind: "set_orders", orders: withNextAt(view.orders.map((o, i) => slot.get(i) ?? o), nextUnder(view.orders)) };
}

/** How many rules run this mix. */
export function rulesUsing(view: View, mixId: string): number {
  return view.orders.filter((o) => o.then.kind === "switch_mix" && o.then.mix_id === mixId).length;
}

/** Every rule that ran `from`, now running `to` (a mix renamed in the editor). */
export function repointAll(view: View, from: string, to: string): Order[] {
  return view.orders.map((o) => (o.then.kind === "switch_mix" && o.then.mix_id === from ? { ...o, then: { kind: "switch_mix", mix_id: to } } : o));
}

/** Some rule runs this mix. */
export function ruled(view: View, mixId: string): boolean {
  return view.orders.some((o) => o.then.kind === "switch_mix" && o.then.mix_id === mixId);
}

/** The rules hold Content.limits.max_orders: no more are offered. */
export function rulesFull(catalog: Catalog, view: View): boolean {
  return view.orders.length >= catalog.content.limits.max_orders;
}

/** The rules with `order` set: appended as the lowest priority (`index` null, under Next when any rule is), or in place
 * of rule `index`, on its side of Next. */
export function setRule(view: View, index: number | null, order: Order): Decision {
  return { kind: "set_orders", orders: index === null ? [...view.orders, order] : view.orders.map((o, i) => (i === index ? { ...order, below_next: o.below_next ?? false } : o)) };
}

/** Another rule (not `index`) already does exactly this. */
export function ruleExists(view: View, index: number | null, order: Order): boolean {
  return view.orders.some((o, i) => i !== index && sameCondition(o.when, order.when) && same(o.then, order.then) && same(o.unless, order.unless) && same(o.or_else, order.or_else));
}

/** A rule of the player's has been seen on and then off, the same rule in the same place: the step that brings
 * writing rules (docs/decisions.md, "The mix"). */
export function ruleLetGo(prev: View, view: View): boolean {
  return view.orders.some((o, i) => prev.orders_on[i] === true && view.orders_on[i] === false && same(prev.orders[i], o));
}

/** The save's record of what its rules did lately (Step.rule_runs) holds a let-go, seen by a page or not. A rule the game
 * removed is no let-go. */
export function ruleRunLetGo(runs: readonly RuleRun[]): boolean {
  return runs.some((r) => r.off_at !== null && r.ended === null);
}
