// A card shows what it is for where its share is set (contract/, the card panel and {pct}): on a person's page a
// card's upside sits on its face, filled from its change_bp, and a card with none shows none.
import { install } from "../../fake-dom";
import { pageRig } from "./personrig";
import { townStep } from "../../../fixtures/town";
import type { Content } from "../../../src/api/types";
import { Catalog } from "../../../src/game/page/catalog";
import { fixtureContent } from "../../../fixtures/content";

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

{  // the upside under the name, from change_bp; none where the card names none
  const catalog = withCard("haul", { upside_key: "up.watch", change_bp: [5000] }, { "up.watch": "{pct} strength while kept" });
  const { open, face } = pageRig(townStep("town").view, catalog);
  open(0);
  expect("haul's upside on its face", face("haul").querySelectorAll(".card-upside").map((n) => n.textContent), ["+50% strength while kept"]);
  expect("chop names none", face("chop").querySelectorAll(".card-upside").length, 0);
}
