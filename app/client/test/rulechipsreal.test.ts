// Every shipped chip and card (fixtures/real_chip_cards.json, which tests/test_rule_chip_cases_wire.py keeps equal to the
// shipped content): the simple rule view offers a chip for a card when the chip falls on a store the card makes (tired
// for rest) or rises on a store it takes (ash-laden for clearing the roofs, #277).
import { fixtureContent } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { CardInfo, ChipInfo, Content, StoreInfo } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { chipStore, whenChoices } from "../src/game/ruleoffers";
import { readFileSync } from "node:fs";

const real = JSON.parse(readFileSync("fixtures/real_chip_cards.json", "utf8")) as {
  cards: { card: string; makes: string[]; takes: string[]; wounds: string[] }[];
  chips: { chip: string; when: ChipInfo["when"] }[];
  stores: { store: string; made_by: string[] }[];
};
const card0 = fixtureContent.card_infos[0] as CardInfo;
const chip0 = fixtureContent.chip_infos[0] as ChipInfo;
const store0 = fixtureContent.store_infos[0] as StoreInfo;
const content: Content = {
  ...fixtureContent,
  card_infos: real.cards.map((c): CardInfo => ({ ...card0, card: c.card, makes: c.makes, takes: c.takes, fight: c.wounds.length === 0 ? null : { ...(card0.fight as NonNullable<CardInfo["fight"]>), wounds: c.wounds.map((store) => ({ store, quantity: 1 })) } })),
  chip_infos: real.chips.map((c): ChipInfo => ({ ...chip0, chip: c.chip, when: c.when })),
  store_infos: real.stores.map((s): StoreInfo => ({ ...store0, store: s.store, made_by: s.made_by })),
  standing_infos: [],
};
const catalog = new Catalog(content);
const view = fixtureStep("restoffer", 100).view;

const pairs: string[] = [];
const missing: string[] = [];
for (const chip of content.chip_infos) {
  const store = chipStore(chip);
  if (store === null || catalog.isLevel(store)) continue;
  for (const card of content.card_infos) {
    const answers = chip.when.kind === "at_most" ? card.makes.includes(store) : chip.when.kind === "at_least" && card.takes.includes(store);
    if (!answers) continue;
    pairs.push(`${chip.chip}/${card.card}`);
    if (!whenChoices(catalog, view, false, [card.card], null).chips.some((c) => c.chip === chip.chip)) missing.push(`${chip.chip}/${card.card}`);
  }
}
if (pairs.length === 0) throw new Error("no chip/card pair was checked");
if (missing.length > 0) throw new Error(`chip/card pairs missing from the simple view (of ${pairs.length}): ${missing.join(", ")}`);
console.log(`rulechipsreal: ${pairs.length} pairs checked: ${pairs.join(", ")}`);
