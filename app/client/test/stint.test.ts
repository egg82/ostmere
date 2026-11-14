// Goal stints (ui/stint.ts, game/queue.ts; CONTRACT.txt, "Goal stints"): the editor lists the dry run's unmet goals
// and queues the mix until the picked row's `until`; Next names a stint by mix and goal, and the running one states
// when its goal lands, or never, with the line that binds it.
import { install } from "./fake-dom";
import { fixtureStep } from "../fixtures/steps";
import { Catalog } from "../src/game/catalog";
import { fixtureContent, Q } from "../fixtures/content";
import type { Condition, GoalRow, QueueEntry, View } from "../src/api/types";
import { controllingEntry, queueStint, shareUntil, stintRow } from "../src/game/queue";
import { stintFacts, stintParts, stintWords } from "../src/ui/stint";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const catalog = new Catalog(fixtureContent);
const R = fixtureContent.scales.rate_per_item_hour;
const H = 3600;
const base = fixtureStep("rulestab", 100, { orders: [], extra: [] }).view;
const woodUntil = { kind: "at_least" as const, watched: { kind: "store_value" as const, store: "wood" }, value: 30 * Q, release: 30 * Q, value_of_cap: false, release_of_cap: false };
const levelUntil = { kind: "at_least" as const, watched: { kind: "skill_level" as const, skill: "foraging" }, value: 4, release: 4, value_of_cap: false, release_of_cap: false };
const wood = (lands: number | null, over: Partial<GoalRow> = {}): GoalRow => ({
  kind: "store", store: "wood", skill: null, target: 30 * Q, lands_at: lands, per_hour: 60 * R, limit: null, until: woodUntil, ...over,
});
const level = (lands: number | null): GoalRow => ({
  kind: "level", store: null, skill: "foraging", target: 4, lands_at: lands, per_hour: 120 * R, limit: null, until: levelUntil,
});
const stint = (mix: string, until: Condition = woodUntil): QueueEntry => ({ verb: { kind: "switch_mix", mix_id: mix }, until });
const view = (over: Partial<View>): View => ({ ...base, ...over });

// queuing: the stint goes at the end of the queue, its until the row's own
{
  const v = view({ queue: [stint("a", levelUntil)] });
  expect("queued at the end", queueStint(v, "b", wood(100 + H).until), { kind: "set_queue", entries: [stint("a", levelUntil), stint("b")] });
}

// a row is found by its until alone: kind, subject, value
{
  const v = view({ goal_rows: [level(100 + H), wood(100 + 2 * H)] });
  expect("store row", stintRow(v, woodUntil)?.store, "wood");
  expect("level row", stintRow(v, levelUntil)?.skill, "foraging");
  expect("another value", stintRow(v, { ...woodUntil, value: 31 * Q, release: 31 * Q }), null);
}

// the controlling entry passes over a switch to a greyed mix
expect("first live", controllingEntry(view({ queue: [stint("a"), stint("b")], greyed_mix_ids: ["a"] })), 1);
expect("none", controllingEntry(view({ queue: [] })), null);

// Next: "{mix} until {goal}", from the row when it is in view, else from the until itself
{
  const v = view({ queue: [stint("a")], goal_rows: [wood(100 + H)] });
  expect("words from the row", stintWords(catalog, v, stint("a")), "a until Dead wood 30");
  expect("words without a row", stintWords(catalog, view({ goal_rows: [] }), stint("a", levelUntil)), "a until Foraging 4");
}

// the running stint's facts: in, or never, and what binds it; none for an entry that does not run
{
  const runs = view({ queue: [stint("a")], goal_rows: [wood(100 + H)], running_mix_id: "a", mix_order: null });
  expect("lands in", stintFacts(catalog, runs, 0), "in 1 h · Dead wood +1/min");
  const never = { ...runs, goal_rows: [wood(null, { per_hour: 0, limit: { store: "stone", in_per_hour: 30 * R } })] };
  expect("never, limited", stintFacts(catalog, never, 0), "never · limited by Flint, +0.5/min");
  expect("a rule's mix runs", stintFacts(catalog, { ...runs, mix_order: 0 }, 0), null);
  expect("not controlling", stintFacts(catalog, { ...runs, queue: [stint("b"), stint("a")] }, 1), null);
}

// the editor's list: closed is the button alone; open lists the unmet goals with their times; a pick hands the row
{
  const after = view({ goal_rows: [wood(100), level(100 + 2 * H)] });
  expect("closed", stintParts(catalog, after, false, false, () => {}, () => {}).length, 1);
  let picked: Condition | null = null;
  const [button, list] = stintParts(catalog, after, true, false, () => {}, (u) => { picked = u; });
  expect("button", button?.textContent, "Run until…");
  const goals = Array.from(list?.children ?? []) as HTMLElement[];
  expect("the met goal is left out", goals.map((g) => g.textContent), ["Foraging 42 h"]);
  goals[0]?.click();
  expect("picked: the row's until", picked, level(100 + 2 * H).until);
  expect("disabled lists nothing", stintParts(catalog, after, true, true, () => {}, () => {}).length, 1);
}

// a store's goal also offers that store's named shares not yet reached; a share until is worded by its share and is
// never taken for a row with the same numbers
{
  const after = view({ goal_rows: [wood(100 + H)] });
  let picked: Condition | null = null;
  const [, list] = stintParts(catalog, after, true, false, () => {}, (u) => { picked = u; });
  const [row, shares] = Array.from(list?.children ?? []) as HTMLElement[];
  expect("the goal, then its shares", [row?.className, shares?.className], ["stint-goal", "stint-shares"]);
  const marks = Array.from(shares?.querySelectorAll(".cond-preset") ?? []) as HTMLElement[];
  expect("full is offered, by name for a screen reader", marks.at(-1)?.getAttribute("aria-label"), "Dead wood at full");
  marks.at(-1)?.click();
  expect("picked: full, as a share", picked, shareUntil("wood", 10000));
  const full = stint("a", shareUntil("wood", 10000));
  expect("Next words a share", stintWords(catalog, view({ goal_rows: [] }), full), "a until Dead wood at full");
  expect("a share is not a row's amount", stintRow(view({ goal_rows: [{ ...wood(100), until: { ...woodUntil, value: 10000, release: 10000 } }] }), full.until), null);
}
