// A rule's simple view offers the chip a task answers, and a chip that rises answers the task that takes the store it
// watches ("clear the roofs when ash-laden", #277): read off the card's inputs and the chip's condition, not names.
import { fixtureContent, Q } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { ChipInfo, Condition } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { whenChoices } from "../src/game/ruleoffers";

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const watch = (store: string) => ({ kind: "store_value" as const, store });
const rising = (store: string): Condition => ({ kind: "at_least", watched: watch(store), value: 4 * Q, release: 2 * Q, value_of_cap: false, release_of_cap: false });
const falling = (store: string): Condition => ({ kind: "at_most", watched: watch(store), value: 1 * Q, release: 3 * Q, value_of_cap: false, release_of_cap: false });
const chip = (id: string, when: Condition): ChipInfo => ({ chip: id, label_key: `chip.${id}`, tone: "cold", when, cost_key: null, change_bp: [], on_line_key: null, off_line_key: null, offered_after: null, chore: false });

// smoke_roots takes roots and damp_wood and makes smoked; "stocked" rises with roots, "dry" falls with damp_wood.
const catalog = new Catalog({ ...fixtureContent, chip_infos: [...fixtureContent.chip_infos, chip("stocked", rising("roots")), chip("dry", falling("damp_wood")), chip("heaped", rising("smoked"))] });
const view = fixtureStep("restoffer", 100).view;
const chips = (cards: string[]) => whenChoices(catalog, view, false, cards, null).chips.map((c) => c.chip);

expect("a rising chip on a store the task takes is offered, with the chip on the store it makes", chips(["smoke_roots"]), ["stocked", "heaped"]);
expect("a falling chip on a store the task takes is not offered", chips(["smoke_roots"]).includes("dry"), false);
expect("a task that touches neither store offers neither chip", chips(["rest"]).filter((c) => c !== "tired"), []);
