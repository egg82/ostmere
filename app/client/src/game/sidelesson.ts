// The side-holder's lesson (docs/design/opening-screen/lessons.md, "Lessons"): a card that holds a side while it runs
// (CardInfo.kept) adds to that side's strength at its share of the mix, so a mix runs it beside the fight it helps. It
// starts from that card's face the first time a fight of its side is served and a card that makes the fight is in play,
// and points at the Mixes control.
import type { View } from "../api/types";
import type { Catalog } from "./catalog";
import { COMBAT } from "./fights";
import type { Lesson } from "./lessons";
import { holdsCard } from "./mix";
import { UI } from "./text";

export const SIDE_MIX = "side_mix";

/** The lesson's subject: the card that holds the side, and the fight card of that side. */
export interface SideCue {
  card: string;
  fight: string;
}

/** The first card in play that holds a side, with the first fight card of that side whose fight is served, when no saved mix
 * holds both; null while combat is off, or nothing pairs. */
export function sideCue(catalog: Catalog, view: View): SideCue | null {
  if (!catalog.unlocked(view, "feature", COMBAT)) return null;
  for (const holder of view.cards) {
    const sides = catalog.cards.get(holder.card)?.kept.flatMap((k) => (k.side === null ? [] : [k.side])) ?? [];
    if (sides.length === 0 || !catalog.mixable(holder.card)) continue;
    const fight = view.fights.find((f) => sides.includes(f.side) && f.runner !== holder.card && catalog.mixable(f.runner) && view.cards.some((c) => c.card === f.runner));
    if (fight && !view.mixes.some((m) => holdsCard(m, holder.card) && holdsCard(m, fight.runner))) return { card: holder.card, fight: fight.runner };
  }
  return null;
}

const label = (c: Catalog, id: string | undefined): string => c.cardLabel(id ?? "");

export const SIDE_LESSON: Lesson = {
  id: SIDE_MIX,
  // once the player has a mix: its Mixes control is there to point at
  may: (view) => view.mixes.length > 0,
  trigger: `[data-teach="side-mix"]`,
  steps: [
    { target: () => `[data-teach="side-mix"]`, line: (c, s) => c.text.fill(UI.lessonSideHold, { card: label(c, s["card"]), task: label(c, s["fight"]) }), ends: "read" },
    { target: () => `[data-teach="mixes"]`, line: (c, s) => c.text.fill(UI.lessonSideOpen, { card: label(c, s["card"]) }), ends: "touch" },
  ],
};
