// A chip's cost, as a contract (api/CONTRACT.txt: "A chip with a cost_key draws that text with its word"). Written
// blind: the band draws a chip's cost_key text inside the chip as .chip-cost; a chip with no cost_key draws only its
// word; and ChipInfo.cost_key is a nullable string.
import { fakeDocument, type FakeEl, install } from "./fake-dom";
import { fixtureContent } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { ChipInfo, Step, View } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { Keeps } from "../src/game/keeps";
import { Screen } from "../src/ui/screen";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

// The API type: cost_key is string | null. Assigning each way type-checks only if the field admits both.
const costed: ChipInfo["cost_key"] = "chip.cold_cost";
const free: ChipInfo["cost_key"] = null;
expect("ChipInfo.cost_key admits a string and null", [costed, free], ["chip.cold_cost", null]);

const AT = 100;
const mid = fixtureStep("mid", AT);
const catalog = new Catalog(fixtureContent);

function mounted(root: HTMLElement): FakeEl {
  document.body.replaceChildren(root);
  const node = fakeDocument.body.firstElementChild;
  if (!node) throw new Error("nothing mounted");
  return node;
}

function drawnChips(view: View): FakeEl[] {
  const screen = new Screen(catalog, () => undefined, () => Promise.resolve(null), new Keeps());
  const top = mounted(screen.root);
  const step: Step = { ...mid, view };
  screen.show(step);
  screen.tick(AT);
  return top.querySelectorAll(".chip");
}

const chips = drawnChips({ ...mid.view, chips: ["cold", "warm"] });
const word = (key: string): string => catalog.label(key);
const chipWith = (label: string): FakeEl => {
  const found = chips.find((c) => c.textContent.includes(label));
  if (!found) throw new Error(`no chip drawn with the word ${label}`);
  return found;
};

// A cost_key: its text, as .chip-cost, inside the chip.
const cold = chipWith(word("chip.cold"));
const costs = cold.querySelectorAll(".chip-cost");
expect("cold chip: one .chip-cost inside it", costs.map((c) => c.textContent), [catalog.text.fill("chip.cold_cost", catalog.format.figures([-2000]))]);
expect("cold chip: the cost text is not empty", word("chip.cold_cost").length > 0, true);

// No cost_key: only its word.
const warm = chipWith(word("chip.warm"));
expect("warm chip: no .chip-cost", warm.querySelectorAll(".chip-cost").length, 0);
expect("warm chip: only its word", warm.textContent.trim(), word("chip.warm"));
