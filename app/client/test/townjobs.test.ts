// Every job a person can be given shows what it does where it is chosen (docs/decisions/principles.md, "Progress is stated,
// never hinted"): in the town editor's Add row each offered card carries its upside, as its card face does on the Tasks page,
// including a job the player never holds as a card of their own (a card of a person's lane).
import { fakeDocument, type FakeEl, install } from "./fake-dom";
import { testContext } from "./context";
import { townStep } from "../fixtures/town";
import { fixtureContent } from "../fixtures/content";
import type { Content, View } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { people, townTasks } from "../src/game/town";
import { LaneRows } from "../src/ui/lanerows";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const MEND = "mend";
const base = fixtureContent.card_infos.find((c) => c.card === "haul");
const haul = townStep("town").view.cards.find((c) => c.card === "haul");
if (!base || !haul) throw new Error("the fixture's town should carry the helper's Haul card");
const content: Content = {
  ...fixtureContent,
  card_infos: [...fixtureContent.card_infos, { ...base, card: MEND, label_key: "card.mend", upside_key: "card.mend.up" }],
  text_entries: [...fixtureContent.text_entries, { key: "card.mend", text: "Mend gear" }, { key: "card.mend.up", text: "gear lasts longer" }],
};
const catalog = new Catalog(content);
const view: View = { ...townStep("town").view, cards: [...townStep("town").view.cards, { ...haul, card: MEND, share_bp: 0 }] };

const { ctx } = testContext(undefined, catalog);
const rows = new LaneRows(ctx);
document.body.replaceChildren(rows.root, rows.town.root);
const editor = fakeDocument.body.children[1] as FakeEl;
rows.update(view);
(fakeDocument.body.firstElementChild as FakeEl).querySelector(".town-change")?.click();

const offered = people(catalog, view).flatMap((lane) => townTasks(catalog, view, lane))
  .filter((id) => !view.mixes.some((m) => m.components.some((c) => c.kind === "card_share" && c.card === id)));
expect("the person-only job is offered", offered.includes(MEND), true);
for (const id of offered) {
  const want = catalog.cards.get(id)?.upside_key;
  if (!want) continue;
  const add = editor.querySelector(`.town-add[data-card="${id}"]`);
  expect(`${id}: its upside is on its Add button`, add?.querySelector(".card-upside")?.textContent, catalog.text.get(want));
}
expect("the mend job reads its name, effect and that it takes nothing", editor.querySelector(`.town-add[data-card="${MEND}"]`)?.textContent, "Mend geargear lasts longerTakes nothing");
