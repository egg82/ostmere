// A card that holds a side while it runs says what it gives at its share of the mix on its face, where the share is set
// (docs/decisions/combat.md, "A card that holds a side"; contract/, {pct}): the face draws the held figure at
// Card.share_bp, rounded down once as the engine rounds it, and the full figure while the card holds no share of the mix.
// The strength sheet's row for it is the served entry, share beside amount (bonuslink.test.ts).
import { fakeDocument, type FakeEl, install } from "./fake-dom";
import { testContext } from "./context";
import { fightsStep } from "../fixtures/fights";
import type { Content, View } from "../src/api/types";
import { Catalog } from "../src/game/page/catalog";
import { NewMarks } from "../src/game/lessons/marks";
import { Cards } from "../src/ui/cards/cards";
import { Glow } from "../src/ui/feedback/fresh";
import { fixtureContent } from "../fixtures/content";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

function withPoultice(over: Partial<Content["card_infos"][number]>): Catalog {
  return new Catalog({
    ...fixtureContent,
    card_infos: fixtureContent.card_infos.map((c) => (c.card === "poultice" ? { ...c, ...over } : c)),
    text_entries: [...fixtureContent.text_entries, { key: "up.kept", text: "{pct} strength, {pct_b} work" }],
  });
}
const held = [{ side: "hands", lane: null, amount_bp: 5000, slot: 0 }];
const fought = fightsStep("fight", 100).view;
const at = (share: number): View => ({ ...fought, cards: fought.cards.map((c) => (c.card === "poultice" ? { ...c, share_bp: share } : c)) });

function face(catalog: Catalog): { cards: Cards; words: () => string } {
  const { ctx } = testContext(new Glow(), catalog);
  const cards = new Cards(ctx, new NewMarks());
  document.body.replaceChildren(cards.root);
  const words = (): string => ((fakeDocument.body.firstElementChild as FakeEl).querySelectorAll(".card").find((c) => c.dataset.card === "poultice") as FakeEl).querySelector(".card-upside")?.textContent ?? "";
  return { cards, words };
}

{  // a side-holder: the held figure at its share, following the mix; the other figure as served
  const { cards, words } = face(withPoultice({ upside_key: "up.kept", change_bp: [5000, 1500], kept: held }));
  cards.update(at(0), null);
  expect("no share of the mix: the full figure", words(), "+50% strength, +15% work");
  cards.update(at(4000), at(0));
  expect("40% of the mix: 40% of the held figure", words(), "+20% strength, +15% work");
  cards.update(at(2500), at(4000));
  expect("a new split moves it", words(), "+12.5% strength, +15% work");
  cards.update(at(0), at(2500));
  expect("out of the mix: back to the full figure", words(), "+50% strength, +15% work");
}

{  // the engine's floor, once
  const { cards, words } = face(withPoultice({ upside_key: "up.kept", change_bp: [3333, 0], kept: [{ side: "hands", lane: null, amount_bp: 3333, slot: 0 }] }));
  cards.update(at(5000), null);
  expect("rounded down, not up", words(), "+16.66% strength, 0% work");
}

{  // a card that holds nothing keeps the served figure at any share
  const { cards, words } = face(withPoultice({ upside_key: "up.kept", change_bp: [5000, 1500], kept: [] }));
  cards.update(at(4000), null);
  expect("served as it is", words(), "+50% strength, +15% work");
}
