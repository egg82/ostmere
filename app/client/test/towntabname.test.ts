// The town has one name everywhere (CONTRACT.txt, "The town's mix"): the rail's and the phone bar's tab and the Town
// view's title read ui.town.title, the key its heading and its mix's label read, so the name can change with the story
// in one place.
import { fakeDocument, type FakeEl, install } from "./fake-dom";
import { testContext } from "./context";
import { LaneRows } from "../src/ui/lanerows";
import { PanelTabs } from "../src/ui/tabs";
import { TownView } from "../src/ui/townview";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const { ctx } = testContext();
const title = ctx.catalog.text.get("ui.town.title");
const tabs = new PanelTabs(ctx.catalog, document.createElement("button"), () => undefined);
const view = new TownView(ctx.catalog, new LaneRows(ctx), tabs.town);
document.body.replaceChildren(tabs.root, view.root);
const body = fakeDocument.body as FakeEl;
expect("the tab", body.querySelector('[data-tab="town"]')?.textContent, title);
expect("the view's title", body.querySelector(".town-tab .view-title")?.textContent, title);
