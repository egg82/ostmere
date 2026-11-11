// The player's mixes as the page edits them: the first-mix offer, a card joining or leaving with a real share (the editor), and the
// decisions that save an edit. Shares always add up to Scales.bp and none is ever zero; whether the server takes the
// mix is still the server's call (a 422 is the answer).
import type { CardShare, Decision, Mix, View } from "../api/types";
import type { Catalog } from "./catalog";
import { repointAll, ruled } from "./orders";
import { UI } from "./text";

/** The smallest share a divider can leave a card with: a card is in the mix with a real share, or not in it. */
export const MIN_SHARE_BP = 500;

/** The mix the hands run now: a rule's while its condition holds, else the player's own (view.running_mix_id). */
export function runningMix(view: View): Mix | null {
  return view.mixes.find((m) => m.id === view.running_mix_id) ?? null;
}

export function cardShares(mix: Mix): CardShare[] {
  return mix.components.flatMap((c) => (c.kind === "card_share" ? [c] : []));
}

export function holdsCard(mix: Mix, card: string): boolean {
  return mix.components.some((c) => c.kind === "card_share" && c.card === card);
}

export function shares(mix: Mix): number[] {
  return mix.components.map((c) => c.share_bp);
}

export function withShares(mix: Mix, next: number[]): Mix {
  return { ...mix, components: mix.components.map((c, i) => ({ ...c, share_bp: next[i] ?? c.share_bp })) };
}

/** Which cards and sub-mixes, in order: two mixes of the same shape differ only in their shares. */
export function shapeOf(mix: Mix | null): string {
  return mix ? mix.components.map((c) => (c.kind === "card_share" ? `c:${c.card}` : `m:${c.mix_id}`)).join("|") : "";
}

/** `total` split over `weights` in proportion, whole numbers adding up exactly, the remainder to the first. */
export function apportion(weights: number[], total: number): number[] {
  const sum = weights.reduce((a, b) => a + b, 0);
  if (weights.length === 0) return [];
  const out = weights.map((w) => (sum > 0 ? Math.floor((w * total) / sum) : Math.floor(total / weights.length)));
  out[0] = (out[0] ?? 0) + total - out.reduce((a, b) => a + b, 0);
  return out;
}

/** A card joins with an equal slice taken from the others: two at a half and one more become three at a third. */
export function joinCard(mix: Mix, card: string, bp: number): Mix {
  const n = mix.components.length + 1;
  const mine = Math.floor(bp / n);
  const rest = apportion(shares(mix), bp - mine);
  return { ...mix, components: [...withShares(mix, rest).components, { kind: "card_share", card, share_bp: mine }] };
}

/** A component leaves; its share goes back to the others in proportion. */
export function dropComponent(mix: Mix, index: number, bp: number): Mix {
  const kept = mix.components.filter((_, i) => i !== index);
  return { ...mix, components: withShares({ ...mix, components: kept }, apportion(kept.map((c) => c.share_bp), bp)).components };
}

/** The first mix's cards, while the view offers it (CONTRACT.txt): the feature is in and no mix exists yet. */
export function firstMixOffer(view: View, catalog: Catalog): string[] | null {
  const offer = catalog.content.first_mix;
  if (view.mixes.length > 0 || !catalog.unlocked(view, "feature", offer.feature)) return null;
  const present = new Set(view.cards.map((c) => c.card));
  const ids = offer.card_ids.filter((id) => present.has(id));
  return ids.length > 0 ? ids : null;
}

/** What else names a saved mix, so deleting it would be refused: an order or queue entry, or another mix. */
export function mixNamedBy(view: View, id: string): "order" | "nested" | null {
  const names = (v: { kind: string; mix_id?: string }) => v.kind === "switch_mix" && v.mix_id === id;
  if (view.orders.some((o) => names(o.then)) || view.queue.some((q) => names(q.verb))) return "order";
  if (nested(view, id)) return "nested";
  return null;
}

function nested(view: View, id: string): boolean {
  return view.mixes.some((m) => m.id !== id && m.components.some((c) => c.kind === "sub_mix" && c.mix_id === id));
}

/** The save holds Content.limits.max_mixes mixes: no new one is offered. */
export function mixesFull(catalog: Catalog, view: View): boolean {
  return view.mixes.length >= catalog.content.limits.max_mixes;
}

/**
 * Saving an edit made from `from` (the saved mix the editor opened on): the edit under its name. A new name with
 * `asNew` false replaces `from`: the rules that ran it run the new name, and `from` is deleted after when nothing else
 * names it; with `asNew`, `from` stays. Saving never changes which mix runs: a new or another saved mix is run from
 * the Mixes list, and the player's own mix renamed stays the player's own under its new name.
 */
export function saveDecisions(view: View, edited: Mix, from: string | null, asNew: boolean): Decision[] {
  const out: Decision[] = [{ kind: "save_mix", mix: edited }];
  const renamed = !asNew && from !== null && from !== edited.id;
  if (renamed && ruled(view, from)) out.push({ kind: "set_orders", orders: repointAll(view, from, edited.id) });
  if (renamed && from === view.active_mix_id) out.push({ kind: "switch_mix", mix_id: edited.id });
  if (renamed && !nested(view, from) && !queued(view, from)) out.push({ kind: "delete_mix", mix_id: from });
  if (from === null && view.active_mix_id === null && view.mixes.length === 0) out.push({ kind: "switch_mix", mix_id: edited.id });   // the first mix ever saved runs: nothing else was running
  return out;
}

function queued(view: View, id: string): boolean {
  return view.queue.some((q) => q.verb.kind === "switch_mix" && q.verb.mix_id === id);
}
