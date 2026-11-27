// A rule's guards and fallbacks on the page (docs/design/rule-guards.md, "How the page words it", statements 25 and
// 26; game/guardwords.ts): the rule reads as one sentence ("…, unless {guard}, and unless {guard}"; "{first}, or else
// {next}"), each guard worded as a state; a paused rule's line names where its held guards let go, from
// order_guards[i][j].lets_go, and the store's amount now; a rule with fallbacks says which one it runs, or that none can
// start, and is passed over only when every one is dead.
import { install } from "./fake-dom";
import { fixtureStep } from "../fixtures/steps";
import { BP, Q, TIRED } from "../fixtures/content";
import type { Condition, LedgerLine, Order, OrderGuard, OrderState, View } from "../src/api/types";
import { guardWords, ruleActions, ruleCondition } from "../src/game/condition/guardwords";
import { RulesTab } from "../src/ui/rules/rules";
import { testContext } from "./context";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const { catalog } = testContext().ctx;
const base = fixtureStep("rulestab", 100).view;   // wood (0, Gather by hand), warmth (1), tired (2, its mix runs), bench task (3)
const at = base.at;
const store = (s: string) => ({ kind: "store_value" as const, store: s });
const atLeast = (s: string, value: number, release: number, share = false): Condition =>
  ({ kind: "at_least", watched: store(s), value, release, value_of_cap: share, release_of_cap: share });
const atMost = (s: string, value: number, release: number, share = false): Condition =>
  ({ kind: "at_most", watched: store(s), value, release, value_of_cap: share, release_of_cap: share });
const FULL = atLeast("smoked", BP, BP, true);
const UNDER_5_WOOD = atMost("wood", 5 * Q - 1, 6 * Q - 1);

/** The store `s` holding `items` at the view's time. */
const line = (s: string, items: number): LedgerLine => ({ ...base.ledger.find((l) => l.store === "wood")!, store: s, segment: { start: at, start_value: items * Q, rate: 0, limit: null } });

/** base with rule 0 replaced by `order`, its states, guards and doing as given (the other rules as rulestab has them). */
function withRule(order: Partial<Order>, state: OrderState, guards: OrderGuard[] = [], doing: number | null = 0, extra: Partial<View> = {}): View {
  const orders = [{ ...base.orders[0]!, ...order }, ...base.orders.slice(1)];
  const order_states: OrderState[] = [state, "waiting", "on", "on"];
  return { ...base, orders, order_states, order_guards: orders.map((_, i) => (i === 0 ? guards : [])), order_doing: orders.map((_, i) => (i === 0 ? doing : null)), ...extra };
}

function draw(view: View): { tab: RulesTab; root: HTMLElement; why: () => Record<string, string | null> } {
  const tab = new RulesTab(testContext().ctx);
  document.body.replaceChildren(tab.root);
  tab.update(view);
  const why = () => Object.fromEntries([...tab.root.querySelectorAll<HTMLElement>(".rule-why")].map((n) => [n.dataset.rule!, n.textContent]));
  return { tab, root: tab.root, why };
}
const text = (root: HTMLElement, sel: string, i = 0) => root.querySelectorAll<HTMLElement>(sel)[i]?.textContent ?? null;

// A guard reads as a state, by its subject and its level's form.
{
  const words = (c: Condition) => guardWords(catalog, base, c);
  expect("full", words(FULL), "Smoked is full");
  expect("empty", words(atMost("smoked", 0, 0, true)), "Smoked is empty");
  expect("n or more", words(atLeast("smoked", 10 * Q, 9 * Q)), "Smoked is 10 or more");
  expect("under n", words(atMost("smoked", 10 * Q - 1, 11 * Q - 1)), "Smoked is under 10");
  expect("a share or more", words(atLeast("smoked", 5000, 5000, true)), "Smoked is half or more");
  expect("a share or less", words(atMost("smoked", 2500, 2500, true)), "Smoked is a quarter or less");
  expect("a chip's, by its label", words(TIRED), "tired");
  const count = (n: number): Condition => ({ kind: "at_least", watched: { kind: "card_count", card: "gather" }, value: n, release: n, value_of_cap: false, release_of_cap: false });
  expect("a count", words(count(5)), "Gather by hand is done 5 times");
  expect("a count of one", words(count(1)), "Gather by hand is done");
  expect("a level", words({ kind: "at_least", watched: { kind: "skill_level", skill: "foraging" }, value: 3, release: 3, value_of_cap: false, release_of_cap: false }), "Foraging is level 3 or more");
}

// The sentence: the first guard after "unless", each further one after "and unless"; actions joined by "or else". A
// rule with neither reads as it always did.
{
  const wood = base.orders[0]!;
  expect("no guard: today's words", ruleCondition(catalog, base, wood), "Under 10 Dead wood, until 20");
  expect("one guard", ruleCondition(catalog, base, { ...wood, unless: [FULL] }), "Under 10 Dead wood, until 20, unless Smoked is full");
  expect("two guards", ruleCondition(catalog, base, { ...wood, unless: [FULL, TIRED] }), "Under 10 Dead wood, until 20, unless Smoked is full, and unless tired");
  expect("no fallback: its one action", ruleActions(catalog, base, wood), "Gather by hand");
  expect("a fallback", ruleActions(catalog, base, { ...wood, or_else: [{ kind: "switch_mix", mix_id: "Rest" }] }), "Gather by hand, or else Rest");
  expect("two fallbacks", ruleActions(catalog, base, { ...wood, or_else: [{ kind: "switch_mix", mix_id: "Rest" }, { kind: "switch_mix", mix_id: "Rest by the fire" }] }), "Gather by hand, or else Rest, or else Rest by the fire");
}

// The row draws the sentence: the guards in the condition's button, the fallbacks in the mix's slot; a task rule's
// fallbacks after its arrow.
{
  const view = withRule({ unless: [FULL], or_else: [{ kind: "switch_mix", mix_id: "Rest" }] }, "on", [{ on: false, lets_go: 11 * Q }]);
  view.orders[3] = { ...view.orders[3]!, then: { kind: "tap_card", card: "smoke_catch" }, or_else: [{ kind: "tap_card", card: "smoke_roots" }] };
  const { root } = draw(view);
  expect("the condition with its guard", text(root, ".rules-list .rule-cond-text"), "Under 10 Dead wood, until 20, unless Smoked is full");
  expect("the mix with its fallback", text(root, ".rules-list .rule-slot-name"), "Gather by hand, or else Rest");
  expect("the slot carries its whole wording, which it truncates", root.querySelector<HTMLElement>(".rules-list .rule-slot")?.title, "Gather by hand, or else Rest");
  expect("the task rule's fallback", text(root, ".task-rule .rule-action"), "Smoke the catch, or else Smoke roots");
}

// Paused on a store guard: where it lets go in whole items, from lets_go, and the amount now, which moves with the clock.
{
  const view = withRule({ unless: [FULL] }, "paused", [{ on: true, lets_go: 11 * Q }], null, { ledger: [...base.ledger, { ...line("smoked", 12), segment: { start: at, start_value: 12 * Q, rate: -Q, limit: null } }] });
  const { tab, why } = draw(view);
  expect("paused, an n-or-more guard", why()["0"], "paused until Smoked is under 11 · now 12");
  tab.tick(at + 1);
  expect("now follows the clock", why()["0"], "paused until Smoked is under 11 · now 11");
  // A release between whole items: "under" the whole item at or below it, so the amount shown is never under the
  // level while the rule is still paused.
  const between = { ...view, order_guards: [[{ on: true, lets_go: 10 * Q + Q / 2 }], [], [], []] };
  expect("a release between items", draw(between).why()["0"], "paused until Smoked is under 10 · now 12");
}

// An "under n" guard lets go at the first whole item past lets_go; a guard off a store reads "while"; two held guards
// are joined, and one that does not hold is left out.
{
  const ledger = [...base.ledger.filter((l) => l.store !== "wood"), line("wood", 4)];
  const under = withRule({ unless: [UNDER_5_WOOD] }, "paused", [{ on: true, lets_go: 6 * Q - 1 }], null, { ledger });
  expect("paused, an under guard", draw(under).why()["0"], "paused until Dead wood is 6 or more · now 4");
  // A release on a whole item (a share read off the cap) still holds there: the first whole item past it is the next.
  const onItem = withRule({ unless: [UNDER_5_WOOD] }, "paused", [{ on: true, lets_go: 6 * Q }], null, { ledger });
  expect("a release on a whole item", draw(onItem).why()["0"], "paused until Dead wood is 7 or more · now 4");
  const chip = withRule({ unless: [TIRED] }, "paused", [{ on: true, lets_go: 6 * Q }], null);
  expect("paused, a chip's guard", draw(chip).why()["0"], "paused while tired");
  const both = withRule({ unless: [UNDER_5_WOOD, FULL, TIRED] }, "paused", [{ on: true, lets_go: 6 * Q - 1 }, { on: false, lets_go: 11 * Q }, { on: true, lets_go: null }], null, { ledger });
  expect("two held guards", draw(both).why()["0"], "paused until Dead wood is 6 or more · now 4, and while tired");
}

// A paused task rule's dot is off, though its condition holds.
{
  const view = withRule({}, "on");
  view.orders[3] = { ...view.orders[3]!, unless: [FULL] };
  view.order_states = ["on", "waiting", "on", "paused"];
  view.order_guards = [[], [], [], [{ on: true, lets_go: 11 * Q }]];
  expect("orders_on still says its condition holds", view.orders_on[3], true);
  expect("no dot on a paused task rule", text(draw(view).root, ".task-rule .selector-dot"), "");
}

// A rule with fallbacks that is on: nothing said while it runs its first, the one it runs past it, or that none can
// start; passed over only with every action dead. A rule with no fallback says none of these.
{
  const fallback = { or_else: [{ kind: "switch_mix" as const, mix_id: "Rest" }] };
  expect("running its first", draw(withRule(fallback, "on", [], 0)).why()["0"], undefined);
  expect("running a fallback", draw(withRule(fallback, "on", [], 1)).why()["0"], "on now · Rest");
  expect("none can start", draw(withRule(fallback, "on", [], null)).why()["0"], "on now · nothing it lists can start yet");
  expect("every action dead", draw(withRule(fallback, "passed_over", [], null)).why()["0"], "passed over · every task it lists is done");
  expect("no fallback, nothing running", draw(withRule({}, "on", [], null)).why()["0"], undefined);
  expect("no fallback, passed over as today", draw(withRule({}, "passed_over", [], null)).why()["0"], "passed over · a task it runs is done");
}

// The row is greyed only when every mix it lists is greyed.
{
  const fallback = { or_else: [{ kind: "switch_mix" as const, mix_id: "Rest" }] };
  const row = (greyed: string[]) => draw(withRule(fallback, "on", [], 1, { greyed_mix_ids: greyed })).root.querySelector(".rules-row")!.classList.contains("greyed");
  expect("one alive", row(["Gather by hand"]), false);
  expect("all greyed", row(["Gather by hand", "Rest"]), true);
}
