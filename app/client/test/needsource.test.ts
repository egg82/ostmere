// Where a short store need comes from (ui/cardneeds.ts, ui/makerlight.ts; docs/design/opening-screen.md, "Cards"): a
// need with a gate (Need.gate) draws the gate in its place as a skill-level or step row and never names its store, even
// one the player has not been shown; with no gate it draws the store as have/need and nothing else. A tap of a short
// row lights its makers (Need.makers): Actions.highlight and their cards on the panel, until the next press, without
// tapping the card; a row not short, or with no maker, takes no tap of its own. A spent need (Need.spent) says none
// is left on its row.
import { FakeEvent, fakeDocument, install } from "./fake-dom";
import { testContext } from "./context";
import { Q, fixtureContent } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { Card, Condition, View } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { CardNeeds } from "../src/ui/cardneeds";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const base = fixtureStep("mid", 100).view;
const catalog = new Catalog(fixtureContent);
const watched = { kind: "store_value" as const, store: "stone" };
const atLevel = (level: number): Condition => ({ kind: "at_least", watched: { kind: "skill_level", skill: "foraging" }, value: level, release: level });
const atCount = (count: number): Condition => ({ kind: "at_least", watched: { kind: "card_count", card: "tend" }, value: count, release: count });

function strike(gate: Condition | null, makers: string[] = [], have = 0, spent = false): Card {
  return { ...base.cards[0]!, card: "stool", blocker: { condition: { kind: "at_least", watched, value: 1 * Q, release: 1 * Q }, ready_at: null },
    needs: [{ store: "stone", quantity: 1 * Q, segment: { start: 0, start_value: have * Q, rate: 0, limit: null }, gate, makers, spent }] };
}

function view(card: Card, level: number, shown: boolean): View {
  const unlocked = base.unlocked.filter((u) => !(u.category === "store" && u.id === "stone"));
  return { ...base, skills: base.skills.map((s) => (s.skill === "foraging" ? { ...s, level } : s)), cards: [card],
    completed: [{ card: "tend", completions: 1 }], unlocked: shown ? [...unlocked, { category: "store", id: "stone" }] : unlocked };
}

function drawn(card: Card, level = 2, shown = true): { needs: CardNeeds; got: ReturnType<typeof testContext>["got"]; row: HTMLElement } {
  const { ctx, got } = testContext(undefined, catalog);
  const needs = new CardNeeds(ctx, "stool");
  const v = view(card, level, shown);
  needs.draw(card, v, false);
  needs.tick(card, v, 100);
  return { needs, got, row: needs.root.querySelector<HTMLElement>(".card-need")! };
}

const text = (r: { row: HTMLElement }): string => (r.row.hidden ? "(hidden)" : r.row.textContent ?? "");
expect("a skill-level gate in the need's place", text(drawn(strike(atLevel(3)))), "Foraging level 2/3");
expect("the store is not named", text(drawn(strike(atLevel(3)))).includes("Flint"), false);
expect("drawn for a store never shown", text(drawn(strike(atLevel(3)), 2, false)), "Foraging level 2/3");
expect("only the level it is short of marked", drawn(strike(atLevel(3))).row.querySelector(".need-have")?.textContent, "2");
expect("a step gate: the card's completions", text(drawn(strike(atCount(2)))), "Tend the fire 1/2");
expect("no gate: the store as have/need, nothing added", text(drawn(strike(null, ["tend"]))), "Flint 0/1");
expect("spent: the store as have/need, none left", text(drawn(strike(null, [], 0, true))), "Flint 0/1, none left");
expect("spent: only the number marked", drawn(strike(null, [], 0, true)).row.querySelector(".need-have")?.textContent, "0");
expect("no gate, a store never shown: no row", text(drawn(strike(null), 2, false)), "(hidden)");
{
  const blocked = drawn(strike(atLevel(3)));
  expect("a failed tap marks the gate's row", blocked.needs.shows({ kind: "at_least", watched, value: 1 * Q, release: 1 * Q }) === blocked.row, true);
}

// A tap of a short row with makers lights them, and the card's own tap never hears it.
{
  const card = fakeDocument.createElement("div");
  card.className = "card";
  card.dataset["card"] = "tend";
  const other = fakeDocument.createElement("div");
  other.className = "card";
  other.dataset["card"] = "gather";
  fakeDocument.body.append(card, other);
  const r = drawn(strike(null, ["tend"]));
  const tapped: string[] = [];
  const button = fakeDocument.createElement("button");
  button.append(r.needs.root as never);
  button.addEventListener("click", () => tapped.push("card"));
  r.row.click();
  expect("highlight asked for the makers", r.got.lit, [["tend"]]);
  expect("the maker's card is lit, no other", [card.classList.contains("lit"), other.classList.contains("lit")], [true, false]);
  expect("the card was not tapped", tapped, []);
  fakeDocument.body.dispatchEvent(new FakeEvent("pointerdown"));
  expect("the next press clears both", [r.got.lit.at(-1), card.classList.contains("lit")], [null, false]);
  const full = drawn(strike(null, ["tend"], 1));
  button.replaceChildren(full.needs.root as never);
  full.row.click();
  expect("a row not short: the tap is the card's", [full.got.lit, tapped], [[], ["card"]]);
  const none = drawn(strike(null, []));
  button.replaceChildren(none.needs.root as never);
  none.row.click();
  expect("a short row with no maker: the tap is the card's", [none.got.lit, tapped], [[], ["card", "card"]]);
}
