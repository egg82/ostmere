// A countdown is a promise (docs/design/opening-screen.md, "When ready"): a card waiting on a store shows the engine's
// ready time, and offers When ready, only while the page can see that time being kept. A rule on that store that is
// on and lets go below the need stops the store short (day one's lean-to: the dry-wood rule stops at 6 against a need
// of 10), so the card shows its need and maker with no countdown and no When ready.
import { install } from "./fake-dom";
import { fixtureContent, Q } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { Card, Order, View } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { Keeps } from "../src/game/keeps";
import { canQueue } from "../src/game/queue";
import { Screen } from "../src/ui/screen";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

function check(label: string, block: () => void): void {
  try { block(); } catch (e) { throw new Error(`${label}: ${(e as Error).message}`); }
}

const catalog = new Catalog(fixtureContent);
const AT = 100;
const still = (v = 0) => ({ start: AT, start_value: v, rate: 0, limit: null });
/** The lean-to, 2 of 10 stone, the engine's ready time 52 s on. */
const lean: Card = {
  card: "lean_to", completions: 0, cap: 1, bar: still(), bar_total: 20, by: null, completes_at: null, share_bp: 0, run: null, cuts_in: false, spent_store: null, gained: [], tap_s: 20,
  blocker: { condition: { kind: "at_least", watched: { kind: "store_value", store: "stone" }, value: 10 * Q, release: 10 * Q }, ready_at: AT + 52 },
  needs: [{ store: "stone", quantity: 10 * Q, segment: still(2 * Q), gate: null, makers: [], spent: false }],
};
/** "Under 2 stone, until `until`: tap tend", the rule making stone. */
const rule = (until: number): Order => ({
  when: { kind: "at_most", watched: { kind: "store_value", store: "stone" }, value: 2 * Q, release: until * Q },
  then: { kind: "tap_card", card: "tend" },
});
const ended = fixtureStep("restoffer", AT);
const viewWith = (orders: Order[], on: boolean[]): View => ({ ...ended.view, cards: [...ended.view.cards, lean], orders, orders_on: on });

function foot(view: View): string {
  const screen = new Screen(catalog, () => undefined, () => Promise.resolve(null), new Keeps());
  document.body.replaceChildren(screen.root);
  screen.show({ ...ended, view });
  screen.tick(AT);
  const title = catalog.label(catalog.cards.get("lean_to")?.label_key);
  const node = [...screen.root.querySelectorAll(".card")].find((n) => n.querySelector(".card-title")?.textContent === title);
  return node?.querySelector(".card-foot")?.textContent ?? "(no card)";
}
const countdown = catalog.format.duration(52);

// The controls: no rule, a rule that is off, a rule that lets go at or past the need. The engine's time stands.
expect("no rule: When ready", canQueue(catalog, viewWith([], []), lean), true);
expect("no rule: the countdown", foot(viewWith([], [])), countdown);
expect("the rule off: When ready", canQueue(catalog, viewWith([rule(6)], [false]), lean), true);
expect("a rule letting go at the need: When ready", canQueue(catalog, viewWith([rule(10)], [true]), lean), true);
const justUnder: Order = { ...rule(10), when: { ...rule(10).when, release: 10 * Q - 1 } as Order["when"] };
expect("a rule letting go as the store reaches the need (release one unit under): When ready", canQueue(catalog, viewWith([justUnder], [true]), lean), true);
const twoUnder: Order = { ...rule(10), when: { ...rule(10).when, release: 10 * Q - 2 } as Order["when"] };
expect("a rule letting go one unit short: no When ready", canQueue(catalog, viewWith([twoUnder], [true]), lean), false);
expect("a rule on another store: When ready", canQueue(catalog, viewWith([{ ...rule(6), when: { ...rule(6).when, watched: { kind: "store_value", store: "wood" } } as Order["when"] }], [true]), lean), true);

// The rule on, letting go at 6 of 10: the store stops short.
check("a rule stopping short: no When ready", () => {
  expect("no When ready", canQueue(catalog, viewWith([rule(6)], [true]), lean), false);
});
check("a rule stopping short: no countdown", () => {
  const shown = foot(viewWith([rule(6)], [true]));
  expect("no countdown", shown === countdown, false);
  expect("the card is drawn", shown === "(no card)", false);
});

// A card waiting on its store's whole cap: the page draws the forecast's fill, which plays out the rules that take the
// hands from the mix, never ready_at under the current rates (day one's screen: its wattle need is the cap, and the
// hands' tap rules make it a few minutes late). None when the forecast has no fill by its horizon.
const full: Card = { ...lean, blocker: { ...lean.blocker!, ready_at: AT + 52 } };
const line = { store: "stone", segment: { start: AT, start_value: 2 * Q, rate: 1, limit: 10 * Q }, net_per_hour: 1,
  contributions: [], empties_at: null, fills_at: AT + 52, falling: false, covered: false, starved: false, cap: 10 * Q };
const capped = (fills: { store: string; at: number }[], cap = 10): View => ({
  ...viewWith([], []), cards: [...ended.view.cards, full], ledger: [{ ...line, cap: cap * Q }],
  forecast: { horizon_at: AT + 3600, level_ups: [], tops_out: [], fills, empties: [] },
});
check("a need of the whole cap: the forecast's fill", () => {
  expect("the countdown", foot(capped([{ store: "stone", at: AT + 90 }])), catalog.format.duration(90));
  expect("When ready", canQueue(catalog, capped([{ store: "stone", at: AT + 90 }]), full), true);
});
check("a need of the whole cap, no fill by the horizon: no countdown, no When ready", () => {
  expect("no countdown", foot(capped([])) === countdown, false);
  expect("no When ready", canQueue(catalog, capped([]), full), false);
});
check("the control: a need under the cap keeps ready_at", () => {
  expect("the countdown", foot(capped([{ store: "stone", at: AT + 90 }], 12)), countdown);
});
