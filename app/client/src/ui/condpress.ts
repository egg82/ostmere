// The condition editor's pressed marks (condition.ts): which Do and When buttons show chosen, and each store's amount.
import type { ChipInfo, View } from "../api/types";
import { sample } from "../game/clock";
import type { Catalog } from "../game/catalog";
import type { DoChoice } from "../game/ruleoffers";
import type { Test } from "../game/storerule";
import { setText } from "./dom";

export const sameChoice = (a: DoChoice | null, b: DoChoice): boolean => JSON.stringify(a) === JSON.stringify(b);

/** Pressed on the Do button that is `pick`; pressed on the When button that is the chip, else the store. */
export function markPressed(catalog: Catalog, view: View, does: HTMLElement, chips: HTMLElement, pick: DoChoice | null, chip: ChipInfo | undefined, rule: { store: string; test: Test }): void {
  for (const b of does.querySelectorAll<HTMLButtonElement>(".cond-task, .cond-mix")) {
    b.setAttribute("aria-pressed", String(sameChoice(pick, b.dataset.card !== undefined ? { kind: "task", card: b.dataset.card } : { kind: "mix", mix: b.dataset.mix ?? "" })));
  }
  for (const b of chips.querySelectorAll<HTMLButtonElement>(".cond-store")) {
    const line = view.ledger.find((l) => l.store === b.dataset.store);
    b.setAttribute("aria-pressed", String(b.dataset.chip !== undefined ? chip?.chip === b.dataset.chip : !chip && b.dataset.store === rule.store));
    const amount = b.querySelector(".cond-amount");
    if (amount) setText(amount, line ? catalog.format.amount(sample(line.segment, view.at), line.cap) : "");
  }
}
