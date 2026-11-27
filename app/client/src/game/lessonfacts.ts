// What a lesson's `may` reads off a view (game/lessons.ts).
import type { View } from "../api/types";

const WHOLE_BP = 10000;

/** The save's town mix is as the game made it: each person's whole time on one card (api/contract/the-towns-mix.txt, "The town's mix"),
 * not split or moved to another task since. */
export function townMixAsMade(view: View): boolean {
  const mix = view.mixes.find((m) => m.id === view.running_town_mix_id);
  return mix !== undefined && mix.components.length > 0 && mix.components.every((c) => c.kind === "card_share" && c.share_bp === WHOLE_BP);
}

/** The nights the save has lived into: a night that has begun is a hidden store (a countdown) whose id is both an action
 * and a feature of view.unlocked. */
export function nightsBegun(view: View): number {
  const features = new Set(view.unlocked.filter((u) => u.category === "feature").map((u) => u.id));
  return view.unlocked.filter((u) => u.category === "action" && features.has(u.id)).length;
}
