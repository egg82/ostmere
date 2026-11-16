// A kept bonus shows what its share gives (CONTRACT.txt, {pct}; CardInfo.kept): in the town editor a card that holds
// an entry while it runs words that entry at the person's share, rounded down once as the engine rounds it, and the
// figure follows the share as it is dragged; a change the card does not hold stays as served.
import { fakeDocument, type FakeEl, install, pointer } from "./fake-dom";
import { testContext } from "./context";
import { townStep } from "../fixtures/town";
import type { Content } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { Glow } from "../src/ui/fresh";
import { makeRow } from "../src/ui/cardrow";
import { LaneRows } from "../src/ui/lanerows";
import { WhenReady } from "../src/ui/whenready";
import { fixtureContent } from "../fixtures/content";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

function withCard(card: string, over: Partial<Content["card_infos"][number]>, text: Record<string, string>): Catalog {
  return new Catalog({
    ...fixtureContent,
    card_infos: fixtureContent.card_infos.map((c) => (c.card === card ? { ...c, ...over } : c)),
    text_entries: [...fixtureContent.text_entries, ...Object.entries(text).map(([key, value]) => ({ key, text: value }))],
  });
}

/** Opens the town editor on haul with the given info and returns its row. */
function editorRow(over: Partial<Content["card_infos"][number]>, text: string): () => FakeEl {
  const catalog = withCard("haul", { upside_key: "up.kept", ...over }, { "up.kept": text });
  const { ctx } = testContext(new Glow(), catalog);
  const rows = new LaneRows(ctx);
  document.body.replaceChildren(rows.root, rows.town.root);
  rows.update(townStep("town").view);
  (fakeDocument.body.firstElementChild as FakeEl).querySelector(".town-change")?.click();
  for (const track of fakeDocument.body.children[1]?.querySelectorAll(".share-track") ?? []) track.rect = { left: 0, top: 0, width: 1000, height: 20, right: 1000, bottom: 20 };
  return () => {
    const helper = (fakeDocument.body.children[1] as FakeEl).querySelectorAll(".town-person")[0] as FakeEl;
    return helper.querySelectorAll(".town-card").find((r) => r.dataset.card === "haul") as FakeEl;
  };
}
const shareOf = (row: FakeEl): string => row.querySelector(".town-card-share")?.textContent ?? "";
/** The helper's chop|haul divider dragged from x0 to x1 on a 1000px bar. */
function drag(x0: number, x1: number): void {
  const helper = (fakeDocument.body.children[1] as FakeEl).querySelectorAll(".town-person")[0] as FakeEl;
  const divider = helper.querySelector(".share-divider") as FakeEl;
  divider.dispatchEvent(pointer("pointerdown", x0, 10));
  divider.dispatchEvent(pointer("pointermove", x1, 10));
  divider.dispatchEvent(pointer("pointerup", x1, 10));
}
const upsideOf = (row: FakeEl): string => row.querySelector(".town-card-upside")?.textContent ?? "";
const held = [{ side: "gap", lane: null, amount_bp: 5000, slot: 0 }];

{  // a held amount is worded at the share, and follows it
  const row = editorRow({ change_bp: [5000], kept: held }, "{pct} strength while kept");
  const share = Number.parseFloat(shareOf(row()));
  expect("the haul share is a percent the test can scale", share > 0 && share < 100, true);
  expect("at its share, not the full amount", upsideOf(row()), `+${share / 2}% strength while kept`);
  drag(600, 700);   // chop takes from haul
  const less = Number.parseFloat(shareOf(row()));
  expect("dragging down moves the share", less < share, true);
  expect("and the figure follows it", upsideOf(row()), `+${less / 2}% strength while kept`);
  drag(700, 600);
  expect("and back", upsideOf(row()), `+${share / 2}% strength while kept`);
}

{  // a change the card does not hold stays as served, beside the one it does
  const row = editorRow({ change_bp: [1500, 5000], kept: [{ ...held[0]!, slot: 1 }] }, "{pct} work, {pct_b} strength");
  const share = Number.parseFloat(shareOf(row()));
  expect("only the held figure scales", upsideOf(row()), `+15% work, +${share / 2}% strength`);
}

{  // a card that holds nothing reads as it always did
  const row = editorRow({ change_bp: [5000], kept: [] }, "{pct} strength");
  expect("no held entry, the served figure", upsideOf(row()), "+50% strength");
}

{  // rounded down once, on the whole amount: a figure that does not divide is cut, not rounded
  const row = editorRow({ change_bp: [3333], kept: [{ side: "gap", lane: null, amount_bp: 3333, slot: 0 }] }, "{pct} strength");
  const bp = Number.parseFloat(shareOf(row())) * 100;
  expect("the engine's floor", upsideOf(row()), `+${Math.floor((3333 * bp) / 10000) / 100}% strength`);
}

{  // an unscaled change equal to a held amount stays as served: only the held slot scales
  const row = editorRow({ change_bp: [5000, 5000], kept: [{ ...held[0]!, slot: 1 }] }, "{pct} work, {pct_b} strength");
  const share = Number.parseFloat(shareOf(row()));
  expect("the equal change at another slot is not scaled", upsideOf(row()), `+50% work, +${share / 2}% strength`);
}

{  // a card's face is worded at its share too (sideface.test.ts holds the rest of it)
  const catalog = withCard("haul", { upside_key: "up.kept", change_bp: [5000], kept: held }, { "up.kept": "{pct} strength while kept" });
  const { ctx } = testContext(new Glow(), catalog);
  const card = townStep("town").view.cards.find((c) => c.card === "haul");
  if (!card) throw new Error("the town fixture has no haul");
  const row = makeRow(ctx, new WhenReady(ctx), { ...card, share_bp: 4000 });
  expect("at its share", row.node.querySelector(".card-upside")?.textContent, "+20% strength while kept");
}
