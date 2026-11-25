// Kinds of one card drawn as one (game/variants.ts, ui/kindpick.ts; CONTRACT.txt, "Cards"): a lead with two kinds in view
// shows one, a picker of both on it, and a pick changes which; one kind alone draws plainly.
import { install } from "./fake-dom";
import { fixtureStep } from "../fixtures/steps";
import { fixtureContent } from "../fixtures/content";
import { Catalog } from "../src/game/catalog";
import type { Card, View } from "../src/api/types";
import { kindLabel, kindsByLead, shownKind } from "../src/game/variants";
import { KindPicks } from "../src/ui/kindpick";
import { testContext } from "./context";
import { Glow } from "../src/ui/fresh";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const content = { ...fixtureContent, card_infos: fixtureContent.card_infos.map((c) => (c.card === "smoke_catch" || c.card === "smoke_roots" ? { ...c, variant_of: "smoke_catch" } : c)) };
const catalog = new Catalog(content);
const base = fixtureStep("rulestab", 100).view;
const like = base.cards[0]!;
const as = (card: string, by: Card["by"] = null): Card => ({ ...like, card, by });
const at = (cards: Card[], running: string | null = null): View => ({ ...base, cards, lanes: running === null ? base.lanes : [...base.lanes, { lane: "smoke", running_card: running, completes_at: null, order: null }] as View["lanes"] });

const both = [as("gather"), as("smoke_catch"), as("smoke_roots")];
expect("a lead with two kinds in view", [...kindsByLead(catalog, both)].map(([lead, ks]) => [lead, ks.map((k) => k.card)]), [["smoke_catch", ["smoke_catch", "smoke_roots"]]]);
expect("one kind alone has no picker", kindsByLead(catalog, [as("gather"), as("smoke_roots")]).size, 0);
const kinds = kindsByLead(catalog, both).get("smoke_catch")!;
expect("the first kind with nothing picked or at work", shownKind(at(both), kinds, null), "smoke_catch");
expect("a kind a lane runs", shownKind(at(both, "smoke_roots"), kinds, null), "smoke_roots");
{
  const mixed = [as("smoke_catch"), as("smoke_roots", "mix")];
  expect("a kind a mix holds", shownKind(at(mixed), kindsByLead(catalog, mixed).get("smoke_catch")!, null), "smoke_roots");
}
expect("the picked kind over one at work", shownKind(at(both, "smoke_roots"), kinds, "smoke_catch"), "smoke_catch");
expect("a pick no longer in view is passed over", shownKind(at(both), kinds, "gone"), "smoke_catch");
expect("a kind is named by the store it makes", kindLabel(catalog, "smoke_roots"), "Smoked");

{
  const rows = new Map(both.map((c) => [c.card, { node: document.createElement("div") }]));
  let applied = 0;
  const marks = { has: () => false, clear: () => undefined };
  const picks: KindPicks = new KindPicks(testContext(new Glow(), catalog).ctx, marks, () => { applied += 1; picks.apply(rows, at(both)); });
  picks.apply(rows, at(both));
  const hidden = (): string[] => [...rows].filter(([, r]) => r.node.hidden).map(([id]) => id);
  expect("the other kind is hidden, a card of its own is not", hidden(), ["smoke_roots"]);
  const picker = rows.get("smoke_catch")!.node.querySelector(".variant-pick");
  const buttons = [...(picker?.querySelectorAll<HTMLButtonElement>(".variant-option") ?? [])];
  expect("one button per kind, the shown one pressed", buttons.map((b) => [b.dataset.card, b.getAttribute("aria-pressed")]), [["smoke_catch", "true"], ["smoke_roots", "false"]]);
  buttons[1]!.dispatchEvent(new Event("click"));
  expect("a pick redraws", applied, 1);
  expect("the picked kind shows", hidden(), ["smoke_catch"]);
  expect("the picker moves to it", rows.get("smoke_roots")!.node.querySelector(".variant-pick") !== null, true);
  picks.apply(rows, at([as("gather"), as("smoke_roots")]));
  expect("down to one kind, nothing is hidden", hidden(), []);
}
