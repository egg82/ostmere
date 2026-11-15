// A kept bonus shows what its share gives (CONTRACT.txt, {pct}; CardInfo.held): in the town editor a card that holds
// an entry while it runs words that entry at the person's share, rounded down once as the engine rounds it, and the
// figure follows the share as it is stepped; a change the card does not hold stays as served.
import { fakeDocument, type FakeEl, install } from "./fake-dom";
import { testContext } from "./context";
import { townStep } from "../fixtures/town";
import type { Content } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { Glow } from "../src/ui/fresh";
import { LaneRows } from "../src/ui/lanerows";
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
  return () => {
    const helper = (fakeDocument.body.children[1] as FakeEl).querySelectorAll(".town-person")[0] as FakeEl;
    return helper.querySelectorAll(".town-card").find((r) => r.dataset.card === "haul") as FakeEl;
  };
}
const shareOf = (row: FakeEl): string => row.querySelector(".town-card-share")?.textContent ?? "";
const upsideOf = (row: FakeEl): string => row.querySelector(".town-card-upside")?.textContent ?? "";
const held = [{ side: "gap", lane: null, amount_bp: 5000 }];

{  // a held amount is worded at the share, and follows it
  const row = editorRow({ change_bp: [5000], held }, "{pct} strength while kept");
  const share = Number.parseFloat(shareOf(row()));
  expect("the haul share is a percent the test can scale", share > 0 && share < 100, true);
  expect("at its share, not the full amount", upsideOf(row()), `+${share / 2}% strength while kept`);
  row().querySelector(".town-minus")?.click();
  const less = Number.parseFloat(shareOf(row()));
  expect("stepping down moves the share", less < share, true);
  expect("and the figure follows it", upsideOf(row()), `+${less / 2}% strength while kept`);
  row().querySelector(".town-plus")?.click();
  expect("and back", upsideOf(row()), `+${share / 2}% strength while kept`);
}

{  // a change the card does not hold stays as served, beside the one it does
  const row = editorRow({ change_bp: [1500, 5000], held }, "{pct} work, {pct_b} strength");
  const share = Number.parseFloat(shareOf(row()));
  expect("only the held figure scales", upsideOf(row()), `+15% work, +${share / 2}% strength`);
}

{  // a card that holds nothing reads as it always did
  const row = editorRow({ change_bp: [5000], held: [] }, "{pct} strength");
  expect("no held entry, the served figure", upsideOf(row()), "+50% strength");
}

{  // rounded down once, on the whole amount: a figure that does not divide is cut, not rounded
  const row = editorRow({ change_bp: [3333], held: [{ side: "gap", lane: null, amount_bp: 3333 }] }, "{pct} strength");
  const bp = Number.parseFloat(shareOf(row())) * 100;
  expect("the engine's floor", upsideOf(row()), `+${Math.floor((3333 * bp) / 10000) / 100}% strength`);
}
