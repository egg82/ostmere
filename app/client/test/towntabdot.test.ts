// The Town tab wears the quiet dot while any person's Change does (ui/townview.ts, ui/personpage.ts): it comes when a
// task the player has not had in front of them arrives, as a row's arrival dots it, never on the first view; it goes once
// the page of the person it is for has been opened, which keeps their tasks.
import { fakeDocument, type FakeEl, install } from "./fake-dom";
import { testContext } from "./context";
import { townStep } from "../fixtures/town";
import { fixtureContent } from "../fixtures/content";
import type { Content, View } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { LaneRows } from "../src/ui/lanerows";
import { PanelTabs } from "../src/ui/tabs";
import { TownView } from "../src/ui/townview";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const base = fixtureContent.card_infos.find((c) => c.card === "haul");
const haul = townStep("town").view.cards.find((c) => c.card === "haul");
if (!base || !haul) throw new Error("the fixture's town should carry the helper's Haul card");
const content: Content = { ...fixtureContent, card_infos: [...fixtureContent.card_infos, { ...base, card: "mend", label_key: "card.haul" }] };
const { ctx } = testContext(undefined, new Catalog(content));
const tabs = new PanelTabs(ctx.catalog, document.createElement("button"), () => undefined);
const rows = new LaneRows(ctx);
const view = new TownView(ctx.catalog, rows, tabs.town);
document.body.replaceChildren(tabs.root, view.root, rows.page.root);
const changes = (): FakeEl[] => fakeDocument.body.querySelectorAll(".person-change");
const dot = (n: FakeEl | HTMLElement): boolean => (n as FakeEl).querySelector(".new-dot") !== null;
const dots = (): [boolean[], boolean] => [changes().map(dot), dot(tabs.town)];

const town = townStep("town").view;
ctx.keeps.keepLaneTasksSeen(town.cards.map((c) => c.card));
rows.update(town);
view.draw(false, false);
expect("every task seen: no dot", dots(), [[false, false], false]);

const newTask: View = { ...town, cards: [...town.cards, { ...haul, card: "mend", share_bp: 0 }] };
rows.update(newTask);
view.draw(false, true);
expect("a new task of the helper's: their Change and the tab wear the dot", dots(), [[true, false], true]);

changes()[0]?.click();
rows.update(newTask);
view.draw(false, true);
expect("their page opened: both are clear", dots(), [[false, false], false]);
