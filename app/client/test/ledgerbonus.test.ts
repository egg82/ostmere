// A store that only feeds a bonus (StoreInfo.bonus_bp: its eaters hold a lane speed while they run) is never drawn as
// an alarm and names no drain; dry, it says the bonus is off, with the bonus as a number (ui/ledger.ts; CONTRACT.txt,
// the ledger's white and red). Any other store keeps the red and "ran dry".
import { install } from "./fake-dom";
import { testContext } from "./context";
import { fixtureContent, Q, R } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { LedgerLine, View } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { Ledger } from "../src/ui/ledger";
import { keepsOf, NEW_FLAT } from "./kept";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const AT = 100;
const mid = fixtureStep("mid", AT).view;

function line(store: string, items: number, by: Array<[string, number]>, over: Partial<LedgerLine> = {}): LedgerLine {
  const net = by.reduce((a, [, n]) => a + n * R, 0);
  return {
    store, segment: { start: AT, start_value: items * Q, rate: net, limit: net < 0 ? 0 : null },
    net_per_hour: net, contributions: by.map(([runner, n]) => ({ runner, per_hour: n * R })),
    empties_at: null, fills_at: null, falling: net < 0, covered: false, starved: false, cap: 20 * Q, ...over,
  };
}

function view(lines: LedgerLine[]): View {
  return { ...mid, ledger: [...lines, ...mid.ledger.filter((l) => l.store === "camp")] };
}

const bonusContent = { ...fixtureContent, store_infos: fixtureContent.store_infos.map((s) => (s.store === "stone" ? { ...s, bonus_bp: 1500 } : s)) };

function ledger(content = bonusContent): Ledger {
  const { ctx } = testContext(undefined, new Catalog(content));
  return new Ledger({ ...ctx, keeps: keepsOf(NEW_FLAT, []) });
}

function drawn(part: Ledger, store: string): { alarm: boolean; eta: string } {
  const row = Array.from(part.root.querySelectorAll(".line")).find((n) => n.querySelector(".line-name")?.textContent === new Catalog(bonusContent).storeLabel(store));
  if (!row) throw new Error(`no line for ${store}`);
  return { alarm: row.classList.contains("alarm"), eta: row.querySelector(".line-eta")?.textContent ?? "" };
}

const dryStone = line("stone", 0, [], { starved: true });
const fallingStone = line("stone", 3, [["tend", -1]]);

{
  const part = ledger();
  part.update(view([dryStone]), null);
  part.tick(AT);
  expect("a dry bonus store is not an alarm", drawn(part, "stone").alarm, false);
  expect("and says the bonus is off, with its number", drawn(part, "stone").eta, "ran dry · +15% work speed off");
}

{
  const part = ledger();
  part.update(view([fallingStone]), null);
  part.tick(AT);
  expect("a falling bonus store is not an alarm", drawn(part, "stone").alarm, false);
  expect("and names no drain", drawn(part, "stone").eta.includes("·"), false);
}

{
  const part = ledger(fixtureContent);
  part.update(view([dryStone]), null);
  part.tick(AT);
  expect("control: the same dry store without a bonus is an alarm", drawn(part, "stone").alarm, true);
  expect("and reads ran dry", drawn(part, "stone").eta, "ran dry");
}
