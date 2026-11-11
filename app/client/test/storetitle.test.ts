// A store's name leads a ledger line, a mix-editor totals row, a card's need and a condition-editor store button, so
// it is capitalised there (Catalog.storeTitle); in a sentence ("Under 5 damp wood") the content's own lowercase label
// stands (Catalog.storeLabel).
import { Q, fixtureContent } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { Card, LedgerLine } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { CardNeeds } from "../src/ui/cardneeds";
import { whenRow } from "../src/ui/condrows";
import { Glow } from "../src/ui/fresh";
import { Ledger } from "../src/ui/ledger";
import { install } from "./fake-dom";
import { testContext } from "./context";
import { keepsOf, NEW_FLAT } from "./kept";

install();
function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

// the opening's own labels are lowercase; the fixture's are not
const lower = { ...fixtureContent, text_entries: fixtureContent.text_entries.map((e) => (e.key === "store.wood" ? { ...e, text: "dead wood" } : e)) };
const catalog = new Catalog(lower);
expect("the label stays as the content has it", catalog.storeLabel("wood"), "dead wood");
expect("the title leads with a capital", catalog.storeTitle("wood"), "Dead wood");
expect("an unknown store has no title", catalog.storeTitle("nothing"), "");

const mid = fixtureStep("mid", 100).view;
const wood = mid.ledger.find((l) => l.store === "wood");
if (!wood) throw new Error("the mid view should carry a wood line");
const red: LedgerLine = { ...wood, falling: true, covered: false, net_per_hour: -1 };
const { ctx } = testContext(new Glow(), catalog);
const part = new Ledger({ ...ctx, keeps: keepsOf(NEW_FLAT) });
part.update({ ...mid, ledger: [red, ...mid.ledger.filter((l) => l.store === "camp")] }, null);
expect("the ledger line's name", Array.from(part.root.querySelectorAll(".line-name"), (n) => n.textContent), ["Dead wood"]);

const stool: Card = { ...mid.cards[0]!, card: "stool", blocker: null,
  needs: [{ store: "wood", quantity: 3 * Q, segment: { start: 0, start_value: 1 * Q, rate: 0, limit: null }, gate: null, makers: [], spent: false }] };
const needs = new CardNeeds(ctx, "stool");
needs.draw(stool, { ...mid, cards: [stool] }, false);
needs.tick(stool, { ...mid, cards: [stool] }, 100);
expect("a card's need", needs.root.querySelector(".card-need")?.textContent, "Dead wood 1/3");

const when = whenRow(catalog, [], ["wood"], () => {}, () => {});
expect("the condition editor's store button", when.filter((b) => b.dataset.store === "wood").map((b) => b.querySelector("span")?.textContent), ["Dead wood"]);
