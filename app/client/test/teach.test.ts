// Day one's teaching cues (game/teach.ts, ui/cardneeds.ts): a build waiting on a store nothing at work
// makes the switch-mix lesson's subject (a saved mix that makes it, or the card that Edit adds; switchlesson.test.ts); a build that will be ready by
// itself gets no cue; and a tap of a short need two cards in play make lights both, the choice of what to smoke.
import { install } from "./fake-dom";
import { testContext } from "./context";
import { dayOneStep } from "../fixtures/dayone";
import { fixtureContent } from "../fixtures/content";
import type { Card, Mix, View } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { switchCue } from "../src/game/teach";
import { CardNeeds } from "../src/ui/cardneeds";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const catalog = new Catalog(fixtureContent);
const builds = dayOneStep("whenready", 100).view;   // larder short of flint (ready at a time), lean-to short of wood (not)
const running = builds.running_mix_id!;
const others = builds.mixes.filter((m) => m.id !== running && m.id !== builds.active_mix_id);
const woodMix = others.find((m) => m.components.some((c) => c.kind === "card_share" && c.card === "gather"))!;
const only = (mixes: Mix[]): View => ({ ...builds, mixes });

// Where the switch cue points.
expect("a saved mix makes the wood: the Mixes list", switchCue(catalog, builds), { build: "lean_to", store: "wood", to: "mixes", mix: woodMix.id });
expect("not before the end", switchCue(catalog, { ...builds, ended_at: null }), null);
const runningOnly = only(builds.mixes.filter((m) => m.id === running));
expect("only the running mix: Edit (its maker is in play)", switchCue(catalog, runningOnly), { build: "lean_to", store: "wood", to: "edit", card: "gather" });
expect("no maker in play: none", switchCue(catalog, { ...runningOnly, cards: runningOnly.cards.filter((c) => c.card !== "gather") }), null);
expect("a greyed mix is no answer", switchCue(catalog, { ...builds, greyed_mix_ids: others.map((m) => m.id) }), { build: "lean_to", store: "wood", to: "edit", card: "gather" });
const own = builds.mixes.find((m) => m.id === builds.active_mix_id)!;
expect("the player's own mix, while a rule's holds the hands, is no answer (its Run is off)", switchCue(catalog, only([own, ...builds.mixes.filter((m) => m.id === running)])), { build: "lean_to", store: "wood", to: "edit", card: "gather" });
const nest: Mix = { id: "Outer", components: [{ kind: "sub_mix", mix_id: woodMix.id, share_bp: 10_000 }] };
const innerRunning: View = { ...builds, running_mix_id: woodMix.id, mixes: [woodMix, nest] };   // it holds the hands, yet makes no wood now
expect("a mix nesting the maker counts; the running one is never the answer", switchCue(catalog, innerRunning), { build: "lean_to", store: "wood", to: "mixes", mix: "Outer" });
expect("the running mix alone: Edit", switchCue(catalog, { ...innerRunning, mixes: [woodMix] }), { build: "lean_to", store: "wood", to: "edit", card: "gather" });
const lean = builds.cards.find((c) => c.card === "lean_to")!;
const timed: Card = { ...lean, blocker: { ...lean.blocker!, ready_at: 900 } };
expect("a build that will be ready by itself: no cue", switchCue(catalog, { ...builds, cards: builds.cards.map((c) => (c.card === "lean_to" ? timed : c)) }), null);
const action: Card = { ...lean, card: "gather" };
expect("work done again and again is no build", switchCue(catalog, { ...builds, cards: [...builds.cards.filter((c) => c.card !== "lean_to"), action] }), null);

// What to smoke: a tap of Take stock's short smoked need lights both smoke tasks (Need.makers), with no words added.
{
  const rising = dayOneStep("rising", 100).view;
  const stock = rising.cards.find((c) => c.card === "take_stock")!;
  const { ctx, got } = testContext();
  const needs = new CardNeeds(ctx, "take_stock");
  needs.draw(stock, rising, false);
  needs.tick(stock, rising, 100);
  const rows = (): HTMLElement[] => [...needs.root.querySelectorAll<HTMLElement>(".card-need")];
  expect("no maker named", rows().map((n) => n.textContent ?? ""), ["Smoked 2/6", "Roots 6/15"]);
  const marked = (): string[] => [...needs.root.querySelectorAll(".need-have")].map((n) => n.textContent ?? "");
  expect("short: only the number it has is marked", marked(), ["2", "6"]);
  rows()[0]!.click();
  expect("a tap of the smoked row lights both smoke tasks", got.lit, [["smoke_catch", "smoke_roots"]]);
  rows()[1]!.click();
  expect("a row with no maker served lights nothing", got.lit.length, 1);
  needs.tick({ ...stock, blocker: null }, rising, 100);
  rows()[0]!.click();
  expect("not short (ready): nothing marked, and a tap lights nothing", [marked(), got.lit.length], [[], 1]);
}
