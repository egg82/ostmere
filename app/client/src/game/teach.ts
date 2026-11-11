// Day one's teaching cues, taught by need (decisions.md, "Taught by need"; content/team/day-one.md, V2 and V3), read
// off the view and the content only:
// - switching mixes: a build waits on a store nothing at work makes (its blocker has no ready time), and a saved mix
//   that makes it could run instead (the strip's Mixes list), or else the running mix could take its maker (Edit); the
//   switch-mix lesson's subject (game/lessons.ts);
// - what to smoke: a tap of a short need's row lights every maker in play (Need.makers, ui/cardneeds.ts), so the
//   choice between them is in view.
import type { Card, Mix, View } from "../api/types";
import type { Catalog } from "./catalog";
import { runningMix } from "./mix";

/** Where the switch cue points: the Mixes list (a saved mix makes the store) or the running mix's editor (a card in play
 * makes it). `build` is the card waiting on `store`. */
export type SwitchCue = { build: string; store: string; to: "mixes"; mix: string } | { build: string; store: string; to: "edit"; card: string };

/** The cards a mix runs, nested mixes flattened. */
function cardsOf(view: View, mix: Mix, seen = new Set<string>()): string[] {
  seen.add(mix.id);
  return mix.components.flatMap((c) => {
    if (c.kind === "card_share") return [c.card];
    const inner = view.mixes.find((m) => m.id === c.mix_id);
    return inner && !seen.has(inner.id) ? cardsOf(view, inner, seen) : [];
  });
}

/** The store a hands build waits on that will not come by itself, or null. */
function stalledBuild(catalog: Catalog, card: Card): string | null {
  const info = catalog.cards.get(card.card);
  const when = card.blocker?.condition;
  if (info?.presentation !== "craft" || info.lane !== "hands" || card.blocker?.ready_at !== null || !when) return null;
  return when.kind === "at_least" && when.watched.kind === "store_value" ? when.watched.store : null;
}

/** After the end, the first build waiting on a store nothing at work makes: where switching would answer it. A mix to switch
 * to is one the list's Run can take: not the running one, nor the player's own while a rule's mix holds the hands. */
export function switchCue(catalog: Catalog, view: View): SwitchCue | null {
  if (view.ended_at === null) return null;
  const running = runningMix(view);
  for (const card of view.cards) {
    const store = stalledBuild(catalog, card);
    if (store === null) continue;
    const makers = new Set(catalog.stores.get(store)?.made_by ?? []);
    const other = view.mixes.find((m) => m.id !== running?.id && m.id !== view.active_mix_id && !view.greyed_mix_ids.includes(m.id) && cardsOf(view, m).some((c) => makers.has(c)));
    if (other) return { build: card.card, store, to: "mixes", mix: other.id };
    const maker = running ? view.cards.find((c) => makers.has(c.card) && catalog.mixable(c.card)) : undefined;
    if (maker) return { build: card.card, store, to: "edit", card: maker.card };
  }
  return null;
}
