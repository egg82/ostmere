// A short need's makers, lit on a tap of its row (ui/cardneeds.ts): the ledger lines they feed or draw on
// (Actions.highlight) and their cards on the panel (each card node's data-card, cards.ts), the first scrolled into view
// if it is out of it, until the next press anywhere.
import type { Actions } from "./part";

export function lightMakers(actions: Actions, makers: readonly string[]): void {
  const cards = makers.flatMap((m) => [...document.querySelectorAll<HTMLElement>(`.card[data-card="${m}"]`)]);
  actions.highlight([...makers]);
  for (const c of cards) c.classList.add("lit");
  cards[0]?.scrollIntoView({ block: "nearest" });
  document.addEventListener("pointerdown", () => {
    actions.highlight(null);
    for (const c of cards) c.classList.remove("lit");
  }, { capture: true, once: true });
}
