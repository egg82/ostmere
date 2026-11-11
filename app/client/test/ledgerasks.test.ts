// On a phone the ledger sits after every task card, so the lines that ask for something (red) or say the extra is lost
// (full) are drawn apart, in `Ledger.asks` above the cards; the other lines stay in the ledger. On a desktop nothing is
// split. The same rows move, so the story mark and the line's state come from the one drawing (ui/ledger.ts).
import { install } from "./fake-dom";
import { testContext } from "./context";
import { Q, R } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { LedgerLine, View } from "../src/api/types";
import { Ledger } from "../src/ui/ledger";
import { keepsOf, NEW_FLAT } from "./kept";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const AT = 100;
const mid = fixtureStep("mid", AT).view;

function line(store: string, items: number, cap: number, by: Array<[string, number]>, over: Partial<LedgerLine> = {}): LedgerLine {
  const net = by.reduce((a, [, n]) => a + n * R, 0);
  return {
    store, segment: { start: AT, start_value: items * Q, rate: net, limit: net < 0 ? 0 : net > 0 ? cap * Q : null },
    net_per_hour: net, contributions: by.map(([runner, n]) => ({ runner, per_hour: n * R })),
    empties_at: null, fills_at: null, falling: net < 0, covered: false, starved: false, cap: cap * Q, ...over,
  };
}

function view(lines: LedgerLine[]): View {
  return { ...mid, ledger: [...lines, ...mid.ledger.filter((l) => l.store === "camp")] };
}

const names = (root: Element): string[] =>
  Array.from(root.querySelectorAll(".line-name"), (n) => n.textContent ?? "");
const label = (store: string): string => testContext().ctx.catalog.storeLabel(store);

const red = line("wood", 14, 40, [["tend", -120]]);
const full = line("warmth", 100, 100, [["gather", 300]]);
const quiet = line("stone", 3, 20, [], { covered: true });   // joins (covered by a rule) but asks nothing

function ledger(): Ledger {
  const { ctx } = testContext();
  return new Ledger({ ...ctx, keeps: keepsOf(NEW_FLAT, []) });
}

{
  const part = ledger();
  part.setSplit(true);
  part.update(view([red, full, quiet]), null);
  part.tick(AT);
  expect("a phone: the red and the full line are above the cards", names(part.asks), [label("wood"), label("warmth")]);
  expect("and the quiet one stays in the ledger", names(part.root), [label("stone")]);
  expect("the ledger is still drawn for it", part.root.hidden, false);
  const alarm = part.asks.querySelector(".line.alarm");
  expect("the red line keeps its drawing (alarm class)", alarm !== null, true);
}

{
  const part = ledger();
  part.setSplit(true);
  part.update(view([quiet]), null);
  part.tick(AT);
  expect("nothing asks: nothing above the cards", names(part.asks), []);
  expect("the quiet line is in the ledger", names(part.root), [label("stone")]);
}

{
  const part = ledger();
  part.setSplit(true);
  part.update(view([red]), null);
  expect("only asking lines: the ledger itself has nothing to show", part.root.hidden, true);
  expect("the line is above the cards", names(part.asks), [label("wood")]);
}

{
  const part = ledger();
  part.setSplit(true);
  part.update(view([red, quiet]), null);
  part.setSplit(false);
  expect("a desktop: nothing above the cards", names(part.asks), []);
  expect("every line in the ledger, in its order", names(part.root), [label("wood"), label("stone")]);
}

{
  const part = ledger();
  part.update(view([red, full, quiet]), null);
  part.tick(AT);
  expect("unsplit from the start: all lines in the ledger", names(part.root), [label("wood"), label("warmth"), label("stone")]);
  expect("and none above the cards", names(part.asks), []);
}

{
  const part = ledger();
  part.setSplit(true);
  const filling = line("warmth", 38, 100, [["gather", 300]]);
  part.update(view([red, filling, quiet]), null);
  part.tick(AT);
  expect("a line still filling is not full: it stays", names(part.asks), [label("wood")]);
  part.update(view([red, full, quiet]), null);
  part.tick(AT);
  expect("it moves up once full", names(part.asks), [label("wood"), label("warmth")]);
}
