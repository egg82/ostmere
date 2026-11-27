// A card that takes from no store says so where a cost would be (ui/cards/cardneeds.ts takesNothing; docs/decisions/principles.md):
// on its face, while it works too, and on a person's page. Read off CardInfo.takes, never a label.
import { install } from "../../fake-dom";
import { testContext } from "../../context";
import { fixtureContent } from "../../../fixtures/content";
import { townStep } from "../../../fixtures/town";
import type { Card, Content, View } from "../../../src/api/types";
import { Catalog } from "../../../src/game/page/catalog";
import { CardNeeds } from "../../../src/ui/cards/cardneeds";
import { pageRig } from "../town/personrig";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const SAYS = "Takes nothing";
const step = townStep("town");
const haul = step.view.cards.find((c) => c.card === "haul");
const info = fixtureContent.card_infos.find((c) => c.card === "haul");
if (!haul || !info) throw new Error("the fixture's town should carry the helper's Haul card");
const held: Card = haul;
const content: Content = {
  ...fixtureContent,
  card_infos: fixtureContent.card_infos.map((c) => (c.card === "haul" ? { ...c, takes: [], upside_key: "card.haul.up" } : c)),
  text_entries: [...fixtureContent.text_entries, { key: "card.haul.up", text: "water for the camp" }],
};

function face(takes: string[], run: Card["run"], upside: string | null = "card.haul.up", card: Card = held): string | undefined {
  const infos = content.card_infos.map((c) => (c.card === "haul" ? { ...c, takes, upside_key: upside } : c));
  const needs = new CardNeeds(testContext(undefined, new Catalog({ ...content, card_infos: infos })).ctx, "haul");
  const shown: Card = { ...card, run, needs: [] };
  const view: View = { ...step.view, cards: [shown] };
  needs.draw(shown, view, false);
  const line = needs.root.querySelector(".card-need.nothing");
  return line && !needs.root.hidden ? line.textContent : undefined;
}

expect("a card taking from no store says so", face([], null), SAYS);
expect("and while it works", face([], "full"), SAYS);
expect("a card with no upside drawn says nothing", face([], null, null), undefined);
expect("a card with an input does not", face(["roots"], null), undefined);
expect("nor one with a drain", face(["hurt"], null), undefined);

const { open, face: pageFace } = pageRig(step.view, new Catalog(content));
open(0);
expect("a person's task says so too", pageFace("haul").querySelector(".card-need.nothing")?.textContent, SAYS);
expect("a task with no upside has none", pageFace("chop").querySelector(".card-need.nothing") ?? null, null);
