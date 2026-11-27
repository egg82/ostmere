// The sections a card sits under, on the Tasks page (ui/cards/cardgroups.ts) and in every list of cards a rule editor offers:
// one per lane, the hands first, a lane's crafts in a section under its other cards.
import type { View } from "../../api/types";
import type { Catalog } from "../page/catalog";
import { UI } from "../page/text";

/** The section of `card`: its lane, with ":craft" after it for a craft. */
export function sectionKey(catalog: Catalog, card: string): string {
  return `${catalog.laneOf(card)}${catalog.cards.get(card)?.presentation === "craft" ? ":craft" : ""}`;
}

/** The section's heading as the Tasks page shows it; empty for the hands. A lane's label is the one `view` has (its
 * person's name once the game has said it); without a view, the lane's first. */
export function sectionHeading(catalog: Catalog, key: string, view?: View): string {
  const [lane = "hands", craft] = key.split(":");
  return craft ? catalog.text.get(UI.craftHeading) : lane === "hands" ? "" : catalog.laneLabel(lane, view);
}

/** Section keys in the page's order: lanes in content order from the hands, a lane's crafts after its other cards. */
export function compareSections(catalog: Catalog): (a: string, b: string) => number {
  const lanes = ["hands", ...catalog.lanes.keys()];
  return (a, b) => {
    const [la = "", ca] = a.split(":");
    const [lb = "", cb] = b.split(":");
    return (lanes.indexOf(la) - lanes.indexOf(lb)) || Number(Boolean(ca)) - Number(Boolean(cb));
  };
}

/** `items` as the sections a picker lists them under: the cards (`cardOf` names an item's card) by section in the
 * page's order, each section's by shown name; then, as a last group under the Mixes heading, the items with no card. */
export function sectioned<T>(catalog: Catalog, items: readonly T[], cardOf: (item: T) => string | null, view?: View): { heading: string; items: T[] }[] {
  const byKey = new Map<string, T[]>();
  const rest: T[] = [];
  for (const item of items) {
    const card = cardOf(item);
    if (card === null) { rest.push(item); continue; }
    const key = sectionKey(catalog, card);
    byKey.set(key, [...(byKey.get(key) ?? []), item]);
  }
  const label = (item: T): string => catalog.cardLabel(cardOf(item) ?? "");
  const groups = [...byKey.keys()].sort(compareSections(catalog)).map((key) => ({
    heading: sectionHeading(catalog, key, view),
    items: (byKey.get(key) ?? []).sort((a, b) => label(a).localeCompare(label(b))),
  }));
  return rest.length > 0 ? [...groups, { heading: catalog.text.get(UI.mixesHeading), items: rest }] : groups;
}

/** `items` flattened from `sectioned`: the order a picker lists them in. */
export const inSectionOrder = <T>(catalog: Catalog, items: readonly T[], cardOf: (item: T) => string | null): T[] =>
  sectioned(catalog, items, cardOf).flatMap((g) => g.items);
