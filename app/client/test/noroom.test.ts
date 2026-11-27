// A card a full pause stopped (Card.full_store; contract/full-output.txt, "FULL OUTPUT") says on its face which store has no room,
// quiet, not short; it has no blocker, so nothing else on the face says why it stopped. Any other card draws no such row.
import { install } from "./fake-dom";
import { testContext } from "./context";
import { Q, fixtureContent } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { Card, View } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { CardNeeds } from "../src/ui/cards/cardneeds";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const base = fixtureStep("mid", 100).view;
const wood = { store: "wood", quantity: 3 * Q, segment: { start: 0, start_value: 5 * Q, rate: 0, limit: null }, gate: null, makers: [], spent: false };
const gather: Card = { ...base.cards[0]!, card: "gather", blocker: null, share_bp: 5000, run: "paused", full_store: "wood", needs: [] };

function face(card: Card): { text: string; short: boolean; rootShown: boolean } {
  const view: View = { ...base, cards: [card], completed: [] };
  const needs = new CardNeeds(testContext(undefined, new Catalog(fixtureContent)).ctx, card.card);
  needs.draw(card, view, false);
  needs.tick(card, view, 100);
  const row = needs.root.querySelector<HTMLElement>(".card-need.full");
  return { text: row !== null && !row.hidden ? row.textContent ?? "" : "", short: row?.classList.contains("short") ?? false, rootShown: !needs.root.hidden };
}

expect("a full-paused card names the store with no room", face(gather), { text: "Dead wood is full", short: false, rootShown: true });
expect("beside its store needs", face({ ...gather, needs: [wood] }).text, "Dead wood is full");
expect("a dry-paused card draws no such row", face({ ...gather, full_store: null }).text, "");
expect("and a card stopped by nothing draws no face at all", face({ ...gather, full_store: null, run: null }).rootShown, false);
expect("the row goes once the pause lifts", (() => {
  const needs = new CardNeeds(testContext(undefined, new Catalog(fixtureContent)).ctx, "gather");
  needs.draw(gather, { ...base, cards: [gather], completed: [] }, false);
  const running = { ...gather, run: "full" as const, full_store: null };
  needs.draw(running, { ...base, cards: [running], completed: [] }, false);
  const row = needs.root.querySelector<HTMLElement>(".card-need.full");
  return row === null || row.hidden;
})(), true);
