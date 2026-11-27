// A condition on a clock the player is never shown, worded as a time of day (StoreInfo.clock; contract/, "Cards",
// "Line causes"): short of the clock's cap it reads as the part of the day ("after dark"), at the cap as that part's
// end ("at first light"). One home for a card's "Opens after dark" and a chronicle line's "↳ after dark". Pure.
import type { Condition, StoreInfo } from "../api/types";
import type { Catalog } from "./catalog";

export const TIME_KEYS = {
  cardOpens: "ui.card.opens", // "{when}": a card waiting on a clock, when it opens
} as const;

const WORDS: Record<NonNullable<StoreInfo["clock"]>, readonly [during: string, end: string]> = {
  dawn: ["ui.when.dawn", "ui.when.dawn_end"],
  day: ["ui.when.day", "ui.when.day_end"],
  evening: ["ui.when.evening", "ui.when.evening_end"],
  night: ["ui.when.night", "ui.when.night_end"],
};

/** When `store` reaches `value`, as a time of day; null when the store is no clock with a part of the day. */
export function clockWords(catalog: Catalog, store: string, value: number): string | null {
  const info = catalog.stores.get(store);
  if (!info?.clock) return null;
  const [during, end] = WORDS[info.clock];
  return catalog.text.get(value >= info.cap ? end : during);
}

/** A condition met on a clock, as a time of day; null for any other condition. */
export function timeWords(catalog: Catalog, when: Condition): string | null {
  if (when.kind !== "at_least" || when.watched.kind !== "store_value") return null;
  return clockWords(catalog, when.watched.store, when.value);
}
