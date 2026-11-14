// A store the player's own rule draws down, as the rule means to, is covered (docs/design/redesign.md, "Ledger": a row
// turns red only when its store is falling with nothing covering it). "As it means to" is read off the rule and the view:
// the rule is on, its condition is "n or more" of that store, and a card it runs is among what takes from the store.
// No button stands under a ledger row: a row a rule watches carries a quiet mark, and tapping the row opens that rule.
// A covering rule that cannot keep up says why on the row: empty by the forecast while a rule "under n" wants the store
// held, or full with more coming in while a rule "n or more" wants it taken.
import { install } from "./fake-dom";
import { testContext } from "./context";
import { fixtureContent, Q, R } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { LedgerLine, Order, OrderState, View } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { UI } from "../src/game/text";
import { Ledger } from "../src/ui/ledger";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const AT = 100;
const catalog = new Catalog(fixtureContent);
const mid = fixtureStep("mid", AT).view;   // wood falling, drawn down by tend, nothing covering it; forecast: wood empties at AT + 420

const SMOKE: Order = { when: { kind: "at_least", watched: { kind: "store_value", store: "catch" }, value: 2 * Q, release: Q }, then: { kind: "tap_card", card: "smoke_catch" } };
const KEEP_WOOD: Order = { when: { kind: "at_most", watched: { kind: "store_value", store: "wood" }, value: 10 * Q - 1, release: 20 * Q - 1 }, then: { kind: "switch_mix", mix_id: "Gather by hand" } };
const KEEP_CATCH: Order = { ...SMOKE, when: { kind: "at_most", watched: { kind: "store_value", store: "catch" }, value: 2 * Q - 1, release: 4 * Q - 1 } };

function line(store: string, items: number, by: Array<[string, number]>, over: Partial<LedgerLine> = {}): LedgerLine {
  const net = by.reduce((a, [, n]) => a + n * R, 0);
  return {
    store, segment: { start: AT, start_value: items * Q, rate: net, limit: net < 0 ? 0 : net > 0 ? 6 * Q : null },
    net_per_hour: net, contributions: by.map(([runner, n]) => ({ runner, per_hour: n * R })),
    empties_at: null, fills_at: null, falling: net < 0, covered: false, starved: false, cap: 6 * Q, ...over,
  };
}

/** mid with the smoke task in play and `lines` in place of its own of the same store, under `orders` standing as `states`. */
function view(lines: LedgerLine[], orders: Order[] = [], states: OrderState[] = []): View {
  return {
    ...mid, orders, order_states: states, orders_on: states.map((s) => s === "on"),
    unlocked: [...mid.unlocked, { category: "card", id: "smoke_catch" }, { category: "store", id: "catch" }],
    ledger: [...mid.ledger.filter((l) => !lines.some((n) => n.store === l.store)), ...lines],
  };
}

function draw(v: View) {
  const { ctx, got } = testContext();
  const part = new Ledger(ctx);
  document.body.replaceChildren(part.root);
  part.update(v, null);
  part.tick(AT);
  const row = (store: string): HTMLElement => {
    const n = Array.from(part.root.querySelectorAll<HTMLElement>(".line")).find((x) => x.querySelector(".line-name")?.textContent === catalog.storeLabel(store));
    if (!n) throw new Error(`no line for ${store}`);
    return n;
  };
  const shown = (store: string) => {
    const r = row(store);
    const mark = r.querySelector<HTMLElement>(".line-rule");
    const edit = r.querySelector<HTMLElement>(".line-edit");
    return { alarm: r.classList.contains("alarm"), mark: mark !== null && !mark.hidden, edit: edit !== null && !edit.hidden, eta: r.querySelector(".line-eta")?.textContent ?? "" };
  };
  return { part, got, row, shown, offers: () => part.root.querySelectorAll(".line-order").length };
}

const behind = (task: string): string => catalog.text.fill("ui.ledger.behind", { task });
const empties = (s: number): string => catalog.text.fill(UI.empties, { d: catalog.format.duration(s) });

// The owner's case: a rule smoking the catch while there is some, until under one, draws the catch down as it means to.
const smoking = line("catch", 4, [["smoke_catch", -4]]);
{
  const d = draw(view([smoking], [SMOKE], ["on"]));
  expect("spent by its own rule: not red", d.shown("catch").alarm, false);
  expect("no row and no button under it", d.offers(), 0);
  expect("the quiet mark, nothing else", [d.shown("catch").mark, d.shown("catch").edit], [true, false]);
  expect("and no reason: the rule is doing what it says", d.shown("catch").eta.includes(behind(catalog.cardLabel("smoke_catch"))), false);
  d.row("catch").click();
  expect("tapping the row opens that rule", d.got.opened, [0]);
}

// Controls: red stays for a store falling with nothing covering it.
expect("no rule: red", draw(view([smoking])).shown("catch").alarm, true);
expect("the rule waiting (not what draws it down): red", draw(view([smoking], [SMOKE], ["waiting"])).shown("catch").alarm, true);
expect("the rule on, but another task takes the store: red", draw(view([line("catch", 4, [["tend", -4]])], [SMOKE], ["on"])).shown("catch").alarm, true);
expect("a rule that keeps the store stocked does not cover by spending: red",
  draw(view([smoking], [KEEP_CATCH], ["on"])).shown("catch").alarm, true);
expect("no rule: no mark", draw(view([smoking])).shown("catch").mark, false);

// A red line whose store a rule watches: still no button under it; the mark opens the rule.
{
  const d = draw(view([], [KEEP_WOOD], ["waiting"]));   // mid's wood: falling, drawn by tend, the rule's mix not making it
  expect("red, the rule not covering it", d.shown("wood").alarm, true);
  expect("no Change under it, no Edit mix in it", [d.offers(), d.shown("wood").edit, d.shown("wood").mark], [0, false, true]);
  d.row("wood").click();
  expect("the row opens the rule", d.got.opened, [0]);
}

// A covering rule that cannot keep up says why, once, on the row.
{
  const wood = { ...mid.ledger.find((l) => l.store === "wood")!, covered: true };   // the rule's mix makes wood, and the forecast still empties it
  const d = draw(view([wood], [KEEP_WOOD], ["on"]));
  expect("covered: white", d.shown("wood").alarm, false);
  expect("empty while the rule wants it held: says why", d.shown("wood").eta, `${empties(420)} · ${behind("Gather by hand")}`);
  const kept = draw({ ...view([wood], [KEEP_WOOD], ["on"]), forecast: { ...mid.forecast!, empties: [] } });
  expect("control: the forecast keeps it: no reason", kept.shown("wood").eta, "");
}
{
  const full = line("catch", 6, [["gather", 6], ["smoke_catch", -4]]);
  const d = draw(view([full], [SMOKE], ["on"]));
  expect("full with more coming in while the rule takes: says why", d.shown("catch").eta, `${catalog.text.get(UI.full)} · ${behind(catalog.cardLabel("smoke_catch"))}`);
  expect("control: full with no rule on it says only full", draw(view([full])).shown("catch").eta, catalog.text.get(UI.full));
}
