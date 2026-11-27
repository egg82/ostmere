// A lane run by rules shows its stores in the task editor (issue 483; ui/laneedit.ts, ui/storetimes.ts), as a person's
// split does: under the tasks, each store the chosen task makes or costs with what it holds of its cap, its rate and
// where it heads; the lane's tasks' stores until one is chosen. A store the task does not touch, whose rate holds, is
// not listed.
import { fakeDocument, type FakeEl, install } from "./fake-dom";
import { testContext } from "./context";
import { fixtureContent } from "../fixtures/content";
import { dayTwoStep } from "../fixtures/daytwo";
import type { Content, StoreRow, View } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { RulesTab } from "../src/ui/rules/rules";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const R = fixtureContent.scales.rate_per_item_hour;
const content: Content = { ...fixtureContent, card_infos: fixtureContent.card_infos.map((c) => (c.card === "chop" ? { ...c, makes: ["wood"] } : c.card === "haul" ? { ...c, makes: ["stone"] } : c)) };
const catalog = new Catalog(content);
const ruled = dayTwoStep("ruled", 100).view;
const row = (store: string, per: number): StoreRow => ({ store, per_hour: per * R, heading: per > 0 ? "fills" : "steady", at: per > 0 ? ruled.at + 3600 : null, mixed: false });
const view: View = { ...ruled, store_rows: [row("wood", 60), row("stone", 10)] };
if (!view.ledger.some((l) => l.store === "wood")) throw new Error("fixture: no wood ledger line to read held / cap from");

const { ctx } = testContext(undefined, catalog);
const tab = new RulesTab(ctx);
document.body.replaceChildren(tab.root);
const root = fakeDocument.body.firstElementChild as FakeEl;
const chop = view.orders.findIndex((o) => o.then.kind === "tap_card" && o.then.card === "chop");
tab.open(view, { lane: "helper", rule: chop });
const lines = (): string[] => root.querySelector(".person-stores")?.querySelectorAll(".store-row, .goal-binds").map((n) => n.textContent ?? "") ?? [];
const wood = catalog.storeTitle("wood");

const shown = lines();
expect("the chosen task's store, with held / cap and heading; not the one it doesn't touch", [shown.length, shown[0], shown[1]?.includes(" / "), shown.some((t) => t.startsWith(catalog.storeTitle("stone")))],
  [2, `${wood}${catalog.format.perMinute(60 * R)}→${catalog.format.perMinute(60 * R)}`, true, false]);

root.querySelectorAll(".card").find((c) => c.dataset.card === "haul")?.querySelector(".card-tap")?.click();
expect("choosing another task follows it to its store", lines().some((t) => t.startsWith(catalog.storeTitle("stone"))) && !lines().some((t) => t.startsWith(wood)), true);
