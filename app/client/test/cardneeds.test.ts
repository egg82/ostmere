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
