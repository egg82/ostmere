// What the condition editor offers (docs/design/opening-screen.md, "The condition editor"), read off the view and the
// content only. Its simple view offers the tasks a rule can do and, once one is chosen, what that task answers: the
// chips whose store it makes and the stores it makes. More options adds the saved mixes and every chip and store a
// rule may watch: every chip from its first showing on, every store with a line. A saved mix of one task alone is
// offered as that task, so nothing is offered twice. And the mix switch the player keeps making by hand, which gets a
// mark.
import type { ChipInfo, LedgerLine, OrderVerb, RepeatedSwitch, Subject, View } from "../api/types";
import type { Catalog } from "./catalog";
import { rulesFull, sameCondition, soloCard } from "./orders";
import { seenChips } from "./shown";
import { buildSubject, type SubjectRule } from "./subjectrule";
import { isTownMix } from "./town";

/** The stores a rule may watch: unlocked, with a ledger line, the Camp store excepted. */
export function ruleStores(view: View, campStore: string | null): LedgerLine[] {
  return view.ledger.filter((l) => l.store !== campStore && view.unlocked.some((u) => u.category === "store" && u.id === l.store));
}

/** One choice of what a rule does: a task, or a saved mix that is not one task alone. */
export type DoChoice = { kind: "task"; card: string } | { kind: "mix"; mix: string };

/** The tasks a rule may do, in the view's order: every card in play that can be done again (a one-off, a card at its
 * cap and a retired one are not), hands and other lanes alike; `keep`, the edited rule's task, stays. */
export function ruleTasks(catalog: Catalog, view: View, keep: string | null): string[] {
  return view.cards
    .filter((c) => c.card === keep || (!catalog.retired(view, c.card) && (c.cap === null || (c.cap > 1 && c.completions < c.cap))))
    .map((c) => c.card);
}

/** The task `then` comes down to: its card, or the card of a saved solo mix; null for any other mix or none. */
export function taskOf(catalog: Catalog, view: View, then: OrderVerb | null): string | null {
  if (then === null) return null;
  if (then.kind === "tap_card") return then.card;
  if (then.kind === "answer_offer" || then.kind === "answer_kind") return null;
  const mix = view.mixes.find((m) => m.id === then.mix_id);
  return mix ? soloCard(mix, catalog.content.scales.bp) : null;
}

/** What the Do row offers: the tasks, then (with More options) the saved mixes that are not a task offered. A town
 * rule (`town`) offers the town's mixes alone; any other, never a town mix (it is set by a rule on the town). */
export function doChoices(catalog: Catalog, view: View, full: boolean, then: OrderVerb | null, town = false): DoChoice[] {
  const tasks = town ? [] : ruleTasks(catalog, view, taskOf(catalog, view, then));
  const shown = new Set(tasks);
  const mixes = full || town ? view.mixes.filter((m) => isTownMix(catalog, view, m) === town && !shown.has(soloCard(m, catalog.content.scales.bp) ?? "")) : [];
  return [...tasks.map((card) => ({ kind: "task" as const, card })), ...mixes.map((m) => ({ kind: "mix" as const, mix: m.id }))];
}

/** The choice `then` is pressed as: its task (a solo mix included), else its mix. */
export function chosen(catalog: Catalog, view: View, then: OrderVerb | null): DoChoice | null {
  const card = taskOf(catalog, view, then);
  if (card !== null) return { kind: "task", card };
  return then?.kind === "switch_mix" ? { kind: "mix", mix: then.mix_id } : null;
}

/** The store a chip watches, or null. */
export function chipStore(chip: ChipInfo): string | null {
  return chip.when.kind === "after_time" || chip.when.watched.kind !== "store_value" ? null : chip.when.watched.store;
}

/** What the When row offers. Simple: with a task chosen, the chips whose store it makes and the stores with a ledger
 * line it makes; nothing before a task is chosen. Full: every chip the band has drawn in the save, whether it shows
 * now and whatever task answers it, and every store a rule may watch, with `editing`'s store last when it has no
 * ledger line. Only stores of two items or more (a band fits). */
export function whenChoices(catalog: Catalog, view: View, full: boolean, task: string | null, editing: string | null): { chips: ChipInfo[]; stores: string[] } {
  const q = catalog.content.scales.quantity_per_item;
  const makes = (store: string, cards: string[]) => (catalog.stores.get(store)?.made_by ?? []).some((c) => cards.includes(c));
  const answers = task === null ? [] : [task];
  const seen = new Set(seenChips(catalog, view));
  const chips = catalog.content.chip_infos.filter((c) => { const s = chipStore(c); return s !== null && (full ? seen.has(c.chip) : makes(s, answers)); });
  const lines = ruleStores(view, catalog.campStore).filter((l) => l.cap >= 2 * q && (full || makes(l.store, answers))).map((l) => l.store);
  return { chips, stores: editing !== null && !lines.includes(editing) ? [...lines, editing] : lines };
}

/** What the full editor's When row offers past the chips and stores, each as the rule it starts from: the Camp's level
 * and each skill's, then each task in play (a count of times done). Only what the save holds, so the list grows with
 * the story; a done card is left out, since its count no longer moves. */
export function subjectChoices(catalog: Catalog, view: View): { levels: SubjectRule[]; tasks: SubjectRule[] } {
  const camp = catalog.campStore;
  const hasCamp = camp !== null && view.ledger.some((l) => l.store === camp) && catalog.unlocked(view, "store", camp);
  const levels: SubjectRule[] = [...(hasCamp ? [{ kind: "camp" as const, n: 1 }] : []), ...view.skills.map((s) => ({ kind: "level" as const, skill: s.skill, n: 1 }))];
  const tasks: SubjectRule[] = view.cards.map((c) => ({ kind: "count" as const, card: c.card, n: 1 }));
  return { levels, tasks };
}

/** Every subject a rule may watch in the full editor (the wire's Subject union): the stores the When row offers, then
 * what subjectChoices offers. */
export function offeredSubjects(catalog: Catalog, view: View): Subject[] {
  const { levels, tasks } = subjectChoices(catalog, view);
  const stores = whenChoices(catalog, view, true, null, null).stores.map((store): Subject => ({ kind: "store_value", store }));
  return [...stores, ...[...levels, ...tasks].flatMap((rule): Subject[] => { const c = buildSubject(catalog, rule); return c.kind === "after_time" ? [] : [c.watched]; })];
}

/** The first switch the player keeps making by hand (Step.repeats.switches, CONTRACT.txt "Repeats") that is worth a mark:
 * its chip is in the content, its mix is saved and not greyed, no rule already makes it on the chip's condition, and it
 * is not yet marked once (`answered`); else null. The mark sits on the chip. */
export function hintedSwitch(catalog: Catalog, view: View, switches: readonly RepeatedSwitch[], answered: (s: RepeatedSwitch) => boolean): RepeatedSwitch | null {
  if (rulesFull(catalog, view)) return null;
  return switches.find((s) => {
    const when = catalog.chips.get(s.chip)?.when;
    return when !== undefined && !answered(s) && view.mixes.some((m) => m.id === s.mix_id) && !view.greyed_mix_ids.includes(s.mix_id)
      && !view.orders.some((o) => o.then.kind === "switch_mix" && o.then.mix_id === s.mix_id && sameCondition(o.when, when));
  }) ?? null;
}
