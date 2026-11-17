// The condition editor's rows of choices (condition.ts): Do, what a rule does (tasks, then saved mixes), and When,
// what it waits on (chips, then stores; the editor fills in the amounts). Each button carries its choice in data-card,
// data-mix, data-chip or data-store, which the editor reads to mark the one pressed.
import type { ChipInfo, Order, OrderVerb, View } from "../api/types";
import { sectioned } from "../game/cardsections";
import type { Catalog } from "../game/catalog";
import { ruleActions, ruleCondition } from "../game/guardwords";
import { actionWords, mixLabel, ruleExists } from "../game/orders";
import type { DoChoice } from "../game/ruleoffers";
import { UI } from "../game/text";
import { el, setText } from "./dom";

/** A section's heading, on a row of its own above its tiles; none for the hands. */
export const sectionHead = (heading: string): HTMLElement[] => (heading === "" ? [] : [el("span", "rules-label cond-subhead", heading)]);

/** A button per choice with its label and its choice in data-card or data-mix (a greyed mix is off), under the
 * Tasks page's section headings with the mixes last (game/cardsections.ts); `click` goes on each. */
export function choiceButtons(catalog: Catalog, view: View, choices: DoChoice[], cls: (c: DoChoice) => string, click: (c: DoChoice) => void): HTMLElement[] {
  return sectioned(catalog, choices, (c) => (c.kind === "task" ? c.card : null), view).flatMap((g) => [...sectionHead(g.heading), ...g.items.map((c) => {
    const b = el("button", cls(c), c.kind === "task" ? catalog.cardLabel(c.card) : mixLabel(catalog, view, c.mix));
    b.type = "button";
    if (c.kind === "task") b.dataset.card = c.card;
    else { b.dataset.mix = c.mix; b.disabled = view.greyed_mix_ids.includes(c.mix); }
    b.addEventListener("click", () => click(c));
    return b;
  })]);
}

/** Do: its label, then the choices (choiceButtons). */
export function doRow(catalog: Catalog, view: View, choices: DoChoice[], pick: (c: DoChoice) => void): HTMLElement[] {
  return [el("span", "rules-label", catalog.text.get(UI.ruleDo)), ...choiceButtons(catalog, view, choices, (c) => `quiet ${c.kind === "task" ? "cond-task" : "cond-mix"}`, pick)];
}

/** When: its label, the chips, then the stores (each with a slot for its amount), then `more` (the levels and tasks);
 * nothing when there is no choice. */
export function whenRow(catalog: Catalog, chips: ChipInfo[], stores: string[], onChip: (c: ChipInfo) => void, onStore: (s: string) => void, more: HTMLElement[] = []): HTMLElement[] {
  if (chips.length + stores.length + more.length === 0) return [];
  return [el("span", "rules-label", catalog.text.get(UI.ruleWhen)), ...chips.map((c) => {
    const b = el("button", "quiet cond-store cond-chip", catalog.label(c.label_key));
    b.type = "button";
    b.dataset.chip = c.chip;
    b.addEventListener("click", () => onChip(c));
    return b;
  }), ...stores.map((store) => {
    const b = el("button", "quiet cond-store");
    b.type = "button";
    b.dataset.store = store;
    b.append(el("span", "", catalog.storeTitle(store)), el("span", "cond-amount"));
    b.addEventListener("click", () => onStore(store));
    return b;
  }), ...more];
}

/** The foot: the rule as a sentence ("{condition} → {action}"; nothing before what it does is chosen; no sentence
 * given, left as it is), the note when the same rule already exists, and Save off until the rule is whole and new. */
export function footRow(catalog: Catalog, view: View, index: number | null, then: OrderVerb | null, order: Order | null, foot: { sentence: HTMLElement | null; note: HTMLElement; save: HTMLButtonElement }): void {
  const hue = then?.kind === "tap_card" ? catalog.rank(then.card) % 6 : 5;
  foot.sentence?.replaceChildren(...(then ? [el("span", "", order ? ruleCondition(catalog, order) ?? "" : ""), " → ",
    el("b", `rule-action hue-${hue}`, order ? ruleActions(catalog, view, order) : actionWords(catalog, view, then))] : []));
  const dup = order !== null && ruleExists(view, index, order);
  setText(foot.note, dup ? catalog.text.get(UI.ruleExists) : "");
  foot.save.disabled = order === null || dup;
}
