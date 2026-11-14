// A card shows what it is for (CONTRACT.txt, the card panel and {pct}): in the town editor a card's upside sits under
// its name, filled from its change_bp, and a card with none shows none; on the card panel an uncapped card with marks
// shows its runs against the next mark, and its bare count once past the last.
import { fakeDocument, type FakeEl, install } from "./fake-dom";
import { testContext } from "./context";
import { fixtureStep } from "../fixtures/steps";
import { townStep } from "../fixtures/town";
import type { Content, View } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { NewMarks } from "../src/game/marks";
import { Glow } from "../src/ui/fresh";
import { Cards } from "../src/ui/cards";
import { LaneRows } from "../src/ui/lanerows";
import { fixtureContent } from "../fixtures/content";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

function withCard(card: string, over: Partial<Content["card_infos"][number]>, text: Record<string, string> = {}): Catalog {
  return new Catalog({
    ...fixtureContent,
    card_infos: fixtureContent.card_infos.map((c) => (c.card === card ? { ...c, ...over } : c)),
    text_entries: [...fixtureContent.text_entries, ...Object.entries(text).map(([key, value]) => ({ key, text: value }))],
  });
}

{  // the town editor: the upside under the name, from change_bp; none where the card names none
  const catalog = withCard("haul", { upside_key: "up.watch", change_bp: [5000] }, { "up.watch": "{pct} strength while kept" });
  const { ctx } = testContext(new Glow(), catalog);
  const rows = new LaneRows(ctx);
  document.body.replaceChildren(rows.root, rows.town.root);
  rows.update(townStep("town").view);
  (fakeDocument.body.firstElementChild as FakeEl).querySelector(".town-change")?.click();
  const helper = (fakeDocument.body.children[1] as FakeEl).querySelectorAll(".town-person")[0] as FakeEl;
  const rowOf = (card: string): FakeEl => helper.querySelectorAll(".town-card").find((r) => r.dataset.card === card) as FakeEl;
  expect("haul's upside under its name", rowOf("haul").querySelectorAll(".town-card-upside").map((n) => n.textContent), ["+50% strength while kept"]);
  expect("chop names none", rowOf("chop").querySelectorAll(".town-card-upside").length, 0);
}

{  // the card panel: runs against the next mark, then the bare count past the last
  const start = fixtureStep("start", 100).view;
  const lone = start.cards[0]!;
  const catalog = withCard(lone.card, { marks: [500, 2000] });
  const count = (completions: number): string | null => {
    const { ctx } = testContext(new Glow(), catalog);
    const cards = new Cards(ctx, new NewMarks());
    document.body.replaceChildren(cards.root);
    const view: View = { ...start, cards: [{ ...lone, cap: null, completions }] };
    cards.update(view, null);
    return (fakeDocument.body.firstElementChild as FakeEl).querySelector(".card-count")?.textContent ?? null;
  };
  expect("before the first mark", count(312), catalog.format.completions(312, 500));
  expect("on a mark, the next one", count(500), catalog.format.completions(500, 2000));
  expect("past the last, the bare count", count(2500), catalog.format.completions(2500, null));
  expect("the forms differ", catalog.format.completions(312, 500) !== catalog.format.completions(312, null), true);
}
