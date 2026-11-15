// What a card waits on, in the words its face draws for that need (ui/cardneeds.ts): a store's have/need, when a clock
// with a part of the day opens, a skill level or a step; a gated store need reads as its gate. Plan lists a card it cannot
// take yet with these words (ui/stintplan.ts). Pure.
import type { Card, Condition, View } from "../api/types";
import type { Catalog } from "./catalog";
import { sample } from "./clock";
import { completionsOf } from "./cues";
import { shownLevel } from "./prestige";
import { UI } from "./text";
import { clockWords } from "./timewords";

/** What `card`'s blocker waits on at view.at, as the card's face words it; null when the face draws nothing for it (a
 * time, a store never shown that is no clock and has no gate). */
export function waitWords(catalog: Catalog, view: View, card: Card): string | null {
  const when = card.blocker?.condition;
  return when === undefined ? null : conditionWords(catalog, view, card, when);
}

function conditionWords(catalog: Catalog, view: View, card: Card, when: Condition): string | null {
  if (when.kind !== "at_least") return null;
  const w = when.watched;
  if (w.kind === "skill_level") {
    const bar = view.skills.find((s) => s.skill === w.skill);
    return catalog.format.needSkill(catalog.skillLabel(w.skill), bar ? shownLevel(bar) : 1, when.value);
  }
  if (w.kind === "card_count") return catalog.format.needStep(catalog.cardLabel(w.card), completionsOf(view, w.card), when.value);
  if (w.kind !== "store_value") return null;
  const need = card.needs.find((n) => n.store === w.store);
  if (need?.gate) return conditionWords(catalog, view, card, need.gate);
  const shown = view.unlocked.some((u) => u.category === "store" && u.id === w.store) || catalog.stores.get(w.store)?.tally === true;
  if (shown && need) return catalog.format.need(catalog.storeTitle(w.store), sample(need.segment, view.at), need.quantity, need.spent);
  const opens = shown ? null : clockWords(catalog, w.store, when.value);
  return opens === null ? null : catalog.text.fill(UI.cardOpens, { when: opens });
}
