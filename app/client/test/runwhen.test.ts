// Run when…: a store rule built and read back for both tests, the levels a store allows and where a new rule starts,
// the wording with and without a band, finding a rule whose levels were changed, writing and editing in place,
// refusing a duplicate, drawing "reaches" rules, and the step that opens writing rules (a rule seen on, then off).
import { fixtureContent, Q } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { Order, View } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { mixRules, ruleExists, ruleFor, ruleLetGo, ruleWords, setRule, taskRules } from "../src/game/orders";
import { whenChoices } from "../src/game/ruleoffers";
import { draftWhen } from "../src/ui/conditiondraft";
import { bounds, buildRule, clampRule, defaultRule, readRule, ruleUntil, ruleWhen, type StoreRule } from "../src/game/storerule";

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const catalog = new Catalog(fixtureContent);
const below: StoreRule = { store: "wood", test: "below", n: 3, m: 8 };
const reaches: StoreRule = { store: "wood", test: "reaches", n: 12, m: 6 };

// Built: each crossing on the amount the page shows (floor of quantity / Q).
expect("below builds at_most n·Q−1, release m·Q−1", buildRule(below, Q),
  { kind: "at_most", watched: { kind: "store_value", store: "wood" }, value: 3 * Q - 1, release: 8 * Q - 1 });
expect("reaches builds at_least n·Q, release m·Q", buildRule(reaches, Q),
  { kind: "at_least", watched: { kind: "store_value", store: "wood" }, value: 12 * Q, release: 6 * Q });
expect("below reads back", readRule(buildRule(below, Q), Q), below);
expect("reaches reads back", readRule(buildRule(reaches, Q), Q), reaches);
for (let cap = 2; cap <= 20; cap++) {
  for (const test of ["below", "reaches"] as const) {
    const r = defaultRule("wood", test, cap);
    expect(`default ${test} cap ${cap} round-trips`, readRule(buildRule(r, Q), Q), r);
    const c = buildRule(r, Q);
    if (c.kind === "after_time") throw new Error("a store rule");
    const always = c.kind === "at_most" ? c.value >= cap * Q : c.value <= 0;
    expect(`default ${test} cap ${cap} is never always true`, always, false);
    expect(`default ${test} cap ${cap} has a band of an item or more`, Math.abs(c.release - c.value) >= Q, true);
  }
}

// An order card's plain threshold (release == value) reads as a rule with no band; with a release, as one with a band.
const card = (value: number, release: number): Order["when"] => ({ kind: "at_most", watched: { kind: "store_value", store: "wood" }, value: value * Q, release: release * Q });
expect("a content threshold with no release has no band", readRule(card(2, 2), Q), { store: "wood", test: "below", n: 2, m: null });
expect("a content threshold with a release", readRule(card(2, 6), Q), { store: "wood", test: "below", n: 2, m: 6 });
expect("a skill level is not a store rule", readRule({ kind: "at_least", watched: { kind: "skill_level", skill: "foraging" }, value: 3, release: 3 }, Q), null);

// Levels a store allows; defaults; clamping.
expect("below on 12", bounds("below", 12, 3), { n: [1, 11], m: [4, 12] });
expect("reaches on 12", bounds("reaches", 12, 12), { n: [2, 12], m: [1, 11] });
expect("a store under two items allows no rule", [bounds("below", 1, 1), bounds("reaches", 1, 1)], [null, null]);
expect("default below on 12", defaultRule("wood", "below", 12), below);
expect("default reaches on 12", defaultRule("wood", "reaches", 12), reaches);
expect("default below on 2", defaultRule("wood", "below", 2), { store: "wood", test: "below", n: 1, m: 2 });
expect("default reaches on 2", defaultRule("wood", "reaches", 2), { store: "wood", test: "reaches", n: 2, m: 1 });
expect("n past the cap comes back, m follows it", clampRule({ ...below, n: 40, m: 3 }, 12), { store: "wood", test: "below", n: 11, m: 12 });
expect("reaches m can't pass n", clampRule({ ...reaches, n: 5, m: 9 }, 12), { ...reaches, n: 5, m: 4 });
expect("no band opens with until at the default", clampRule({ store: "wood", test: "below", n: 2, m: null }, 12), { store: "wood", test: "below", n: 2, m: 7 });

// Words.
expect("below with until", ruleWhen(catalog, below), "Under 3 Dead wood, until 8");
expect("reaches with until", ruleWhen(catalog, reaches), "12 or more Dead wood, until under 6");
expect("below with no band", ruleWhen(catalog, { ...below, m: null }), "Under 3 Dead wood");
expect("reaches with no band", ruleWhen(catalog, { ...reaches, m: null }), "12 or more Dead wood");
expect("strip: below", ruleUntil(catalog, below), "until 8 Dead wood");
expect("strip: reaches", ruleUntil(catalog, reaches), "until under 6 Dead wood");
expect("strip: no band, while under", ruleUntil(catalog, { ...below, m: null }), "while under 3 Dead wood");

// Finding, writing and editing rules.
const [woodCard] = fixtureContent.order_cards;
if (!woodCard) throw new Error("the fixture has an order card");
const list = fixtureStep("orderlist", 100).view;
const edited: View = { ...list, orders: list.orders.map((o, i) => (i === 0 ? { ...o, when: buildRule({ store: "wood", test: "below", n: 4, m: 9 }, Q) } : o)) };
expect("ruleFor finds a rule whose levels were changed", ruleFor(edited, woodCard), 0);
const high: View = { ...list, orders: [{ ...list.orders[0]!, when: buildRule({ store: "wood", test: "reaches", n: 30, m: 20 }, Q) }] };
expect("ruleFor does not take a reaches rule for a below card", ruleFor(high, woodCard), -1);

const evening: Order = { when: buildRule(below, Q), then: { kind: "switch_mix", mix_id: "Evening" } };
const added = setRule(list, null, evening);
expect("a new rule is the lowest priority", added.kind === "set_orders" ? added.orders : null, [...list.orders, evening]);
const changed = setRule(list, 1, evening);
expect("an edit keeps its place", changed.kind === "set_orders" ? changed.orders : null, [list.orders[0], evening, list.orders[2]]);
expect("a rule identical to another is a duplicate", ruleExists(list, null, list.orders[1]!), true);
expect("a rule is not its own duplicate", ruleExists(list, 1, list.orders[1]!), false);
expect("same condition, another mix: not a duplicate", ruleExists(list, null, { ...list.orders[1]!, then: { kind: "switch_mix", mix_id: "Evening" } }), false);

const written = fixtureStep("written", 100).view;
expect("reaches rules are drawn: hands", mixRules(written), [0, 1]);
expect("reaches rules are drawn: tasks", taskRules(written), [2]);
expect("an after_time rule is not drawn", mixRules({ ...written, orders: [{ when: { kind: "after_time", at: 5 }, then: { kind: "switch_mix", mix_id: "Evening" } }] }), []);
expect("an old rule with no band reads without until", ruleWords(catalog, written.orders[0]!)?.when, "Under 10 Dead wood");
expect("a reaches rule's words", ruleWords(catalog, written.orders[1]!)?.when, "80 or more Warmth, until under 40");

// The step that opens writing rules: a rule seen on, then off, the same rule in the same place.
const on: View = { ...list, orders_on: [true, false, false] };
const off: View = { ...list, orders_on: [false, false, false] };
expect("on then off", ruleLetGo(on, off), true);
expect("off then on is not it", ruleLetGo(off, on), false);
expect("staying on is not it", ruleLetGo(on, on), false);
expect("a rule removed is not it", ruleLetGo(on, { ...off, orders: list.orders.slice(1), orders_on: [false, false] }), false);
expect("a rule replaced in that place is not it", ruleLetGo(on, { ...off, orders: [evening, ...list.orders.slice(1)] }), false);

// The condition editor on a rule whose store has no ledger line (a chip's, on energy): that store's chip is drawn
// (pressed, as the rule's), after the stores a rule may watch; a new rule never offers it.
{
  const restrule = fixtureStep("restrule", 100).view;
  const stores = (editing: string | null) => whenChoices(catalog, restrule, true, null, editing).stores;
  const watchable = stores(null);
  expect("a new rule: only stores with a line", watchable.includes("energy"), false);
  expect("editing the energy rule: energy last", stores("energy"), [...watchable, "energy"]);
  expect("editing a wood rule: no extra", stores("wood"), watchable);
}

// Saving a rule edited back to the levels it opened at keeps its own condition: a chip's still reads as the chip, and a
// content card's exact threshold is not rebuilt one unit lower. Any other levels build a store rule.
{
  const tired = fixtureContent.chip_infos.find((c) => c.chip === "tired")!.when;
  const opened = readRule(tired, Q)!;
  expect("unchanged: the chip's own condition", draftWhen(opened, { rule: opened, when: tired }, Q), tired);
  expect("unchanged, built, would not be the chip's", JSON.stringify(buildRule(opened, Q)) === JSON.stringify(tired), false);
  const moved = { ...opened, m: (opened.m ?? opened.n) + 1 };
  expect("changed: built from the levels", draftWhen(moved, { rule: opened, when: tired }, Q), buildRule(moved, Q));
  expect("a new rule: built", draftWhen(opened, undefined, Q), buildRule(opened, Q));
}
