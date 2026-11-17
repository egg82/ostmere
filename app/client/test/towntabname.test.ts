// The town has one name everywhere (CONTRACT.txt, "The town's mix"): the rail's and the phone bar's tab, the Town view's
// title, the Rules page's switch and a game mix's label read the town's name as the view's unlocks give it (Content.
// town_later_labels, else ui.town.title), so it changes with the story in one place.
import { fakeDocument, type FakeEl, install } from "./fake-dom";
import { testContext } from "./context";
import { Catalog } from "../src/game/catalog";
import { mixLabel } from "../src/game/orders";
import { fixtureContent } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import { LaneRows } from "../src/ui/lanerows";
import { sideSwitch } from "../src/ui/ruleswitch";
import { PanelTabs } from "../src/ui/tabs";
import { TownView } from "../src/ui/townview";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const content = {
  ...fixtureContent,
  town_later_labels: [{ after: { category: "feature" as const, id: "founded" }, label_key: "ui.town.later" }],
  text_entries: [...fixtureContent.text_entries, { key: "ui.town.later", text: "Town" }],
};
const { ctx } = testContext(undefined, new Catalog(content));
const before = fixtureStep("mid", 100).view;
const after = { ...before, unlocked: [...before.unlocked, { category: "feature" as const, id: "founded" }] };
const tabs = new PanelTabs(ctx.catalog, document.createElement("button"), () => undefined);
const view = new TownView(ctx.catalog, new LaneRows(ctx), tabs.town);
document.body.replaceChildren(tabs.root, view.root);
const body = fakeDocument.body as FakeEl;

const read = (): unknown[] => [body.querySelector('[data-tab="town"]')?.textContent, body.querySelector(".town-tab .view-title")?.textContent];
const switchLabels = (v: typeof before): unknown => Array.from(sideSwitch(ctx.catalog, v, "mine", () => undefined).querySelectorAll("button"), (b) => b.textContent);
const mix = (v: typeof before): string => mixLabel(ctx.catalog, v, "town:main");

view.draw(before, false, false);
expect("before the unlock: the tab and the title", read(), ["Camp", "Camp"]);
expect("before: the Rules switch", switchLabels(before), ["Mine", "Camp"]);
expect("before: a game mix", mix(before), "Camp");
view.draw(after, false, false);
expect("after the unlock: the tab and the title", read(), ["Town", "Town"]);
expect("after: the Rules switch", switchLabels(after), ["Mine", "Town"]);
expect("after: a game mix", mix(after), "Town");
expect("a mix of the player's keeps its own name", mixLabel(ctx.catalog, after, "Evening"), "Evening");
