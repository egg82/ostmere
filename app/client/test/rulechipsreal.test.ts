// The shipped cards and chips (fixtures/real_chip_cards.json, which tests/test_rule_chip_cases_wire.py keeps equal to the
// shipped content): the simple rule view offers ash-laden for clearing the roofs and draughty for pegging the flaps, on
// either lane (#277). Both chips rise on a store their task takes.
import { fixtureContent } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { CardInfo, ChipInfo } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { whenChoices } from "../src/game/ruleoffers";
import { readFileSync } from "node:fs";

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const real = JSON.parse(readFileSync("fixtures/real_chip_cards.json", "utf8")) as { cards: { card: string; takes: string[] }[]; chips: { chip: string; when: ChipInfo["when"] }[] };
const base = fixtureContent.card_infos[0] as CardInfo;
const baseChip = fixtureContent.chip_infos[0] as ChipInfo;
const catalog = new Catalog({
  ...fixtureContent,
  card_infos: [...fixtureContent.card_infos, ...real.cards.map((c): CardInfo => ({ ...base, card: c.card, makes: [], takes: c.takes }))],
  chip_infos: [...fixtureContent.chip_infos, ...real.chips.map((c): ChipInfo => ({ ...baseChip, chip: c.chip, when: c.when }))],
});
const view = fixtureStep("restoffer", 100).view;
const chips = (card: string) => whenChoices(catalog, view, false, [card], null).chips.map((c) => c.chip);

expect("the shipped content has the cases", real.cards.length > 0 && real.chips.length > 0, true);
for (const card of ["clear_roofs", "n2_clear_roofs"]) expect(`${card} offers ash-laden`, chips(card), ["ash_laden"]);
for (const card of ["peg_flaps", "n1_peg_flaps"]) expect(`${card} offers draughty`, chips(card), ["draughty"]);
