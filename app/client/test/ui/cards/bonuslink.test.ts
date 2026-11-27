// A kept bonus leads to the strength it feeds (CardInfo.kept[].side; docs/decisions/principles.md, "Make what is already
// there tappable before adding words"): on a person's page a task's bonus line, and on a card's face its upside, is a
// button once a fight of that side is served, and a tap opens that side's strength sheet, the same rows the fight's own
// strength figure opens. With no fight showing (the feature off, or none served) it is plain text.
import { fakeDocument, type FakeEl, install } from "../../fake-dom";
import { testContext } from "../../context";
import { pageRig, type PageRig } from "../town/personrig";
import { fightsStep } from "../../../fixtures/fights";
import { townStep } from "../../../fixtures/town";
import type { Content, View } from "../../../src/api/types";
import { Catalog } from "../../../src/game/page/catalog";
import { Cards } from "../../../src/ui/cards/cards";
import { Glow } from "../../../src/ui/feedback/fresh";
import { NewMarks } from "../../../src/game/lessons/marks";
import { fixtureContent } from "../../../fixtures/content";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const kept = [{ side: "hands", lane: null, amount_bp: 5000, slot: 0 }];
function withCard(card: string, over: Partial<Content["card_infos"][number]>): Catalog {
  return new Catalog({
    ...fixtureContent,
    card_infos: fixtureContent.card_infos.map((c) => (c.card === card ? { ...c, ...over } : c)),
    text_entries: [...fixtureContent.text_entries, { key: "up.kept", text: "{pct} strength while kept" }],
  });
}
const fought = fightsStep("fight", 100).view;
const sheet = ["Your hands", "base strength6", "Hatchet+50%", "Foraging+25%", "Stool50%+12.5%", "Cold×0.8"];
const texts = (nodes: FakeEl[]): string[] => nodes.map((n) => n.textContent);

/** A person's page open on a view with the haul card keeping the hands' strength; its settle and haul face. */
function editor(view: View): { row: () => FakeEl; rig: PageRig } {
  const rig = pageRig(view, withCard("haul", { upside_key: "up.kept", change_bp: [5000], kept }));
  rig.open(0);
  return { row: () => rig.face("haul"), rig };
}
const town = townStep("town").view;
const withFights: View = { ...town, fights: fought.fights, unlocked: [...town.unlocked, { category: "feature", id: "combat" }] };

{  // a fight of the side is served: the line is a button, and a tap opens that side's strength under it
  const { row, rig } = editor(withFights);
  const link = row().querySelector("button.bonus-link");
  expect("the line is a button", link?.textContent.endsWith("strength while kept"), true);
  expect("shut until tapped", row().querySelector(".fight-entries")?.hidden, true);
  expect("and says so", link?.getAttribute("aria-expanded"), "false");
  link?.click();
  expect("a tap opens the side's strength", texts(row().querySelectorAll(".fight-entries li")), sheet);
  expect("and says so open", row().querySelector(".bonus-link")?.getAttribute("aria-expanded"), "true");
  rig.rows.update(withFights);
  expect("a new view redraws the face, the sheet stays open", texts(row().querySelectorAll(".fight-entries li")), sheet);
  row().querySelector(".bonus-link")?.click();
  expect("a second tap shuts it", row().querySelector(".fight-entries")?.hidden, true);
}

{  // no fight showing for the side: plain text, nothing to tap
  const { row } = editor({ ...withFights, fights: [] });
  expect("no fight served: no button", row().querySelector("button.bonus-link"), null);
  expect("the words stay", row().querySelector(".card-upside")?.textContent.endsWith("strength while kept"), true);
  const { row: off } = editor({ ...withFights, unlocked: town.unlocked });
  expect("combat off: no button", off().querySelector("button.bonus-link"), null);
}

{  // a card's face: its upside leads to the same strength, beside the tap and not inside it
  const catalog = withCard("poultice", { upside_key: "up.kept", change_bp: [5000], kept });
  const { ctx } = testContext(new Glow(), catalog);
  const cards = new Cards(ctx, new NewMarks());
  document.body.replaceChildren(cards.root);
  const off: View = { ...fought, unlocked: fought.unlocked.filter((u) => u.id !== "combat") };
  cards.update(off, null);
  const face = (): FakeEl => (fakeDocument.body.firstElementChild as FakeEl).querySelectorAll(".card").find((c) => c.dataset.card === "poultice") as FakeEl;
  expect("no fight showing: plain upside", face().querySelector("button.bonus-link"), null);
  expect("its words are on the card", face().querySelector(".card-upside")?.textContent, "+50% strength while kept");
  cards.update(fought, off);
  const link = face().querySelector("button.bonus-link");
  expect("a fight of the side is served: a button", link?.textContent, "+50% strength while kept");
  expect("beside the tap, not inside it", face().querySelector(".card-tap .bonus-link"), null);
  link?.click();
  expect("a tap opens the side's strength", texts(face().querySelectorAll(".bonus .fight-entries li")), sheet);
  cards.update(fought, fought);
  expect("a new view keeps the button and the sheet", [face().querySelector(".bonus-link") === link, texts(face().querySelectorAll(".bonus .fight-entries li"))], [true, sheet]);
}
