// The page's trips (docs/design/banked-time-plan.md, item 6): a trip is a card known by its id. The figure is away
// while one runs on a tap and for its share of each cycle while it runs mixed; its completions go to the chronicle and its
// finds (triggers with lines, no card) to the band; and nothing on the page totals what a cap lost.
import { Q, fixtureContent } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { Card, LogLine, View } from "../src/api/types";
import { awayLines } from "../src/game/awaylines";
import { Catalog } from "../src/game/catalog";
import { UI } from "../src/game/text";
import { SceneFacts, TURN_ROUND_S } from "../src/scene/conditions";
import { Glow } from "../src/ui/fresh";
import { Ledger } from "../src/ui/ledger";
import { install } from "./fake-dom";
import { testContext } from "./context";
import { keepsOf, NEW_FLAT } from "./kept";

install();
function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const AT = 1_000;
const base = fixtureStep("mid", AT).view;
const template = base.cards.find((c) => c.card === "gather")!;
const trip = (extra: Partial<Card>): Card => ({ ...template, card: "far_hunt", cap: null, share_bp: 0, run: null, by: null, ...extra });
const mixed = (card: string, share_bp: number): Card => ({ ...template, card, cap: null, share_bp, run: "full", by: "mix" });
const away = "running:far_hunt|mix:far_hunt";

// Tapped: the hands lane runs the trip, so the figure is away; with the hands on another card it is not.
{
  const tapped: View = { ...base, lanes: base.lanes.map((l) => (l.lane === "hands" ? { ...l, running_card: "far_hunt" } : l)), cards: [trip({})] };
  const facts = new SceneFacts();
  facts.observe(tapped);
  expect("tapped trip: figure away", facts.holds(away, AT, Q), true);
  facts.observe({ ...tapped, lanes: tapped.lanes.map((l) => ({ ...l, running_card: "gather" })) });
  expect("another card tapped: figure not away", facts.holds(away, AT, Q), false);
}

// Mixed: away for the trip's share of a round, in whole turns beside the other cards, and never both at once.
{
  const view: View = { ...base, cards: [mixed("far_hunt", 2500), mixed("gather", 7500)] };
  const facts = new SceneFacts();
  facts.observe(view);
  let tripS = 0;
  for (let i = 0; i < TURN_ROUND_S * 10 * 4; i++) if (facts.holds(away, i / 4, Q)) tripS += 0.25;
  expect("mixed trip: seconds away in ten rounds", tripS, TURN_ROUND_S * 10 * 0.25);
  facts.observe({ ...view, cards: [mixed("far_hunt", 0), mixed("gather", 7500)] });
  let none = 0;
  for (let t = 0; t < TURN_ROUND_S; t++) if (facts.holds(away, t, Q)) none++;
  expect("a trip with no share is never away", none, 0);
}

// Arrivals: an uncapped trip's completions go to the chronicle, its finds (a trigger's line, no card) play on the band.
{
  const catalog = new Catalog(fixtureContent);
  const lines: LogLine[] = [{ at: 3000, seq: 0, key: "trip.done", card: "far_hunt" }, { at: 3001, seq: 1, key: "find.1", card: null }];
  const view: View = { ...base, cards: [trip({})] };
  expect("trip completion and find", awayLines(catalog, lines, view, { ...base, cards: [] }), ["chronicle", "band"]);
  const capped: View = { ...base, cards: [trip({ cap: 3 })] };
  expect("control: a capped card's line plays", awayLines(catalog, lines.slice(0, 1), capped, base)[0], "band");
}

// Nothing totals a cap's loss: a full store fed by a maker reads "full", and no figure on its line is the maker's gross.
// The line is as the engine serves one at its cap: the segment flat at the cap, the net 0, the maker still listed.
function ledgerTexts(view: View, extra = ""): string[] {
  const { ctx } = testContext(new Glow(), new Catalog(fixtureContent));
  const part = new Ledger({ ...ctx, keeps: keepsOf(NEW_FLAT) });
  part.update(view, null);
  part.tick(view.at);
  return [...Array.from(part.root.querySelectorAll(".ledger-lines span"), (n) => n.textContent ?? ""), extra];
}
{
  const R = 1_000;
  const gross = 300 * R;
  const wood = base.ledger.find((l) => l.store === "wood")!;
  const atCap = { ...wood, store: "warmth", segment: { start: AT, start_value: 100 * Q, rate: 0, limit: null }, net_per_hour: 0,
    contributions: [{ runner: "gather", per_hour: gross }], empties_at: null, fills_at: null, falling: false, covered: false,
    starved: false, cap: 100 * Q };
  const camp = base.ledger.filter((l) => l.store === "camp");
  const full: View = { ...base, ledger: [atCap, ...camp] };
  const catalog = new Catalog(fixtureContent);
  const made = catalog.format.perMinute(gross);
  const leaks = (texts: string[]): boolean => texts.some((t) => t.includes(made));
  expect("a full store's line says full", ledgerTexts(full).includes(catalog.text.get(UI.full)), true);
  expect("the maker's gross is nowhere on the line", leaks(ledgerTexts(full)), false);
  expect("control: a line that totalled production would be caught", leaks(ledgerTexts(full, `lost ${made}`)), true);
}
