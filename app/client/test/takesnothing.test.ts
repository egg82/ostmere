// A card that takes from no store says so where a cost would be (ui/cardneeds.ts takesNothing; docs/decisions/principles.md):
// on its face, while it works too, and on a Camp person's rows. Read off CardInfo.takes, never a label.
import { fakeDocument, type FakeEl, install } from "./fake-dom";
import { testContext } from "./context";
import { fixtureContent } from "../fixtures/content";
import { townStep } from "../fixtures/town";
import type { Card, Content, View } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { CardNeeds } from "../src/ui/cardneeds";
import { LaneRows } from "../src/ui/lanerows";

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
  card_infos: fixtureContent.card_infos.map((c) => (c.card === "haul" ? { ...c, takes: [] } : c)),
};

function face(takes: string[], drains: string[], run: Card["run"], card: Card = held): string | undefined {
  const infos = content.card_infos.map((c) => (c.card === "haul" ? { ...c, takes, drains } : c));
  const needs = new CardNeeds(testContext(undefined, new Catalog({ ...content, card_infos: infos })).ctx, "haul");
  const shown: Card = { ...card, run, needs: [] };
  const view: View = { ...step.view, cards: [shown] };
  needs.draw(shown, view, false);
  const line = needs.root.querySelector(".card-need.nothing");
  return line && !needs.root.hidden ? line.textContent : undefined;
}

expect("a card taking from no store says so", face([], [], null), SAYS);
expect("and while it works", face([], [], "full"), SAYS);
expect("a card with an input does not", face(["roots"], [], null), undefined);
expect("nor one with a drain", face(["hurt"], ["hurt"], null), undefined);

const catalog = new Catalog(content);
const { ctx } = testContext(undefined, catalog);
const rows = new LaneRows(ctx);
document.body.replaceChildren(rows.root, rows.town.root);
const editor = fakeDocument.body.children[1] as FakeEl;
rows.update(step.view);
(fakeDocument.body.firstElementChild as FakeEl).querySelector(".town-change")?.click();
const row = editor.querySelector('.town-card[data-card="haul"]') ?? editor.querySelector('.town-add[data-card="haul"]');
expect("a Camp person's task says so too", row?.querySelector(".card-need.nothing")?.textContent, SAYS);
