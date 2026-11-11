// Hints (docs/design/opening-screen.md, the hands strip, "Hints"): what the page marks with a quiet dot where a rule or a
// mix could answer something, read off the view, the content and what was kept. The game decides nothing and builds
// nothing: the mark sits on the thing itself, a card, a chip or a ledger line, and the player uses the tools the lessons
// taught. The page walks the player through only the first mix, the first rule, a second mix and the cap rule
// (game/lessons.ts).
import type { RepeatedSwitch, RepeatedTap, View } from "../api/types";
import type { Catalog } from "./catalog";
import { chipCards } from "./cues";
import { FIRST_MIX, FIRST_RULE, guided, guidedRule, SECOND_MIX } from "./lessons";
import type { Keeps } from "./keeps";
import { holdsCard, mixesFull } from "./mix";
import { hintedSwitch, ruleTasks } from "./ruleoffers";

/** The cards to mark: ones the player keeps tapping by hand (`repeated`, Step.repeats.taps) that the player's own mix
 * could take: mixable, in play, can be done again, outside the mix, and not yet marked once (`answered`). Only while the
 * mix is saved and runs (not greyed). */
export function hintedCards(catalog: Catalog, view: View, answered: (card: string) => boolean, repeated: readonly RepeatedTap[]): string[] {
  const own = view.mixes.find((m) => m.id === view.active_mix_id);
  if (!own || view.greyed_mix_ids.includes(own.id)) return [];
  const tapped = new Set(repeated.map((t) => t.card));
  return ruleTasks(catalog, view, null).filter((c) => tapped.has(c) && catalog.mixable(c) && !holdsCard(own, c) && !answered(c));
}

/** The cards to mark now: while no lesson runs and the first mix's is behind (it is taught on the editor, not hinted). */
export function cardHints(catalog: Catalog, view: View, keeps: Keeps, lesson: string | null, repeated: readonly RepeatedTap[]): string[] {
  return lesson === null && !guided(FIRST_MIX, view, keeps) ? hintedCards(catalog, view, (c) => keeps.mixOffered(c), repeated) : [];
}

/** The card the second mix's lesson starts from, while it may: the first one a mark would go on, whether or not that mark
 * was touched (a dot touched before the lesson still counts), and only while a new mix can be saved. */
export function secondMixCard(catalog: Catalog, view: View, keeps: Keeps, repeated: readonly RepeatedTap[]): string | null {
  if (!guided(SECOND_MIX, view, keeps) || mixesFull(catalog, view)) return null;
  return hintedCards(catalog, view, () => false, repeated)[0] ?? null;
}

/** What a chip's mark is for: a mix switch the player keeps making under it, or a rule its card could answer. */
export interface ChipHint { chip: string; switch: RepeatedSwitch | null }

/** The chips to mark now, none during a lesson or before the first rule's is behind: the chip of a switch the player keeps
 * making by hand, and the chips of the order cards the strip would have offered (cues.chipCards). */
export function chipHints(catalog: Catalog, view: View, keeps: Keeps, lesson: string | null, switches: readonly RepeatedSwitch[], endBehind: boolean): ChipHint[] {
  if (lesson !== null || guided(FIRST_RULE, view, keeps)) return [];
  const made = hintedSwitch(catalog, view, switches, (s) => keeps.switchOffered(s));
  const cards = chipCards(catalog, view, endBehind).filter((c) => c.chip !== null && !guidedRule(view, keeps, c));
  return [...(made ? [{ chip: made.chip, switch: made }] : []), ...cards.map((c) => ({ chip: c.chip ?? "", switch: null }))];
}
