// Whether a dry store holds back the player's own work (issue 467): a card the hands' running mix holds, or one a rule
// or the queue would run (its tap, or a card of the mix it switches to), takes from the store. A town mix is the
// townsfolk's: a person stopped on it says so on their Town row (game/stuck.ts), so their need alone does not make the
// ledger's "ran dry" an alarm at the top of Tasks. Read off the view and the content's CardInfo.takes.
import type { Mix, OrderVerb, View } from "../api/types";
import type { Catalog } from "./catalog";
import { runningMix } from "./mix";
import { flatCards, isTownMix } from "./town";

/** The cards a verb would run: its tap, or the cards of the mix it switches to unless that is a town mix; an answer runs none. */
function verbCards(catalog: Catalog, view: View, verb: OrderVerb): string[] {
  if (verb.kind === "tap_card") return [verb.card];
  if (verb.kind !== "switch_mix") return [];
  const mix = view.mixes.find((m) => m.id === verb.mix_id);
  return mix && !isTownMix(catalog, view, mix) ? flatCards(view, mix) : [];
}

/** The cards the player runs or has queued: the hands' running mix, and what each rule and queue entry would run. */
export function playerWork(catalog: Catalog, view: View): Set<string> {
  const running: Mix | null = runningMix(view);
  return new Set([...(running ? flatCards(view, running) : []), ...view.orders.flatMap((o) => verbCards(catalog, view, o.then)),
    ...view.queue.flatMap((q) => verbCards(catalog, view, q.verb))]);
}

/** A card of the player's own work takes from `store`. */
export function workNeeds(catalog: Catalog, view: View, store: string): boolean {
  return [...playerWork(catalog, view)].some((card) => catalog.cards.get(card)?.takes.includes(store) === true);
}
