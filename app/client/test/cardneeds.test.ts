// A card's needs (ui/cardneeds.ts): a step or skill level once met is not drawn (completions and levels never fall); one
// not yet met is; a store need stays, as a store can fall.
import { install } from "./fake-dom";
import { testContext } from "./context";
import { Q, fixtureContent } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { Card, View } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { CardNeeds } from "../src/ui/cardneeds";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const base = fixtureStep("mid", 100).view;
const level = base.skills.find((s) => s.skill === "foraging")?.level ?? 0;
const content = { ...fixtureContent, card_infos: fixtureContent.card_infos.map((c) => (c.card === "stool"
  ? { ...c, step_needs: [{ card: "stand", count: 2 }], skill_needs: [{ skill: "foraging", level }, { skill: "foraging", level: level + 1 }] } : c)) };
const stool: Card = { ...base.cards[0]!, card: "stool", blocker: null,
  needs: [{ store: "wood", quantity: 3 * Q, segment: { start: 0, start_value: 1 * Q, rate: 0, limit: null }, gate: null, makers: [], spent: false }] };

function rows(stand: number, card: Card = stool): Record<string, boolean[]> {
  const view: View = { ...base, cards: [card], completed: [{ card: "stand", completions: stand }] };
  const needs = new CardNeeds(testContext(undefined, new Catalog(content)).ctx, "stool");
  needs.draw(card, view, false);
  needs.tick(card, view, 100);
  const shown = (cls: string): boolean[] => Array.from(needs.root.querySelectorAll(`.card-need.${cls}`), (n) => !(n as HTMLElement).hidden);
  return { step: shown("step"), skill: shown("skill"), all: Array.from(needs.root.querySelectorAll(".card-need"), (n) => !(n as HTMLElement).hidden) };
}

expect("a step not yet met is drawn", rows(1)["step"], [true]);
expect("a step met is not", rows(2)["step"], [false]);
expect("a skill level met is not drawn, one not yet met is", rows(0)["skill"], [false, true]);
expect("the store need stays", rows(2)["all"]?.[0], true);
expect("with no store need, a step not yet met is still drawn", rows(1, { ...stool, needs: [] })["step"], [true]);
expect("and a skill level not yet met", rows(1, { ...stool, needs: [] })["skill"], [false, true]);

function shownWith(run: Card["run"]): boolean {
  const card = { ...stool, run };
  const view: View = { ...base, cards: [card], completed: [] };
  const needs = new CardNeeds(testContext(undefined, new Catalog(content)).ctx, "stool");
  needs.draw(card, view, false);
  return !needs.root.hidden;
}

expect("a card at full work draws no needs", shownWith("full"), false);
expect("a run paused for want of an input draws them", shownWith("paused"), true);
expect("a card not running draws them", shownWith(null), true);

// A drain (CardInfo.drains) waits on its store above 0: drawn as have/need though the store was never shown, unless
// the store is hidden.
function drainRow(store: string): { shown: boolean; text: string } {
  const drains = { ...content, card_infos: content.card_infos.map((c) => (c.card === "stool" ? { ...c, drains: [store] } : c)) };
  const card: Card = { ...stool, needs: [{ store, quantity: 1, segment: { start: 0, start_value: 0, rate: 0, limit: null }, gate: null, makers: [], spent: false }] };
  const view: View = { ...base, cards: [card], completed: [] };
  const needs = new CardNeeds(testContext(undefined, new Catalog(drains)).ctx, "stool");
  needs.draw(card, view, false);
  needs.tick(card, view, 100);
  const row = needs.root.querySelector<HTMLElement>(".card-need");
  return { shown: row !== null && !row.hidden, text: row?.textContent ?? "" };
}

expect("the control store is never shown", base.unlocked.some((u) => u.category === "store" && u.id === "hurt"), false);
expect("a drained store never shown draws its row", drainRow("hurt"), { shown: true, text: "Hurt 0/1" });
expect("a drained hidden store does not", drainRow("clock").shown, false);

// A reach stake (CardInfo.reach) draws its store against the next reach though the line is not in the ledger's
// view of what to show: even while the card works, none once every reach is passed or the store has no line.
function reachRow(have: number | null, run: Card["run"] = null): { shown: boolean; text: string; rootShown: boolean } {
  const reach = { ...content, card_infos: content.card_infos.map((c) => (c.card === "stool"
    ? { ...c, reach: { store: "wood", stops: [2 * Q, 5 * Q, 9 * Q] } } : c)) };
  const card: Card = { ...stool, needs: [], run };
  const line = have === null ? [] : [{ ...base.ledger[0]!, store: "wood", segment: { start: 0, start_value: have, rate: 0, limit: null } }];
  const view: View = { ...base, cards: [card], completed: [], ledger: line };
  const needs = new CardNeeds(testContext(undefined, new Catalog(reach)).ctx, "stool");
  needs.draw(card, view, false);
  needs.tick(card, view, 100);
  const row = needs.root.querySelector<HTMLElement>(".card-need.reach");
  return { shown: row !== null && !row.hidden, text: row?.textContent ?? "", rootShown: !needs.root.hidden };
}

expect("the reach row names the store and the next reach", reachRow(3 * Q), { shown: true, text: "Dead wood 3, next reach at 5", rootShown: true });
expect("the next reach moves up once one is passed", reachRow(5 * Q).text, "Dead wood 5, next reach at 9");
expect("it is drawn while the card works", reachRow(3 * Q, "full").rootShown, true);
expect("none once every reach is passed", reachRow(9 * Q).shown, false);
expect("none with no ledger line for the store", reachRow(null).shown, false);
