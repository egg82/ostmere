// The mix editor's + Add lists the cards that can join in the page's order (docs/decisions/principles.md, "Every option
// offered works as worded"): the Tasks page's sections, a section's cards by shown name. Fed the cards in reverse.
import { install } from "./fake-dom";
import { fixtureContent } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import { Catalog } from "../src/game/catalog";
import { NewMarks } from "../src/game/marks";
import { AddFold } from "../src/ui/editoradds";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const catalog = new Catalog(fixtureContent);
const base = fixtureStep("rulestab", 100).view;
const free = base.cards.filter((c) => catalog.mixable(c.card));
const reversed = { ...base, cards: [...base.cards].reverse() };
const empty = { id: "none", components: [] };

const fold = new AddFold(catalog, new NewMarks(), () => document.createElement("div"), () => undefined);
fold.draw(reversed, empty);
const offered = (fold.root as unknown as { querySelectorAll(s: string): { dataset: Record<string, string> }[] }).querySelectorAll(".add-card").map((b) => b.dataset["card"] ?? "");
const byName = (cards: string[]): string[] => [...cards].sort((a, b) => catalog.cardLabel(a).localeCompare(catalog.cardLabel(b)));
const craft = (c: string): boolean => catalog.cards.get(c)?.presentation === "craft";
const ids = free.map((c) => c.card);
expect("some cards are offered, crafts among them", [offered.length > 3, offered.some(craft), offered.some((c) => !craft(c))], [true, true, true]);
expect("the page's order: a section's cards by name, crafts after the rest", offered, [...byName(ids.filter((c) => !craft(c))), ...byName(ids.filter(craft))]);
