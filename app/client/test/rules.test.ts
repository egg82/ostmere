// game/orders.ts and the editor's save decisions against the fixture's views: an order card on a hands task becomes a
// rule running a one-task mix (reused when saved), a side-lane task stays a task rule, reordering moves only hands
// rules, and a renamed mix takes its rules with it.
import { fixtureContent, Q } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { Decision, Mix, Order, View } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { saveDecisions } from "../src/game/mix";
import { addRule, chipOf, handsRule, mixRules, moveRule, removeRule, repointRule, ruleFor, ruleRunning, ruleWords, taskRules } from "../src/game/orders";

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const catalog = new Catalog(fixtureContent);
const [woodCard, stoneCard] = fixtureContent.order_cards;
if (!woodCard || !stoneCard) throw new Error("the fixture has two order cards");
const mid = fixtureStep("mid", 100).view;
const list = fixtureStep("orderlist", 100).view;
const ordersOf = (ds: Decision[]) => ds.flatMap((d) => (d.kind === "set_orders" ? [d.orders] : []));

// A hands task: a mix of that card alone, saved under its label, and a rule running it.
const added = addRule(mid, catalog, woodCard);
const solo: Mix = { id: "Gather by hand", components: [{ kind: "card_share", card: "gather", share_bp: 10_000 }] };
expect("hands offer saves a one-task mix", added[0], { kind: "save_mix", mix: solo });
expect("then a rule runs it", ordersOf(added), [[{ when: woodCard.when, then: { kind: "switch_mix", mix_id: solo.id } }]]);

// The same mix already saved: reused, nothing saved.
const withSolo: View = { ...mid, mixes: [...mid.mixes, solo] };
expect("an equal mix is reused", addRule(withSolo, catalog, woodCard).map((d) => d.kind), ["set_orders"]);
// A different mix holding the label: the new one gets a free name.
const taken: View = { ...mid, mixes: [...mid.mixes, { ...solo, components: [{ kind: "card_share", card: "tend", share_bp: 10_000 }] }] };
const renamed = addRule(taken, catalog, woodCard)[0];
expect("a taken name is not reused", renamed?.kind === "save_mix" ? renamed.mix.id : null, "Gather by hand 2");

// A side-lane task stays a task rule.
expect("bench offer is a task rule", ordersOf(addRule(mid, catalog, stoneCard)), [[{ when: stoneCard.when, then: stoneCard.then }]]);

// Finding, wording and grouping rules.
expect("ruleFor finds the rule by its condition", ruleFor(list, woodCard), 0);
expect("ruleFor misses", ruleFor(mid, woodCard), -1);
expect("words", ruleWords(catalog, list.orders[0]!), { when: "Under 10 Dead wood, until 20", action: "Gather by hand" });
expect("a condition that is not on a store is not drawn", ruleWords(catalog, { when: { kind: "after_time", at: 5 }, then: woodCard.then }), null);
expect("hands rules", mixRules(list), [0, 1]);
expect("task rules", taskRules(list), [2]);

// Editing the list.
const moved = moveRule(list, 1, -1);
expect("move up swaps two hands rules, the task rule stays", moved && moved.kind === "set_orders" ? moved.orders : null,
  [list.orders[1], list.orders[0], list.orders[2]]);
expect("the first cannot move up", moveRule(list, 0, -1), null);
expect("the last hands rule cannot move down past a task rule", moveRule(list, 1, 1), null);
const repointed = repointRule(list, 0, "Rest by the fire");
expect("repoint", repointed.kind === "set_orders" ? repointed.orders[0]?.then : null, { kind: "switch_mix", mix_id: "Rest by the fire" });
const removed = removeRule(list, 1);
expect("remove keeps the others", removed.kind === "set_orders" ? removed.orders : null, [list.orders[0], list.orders[2]]);

// The hands doing a rule's task.
const tapping: View = { ...list, lanes: [{ lane: "hands", running_card: "shelter", completes_at: 200, order: null }] };
expect("handsRule needs the rule on and its card on the hands", handsRule(tapping), 2);
expect("handsRule: off", handsRule({ ...tapping, orders_on: [false, false, false] }), -1);

// saveDecisions: a rule's mix edited is saved, not switched to; a rename takes its rules along and deletes the old one.
const rest = list.mixes.find((m) => m.id === "Rest by the fire")!;
expect("editing a rule's mix does not make it the default", saveDecisions(list, rest, rest.id, false).map((d) => d.kind), ["save_mix"]);
const restRenamed = { ...rest, id: "Warm up" };
const ds = saveDecisions(list, restRenamed, rest.id, false);
expect("rename: save, re-point, delete", ds.map((d) => d.kind), ["save_mix", "set_orders", "delete_mix"]);
expect("rename re-points the rule", ordersOf(ds)[0]?.[1]?.then, { kind: "switch_mix", mix_id: "Warm up" });
const own = list.mixes.find((m) => m.id === list.active_mix_id)!;
expect("the player's own mix edited: saved only", saveDecisions(list, own, own.id, false).map((d) => d.kind), ["save_mix"]);
expect("the player's own mix renamed: still the default", saveDecisions(list, { ...own, id: "Day" }, own.id, false).map((d) => d.kind),
  ["save_mix", "switch_mix", "delete_mix"]);
const fresh = { ...own, id: "Night" };
expect("a new mix is saved, not run", saveDecisions(list, fresh, null, false).map((d) => d.kind), ["save_mix"]);
expect("a copy of the player's own (Save as new) is saved, not run", saveDecisions(list, fresh, own.id, true).map((d) => d.kind), ["save_mix"]);
const other = list.mixes.find((m) => m.id !== list.active_mix_id && m.id !== list.running_mix_id && !list.orders.some((o) => o.then.kind === "switch_mix" && o.then.mix_id === m.id));
if (other) expect("another saved mix edited is saved, not run", saveDecisions(list, other, other.id, false).map((d) => d.kind), ["save_mix"]);

// A rule whose condition is a chip's reads as the chip, whatever order its fields come in; one level off and it is a
// store rule again, worded by its numbers.
{
  const tired = fixtureContent.chip_infos.find((c) => c.chip === "tired")!.when;
  const rest: Order = { when: tired, then: { kind: "switch_mix", mix_id: "Rest" } };
  expect("chip words in the list", ruleWords(catalog, rest), { when: "While tired", action: "Rest" });
  expect("chip words on the strip", ruleRunning(catalog, rest), "while tired");
  if (tired.kind === "after_time") throw new Error("a store condition");
  const shuffled = JSON.parse(JSON.stringify({ release: tired.release, watched: tired.watched, value: tired.value, kind: tired.kind })) as Order["when"];
  expect("field order does not matter", chipOf(catalog, shuffled)?.chip, "tired");
  const nudged: Order = { ...rest, when: { ...tired, release: tired.release + Q } };
  expect("one level off reads as numbers", ruleWords(catalog, nudged)?.when, "Under 3 Energy, until 7");
  expect("one level off: the strip's numbers", ruleRunning(catalog, nudged), "until 7 Energy");
  expect("a store rule on the strip", ruleRunning(catalog, list.orders[0]!), "until 20 Dead wood");
}
