// Ledger lines join one at a time (ui/ledger.ts, game/shown.ts; docs/design/opening-screen.md, "Ledger and rules"):
// when the ledger arrives it draws only the lines that ask something (red, starved, or carrying an offer); any other
// line joins the first time it is falling (not just from the hands' passing tap), full while something feeds it, or
// covered by a rule. Once drawn a line stays, kept for the account, so a reload keeps it; with nothing kept, the
// lines that ask something still show.
import { install } from "./fake-dom";
import { testContext } from "./context";
import { Q, R } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { LedgerLine, View } from "../src/api/types";
import { Ledger } from "../src/ui/ledger";
import { keepsOf, NEW_FLAT, type Flat } from "./kept";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const AT = 100;
const mid = fixtureStep("mid", AT).view;

/** A line for `store` at `items` of `cap`, its contributions as given (per hour, in items). */
function line(store: string, items: number, cap: number, by: Array<[string, number]>, over: Partial<LedgerLine> = {}): LedgerLine {
  const net = by.reduce((a, [, n]) => a + n * R, 0);
  return {
    store, segment: { start: AT, start_value: items * Q, rate: net, limit: net < 0 ? 0 : net > 0 ? cap * Q : null },
    net_per_hour: net, contributions: by.map(([runner, n]) => ({ runner, per_hour: n * R })),
    empties_at: null, fills_at: null, falling: net < 0, covered: false, starved: false, cap: cap * Q, ...over,
  };
}

/** mid with its ledger replaced by `lines` (plus the Camp store, never a line) and the hands tapping `tapped`. */
function view(lines: LedgerLine[], tapped: string | null = null): View {
  const camp = mid.ledger.filter((l) => l.store === "camp");
  return { ...mid, ledger: [...lines, ...camp], lanes: mid.lanes.map((l) => (l.lane === "hands" ? { ...l, running_card: tapped } : l)) };
}

function ledger(account: Flat = NEW_FLAT): { part: Ledger; sent: Flat[] } {
  const sent: Flat[] = [];
  const { ctx } = testContext();
  const part = new Ledger({ ...ctx, keeps: keepsOf(account, sent) });
  return { part, sent };
}

const drawn = (l: Ledger): string[] => Array.from(l.root.querySelectorAll(".line-name"), (n) => n.textContent ?? "");
const label = (store: string): string => testContext().ctx.catalog.storeLabel(store);

const still = line("stone", 3, 20, []);
const red = line("wood", 14, 40, [["tend", -120]]);   // falling, nothing covers it; the fixture's wood order card answers it
const filling = line("warmth", 38, 100, [["gather", 300]]);
const full = line("warmth", 100, 100, [["gather", 300]]);

{
  const { part, sent } = ledger();
  part.update(view([red, filling, still]), null);
  expect("the ledger arrives with the line that asks something", drawn(part), [label("wood")]);
  part.update(view([red, full, still]), null);
  expect("full while fed: it joins", drawn(part), [label("wood"), label("warmth")]);
  part.update(view([red, filling, still]), null);
  expect("once drawn a line stays", drawn(part), [label("wood"), label("warmth")]);
  expect("each line is kept once, for the account", sent.at(-1)?.ledger_lines, ["wood", "warmth"]);
  expect("sent once per line", sent.length, 2);
}

{
  const { part } = ledger();
  part.update(view([line("warmth", 30, 100, [["look", -60]])], "look"), null);   // no order card for warmth
  expect("drawn down only by the hands' passing tap: not yet", drawn(part), []);
  part.update(view([line("warmth", 30, 100, [["look", -60]])], null), null);
  expect("drawn down by something else: it joins", drawn(part), [label("warmth")]);
}

{
  const { part } = ledger();
  part.update(view([line("stone", 3, 20, [], { covered: true })]), null);
  expect("covered by a rule: it joins", drawn(part), [label("stone")]);
}

{
  const { part } = ledger();
  part.update(view([line("stone", 0, 20, [], { starved: true })]), null);
  expect("starved: it asks something", drawn(part), [label("stone")]);
}

{
  const kept: Flat = { ...NEW_FLAT, ledger_lines: ["wood", "warmth"] };
  const { part } = ledger(kept);
  part.update(view([red, filling, still]), null);
  expect("a reload with the lines kept: they are drawn", drawn(part), [label("wood"), label("warmth")]);
  const fresh = ledger();
  fresh.part.update(view([red, filling, still]), null);
  expect("another device with nothing kept: the line that asks still shows", drawn(fresh.part), [label("wood")]);
}

{
  const { part } = ledger();
  part.update({ ...view([red]), unlocked: mid.unlocked.filter((u) => u.id !== "ledger") }, null);
  expect("before the ledger's feature: nothing", drawn(part), []);
  expect("and the ledger is not drawn", part.root.hidden, true);
}

{  // a hidden store is never drawn, whatever it asks, kept for the account or not
  const clock = line("clock", 0, 12, [["tick", -120]], { starved: true });
  const { part, sent } = ledger();
  part.update(view([red, clock]), null);
  expect("a starved hidden store asks and is not drawn", drawn(part), [label("wood")]);
  expect("and is never kept", sent.at(-1)?.ledger_lines, ["wood"]);
  const kept = ledger({ ...NEW_FLAT, ledger_lines: ["clock", "wood"] });
  kept.part.update(view([red, clock]), null);
  expect("kept for the account, still not drawn", drawn(kept.part), [label("wood")]);
}
