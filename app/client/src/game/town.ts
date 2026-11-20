// The town's mix (CONTRACT.txt, "The town's mix"): once people join, the townsfolk's lanes are run by one saved mix whose
// shares are parts of one person's time. These are the page's questions about it, all read off the view: who is present,
// each person's shares and what they are doing, which mix Change opens, and the decisions that save an edit. The split
// is each person's own parts of 100%; nothing here adds shares across people or moves one between them.
import type { CardShare, Decision, Mix, Order, View } from "../api/types";
import type { Catalog } from "./catalog";
import { ALWAYS } from "./lanes";
import { apportion, MIN_SHARE_BP } from "./mix";
import { freeName } from "./orders";

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

/** Whether `lane` is a person who has handed their split to their group (LaneBar.own_split false). */
function unmarked(view: View, lane: string): boolean {
  return view.lanes.find((l) => l.lane === lane)?.own_split === false;
}

/** The people who run their own split, as the strip draws a row each: the people present, minus the group's members. */
export function marked(catalog: Catalog, view: View): string[] {
  return people(catalog, view).filter((lane) => !unmarked(view, lane));
}

/** A group's members: the people present whose mark is off and whose LaneInfo.group is `group`. A marked person who names
 * the group is not one (CONTRACT.txt, "GROUPS"). */
export function members(catalog: Catalog, view: View, group: string): string[] {
  return people(catalog, view).filter((lane) => unmarked(view, lane) && catalog.lanes.get(lane)?.group === group);
}

/** The groups with at least one member, in view order: a row each. */
export function groups(catalog: Catalog, view: View): string[] {
  return view.lanes.filter((l) => catalog.lanes.get(l.lane)?.pooled === true && members(catalog, view, l.lane).length > 0).map((l) => l.lane);
}

/** The person a row or page for `lane` stands for: the person themselves, or a group of one's only member; null for a group
 * of more. */
export function soloOf(catalog: Catalog, view: View, lane: string): string | null {
  if (catalog.lanes.get(lane)?.pooled !== true) return lane;
  const all = members(catalog, view, lane);
  return all.length === 1 ? all[0]! : null;
}

/** A group's free members now, as its cards serve it (Card.crew); null when it serves none. */
export function crewOf(catalog: Catalog, view: View, group: string): number | null {
  return view.cards.find((c) => catalog.laneOf(c.card) === group && c.crew !== null)?.crew ?? null;
}

/** A person as the strip draws them: the shares of the running town mix on their lane, the rest idle, and the card they
 * are on (a rule's tap first, else the share card the mix is running). A group's shares are the mix's own: each is a part
 * of each member's time, where the group card's served share is the total over its crew. */
export function personOf(catalog: Catalog, view: View, lane: string): Person {
  const own = view.cards.filter((c) => catalog.laneOf(c.card) === lane);
  const mix = catalog.lanes.get(lane)?.pooled === true ? townMixToEdit(catalog, view) : null;
  const saved = (card: string): number => mix?.components.find((c) => c.kind === "card_share" && c.card === card)?.share_bp ?? 0;
  const held = own.flatMap((c) => { const bp = mix ? saved(c.card) : c.share_bp; return bp > 0 ? [{ card: c.card, bp }] : []; });
  const sharing = own.find((c) => c.by === "mix" && c.run === "full");
  const total = held.reduce((n, s) => n + s.bp, 0);
  return { lane, shares: held, idleBp: Math.max(0, catalog.content.scales.bp - total), running: view.lanes.find((l) => l.lane === lane)?.running_card ?? sharing?.card ?? null };
}

/** The cards a mix holds with nested mixes flattened. */
export function flatCards(view: View, mix: Mix, seen: Set<string> = new Set()): string[] {
  if (seen.has(mix.id)) return [];
  seen.add(mix.id);
  return mix.components.flatMap((c) => {
    if (c.kind === "card_share") return [c.card];
    const inner = view.mixes.find((m) => m.id === c.mix_id);
    return inner ? flatCards(view, inner, seen) : [];
  });
}

/** A town mix: every card it holds is on a ruled lane; holding none, it is one the game made (CONTRACT.txt). */
export function isTownMix(catalog: Catalog, view: View, mix: Mix): boolean {
  const cards = flatCards(view, mix);
  return cards.length > 0 ? cards.every((c) => catalog.ruled(c)) : catalog.content.game_mix_ids.includes(mix.id);
}

/** The town's always rule: after_time 0, switching a mix. */
function townAlways(order: Order): boolean {
  return order.when.kind === "after_time" && order.when.at === 0 && order.then.kind === "switch_mix";
}

/** The one town mix holding everyone, which a person's edit changes: the one running, else the one the town's first always
 * rule names; null only when there is none (a new one, under a new always rule). */
export function townMixToEdit(catalog: Catalog, view: View): Mix | null {
  const fromRule = view.orders.flatMap((o) => (townAlways(o) && o.then.kind === "switch_mix" ? [o.then.mix_id] : []))[0];
  const named = view.running_town_mix_id ?? fromRule ?? null;
  const mix = view.mixes.find((m) => m.id === named);
  return mix && isTownMix(catalog, view, mix) ? mix : null;
}

/** Basis points of a person's time the mix gives their cards. */
export function given(catalog: Catalog, mix: Mix, lane: string): number {
  return mix.components.reduce((n, c) => (c.kind === "card_share" && catalog.laneOf(c.card) === lane ? n + c.share_bp : n), 0);
}

/** The mix with `card` given `bp` of its person's time (a card not in the mix joins): null below the smallest share, or above what
 * the person has free. */
export function withTownShare(catalog: Catalog, mix: Mix, card: string, bp: number): Mix | null {
  const now = mix.components.find((c): c is CardShare => c.kind === "card_share" && c.card === card)?.share_bp ?? 0;
  if (bp < MIN_SHARE_BP || given(catalog, mix, catalog.laneOf(card)) - now + bp > catalog.content.scales.bp) return null;
  const components = now > 0 ? mix.components.map((c) => (c.kind === "card_share" && c.card === card ? { ...c, share_bp: bp } : c))
    : [...mix.components, { kind: "card_share" as const, card, share_bp: bp }];
  return { ...mix, components };
}

/** A card joining a person's time: all of it when they have no other card (time left free is time idle), else half of
 * what is free, or all of it when that is less; with under the smallest share free, an equal slice from their cards, as
 * a card joins the hands' mix (game/mix.ts joinCard). */
export function joinTownCard(catalog: Catalog, mix: Mix, card: string): Mix | null {
  const lane = catalog.laneOf(card);
  const bp = catalog.content.scales.bp;
  const free = bp - given(catalog, mix, lane);
  const mine = mix.components.filter((c) => c.kind === "card_share" && catalog.laneOf(c.card) === lane);
  if (free >= MIN_SHARE_BP) return withTownShare(catalog, mix, card, mine.length === 0 ? free : Math.min(JOIN_BP, free));
  const slice = Math.floor(bp / (mine.length + 1));
  if (slice < MIN_SHARE_BP) return null;
  const rest = apportion(mine.map((c) => c.share_bp), bp - slice);
  let k = 0;
  const kept = mix.components.map((c) => (c.kind === "card_share" && catalog.laneOf(c.card) === lane ? { ...c, share_bp: rest[k++] ?? c.share_bp } : c));
  return { ...mix, components: [...kept, { kind: "card_share", card, share_bp: slice }] };
}

/** The mix with one person's cards given `shares`, in the order the mix lists them (a bar's last part may be the idle
 * rest, which no card holds). */
export function withTownShares(catalog: Catalog, mix: Mix, lane: string, shares: number[]): Mix {
  let k = 0;
  return { ...mix, components: mix.components.map((c) => (c.kind === "card_share" && catalog.laneOf(c.card) === lane ? { ...c, share_bp: shares[k++] ?? c.share_bp } : c)) };
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
  const orders = at >= 0 ? view.orders.map((o, i) => (i === at ? { ...o, then } : o)) : [...view.orders, { when: ALWAYS, then, unless: [], or_else: [], below_next: false }];
  return [save, { kind: "set_orders", orders }];
}

/** A new town mix: no cards, a name no saved mix has. */
export function newTownMix(view: View, name: string): Mix {
  return { id: freeName(view, name), components: [] };
}
