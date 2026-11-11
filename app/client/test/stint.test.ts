// Goal stints (ui/stint.ts, game/queue.ts; CONTRACT.txt, "Goal stints"): the editor lists the dry run's unmet goals
// and queues the mix until the picked row's `until`; Next names a stint by mix and goal, and the running one states
// when its goal lands, or never, with the line that binds it.
import { install } from "./fake-dom";
import { fixtureStep } from "../fixtures/steps";
import { Catalog } from "../src/game/catalog";
import { fixtureContent, Q } from "../fixtures/content";
import type { Condition, GoalRow, QueueEntry, View } from "../src/api/types";
import { controllingEntry, queueStint, stintRow } from "../src/game/queue";
import { stintFacts, stintParts, stintWords } from "../src/ui/stint";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const catalog = new Catalog(fixtureContent);
const R = fixtureContent.scales.rate_per_item_hour;
const H = 3600;
const base = fixtureStep("rulestab", 100, { orders: [], extra: [] }).view;
const woodUntil = { kind: "at_least" as const, watched: { kind: "store_value" as const, store: "wood" }, value: 30 * Q, release: 30 * Q };
const levelUntil = { kind: "at_least" as const, watched: { kind: "skill_level" as const, skill: "foraging" }, value: 4, release: 4 };
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
  expect("queued at the end", queueStint(v, "b", wood(100 + H)), { kind: "set_queue", entries: [stint("a", levelUntil), stint("b")] });
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
  let picked: GoalRow | null = null;
  const [button, list] = stintParts(catalog, after, true, false, () => {}, (r) => { picked = r; });
  expect("button", button?.textContent, "Run until…");
  const goals = Array.from(list?.children ?? []) as HTMLElement[];
  expect("the met goal is left out", goals.map((g) => g.textContent), ["Foraging 42 h"]);
  goals[0]?.click();
  expect("picked", (picked as GoalRow | null)?.skill, "foraging");
  expect("disabled lists nothing", stintParts(catalog, after, true, true, () => {}, () => {}).length, 1);
}
