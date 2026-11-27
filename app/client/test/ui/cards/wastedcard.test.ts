// A card working into full stores (issue 467; game/cards/wasted.ts): while it runs on a share and every store it makes sits at
// its cap, its face says the work is wasted, in a need's place, and so does the Town row of the person working it. A
// store with no ledger line is not known full; a tapped card, or one with room, says nothing.
import { install, type FakeEl } from "../../fake-dom";
import { testContext } from "../../context";
import { pageRig } from "../town/personrig";
import { fixtureContent } from "../../../fixtures/content";
import { fixtureStep } from "../../../fixtures/steps";
import { townStep } from "../../../fixtures/town";
import type { Card, Content, LedgerLine, View } from "../../../src/api/types";
import { Catalog } from "../../../src/game/page/catalog";
import { wastedOn } from "../../../src/game/cards/wasted";
import { CardNeeds } from "../../../src/ui/cards/cardneeds";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const base = fixtureStep("mid", 100).view;
const catalog = new Catalog(fixtureContent);
const gather: Card = { ...base.cards[0]!, card: "gather", run: "full", by: "mix", share_bp: 5000, blocker: null, needs: [] };
const line = (store: string, held: number, cap: number): LedgerLine =>
  ({ ...base.ledger[0]!, store, cap, segment: { start: 0, start_value: held, rate: 0, limit: null } });
const at = (ledger: LedgerLine[]): View => ({ ...base, cards: [gather], ledger });

expect("its store full: wasted on it", wastedOn(catalog, at([line("wood", 40, 40)]), gather), "wood");
expect("control: room in its store", wastedOn(catalog, at([line("wood", 39, 40)]), gather), null);
expect("no ledger line: not known full", wastedOn(catalog, at([]), gather), null);
expect("a tap is not a share's work", wastedOn(catalog, at([line("wood", 40, 40)]), { ...gather, by: "tap" }), null);

{
  const needs = new CardNeeds(testContext(undefined, catalog).ctx, "gather");
  needs.draw(gather, at([line("wood", 40, 40)]), false);
  const node = needs.root.querySelector(".card-need.wasted") as HTMLElement | null;
  expect("the face says so", [node?.hidden, node?.textContent], [false, `${catalog.storeTitle("wood")} is full`]);
}

{  // the Town row of the mason, working Hew on shares into a full store
  const town = townStep("town").view;
  const content: Content = { ...fixtureContent, card_infos: fixtureContent.card_infos.map((c) => (c.card === "hew" ? { ...c, makes: ["stone"] } : c)) };
  const full: View = { ...town, ledger: [...town.ledger.filter((l) => l.store !== "stone"), line("stone", 20, 20)] };
  const { root, settle } = pageRig(town, new Catalog(content));
  const said = (): string[] => (root.querySelectorAll(".town-person").find((r) => r.dataset.lane === "mason") as FakeEl).querySelectorAll(".wasted-line").map((n) => n.textContent ?? "");
  const plain = said();
  settle(full, []);
  const hew = new Catalog(content).cardLabel("hew");
  expect("the row says the work is wasted", [plain, said()], [[], [`${hew}: ${new Catalog(content).storeLabel("stone")} is full`]]);
}
