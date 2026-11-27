// A card's needs in words, one home for the card's face (ui/cards/cardneeds.ts) and Plan's waiting rows (ui/next/stintplan.ts):
// a store's have/need, when a clock with a part of the day opens (game/condition/timewords.ts), a skill level, a step. The face
// passes its have as a mark it later fills (Format takes a have as text); Plan passes the number. Pure.
import type { Card, Condition, Need, View } from "../../api/types";
import type { Catalog } from "../page/catalog";
import { sample } from "../page/clock";
import { completionsOf } from "../ledger/cues";
import { shownLevel } from "../skills/prestige";
import { UI } from "../page/text";
import { clockWords } from "../condition/timewords";

/** How a card's face draws a store need: by its gate, as have/need (a store shown or a tally), as when it opens (a clock with a part of the day), or not at all (any other
 * store the player has never been shown). */
export type NeedKind = "gate" | "store" | "when" | "unseen";

export function needKind(catalog: Catalog, view: View, need: Need): NeedKind {
  if (need.gate !== null) return "gate";
  const store = catalog.stores.get(need.store);
  if (view.unlocked.some((u) => u.category === "store" && u.id === need.store) || store?.tally === true) return "store";
  return store?.clock ? "when" : "unseen";
}

/** A store need as have/need. */
export function storeWords(catalog: Catalog, need: Need, have: number | string): string {
  return catalog.format.need(catalog.storeTitle(need.store), have, need.quantity, need.spent);
}

/** A need on a clock with a part of the day: when the card opens. */
export function opensWords(catalog: Catalog, need: Need): string {
  return catalog.text.fill(UI.cardOpens, { when: clockWords(catalog, need.store, need.quantity) ?? "" });
}

/** A skill-level need. */
export function skillWords(catalog: Catalog, skill: string, have: number | string, level: number): string {
  return catalog.format.needSkill(catalog.skillLabel(skill), have, level);
}

/** A step need: another card's completions. */
export function stepWords(catalog: Catalog, card: string, have: number | string, count: number): string {
  return catalog.format.needStep(catalog.cardLabel(card), have, count);
}

/** The level a skill shows (1 before its bar is in view). */
export function levelOf(view: View, skill: string): number {
  const bar = view.skills.find((s) => s.skill === skill);
  return bar ? shownLevel(bar) : 1;
}

/** What `card`'s blocker waits on at view.at, as its face words that need; null when the face draws no row for it (a
 * time, a store never shown that is no clock and has no gate). */
export function waitWords(catalog: Catalog, view: View, card: Card): string | null {
  const when = card.blocker?.condition;
  return when === undefined ? null : conditionWords(catalog, view, card, when);
}

function conditionWords(catalog: Catalog, view: View, card: Card, when: Condition): string | null {
  if (when.kind !== "at_least") return null;
  const w = when.watched;
  if (w.kind === "skill_level") return skillWords(catalog, w.skill, levelOf(view, w.skill), when.value);
  if (w.kind === "card_count") return stepWords(catalog, w.card, completionsOf(view, w.card), when.value);
  const need = w.kind === "store_value" ? card.needs.find((n) => n.store === w.store) : undefined;
  if (need === undefined) return null;
  const kind = needKind(catalog, view, need);
  return kind === "gate" && need.gate !== null ? conditionWords(catalog, view, card, need.gate)
    : kind === "store" ? storeWords(catalog, need, sample(need.segment, view.at)) : kind === "when" ? opensWords(catalog, need) : null;
}
