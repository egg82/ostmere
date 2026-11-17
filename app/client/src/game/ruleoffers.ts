// What the condition editor offers (docs/design/opening-screen.md, "The condition editor"), read off the view and the
// content only. Its simple view offers the tasks a rule can do and, once one is chosen, what that task answers: the
// chips whose store it makes and the stores relevant to it (game/relevant.ts). More options adds the saved mixes and
// every chip and store a rule may watch, the relevant stores first: every chip from its first showing on, every store
// with a line. A saved mix of one task alone is offered as that task, so nothing is offered twice. And the mix switch
// the player keeps making by hand, which gets a mark.
import type { ChipInfo, LedgerLine, OrderVerb, RepeatedSwitch, Subject, View } from "../api/types";
import type { Catalog } from "./catalog";
import { inSectionOrder } from "./cardsections";
import { rulesFull, sameCondition, soloCard } from "./orders";
import { sample } from "./clock";
import { seenChips } from "./shown";
import { buildSubject, type SubjectRule } from "./subjectrule";
import { relevantStores, type Relevant } from "./relevant";
import type { RuleSide } from "./ruleside";
import { flatCards, isTownMix } from "./town";

/** The stores a rule may watch: unlocked, with a ledger line, the Camp store excepted. */
export function ruleStores(view: View, campStore: string | null): LedgerLine[] {
  return view.ledger.filter((l) => l.store !== campStore && view.unlocked.some((u) => u.category === "store" && u.id === l.store));
}

/** The stores a lost fight adds to (Catalog.isLevel) whose chip the band has drawn, with room for a band: they have no
 * ledger line and are never unlocked as stores, so their chip is the way in. */
function levelStores(catalog: Catalog, view: View): string[] {
  const q = catalog.content.scales.quantity_per_item;
  const drawn = seenChips(catalog, view).flatMap((id) => { const info = catalog.chips.get(id); return info ? [chipStore(info)] : []; });
  return [...new Set(drawn)].filter((s): s is string => s !== null && catalog.isLevel(s) && (catalog.stores.get(s)?.cap ?? 0) >= 2 * q);
}

/** A store's level in items at the view's time: the ledger line's, or for a level its served one in whole items rounded
 * up (View.levels); null with neither. */
export function storeItems(catalog: Catalog, view: View, store: string): number | null {
  const q = catalog.content.scales.quantity_per_item;
  const line = view.ledger.find((l) => l.store === store);
  if (line) return sample(line.segment, view.at) / q;
  const level = catalog.isLevel(store) ? view.levels.find((l) => l.store === store) : undefined;
  return level ? Math.ceil(sample(level.segment, view.at) / q) : null;
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

/** The cards `then` runs: its task's card, or every card of its mix, nested mixes flattened; none for any other verb. */
export function ruleCards(view: View, then: OrderVerb | null): string[] {
  if (then?.kind === "tap_card") return [then.card];
  const mix = then?.kind === "switch_mix" ? view.mixes.find((m) => m.id === then.mix_id) : undefined;
  return mix ? flatCards(view, mix) : [];
}

/** What the Do row offers: the tasks in the Tasks page's sections, each by name (game/cardsections.ts), then (with
 * More options) the saved mixes that are not a task offered. A town
 * rule (`town`) offers the town's mixes alone; any other, never a town mix (it is set by a rule on the town). A new rule
 * made on one side of the Rules page (`scope`) offers that side's tasks alone (one person's, given their `lane`), and on Camp no
 * saved mix (they are the hands'). */
export function doChoices(catalog: Catalog, view: View, full: boolean, then: OrderVerb | null, town = false, scope?: RuleSide, lane?: string): DoChoice[] {
  const keep = taskOf(catalog, view, then);
  const tasks = town ? [] : ruleTasks(catalog, view, keep).filter((c) => scope === undefined || c === keep || (catalog.ruled(c) === (scope === "camp") && (lane === undefined || catalog.laneOf(c) === lane)));
  const shown = new Set(tasks);
  const mixes = (full || town) && (scope !== "camp" || town) ? view.mixes.filter((m) => isTownMix(catalog, view, m) === town && !shown.has(soloCard(m, catalog.content.scales.bp) ?? "")) : [];
  const all = [...tasks.map((card) => ({ kind: "task" as const, card })), ...mixes.map((m) => ({ kind: "mix" as const, mix: m.id }))];
  return inSectionOrder(catalog, all, (c) => (c.kind === "task" ? c.card : null));
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

/** What the When row offers for a rule doing `cards` (ruleCards). Simple: the chips on a store they make, or rising on a store they take, and the
 * stores relevant to them (game/relevant.ts), in its order; nothing before a task is chosen. Full: every chip the band
 * has drawn in the save, whether it shows now and whatever task answers it, and every store a rule may watch, the
 * relevant ones first, with `editing`'s store last when it has no ledger line. Only stores with a ledger line of two
 * items or more (a band fits). A store a fight wounds (Catalog.isLevel) is offered as the store alone, never as its chip:
 * a chip's rule carries no level. `relevant` is the tiers the stores came from. */
export function whenChoices(catalog: Catalog, view: View, full: boolean, cards: readonly string[], editing: string | null): { chips: ChipInfo[]; stores: string[]; relevant: Relevant } {
  const q = catalog.content.scales.quantity_per_item;
  const makes = (store: string) => (catalog.stores.get(store)?.made_by ?? []).some((c) => cards.includes(c));
  const takes = (store: string) => cards.some((c) => catalog.cards.get(c)?.takes.includes(store));
  const seen = new Set(seenChips(catalog, view));
  const lines = [...ruleStores(view, catalog.campStore).filter((l) => l.cap >= 2 * q).map((l) => l.store), ...levelStores(catalog, view)];
  const relevant = relevantStores(catalog, cards, view.cards.map((c) => c.card), lines);
  const answers = (c: ChipInfo, s: string) => makes(s) || (c.when.kind === "at_least" && takes(s));
  const chips = catalog.content.chip_infos.filter((c) => { const s = chipStore(c); return s !== null && !catalog.isLevel(s) && (full ? seen.has(c.chip) : answers(c, s)); });
  const first = [...relevant.makes, ...relevant.takes, ...relevant.near];
  const offered = full ? [...first, ...lines.filter((s) => !first.includes(s))] : first;
  return { chips, stores: editing !== null && !offered.includes(editing) ? [...offered, editing] : offered, relevant };
}

/** What the full editor's When row offers past the chips and stores, each as the rule it starts from: the Camp's level
 * and each skill's, then each task in play (a count of times done). Only what the save holds, so the list grows with
 * the story; a done card is left out, since its count no longer moves. */
/** The levels and tasks a rule may watch; and, for a rule whose every action (`actions`: its verb and fallbacks) taps a
 * card of one person's lane, the cards of every other lane, the hands' included, it may watch running: the one Running
 * shape set_orders takes (CONTRACT.txt, "Decisions"). */
export function subjectChoices(catalog: Catalog, view: View, actions: readonly (OrderVerb | null)[] = []): { levels: SubjectRule[]; tasks: SubjectRule[]; running: SubjectRule[] } {
  const camp = catalog.campStore;
  const hasCamp = camp !== null && view.ledger.some((l) => l.store === camp) && catalog.unlocked(view, "store", camp);
  const levels: SubjectRule[] = [...(hasCamp ? [{ kind: "camp" as const, n: 1 }] : []), ...view.skills.map((s) => ({ kind: "level" as const, skill: s.skill, n: 1 }))];
  const tasks = inSectionOrder(catalog, view.cards.map((c) => c.card), (c) => c).map((card): SubjectRule => ({ kind: "count", card, n: 1 }));
  const lanes = new Set(actions.map((a) => (a?.kind === "tap_card" ? catalog.laneOf(a.card) : "hands")));
  const lane = lanes.size === 1 ? [...lanes][0]! : "hands";
  const running = lane === "hands" ? [] : inSectionOrder(catalog, view.cards.map((c) => c.card).filter((c) => catalog.laneOf(c) !== lane), (c) => c)
    .map((card): SubjectRule => ({ kind: "running", card, n: 1 }));
  return { levels, tasks, running };
}

/** Every subject a rule may watch in the full editor (the wire's Subject union): the stores the When row offers, then
 * what subjectChoices offers. */
export function offeredSubjects(catalog: Catalog, view: View): Subject[] {
  const { levels, tasks } = subjectChoices(catalog, view);
  const stores = whenChoices(catalog, view, true, [], null).stores.map((store): Subject => ({ kind: "store_value", store }));
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
