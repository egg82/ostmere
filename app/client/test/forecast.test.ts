// Times the page draws come true by themselves (CONTRACT.txt, "Forecast"; docs/decisions.md, "Leaving and coming
// back always pays"):
// a skill row's time to its next level and a ledger line's "full in" are the view's forecast, never the segment's own
// next_level_at or fills_at; a row with nothing ahead says so; a card waiting on a store the player has never been
// shown draws its countdown alone, with no need row and no When ready.
import { install } from "./fake-dom";
import { testContext } from "./context";
import { fixtureContent, Q } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { Card, View } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { canQueue } from "../src/game/queue";
import { waitsOnUnseen } from "../src/game/ready";
import { UI } from "../src/game/text";
import { CardNeeds } from "../src/ui/cardneeds";
import { Ledger } from "../src/ui/ledger";
import { Skills } from "../src/ui/skills";
import { keepsOf } from "./kept";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const catalog = new Catalog(fixtureContent);
const AT = 100;
const mid = fixtureStep("mid", AT).view;

function rows(view: View): Record<string, { next: string; done: boolean }> {
  const { ctx } = testContext(undefined, catalog);
  const part = new Skills(ctx);
  part.update(view, null);
  part.tick(AT);
  const out: Record<string, { next: string; done: boolean }> = {};
  for (const node of part.root.querySelectorAll<HTMLElement>(".skill")) {
    const name = node.querySelector(".skill-name")?.textContent ?? "";
    out[name] = { next: node.querySelector(".skill-next")?.textContent ?? "", done: node.classList.contains("done-for-now") };
  }
  return out;
}

const foraging = catalog.skillLabel("foraging");
const firecraft = catalog.skillLabel("firecraft");
const next = catalog.skills.get("foraging")?.levels[0];
const pays = catalog.text.fill(next?.pays_key ?? "", catalog.format.figures(next?.change_bp ?? []));

// The control: the forecast's time, not the bar's own next_level_at (both 70 s on here).
expect("foraging: what it pays and the forecast's time", rows(mid)[foraging]?.next,
  catalog.text.fill(UI.skillNextIn, { pays, d: catalog.format.duration(70) }));
{
  const later = { ...mid, forecast: { ...mid.forecast!, level_ups: [{ skill: "foraging", at: AT + 300 }] } };
  expect("the forecast moved, the bar's next_level_at not: the forecast's", rows(later)[foraging]?.next,
    catalog.text.fill(UI.skillNextIn, { pays, d: catalog.format.duration(300) }));
  const none = { ...mid, forecast: { ...mid.forecast!, level_ups: [] } };
  expect("not in the forecast: its pays, no time", rows(none)[foraging]?.next, pays);
}
// firecraft's content has no level marked: nothing ahead, said so, muted.
expect("nothing ahead: no more yet", rows(mid)[firecraft], { next: catalog.text.get(UI.skillNone), done: true });
expect("something ahead: not muted", rows(mid)[foraging]?.done, false);

// "full in": the forecast's time, and none when the forecast has no fill (a rule takes from the store first). Every
// line has been shown before (kept), so each is drawn whatever it is doing now.
function lineEta(view: View, store: string): string {
  const { ctx } = testContext(undefined, catalog);
  const part = new Ledger({ ...ctx, keeps: keepsOf({ ledger_lines: view.ledger.map((l) => l.store) }) });
  part.update(view, null);
  part.tick(AT);
  const node = [...part.root.querySelectorAll<HTMLElement>(".line")]
    .find((n) => n.textContent?.includes(catalog.storeLabel(store)));
  return node?.textContent ?? "(no line)";
}
const fullIn = (s: number) => catalog.text.fill(UI.fills, { d: catalog.format.duration(s) });
expect("warmth: full in the forecast's time", lineEta(mid, "warmth").includes(fullIn(744)), true);
{
  const taken = { ...mid, forecast: { ...mid.forecast!, fills: [] } };
  const text = lineEta(taken, "warmth");
  expect("the line is drawn", text === "(no line)", false);
  expect("no fill forecast: no full-in, though the segment rises", text.includes(fullIn(744)), false);
}

// "empty in": the forecast's time too, and none when the forecast has no emptying (a rule tops the store up first).
const emptyIn = (s: number) => catalog.text.fill(UI.empties, { d: catalog.format.duration(s) });
{
  const uncovered = { ...mid, ledger: mid.ledger.map((l) => (l.store === "wood" ? { ...l, covered: false } : l)) };
  expect("wood: empty in the forecast's time", lineEta(uncovered, "wood").includes(emptyIn(420)), true);
  const toppedUp = { ...uncovered, forecast: { ...mid.forecast!, empties: [] } };
  expect("no emptying forecast: no empty-in, though the segment falls", lineEta(toppedUp, "wood").includes(emptyIn(420)), false);
}

// A card on the night, a store never shown: its countdown only.
const ended = fixtureStep("restoffer", AT).view;
const nightCard: Card = {
  card: "look", completions: 0, cap: 1, bar: { start: AT, start_value: 0, rate: 0, limit: null }, bar_total: 5, by: null,
  completes_at: null, share_bp: 0, run: null, cuts_in: false, spent_store: null, gained: [], tap_s: 5,
  blocker: { condition: { kind: "at_least", watched: { kind: "store_value", store: "night" }, value: 20 * Q, release: 20 * Q }, ready_at: AT + 900 },
  needs: [{ store: "night", quantity: 20 * Q, segment: { start: AT, start_value: 3 * Q, rate: 1, limit: 20 * Q }, gate: null, makers: [], spent: false }],
};
const withNight = { ...ended, cards: [...ended.cards, nightCard] };
expect("waits on an unseen store", waitsOnUnseen(withNight, nightCard), true);
expect("no When ready on it", canQueue(catalog, withNight, nightCard), false);
{
  const seen = { ...withNight, unlocked: [...withNight.unlocked, { category: "store" as const, id: "night" }] };
  expect("control: once the store is shown, When ready again", canQueue(catalog, seen, nightCard), true);
  const { ctx } = testContext(undefined, catalog);
  const needs = new CardNeeds(ctx, "look");
  needs.draw(nightCard, withNight, false);
  needs.tick(nightCard, withNight, AT);
  expect("no need row for the unseen store", needs.root.hidden, true);
  const shown = new CardNeeds(ctx, "look");
  shown.draw(nightCard, seen, false);
  shown.tick(nightCard, seen, AT);
  expect("control: a need row once it is shown", shown.root.hidden, false);
}
