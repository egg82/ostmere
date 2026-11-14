// What a card waits on is on its face before a tap (ui/cardneeds.ts, game/timewords.ts; docs/decisions/principles.md,
// "Progress is stated, never hinted"): a need on a clock with a part of the day reads as when it opens until it is met,
// and a failed tap marks that row; a tally reads as have/need though it has no ledger line; a need on any other store
// the player was never shown draws no row (the countdown is all of it). A chronicle cause on such a clock reads as the
// same time of day, never as an amount.
import { install } from "./fake-dom";
import { testContext } from "./context";
import { Q, fixtureContent } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { Card, Condition, Content, Need, View } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { whenWords } from "../src/game/chronwords";
import { CardNeeds } from "../src/ui/cardneeds";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const store = (id: string, cap: number, extra: { tally?: boolean; clock?: "night" | null }) =>
  ({ store: id, label_key: `store.${id}`, cap, made_by: [], hidden: false, tally: extra.tally ?? false, clock: extra.clock ?? null, bonus_bp: null });
const content: Content = {
  ...fixtureContent,
  store_infos: [...fixtureContent.store_infos, store("night", 20 * Q, { clock: "night" }), store("arrivals", 10 * Q, { tally: true }), store("tick", 20 * Q, {})],
  text_entries: [...fixtureContent.text_entries, ...Object.entries({
    "ui.card.opens": "Opens {when}", "ui.when.night": "after dark", "ui.when.night_end": "at first light",
    "store.night": "night", "store.arrivals": "Arrivals", "store.tick": "tick",
  }).map(([key, text]) => ({ key, text }))],
};
const catalog = new Catalog(content);
const base = fixtureStep("mid", 100).view;
const need = (id: string, quantity: number, have: number): Need =>
  ({ store: id, quantity: quantity * Q, segment: { start: 0, start_value: have * Q, rate: 0, limit: null }, gate: null, makers: [], spent: false });
const atLeast = (id: string, value: number): Condition => ({ kind: "at_least", watched: { kind: "store_value", store: id }, value: value * Q, release: value * Q });

function face(needs: Need[]): CardNeeds {
  const card: Card = { ...base.cards[0]!, card: "stool", run: null, blocker: { condition: atLeast(needs[0]!.store, needs[0]!.quantity / Q), ready_at: null }, needs };
  const view: View = { ...base, cards: [card], completed: [] };
  const drawn = new CardNeeds(testContext(undefined, catalog).ctx, "stool");
  drawn.draw(card, view, false);
  drawn.tick(card, view, 100);
  return drawn;
}
const shownText = (drawn: CardNeeds): string[] =>
  Array.from(drawn.root.querySelectorAll(".card-need"), (n) => n as HTMLElement).filter((n) => !n.hidden).map((n) => n.textContent ?? "");

expect("a night not yet come reads as when it opens", shownText(face([need("night", 5, 0)])), ["Opens after dark"]);
expect("once its clock reaches the need, the row goes", shownText(face([need("night", 5, 6)])), []);
expect("a failed tap on the night marks that row", face([need("night", 5, 0)]).shows(atLeast("night", 5))?.textContent, "Opens after dark");
expect("a tally reads as have/need", shownText(face([need("arrivals", 3, 2)])), ["Arrivals 2/3"]);
expect("a store never shown and no clock draws no row", shownText(face([need("tick", 5, 0)])), []);
expect("a cause on the clock short of its cap is the part of the day", whenWords(catalog, atLeast("night", 1)), "after dark");
expect("a cause at the clock's cap is that part's end", whenWords(catalog, atLeast("night", 20)), "at first light");
