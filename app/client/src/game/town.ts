// The town's mix (CONTRACT.txt, "The town's mix"): once people join, the townsfolk's lanes are run by one saved mix whose
// shares are parts of one person's time. These are the page's questions about it, all read off the view: who is present,
// each person's shares and what they are doing, which mix Change opens, and the decisions that save an edit. The split
// is each person's own parts of 100%; nothing here adds shares across people or moves one between them.
import type { CardShare, Decision, Mix, Order, View } from "../api/types";
import type { Catalog } from "./catalog";
import { ALWAYS } from "./lanes";
import { MIN_SHARE_BP } from "./mix";
import { freeName, TOWN_PREFIX } from "./orders";

/** One share step in the editor: the smallest share a card can hold. */
export const TOWN_STEP_BP = MIN_SHARE_BP;
/** The share a card joins a person's time with, when that much is free. */
const JOIN_BP = 5_000;

export interface Person {
  lane: string;
  /** The person's cards that hold a share in the running town mix, as the view serves them. */
  shares: { card: string; bp: number }[];
  /** What is left of the person's time, in basis points of the scale. */
  idleBp: number;
  /** The card the person is working now, by a rule's tap or by a share; null when they idle. */
  running: string | null;
}

/** The people present: the ruled lanes, in view order, whose `joined` unlock the view holds. */
export function people(catalog: Catalog, view: View): string[] {
  return view.lanes.filter((l) => catalog.lanes.get(l.lane)?.ruled === true && catalog.unlocked(view, "joined", l.lane)).map((l) => l.lane);
}

/** A person as the strip draws them: the shares of the running town mix on their lane, the rest idle, and the card they
 * are on (a rule's tap first, else the share card the mix is running). */
export function personOf(catalog: Catalog, view: View, lane: string, stopped: Mix | null = null): Person {
  const own = view.cards.filter((c) => catalog.laneOf(c.card) === lane);
  const held = stopped === null ? own.filter((c) => c.share_bp > 0).map((c) => ({ card: c.card, bp: c.share_bp }))
    : stopped.components.flatMap((c) => (c.kind === "card_share" && catalog.laneOf(c.card) === lane ? [{ card: c.card, bp: c.share_bp }] : []));
  const sharing = own.find((c) => c.by === "mix" && c.run === "full");
  const total = held.reduce((n, s) => n + s.bp, 0);
  return { lane, shares: held, idleBp: Math.max(0, catalog.content.scales.bp - total), running: view.lanes.find((l) => l.lane === lane)?.running_card ?? sharing?.card ?? null };
}

/** The cards a mix holds with nested mixes flattened. */
function flatCards(view: View, mix: Mix, seen: Set<string> = new Set()): string[] {
  if (seen.has(mix.id)) return [];
  seen.add(mix.id);
  return mix.components.flatMap((c) => {
    if (c.kind === "card_share") return [c.card];
    const inner = view.mixes.find((m) => m.id === c.mix_id);
    return inner ? flatCards(view, inner, seen) : [];
  });
}

/** A town mix: every card it holds is on a ruled lane; holding none, its id is the game's (CONTRACT.txt). */
export function isTownMix(catalog: Catalog, view: View, mix: Mix): boolean {
  const cards = flatCards(view, mix);
  return cards.length > 0 ? cards.every((c) => catalog.ruled(c)) : mix.id.startsWith(TOWN_PREFIX);
}

/** The town's always rule: after_time 0, switching a mix. */
function townAlways(order: Order): boolean {
  return order.when.kind === "after_time" && order.when.at === 0 && order.then.kind === "switch_mix";
}

/** The rules with a new town rule set: immediately before the town's first always rule, else appended
 * (CONTRACT.txt, "The town's mix"). */
export function townNewRule(view: View, order: Order): Decision {
  const at = view.orders.findIndex(townAlways);
  return { kind: "set_orders", orders: at < 0 ? [...view.orders, order] : [...view.orders.slice(0, at), order, ...view.orders.slice(at)] };
}

/** The mix Change opens: the one running, else the one the town's first always rule not passed over points at; null
 * when there is none (a new one, under a new always rule). */
export function townMixToEdit(catalog: Catalog, view: View): Mix | null {
  const fromRule = view.orders.flatMap((o, i) => (townAlways(o) && o.then.kind === "switch_mix" && view.order_states[i] !== "passed_over" ? [o.then.mix_id] : []))[0];
  const named = view.running_town_mix_id ?? fromRule ?? null;
  const mix = view.mixes.find((m) => m.id === named);
  return mix && isTownMix(catalog, view, mix) ? mix : null;
}

/** The town's mix when it is greyed (its always rule is passed over, so nobody runs shares): the mix the town's first
 * always rule names, else null. */
export function townGreyed(catalog: Catalog, view: View): Mix | null {
  const named = view.orders.flatMap((o) => (townAlways(o) && o.then.kind === "switch_mix" ? [o.then.mix_id] : []))[0];
  const mix = view.mixes.find((m) => m.id === named);
  return mix && view.greyed_mix_ids.includes(mix.id) && isTownMix(catalog, view, mix) ? mix : null;
}

/** The card a greyed town mix holds that is gone (retired), else null. */
export function townStoppedBy(catalog: Catalog, view: View): string | null {
  const mix = townGreyed(catalog, view);
  return mix === null ? null : flatCards(view, mix).find((c) => !view.cards.some((v) => v.card === c)) ?? null;
}

/** The rules whose switch_mix names a town mix, in order: the town's, listed under its heading in the Rules tab. */
export function townRules(catalog: Catalog, view: View): number[] {
  return view.orders.flatMap((o, i) => {
    const then = o.then;
    const mix = then.kind === "switch_mix" ? view.mixes.find((m) => m.id === then.mix_id) : undefined;
    return mix && isTownMix(catalog, view, mix) ? [i] : [];
  });
}

/** The cards a person may be given as tasks: theirs, in play, with no cap (a capped card is refused in a town mix). */
export function townTasks(catalog: Catalog, view: View, lane: string): string[] {
  return view.cards.filter((c) => catalog.laneOf(c.card) === lane && c.cap === null).map((c) => c.card);
}

/** Basis points of a person's time the mix gives their cards. */
export function given(catalog: Catalog, mix: Mix, lane: string): number {
  return mix.components.reduce((n, c) => (c.kind === "card_share" && catalog.laneOf(c.card) === lane ? n + c.share_bp : n), 0);
}

/** The mix with `card` given `bp` of its person's time (a card not in the mix joins): null below one step, or above what
 * the person has free. */
export function withTownShare(catalog: Catalog, mix: Mix, card: string, bp: number): Mix | null {
  const now = mix.components.find((c): c is CardShare => c.kind === "card_share" && c.card === card)?.share_bp ?? 0;
  if (bp < TOWN_STEP_BP || given(catalog, mix, catalog.laneOf(card)) - now + bp > catalog.content.scales.bp) return null;
  const components = now > 0 ? mix.components.map((c) => (c.kind === "card_share" && c.card === card ? { ...c, share_bp: bp } : c))
    : [...mix.components, { kind: "card_share" as const, card, share_bp: bp }];
  return { ...mix, components };
}

/** A card joining a person's time: half of it, or what is free when that is less; null when under one step is free. */
export function joinTownCard(catalog: Catalog, mix: Mix, card: string): Mix | null {
  const free = catalog.content.scales.bp - given(catalog, mix, catalog.laneOf(card));
  return withTownShare(catalog, mix, card, Math.min(JOIN_BP, free));
}

export function dropTownCard(mix: Mix, card: string): Mix {
  return { ...mix, components: mix.components.filter((c) => !(c.kind === "card_share" && c.card === card)) };
}

/** Saving the town's mix: save_mix of it, and for a new mix the town's always rule pointed at it (the first such rule,
 * else a new one appended). */
export function townSaveDecisions(view: View, edited: Mix, isNew: boolean): Decision[] {
  const save: Decision = { kind: "save_mix", mix: edited };
  if (!isNew) return [save];
  const then = { kind: "switch_mix" as const, mix_id: edited.id };
  const at = view.orders.findIndex(townAlways);
  const orders = at >= 0 ? view.orders.map((o, i) => (i === at ? { ...o, then } : o)) : [...view.orders, { when: ALWAYS, then }];
  return [save, { kind: "set_orders", orders }];
}

/** A new town mix: no cards, a name no saved mix has (a name beginning "town:" is the game's). */
export function newTownMix(view: View, name: string): Mix {
  return { id: freeName(view, name), components: [] };
}
