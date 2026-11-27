// A person's split shows its stores (issue 467; ui/town/personmix.ts, ui/mixes/storetimes.ts), as the hands' mix editor does: under the
// bar, each store the person's cards make or cost, with what it holds of its cap, its rate and where it heads. At rest the
// rate now alone; while a divider is held, now → after from a dry run of the split under the finger. A store none of
// their cards touch, whose rate holds, is not listed.
import { type FakeEl, fakeDocument, install, pointer } from "./fake-dom";
import { testContext } from "./context";
import { townStep } from "../fixtures/town";
import { fixtureContent } from "../fixtures/content";
import type { Content, Decision, StoreRow, View } from "../src/api/types";
import { Catalog } from "../src/game/page/catalog";
import { LaneRows } from "../src/ui/town/lanerows";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const R = fixtureContent.scales.rate_per_item_hour;
const content: Content = { ...fixtureContent, card_infos: fixtureContent.card_infos.map((c) => (c.card === "chop" ? { ...c, makes: ["wood"] } : c)) };
const catalog = new Catalog(content);
const town = townStep("town").view;
const row = (store: string, per: number): StoreRow => ({ store, per_hour: per * R, heading: per > 0 ? "fills" : "steady", at: per > 0 ? town.at + 3600 : null, mixed: false });
const lanes = town.lanes.map((l) => (l.lane === "helper" ? { ...l, running_card: null } : l));   // the helper on shares, so the bar can be dragged
const view: View = { ...town, lanes, store_rows: [row("wood", 60), row("stone", 10)] };
if (!view.ledger.some((l) => l.store === "wood")) throw new Error("fixture: no wood ledger line to read held / cap from");

const { ctx } = testContext(undefined, catalog);
const asked: Decision[][] = [];
ctx.actions.dryRun = (ds) => { asked.push(ds); return Promise.resolve({ ...view, store_rows: [row("wood", 120), row("stone", 10)] }); };
const rows = new LaneRows(ctx);
document.body.replaceChildren(rows.root, rows.page.root);
rows.update(view);
const root = fakeDocument.body.firstElementChild as FakeEl;
const page = fakeDocument.body.children[1] as FakeEl;
root.querySelectorAll(".town-person").find((r) => r.dataset.lane === "helper")?.querySelector(".person-change")?.click();
for (const track of page.querySelectorAll(".share-track")) track.rect = { left: 0, top: 0, width: 1000, height: 20, right: 1000, bottom: 20 };
const stores = (): FakeEl => page.querySelector(".person-stores") as FakeEl;
const lines = (): string[] => stores().querySelectorAll(".store-row, .goal-binds").map((n) => n.textContent ?? "");
const wood = catalog.storeTitle("wood");

expect("at rest: the now column alone", stores().classList.contains("at-rest"), true);
const rest = lines();
expect("at rest: the store their cards make, with held / cap and heading; not the one they don't touch", [rest.length, rest[0]?.startsWith(wood), rest[1]?.includes(" / "), rest.some((t) => t.startsWith(catalog.storeTitle("stone")))], [2, true, true, false]);

const divider = page.querySelectorAll(".share-divider")[0] as FakeEl;
divider.dispatchEvent(pointer("pointerdown", 600, 10));
divider.dispatchEvent(pointer("pointermove", 500, 10));
await new Promise((r) => setTimeout(r, 300));
expect("mid-drag a dry run of the split under the finger was asked", asked.at(-1)?.[0]?.kind, "save_mix");
expect("and the after column shows", [stores().classList.contains("at-rest"), lines()[0]], [false, `${wood}${catalog.format.perMinute(60 * R)}→${catalog.format.perMinute(120 * R)}`]);
divider.dispatchEvent(pointer("pointerup", 500, 10));
expect("let go: back to the rates now", stores().classList.contains("at-rest"), true);
