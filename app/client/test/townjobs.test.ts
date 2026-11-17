// Every job a person can be given shows what it does where it is chosen (docs/decisions/principles.md, "Progress is stated,
// never hinted"): on a person's page each task's face carries its upside, as a card face does on the Tasks page, including
// a job the player never holds as a card of their own (a card of a person's lane).
import { install } from "./fake-dom";
import { pageRig } from "./personrig";
import { townStep } from "../fixtures/town";
import { fixtureContent } from "../fixtures/content";
import type { Content, View } from "../src/api/types";
import { Catalog } from "../src/game/catalog";

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

const { open, face } = pageRig(view, catalog);
const page = open(0);
const lane = catalog.laneOf(MEND);
const offered = view.cards.filter((c) => catalog.laneOf(c.card) === lane).map((c) => c.card);
expect("the person-only job is offered", offered.includes(MEND) && page.querySelectorAll(".person-cards .card").some((c) => c.dataset.card === MEND), true);
for (const id of offered) {
  const want = catalog.cards.get(id)?.upside_key;
  if (!want) continue;
  expect(`${id}: its upside is on its face`, face(id).querySelector(".card-upside")?.textContent, catalog.text.get(want));
}
const mend = face(MEND);
expect("the mend job reads its name, effect and that it takes nothing", [".card-title", ".card-upside", ".card-need.nothing"].map((q) => mend.querySelector(q)?.textContent), ["Mend gear", "gear lasts longer", "Takes nothing"]);
